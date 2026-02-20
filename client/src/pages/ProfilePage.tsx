import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { gameService, authService } from '../services/api';
import { Loader2, User, Trophy, Target, Edit2, Check, X } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { toast } from 'react-hot-toast';

export default function ProfilePage() {
  const { username } = useParams();
  const { user: currentUser, setUser } = useAuthStore();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [isEditing, setIsEditing] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [updateLoading, setUpdateLoading] = useState(false);

  const isOwnProfile = currentUser?.username === username;

  useEffect(() => {
    if (username) {
      setLoading(true);
      gameService.getUserStats(username)
        .then(data => {
          setStats(data);
          setNewUsername(data.user.username);
        })
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [username]);

  const handleUpdateUsername = async () => {
    if (!newUsername.trim() || newUsername === stats.user.username) {
      setIsEditing(false);
      return;
    }

    try {
      setUpdateLoading(true);
      // We need to send both username and email as per the mandatory schema
      await authService.updateProfile({
        username: newUsername.trim(),
        email: currentUser?.email || stats.user.email
      });
      
      toast.success('Username updated successfully!');
      
      // Update local state
      const updatedUser = { ...stats.user, username: newUsername.trim() };
      setStats({ ...stats, user: updatedUser });
      
      // Update auth store if it's the current user
      if (isOwnProfile && currentUser) {
        setUser({ ...currentUser, username: newUsername.trim() });
      }
      
      setIsEditing(false);
      
      // If username changed, we might want to redirect to the new profile URL
      // but for now just updating the state is enough.
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update username');
    } finally {
      setUpdateLoading(false);
    }
  };

  if (loading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin text-blue-500" size={48} /></div>;

  if (!stats) return <div className="text-center p-20 text-red-500">User not found</div>;

  return (
    <div className="max-w-4xl mx-auto px-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 mb-8 flex flex-col md:flex-row items-center gap-8 shadow-xl">
        <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-blue-500 to-teal-500 flex items-center justify-center text-4xl font-bold text-white shadow-lg shrink-0">
          {stats.user.username ? stats.user.username.substring(0, 2).toUpperCase() : '??'}
        </div>
        
        <div className="text-center md:text-left flex-1">
            {isEditing ? (
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1 text-xl font-bold focus:outline-none focus:border-blue-500 w-full max-w-xs"
                    autoFocus
                  />
                  <button 
                    onClick={handleUpdateUsername}
                    disabled={updateLoading}
                    className="p-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {updateLoading ? <Loader2 size={20} className="animate-spin" /> : <Check size={20} />}
                  </button>
                  <button 
                    onClick={() => {
                      setIsEditing(false);
                      setNewUsername(stats.user.username);
                    }}
                    className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>
                <p className="text-xs text-zinc-500">Username can be changed once every 30 days.</p>
              </div>
            ) : (
              <div className="flex items-center justify-center md:justify-start gap-3">
                <h2 className="text-3xl font-bold">{stats.user.username || 'Anonymous'}</h2>
                {isOwnProfile && (
                  <button 
                    onClick={() => setIsEditing(true)}
                    className="p-1.5 text-zinc-500 hover:text-white hover:bg-zinc-800 rounded-lg transition-all"
                    title="Edit nickname"
                  >
                    <Edit2 size={18} />
                  </button>
                )}
              </div>
            )}
            <p className="text-zinc-400 text-sm mt-1">Member since {new Date(stats.user.created_at).toLocaleDateString()}</p>
        </div>
        
        <div className="flex justify-center md:justify-end gap-8">
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
