"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { JobCard } from "@/components/JobCard";
import { SearchBar } from "@/components/SearchBar";
import { fadeIn, staggerContainer } from "@/utils/motion";
import axiosInstance from "@/utils/axios";
import { AnimatedBackground } from "@/components/AnimatedBackground";

// Types
interface Job {
  id: string;
  title: string;
  industry: string;
  location: string;
  salary: string;
  type: string;
  publication_date: string;
}

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await axiosInstance.get("/api/jobs/");
        setJobs(response.data.results);
      } catch (error) {
        console.error("Error fetching jobs:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Hero Section */}
      <motion.section
        variants={staggerContainer}
        initial="hidden"
        whileInView="show"
        viewport={{ once: false, amount: 0.25 }}
        className="relative h-[80vh] flex items-center justify-center overflow-hidden"
      >
        <AnimatedBackground />

        <div className="relative z-10 text-center px-4">
          <motion.h1
            variants={fadeIn("up", "tween", 0.2, 1)}
            className="text-6xl font-bold mb-6 bg-gradient-to-r from-green-400 to-blue-500 
            bg-clip-text text-transparent"
          >
            Find Your Dream Job
          </motion.h1>
          <motion.p
            variants={fadeIn("up", "tween", 0.4, 1)}
            className="text-xl mb-8 text-gray-300"
          >
            Discover opportunities that match your expertise
          </motion.p>
          <SearchBar />
        </div>
      </motion.section>

      {/* Job Listings Section */}
      <motion.section
        variants={staggerContainer}
        initial="hidden"
        whileInView="show"
        className="max-w-7xl mx-auto px-4 py-16"
      >
        <motion.h2
          variants={fadeIn("up", "tween", 0.2, 1)}
          className="text-3xl font-bold mb-8 text-center"
        >
          Latest Opportunities
        </motion.h2>

        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </motion.section>
    </div>
  );
}
