import requests
from lxml import etree
from datetime import datetime
from django.conf import settings
from typing import List, Dict, Any, Optional
import logging
import os
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from io import BytesIO
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Job
from .search import SearchIndex
from django.core.cache import cache
from functools import lru_cache, cached_property
import aiohttp
import asyncio
from dateutil import parser as date_parser
import re
import pickle
import hashlib

logger = logging.getLogger(__name__)

class JobFetcher:
    def __init__(self):
        self.url = "https://www.myjobmag.co.ke/jobsxml_by_categories.xml"
        self.allowed_industries = set(settings.ALLOWED_INDUSTRIES)
        
        # Pre-process tech job titles to lowercase
        self.tech_job_titles_lower = {
            title.lower() for title in settings.TECH_JOB_TITLES
        }
        
        # Pre-process skills to lowercase
        self.tech_skills_lower = {
            skill.lower() for skill in settings.TECH_SKILLS
        }
        self.soft_skills_lower = {
            skill.lower() for skill in settings.SOFT_SKILLS
        }
        self.search_index = SearchIndex()
        self.timeout = aiohttp.ClientTimeout(total=20)  # Optimized timeout
        
        self._skill_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.tech_skills_lower)) + r')\b',
            re.IGNORECASE
        )
        self._soft_skill_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, self.soft_skills_lower)) + r')\b',
            re.IGNORECASE
        )
        
        logger.info(f"JobFetcher initialized with URL: {self.url}")

    @cached_property
    def session(self):
        """Lazy session initialization with connection pooling"""
        return aiohttp.ClientSession(
            timeout=self.timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            connector=aiohttp.TCPConnector(limit=10)
        )

    async def fetch_jobs(self) -> List[Dict[str, Any]]:
        """Asynchronous job fetching"""
        try:
            async with self.session.get(self.url) as response:
                response.raise_for_status()
                content = await response.read()
                
                # Use iterparse for memory efficiency
                context = etree.iterparse(
                    BytesIO(content),
                    events=('end',),
                    tag='item',
                    remove_blank_text=True,
                    recover=True
                )
                
                jobs = []
                for _, elem in context:
                    if job := self._parse_job_item(elem):
                        if self._should_include_job(job):
                            jobs.append(job)
                    elem.clear()  # Free memory
                
                return jobs
                
        except Exception as e:
            logger.error(f"Error fetching jobs: {str(e)}")
            return []

    def _parse_job_item(self, item) -> Dict[str, Any]:
        try:
            def get_text(elem, xpath):
                el = elem.find(xpath)
                if el is not None:
                    text = el.text or ''
                    if isinstance(text, bytes):
                        text = text.decode('utf-8')
                    return text.strip()
                return ''

            title = get_text(item, 'title')
            description = get_text(item, 'description')
            link = get_text(item, 'link')
            pub_date = get_text(item, 'pubDate')
            industry = get_text(item, 'industry')
            position = get_text(item, 'position')
            company = get_text(item, 'company')
            location = get_text(item, 'location')

            # Clean CDATA if present
            for field in [title, description, link, industry, position, company, location]:
                if field.startswith('<![CDATA[') and field.endswith(']]>'):
                    field = field[9:-3].strip()

            try:
                pub_date = self._parse_date(pub_date)
            except ValueError:
                logger.error(f"Could not parse date: {pub_date}")
                return None

            # Extract skills
            tech_skills = self._extract_tech_skills(description)
            soft_skills = self._extract_soft_skills(description)
            all_skills = tech_skills.union(soft_skills)

            return {
                'title': title,
                'description': description,
                'job_link': link,
                'publication_date': pub_date,
                'industry': industry,
                'position': position,
                'company': company,
                'location': location,
                'skills': list(all_skills),
                'tech_skills': list(tech_skills),
                'soft_skills': list(soft_skills)
            }
        except Exception as e:
            logger.error(f"Error parsing job item: {str(e)}")
            return None

    def _should_include_job(self, job: Dict[str, Any]) -> bool:
        """Optimized job matching using search index"""
        # Add job to search index
        job_id = self.search_index.add_job(job)
        
        # Search for matching jobs
        matches = self.search_index.search(
            industries=list(self.allowed_industries),
            title_patterns=list(self.tech_job_titles_lower)
        )
        
        # Check if this job is in matches
        return any(match['job_link'] == job['job_link'] for match in matches)

    def _extract_tech_skills(self, text: str) -> set:
        """Optimized skill extraction using regex"""
        return set(match.group(1).lower() 
                  for match in self._skill_pattern.finditer(text))

    def _extract_soft_skills(self, text: str) -> set:
        """Optimized soft skill extraction using regex"""
        return set(match.group(1).lower() 
                  for match in self._soft_skill_pattern.finditer(text))

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Optimized date parsing"""
        try:
            return date_parser.parse(date_str)
        except Exception:
            logger.error(f"Could not parse date: {date_str}")
            return None

    @lru_cache(maxsize=1000)
    def _check_title_match(self, title: str) -> bool:
        """Cache title matching results"""
        cache_key = f"title_match:{title}"
        result = cache.get(cache_key)
        
        if result is None:
            matches = self.search_index.search(title_patterns=[title])
            result = bool(matches)
            cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
            
        return result

    def _cache_key(self, criteria: Dict[str, Any]) -> str:
        """Generate cache key for search criteria"""
        criteria_str = pickle.dumps(sorted(criteria.items()))
        return f"job_search:{hashlib.md5(criteria_str).hexdigest()}"

    async def search_jobs(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search jobs with caching"""
        cache_key = self._cache_key(criteria)
        
        # Try to get from cache
        if cached_results := cache.get(cache_key):
            return cached_results
        
        # Perform search
        results = self.search_index.search(**criteria)
        
        # Cache results
        cache.set(cache_key, results, timeout=3600)  # 1 hour
        
        return results

class JobEmailService:
    @staticmethod
    def send_job_alert(email: str, jobs: List[Job], alert_criteria: dict) -> bool:
        try:
            # Prepare email content
            context = {
                'jobs': jobs,
                'criteria': alert_criteria
            }
            
            html_content = render_to_string('jobs/email/job_alert.html', context)
            text_content = render_to_string('jobs/email/job_alert.txt', context)
            
            # Send email
            send_mail(
                subject='New Job Matches Found!',
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_content,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Error sending job alert email: {str(e)}")
            return False 