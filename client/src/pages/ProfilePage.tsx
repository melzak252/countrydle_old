import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { gameService } from '../services/api';
import { Loader2, User, Trophy, Target } from 'lucide-react';

export default function ProfilePage() {
  const { username } = useParams();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (username) {
      gameService.getUserStats(username)
        .then(setStats)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [username]);

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-blue-500" size={48} /></div>;

  if (!stats) return <div className="text-center p-20 text-red-500">User not found</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 mb-8 flex flex-col md:flex-row items-center gap-8">
        <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-500 to-teal-500 flex items-center justify-center text-4xl font-bold text-white shadow-lg">
          {stats.user.username.substring(0, 2).toUpperCase()}
        </div>
        <div className="text-center md:text-left">
            <h2 className="text-3xl font-bold mb-2">{stats.user.username}</h2>
            <p className="text-zinc-400 text-sm">Member since {new Date(stats.user.created_at).toLocaleDateString()}</p>
        </div>
        
        <div className="flex-1 flex justify-center md:justify-end gap-8">
            <div className="text-center">
                <div className="text-3xl font-bold text-yellow-500">{stats.points}</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wider">Points</div>
            </div>
            <div className="text-center">
                <div className="text-3xl font-bold text-green-500">{stats.wins}</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wider">Wins</div>
            </div>
            <div className="text-center">
                <div className="text-3xl font-bold text-orange-500">{stats.streak}</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wider">Streak</div>
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl flex items-center gap-4">
            <div className="p-3 bg-blue-500/20 text-blue-500 rounded-lg">
                <Target size={24} />
            </div>
            <div>
                <div className="text-2xl font-bold">{stats.guesses_made > 0 ? Math.round((stats.guesses_correct / stats.guesses_made) * 100) : 0}%</div>
                <div className="text-sm text-zinc-500">Guess Accuracy</div>
            </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl flex items-center gap-4">
            <div className="p-3 bg-teal-500/20 text-teal-500 rounded-lg">
                <User size={24} />
            </div>
            <div>
                <div className="text-2xl font-bold">{stats.guesses_made}</div>
                <div className="text-sm text-zinc-500">Total Guesses</div>
            </div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl flex items-center gap-4">
            <div className="p-3 bg-purple-500/20 text-purple-500 rounded-lg">
                <Trophy size={24} />
            </div>
            <div>
                <div className="text-2xl font-bold">{stats.questions_asked}</div>
                <div className="text-sm text-zinc-500">Questions Asked</div>
            </div>
        </div>
      </div>

      <h3 className="text-xl font-bold mb-4">Recent Games</h3>
      <div className="space-y-4">
        {stats.history && stats.history.length > 0 ? (
            stats.history.map((game: any, index: number) => (
                <div key={index} className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl flex justify-between items-center">
                    <div>
                        <div className="font-bold">{game.day.date}</div>
                        <div className="text-sm text-zinc-400">
                             {game.won ? 'Won' : 'Lost'} with {game.guesses_made} guesses
                        </div>
                    </div>
                    <div className={`text-xl font-bold ${game.won ? 'text-green-500' : 'text-red-500'}`}>
                        {game.points} pts
                    </div>
                </div>
            ))
        ) : (
            <div className="text-center text-zinc-500 py-8">No games played yet.</div>
        )}
      </div>
    </div>
  );
}
