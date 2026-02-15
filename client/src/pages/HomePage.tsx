import { Link } from 'react-router-dom';
import { Globe, HelpCircle, Trophy } from 'lucide-react';
import { motion } from 'framer-motion';

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-6xl font-extrabold mb-6 bg-gradient-to-r from-blue-500 via-teal-400 to-green-500 text-transparent bg-clip-text">
          Countrydle
        </h1>
        <p className="text-xl text-zinc-400 max-w-2xl mb-12">
          Can you guess the country? Ask questions, get hints, and test your geography knowledge.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
      >
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex flex-col items-center">
          <Globe className="text-blue-500 mb-4" size={48} />
          <h3 className="text-xl font-bold mb-2">Daily Challenge</h3>
          <p className="text-zinc-400">A new mystery country every day for you to discover.</p>
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex flex-col items-center">
          <HelpCircle className="text-teal-500 mb-4" size={48} />
          <h3 className="text-xl font-bold mb-2">Ask Questions</h3>
          <p className="text-zinc-400">Ask yes/no questions to narrow down the possibilities.</p>
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex flex-col items-center">
          <Trophy className="text-yellow-500 mb-4" size={48} />
          <h3 className="text-xl font-bold mb-2">Compete</h3>
          <p className="text-zinc-400">Climb the leaderboard and show off your skills.</p>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.5 }}
      >
        <Link
          to="/game"
          className="px-8 py-4 bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 rounded-full text-xl font-bold shadow-lg transform hover:scale-105 transition-all"
        >
          Play Now
        </Link>
      </motion.div>
    </div>
  );
}
