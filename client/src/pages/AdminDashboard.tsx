import { useState, useEffect, useMemo } from 'react';
import { adminService } from '../services/api';
import { Search, Calendar, User as UserIcon, Globe, Flag } from 'lucide-react';

type GameType = 'countrydle' | 'powiatdle' | 'us_statedle' | 'wojewodztwodle';

export default function AdminDashboard() {
  const [gameType, setGameType] = useState<GameType>('countrydle');
  const [questions, setQuestions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [userFilter, setUserFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [targetFilter, setTargetFilter] = useState('');

  useEffect(() => {
    fetchQuestions();
  }, [gameType]);

  const fetchQuestions = async () => {
    setIsLoading(true);
    try {
      let data: any[] = [];
      switch (gameType) {
        case 'countrydle':
          data = await adminService.getCountrydleQuestions();
          break;
        case 'powiatdle':
          data = await adminService.getPowiatdleQuestions();
          break;
        case 'us_statedle':
          data = await adminService.getUSStatedleQuestions();
          break;
        case 'wojewodztwodle':
          data = await adminService.getWojewodztwodleQuestions();
          break;
      }
      setQuestions(data);
    } catch (error) {
      console.error('Failed to fetch questions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredQuestions = useMemo(() => {
    return questions.filter((q) => {
      const matchesSearch = 
        q.original_question.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (q.question && q.question.toLowerCase().includes(searchTerm.toLowerCase())) ||
        q.explanation.toLowerCase().includes(searchTerm.toLowerCase());
      
      const username = q.user?.username || 'Guest';
      const matchesUser = username.toLowerCase().includes(userFilter.toLowerCase());
      
      const dateStr = new Date(q.asked_at).toISOString().split('T')[0];
      const matchesDate = !dateFilter || dateStr === dateFilter;
      
      const targetName = q.country?.name || q.powiat?.nazwa || q.us_state?.name || q.wojewodztwo?.nazwa || '';
      const matchesTarget = targetName.toLowerCase().includes(targetFilter.toLowerCase());

      return matchesSearch && matchesUser && matchesDate && matchesTarget;
    });
  }, [questions, searchTerm, userFilter, dateFilter, targetFilter]);

  const getTargetName = (q: any) => {
    return q.country?.name || q.powiat?.nazwa || q.us_state?.name || q.wojewodztwo?.nazwa || 'Unknown';
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
        
        <div className="flex bg-zinc-800 p-1 rounded-lg">
          {(['countrydle', 'powiatdle', 'us_statedle', 'wojewodztwodle'] as GameType[]).map((type) => (
            <button
              key={type}
              onClick={() => setGameType(type)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                gameType === type 
                  ? 'bg-blue-600 text-white' 
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-700'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
          <input
            type="text"
            placeholder="Search questions/explanations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="relative">
          <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
          <input
            type="text"
            placeholder="Filter by user..."
            value={userFilter}
            onChange={(e) => setUserFilter(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
          <input
            type="date"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="relative">
          <Flag className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
          <input
            type="text"
            placeholder="Filter by target..."
            value={targetFilter}
            onChange={(e) => setTargetFilter(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Questions List */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-zinc-400 text-sm mb-2">
            Showing {filteredQuestions.length} of {questions.length} questions
          </div>
          
          {filteredQuestions.map((q) => (
            <div key={q.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-zinc-700 transition-colors">
              <div className="flex flex-wrap justify-between items-start gap-4 mb-4">
                <div className="flex flex-wrap gap-3">
                  <div className="flex items-center gap-1.5 px-3 py-1 bg-zinc-800 rounded-full text-xs font-medium text-zinc-300">
                    <UserIcon size={14} />
                    {q.user?.username || 'Guest'}
                  </div>
                  <div className="flex items-center gap-1.5 px-3 py-1 bg-zinc-800 rounded-full text-xs font-medium text-zinc-300">
                    <Calendar size={14} />
                    {formatDate(q.asked_at)}
                  </div>
                  <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-900/30 text-blue-400 rounded-full text-xs font-medium border border-blue-800/50">
                    <Globe size={14} />
                    {getTargetName(q)}
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium border ${
                    q.answer === true 
                      ? 'bg-green-900/30 text-green-400 border-green-800/50' 
                      : q.answer === false 
                        ? 'bg-red-900/30 text-red-400 border-red-800/50'
                        : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                  }`}>
                    {q.answer === true ? 'TRUE' : q.answer === false ? 'FALSE' : 'NULL'}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">Original Question</h3>
                  <p className="text-white text-lg mb-4">"{q.original_question}"</p>
                  
                  {q.question && q.question !== q.original_question && (
                    <>
                      <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">Enhanced Question</h3>
                      <p className="text-zinc-300 italic mb-4">"{q.question}"</p>
                    </>
                  )}
                </div>
                
                <div>
                  <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">Explanation</h3>
                  <p className="text-zinc-300 bg-zinc-800/50 p-3 rounded-lg text-sm leading-relaxed">
                    {q.explanation}
                  </p>
                </div>
              </div>

              {q.context && (
                <div className="mt-6 pt-6 border-t border-zinc-800">
                  <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">Context Provided to LLM</h3>
                  <div className="bg-black/30 p-4 rounded-lg text-xs text-zinc-500 font-mono max-h-40 overflow-y-auto whitespace-pre-wrap">
                    {q.context}
                  </div>
                </div>
              )}
            </div>
          ))}

          {filteredQuestions.length === 0 && (
            <div className="text-center py-20 bg-zinc-900/50 rounded-xl border border-zinc-800 border-dashed">
              <p className="text-zinc-500">No questions found matching your filters.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
