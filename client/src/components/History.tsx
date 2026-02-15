import type { Question } from '../types';
import { Check, X, HelpCircle, AlertTriangle, Info } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';
import { useGameStore } from '../stores/gameStore';

interface HistoryProps {
  questions: Question[];
}

export default function History({ questions }: HistoryProps) {
  const { gameState } = useGameStore();
  // Sort questions by ID descending (newest first)
  const sortedQuestions = [...questions].sort((a, b) => b.id - a.id);

  return (
    <div className="w-full space-y-4 mb-8">
      {sortedQuestions.length === 0 ? (
        <div className="text-center text-zinc-500 py-8">
          No questions asked yet. Start by asking something!
        </div>
      ) : (
        sortedQuestions.map((q, index) => (
          <motion.div
            key={q.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className={cn(
              "p-4 rounded-xl border flex items-center gap-4 shadow-sm relative group transition-all",
              q.valid ? "bg-zinc-900 border-zinc-800" : "bg-red-900/20 border-red-900/50"
            )}
          >
             <div className="flex-shrink-0">
                {!q.valid ? (
                   <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-500">
                     <AlertTriangle size={18} />
                   </div>
                ) : q.answer === true ? (
                  <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-500">
                    <Check size={18} />
                  </div>
                ) : q.answer === false ? (
                  <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-500">
                    <X size={18} />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500">
                    <HelpCircle size={18} />
                  </div>
                )}
            </div>
            
            <div className="flex-1">
              <p className="font-medium text-lg">{q.original_question}</p>
              {q.explanation && gameState?.is_game_over && (
                 <div className="hidden group-hover:block absolute top-full left-0 mt-2 p-3 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-300 shadow-xl z-20 w-full max-w-md">
                    <div className="absolute -top-2 left-8 w-4 h-4 bg-zinc-800 border-t border-l border-zinc-700 transform rotate-45"></div>
                    {q.explanation}
                 </div>
              )}
            </div>
            
            {q.explanation && gameState?.is_game_over && (
                <div className="text-zinc-500 hover:text-blue-400 cursor-help transition-colors" title="Hover for explanation">
                    <Info size={18} />
                </div>
            )}
            
            <div className="text-xs text-zinc-500 font-mono ml-2">
              #{questions.length - index}
            </div>
          </motion.div>
        ))
      )}
    </div>
  );
}
