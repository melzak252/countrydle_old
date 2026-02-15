import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { LogOut, User as UserIcon } from 'lucide-react';

export default function Header() {
  const { user, logout, isAuthenticated } = useAuthStore();

  return (
    <header className="bg-zinc-900 border-b border-zinc-800 text-white">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 text-transparent bg-clip-text">
          Countrydle
        </Link>

        <nav className="flex items-center gap-6">
          <Link to="/game" className="hover:text-blue-400 transition-colors">Play</Link>
          <Link to="/leaderboard" className="hover:text-blue-400 transition-colors">Leaderboard</Link>
          
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <UserIcon size={18} />
                <span className="font-medium">{user?.username}</span>
              </div>
              <button 
                onClick={() => logout()}
                className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-800 hover:bg-zinc-700 transition-colors text-sm"
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <Link to="/login" className="hover:text-blue-400 transition-colors">Login</Link>
              <Link 
                to="/register" 
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md font-medium transition-colors"
              >
                Sign Up
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
