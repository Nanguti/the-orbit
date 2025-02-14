from typing import Set, Dict, List, Any, Generator
from collections import defaultdict
import re
from concurrent.futures import ThreadPoolExecutor

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.job_ids = set()  # Store job IDs that match this pattern

class SearchIndex:
    def __init__(self):
        self.title_trie = TrieNode()
        self.skill_trie = TrieNode()
        self.industry_map = defaultdict(set)  # Industry -> job_ids
        self.location_map = defaultdict(set)  # Location -> job_ids
        self.jobs = {}  # job_id -> job_data
        self.next_id = 0
        self._bulk_buffer = []
        self._bulk_size = 1000
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def _insert_into_trie(self, trie: TrieNode, text: str, job_id: int):
        """Insert word into trie and associate with job_id"""
        words = set(re.findall(r'\w+', text.lower()))
        for word in words:
            node = trie
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
                node.job_ids.add(job_id)
            node.is_end = True
    
    def _search_trie(self, trie: TrieNode, pattern: str) -> Set[int]:
        """Search for pattern in trie and return matching job_ids"""
        pattern = pattern.lower()
        node = trie
        for char in pattern:
            if char not in node.children:
                return set()
            node = node.children[char]
        return node.job_ids

    def add_job(self, job: Dict[str, Any]) -> int:
        """Add job to search index"""
        job_id = self.next_id
        self.next_id += 1
        
        # Store job data
        self.jobs[job_id] = job
        
        # Index title and position
        title_text = f"{job['title']} {job['position']}"
        self._insert_into_trie(self.title_trie, title_text, job_id)
        
        # Index skills
        for skill in job['tech_skills']:
            self._insert_into_trie(self.skill_trie, skill, job_id)
        
        # Index industry and location
        self.industry_map[job['industry'].lower()].add(job_id)
        self.location_map[job['location'].lower()].add(job_id)
        
        return job_id

    def bulk_add_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """Bulk add jobs to index"""
        # Process jobs in parallel
        with self._executor:
            job_ids = list(self._executor.map(self.add_job, jobs))
            
        # Bulk update tries
        self._bulk_update_tries(jobs, job_ids)
        
    def _bulk_update_tries(self, jobs: List[Dict[str, Any]], job_ids: List[int]) -> None:
        """Update tries in bulk"""
        title_updates = defaultdict(set)
        skill_updates = defaultdict(set)
        
        for job, job_id in zip(jobs, job_ids):
            # Process title words
            title_text = f"{job['title']} {job['position']}"
            words = set(re.findall(r'\w+', title_text.lower()))
            for word in words:
                title_updates[word].add(job_id)
            
            # Process skills
            for skill in job['tech_skills']:
                skill_words = set(re.findall(r'\w+', skill.lower()))
                for word in skill_words:
                    skill_updates[word].add(job_id)
        
        # Bulk update tries
        self._bulk_update_trie(self.title_trie, title_updates)
        self._bulk_update_trie(self.skill_trie, skill_updates)

    def _bulk_update_trie(self, trie: TrieNode, updates: Dict[str, Set[int]]) -> None:
        """Update trie with bulk updates"""
        for word, job_ids in updates.items():
            node = trie
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
                node.job_ids.update(job_ids)
            node.is_end = True

    def search(self, 
              title_patterns: List[str] = None,
              skills: List[str] = None,
              industries: List[str] = None,
              locations: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for jobs matching the given criteria
        Returns jobs sorted by relevance
        """
        matching_ids = None
        
        # Find jobs matching title patterns
        if title_patterns:
            title_matches = set()
            for pattern in title_patterns:
                title_matches.update(self._search_trie(self.title_trie, pattern))
            matching_ids = title_matches if matching_ids is None else matching_ids.intersection(title_matches)
        
        # Find jobs matching skills
        if skills:
            skill_matches = set()
            for skill in skills:
                skill_matches.update(self._search_trie(self.skill_trie, skill))
            matching_ids = skill_matches if matching_ids is None else matching_ids.intersection(skill_matches)
        
        # Find jobs matching industries
        if industries:
            industry_matches = set()
            for industry in industries:
                industry_matches.update(self.industry_map[industry.lower()])
            matching_ids = industry_matches if matching_ids is None else matching_ids.intersection(industry_matches)
        
        # Find jobs matching locations
        if locations:
            location_matches = set()
            for location in locations:
                location_matches.update(self.location_map[location.lower()])
            matching_ids = location_matches if matching_ids is None else matching_ids.intersection(location_matches)
        
        if matching_ids is None:
            return list(self.jobs.values())
        
        # Return matching jobs
        return [self.jobs[job_id] for job_id in matching_ids] 