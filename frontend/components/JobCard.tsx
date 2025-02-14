import { motion } from "framer-motion";
import { fadeIn } from "@/utils/motion";
import { useRouter } from "next/navigation";
import { humanizeDate } from "@/utils/dateFormat";

interface JobCardProps {
  job: {
    id: string;
    title: string;
    industry: string;
    location: string;
    salary: string;
    type: string;
    publication_date: string;
  };
}

export const JobCard = ({ job }: JobCardProps) => {
  const router = useRouter();

  const handleClick = () => {
    const searchParams = new URLSearchParams({
      ref: "job-listing",
    });
    router.push(`/jobs/${job.id}?${searchParams.toString()}`);
  };

  return (
    <motion.div
      variants={fadeIn("up", "spring", 0.3, 0.75)}
      initial="hidden"
      animate="show"
      onClick={handleClick}
      className="bg-gray-800 rounded-xl p-6 hover:shadow-xl transition-all 
      duration-300 hover:scale-105 cursor-pointer border border-gray-700"
      whileHover={{ y: -5 }}
      whileTap={{ scale: 0.98 }}
    >
      <h6 className="text-base font-semibold mb-2">{job.title}</h6>
      <p className="text-gray-400 mb-4">Industry: {job.industry}</p>
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="px-3 py-1 bg-gray-700 rounded-full text-sm">
          {job.location}
        </span>
        <span className="px-3 py-1 bg-gray-700 rounded-full text-sm">
          {job.type}
        </span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-green-400 font-semibold">{job.salary}</span>
        <span className="text-sm text-gray-400">
          {humanizeDate(job.publication_date)}
        </span>
      </div>
    </motion.div>
  );
};
