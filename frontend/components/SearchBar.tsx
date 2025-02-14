import { motion } from "framer-motion";
import { useState } from "react";
import { FiSearch } from "react-icons/fi";

export const SearchBar = () => {
  const [query, setQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Implement search functionality
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      onSubmit={handleSearch}
      className="flex w-full max-w-2xl mx-auto"
    >
      <div className="relative flex-1">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for jobs..."
          className="w-full px-6 py-4 rounded-l-full bg-white/10 backdrop-blur-md border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-400"
        />
      </div>
      <button
        type="submit"
        className="px-8 rounded-r-full bg-gradient-to-r from-green-400 to-blue-500 hover:opacity-90 transition-opacity"
      >
        <FiSearch className="w-5 h-5" />
      </button>
    </motion.form>
  );
};
