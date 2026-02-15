import { useState, useEffect } from 'react';
import { gameService } from '../services/api';
import { Loader2, Medal } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    gameService.getLeaderboard()
      .then(setLeaderboard)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-blue-500" size={48} /></div>;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-center gap-3 mb-8">
        <Medal className="text-yellow-500" size={40} />
        <h2 className="text-3xl font-bold">Leaderboard</h2>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-zinc-800/50 text-zinc-400 border-b border-zinc-800">
            <tr>
              <th className="px-6 py-4 font-medium w-16 text-center">#</th>
              <th className="px-6 py-4 font-medium">Player</th>
              <th className="px-6 py-4 font-medium text-right">Points</th>
              <th className="px-6 py-4 font-medium text-right">Wins</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {leaderboard.map((entry: any, index: number) => (
              <tr key={entry.id} className="hover:bg-zinc-800/30 transition-colors">
                <td className="px-6 py-4 text-center text-zinc-500 font-mono">
                  {index + 1}
                </td>
                <td className="px-6 py-4">
                  <Link to={`/profile/${entry.username}`} className="flex items-center gap-3 font-medium hover:text-blue-400 transition-colors">
                    {/* Placeholder Avatar */}
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-teal-500 flex items-center justify-center text-xs font-bold text-white">
                      {entry.username.substring(0, 2).toUpperCase()}
                    </div>
                    {entry.username}
                  </Link>
                </td>
                <td className="px-6 py-4 text-right font-mono text-yellow-500 font-bold">
                  {entry.points}
                </td>
                <td className="px-6 py-4 text-right font-mono text-green-500">
                  {entry.wins}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {leaderboard.length === 0 && (
          <div className="p-8 text-center text-zinc-500">
            No entries yet. Be the first!
          </div>
        )}
      </div>
    </div>
  );
}
