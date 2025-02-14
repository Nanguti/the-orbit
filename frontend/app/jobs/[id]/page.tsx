"use client";

import { motion } from "framer-motion";
import { useEffect, useState, use } from "react";
import axiosInstance from "@/utils/axios";
import { fadeIn, staggerContainer } from "@/utils/motion";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { useSearchParams } from "next/navigation";
import { humanizeDate } from "@/utils/dateFormat";

interface JobDetail {
  id: string;
  title: string;
  industry: string;
  location: string;
  salary: string;
  type: string;
  publication_date: string;
  description: string;
  requirements: string[];
  benefits: string[];
}

export default function JobDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const jobId = use(params).id;
  const searchParams = useSearchParams();
  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);

  const referrer = searchParams.get("ref") || "direct";

  useEffect(() => {
    const fetchJobDetail = async () => {
      try {
        const response = await axiosInstance.get(`/api/jobs/${jobId}`);
        setJob(response.data);
      } catch (error) {
        console.error("Error fetching job details:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobDetail();
  }, [jobId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <h1 className="text-white text-2xl">Job not found</h1>
      </div>
    );
  }

  const handleApply = () => {
    console.log(`Applying to job from ${referrer}`);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <AnimatedBackground />

      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="relative z-10 max-w-4xl mx-auto px-4 py-16"
      >
        <motion.div
          variants={fadeIn("down", "tween", 0.2, 1)}
          className="bg-gray-800/50 backdrop-blur-md rounded-xl p-8 border border-gray-700"
        >
          <div className="space-y-6">
            <div className="space-y-2">
              <motion.h1
                variants={fadeIn("up", "tween", 0.3, 1)}
                className="text-3xl font-bold bg-gradient-to-r from-green-400
                 to-blue-500 bg-clip-text text-transparent"
              >
                {job.title}
              </motion.h1>
              <motion.div
                variants={fadeIn("up", "tween", 0.4, 1)}
                className="flex flex-wrap gap-3"
              >
                <span className="px-3 py-1 bg-gray-700 rounded-full text-sm">
                  {job.location}
                </span>
                <span className="px-3 py-1 bg-gray-700 rounded-full text-sm">
                  {job.type}
                </span>
                <span className="px-3 py-1 bg-gray-700 rounded-full text-sm">
                  {job.industry}
                </span>
              </motion.div>
            </div>

            <motion.div
              variants={fadeIn("up", "tween", 0.5, 1)}
              className="flex items-center justify-between py-4 border-t border-b border-gray-700"
            >
              <span className="text-green-400 font-semibold text-xl">
                {job.salary}
              </span>
              <span className="text-gray-400">
                Posted {humanizeDate(job.publication_date)}
              </span>
            </motion.div>

            <motion.div
              variants={fadeIn("up", "tween", 0.6, 1)}
              className="space-y-4"
            >
              <h2 className="text-xl font-semibold">Job Description</h2>
              <p className="text-gray-300 leading-relaxed">{job.description}</p>
            </motion.div>

            <motion.div
              variants={fadeIn("up", "tween", 0.7, 1)}
              className="space-y-4"
            >
              <h2 className="text-xl font-semibold">Requirements</h2>
              {/* <ul className="list-disc list-inside space-y-2 text-gray-300">
                {job.requirements.map((req, index) => (
                  <li key={index}>{req}</li>
                ))}
              </ul> */}
            </motion.div>

            <motion.div
              variants={fadeIn("up", "tween", 0.8, 1)}
              className="space-y-4"
            >
              <h2 className="text-xl font-semibold">Benefits</h2>
              {/* <ul className="list-disc list-inside space-y-2 text-gray-300">
                {job.benefits.map((benefit, index) => (
                  <li key={index}>{benefit}</li>
                ))}
              </ul> */}
            </motion.div>

            <motion.div
              variants={fadeIn("up", "tween", 0.9, 1)}
              className="flex justify-center pt-6"
            >
              <button
                onClick={handleApply}
                className="px-8 py-3 bg-gradient-to-r from-green-400 to-blue-500 rounded-full 
                font-semibold hover:opacity-90 transition-opacity"
              >
                Apply Now
              </button>
            </motion.div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
