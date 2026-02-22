import { useState, useEffect } from 'react';
import { gameService, powiatService, usStateService, wojewodztwoService } from '../services/api';
import { Loader2, Medal, Globe, Map, Flag, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../lib/utils';

type GameType = 'country' | 'powiat' | 'us_state' | 'wojewodztwo';

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [gameType, setGameType] = useState<GameType>('country');

  useEffect(() => {
    setLoading(true);
    const fetchLeaderboard = async () => {
        try {
            let data = [];
            if (gameType === 'country') data = await gameService.getLeaderboard();
            else if (gameType === 'powiat') data = await powiatService.getLeaderboard();
            else if (gameType === 'us_state') data = await usStateService.getLeaderboard();
            else if (gameType === 'wojewodztwo') data = await wojewodztwoService.getLeaderboard();
            setLeaderboard(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };
    fetchLeaderboard();
  }, [gameType]);

  const tabs = [
    { id: 'country', label: 'Countries', icon: Globe },
    { id: 'powiat', label: 'Powiaty', icon: Map },
    { id: 'us_state', label: 'US States', icon: Flag },
    { id: 'wojewodztwo', label: 'Województwa', icon: MapPin },
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-center gap-2 md:gap-3 mb-6 md:mb-8">
        <Medal className="text-yellow-500 w-[32px] h-[32px] md:w-[40px] md:h-[40px]" />
        <h2 className="text-2xl md:text-3xl font-bold">Leaderboard</h2>
      </div>

      <div className="flex justify-center gap-2 mb-6 md:mb-8 flex-wrap">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setGameType(tab.id as GameType)}
            className={cn(
              "flex items-center gap-1.5 md:gap-2 px-3 py-1.5 md:px-4 md:py-2 rounded-full transition-all border text-sm md:text-base",
              gameType === tab.id 
                ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-900/20" 
                : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
            )}
          >
            <tab.icon className="w-[14px] h-[14px] md:w-[16px] md:h-[16px]" />
            <span className="font-medium">{tab.label}</span>
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex justify-center p-20"><Loader2 className="animate-spin text-blue-500" size={48} /></div>
      ) : (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500 shadow-xl mx-2 md:mx-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left min-w-[320px]">
              <thead className="bg-zinc-800/50 text-zinc-400 border-b border-zinc-800">
                <tr>
                  <th className="px-3 md:px-6 py-3 md:py-4 font-medium w-12 md:w-16 text-center">#</th>
                  <th className="px-3 md:px-6 py-3 md:py-4 font-medium">Player</th>
                  <th className="px-3 md:px-6 py-3 md:py-4 font-medium text-right">Points</th>
                  <th className="px-3 md:px-6 py-3 md:py-4 font-medium text-right">Wins</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {leaderboard.map((entry: any, index: number) => (
                  <tr key={entry.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-3 md:px-6 py-3 md:py-4 text-center text-zinc-500 font-mono text-xs md:text-sm">
                      {index + 1}
                    </td>
                    <td className="px-3 md:px-6 py-3 md:py-4">
                      <Link to={`/profile/${entry.username}`} className="flex items-center gap-2 md:gap-3 font-medium hover:text-blue-400 transition-colors text-sm md:text-base">
                        {/* Placeholder Avatar */}
                        <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-gradient-to-tr from-blue-500 to-teal-500 flex items-center justify-center text-[10px] md:text-xs font-bold text-white shrink-0">
                          {entry.username.substring(0, 2).toUpperCase()}
                        </div>
                        <span className="truncate max-w-[80px] sm:max-w-[150px] md:max-w-none">{entry.username}</span>
                      </Link>
                    </td>
                    <td className="px-3 md:px-6 py-3 md:py-4 text-right font-mono text-yellow-500 font-bold text-sm md:text-base">
                      {entry.points}
                    </td>
                    <td className="px-3 md:px-6 py-3 md:py-4 text-right font-mono text-green-500 text-sm md:text-base">
                      {entry.wins}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {leaderboard.length === 0 && (
            <div className="p-8 text-center text-zinc-500">
              No entries yet. Be the first!
            </div>
          )}
        </div>
      )}
    </div>
  );
}
