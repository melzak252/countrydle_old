import type { Question } from '../types';
import { Check, X, HelpCircle, Info, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../lib/utils';
import { useState } from 'react';

interface HistoryProps {
  questions: Question[];
  isGameOver?: boolean;
}

export default function History({ questions, isGameOver = false }: HistoryProps) {
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  
  // Sort questions by ID descending (newest first)
  const sortedQuestions = [...questions].sort((a, b) => b.id - a.id);

  return (
    <div className="w-full space-y-3 mb-8">
      {sortedQuestions.length === 0 ? (
        <div className="text-center text-zinc-500 py-8">
          No questions asked yet. Start by asking something!
        </div>
      ) : (
        sortedQuestions.map((q, index) => {
          const showExplanation = (!q.valid) || (q.explanation && isGameOver);
          const isExpanded = hoveredId === q.id;

          return (
            <motion.div
              key={q.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onMouseEnter={() => setHoveredId(q.id)}
              onMouseLeave={() => setHoveredId(null)}
              className={cn(
                "rounded-xl border shadow-sm transition-all overflow-hidden flex flex-col w-full",
                q.valid ? "bg-zinc-900 border-zinc-800" : "bg-red-900/10 border-red-900/30"
              )}
            >
              {/* Main Card Header */}
              <div className="p-3 md:p-4 flex items-center gap-3 md:gap-4">
                <div className="flex-shrink-0">
                  {!q.valid ? (
                    <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-500">
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
                
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm md:text-base break-words leading-tight">{q.original_question}</p>
                </div>

                {showExplanation && (
                  <div className={cn("transition-colors", isExpanded ? "text-blue-400" : "text-zinc-600")}>
                    <Info size={16} />
                  </div>
                )}
                
                <div className="text-[10px] text-zinc-600 font-mono ml-1 shrink-0">
                  #{questions.length - index}
                </div>
              </div>

              {/* Expanded Section (Explanation) */}
              <AnimatePresence>
                {showExplanation && isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="px-4 pb-4">
                      <div className={cn(
                        "p-3 rounded-lg text-xs md:text-sm leading-relaxed",
                        q.valid ? "bg-zinc-800 text-zinc-300" : "bg-amber-500/10 text-amber-200 border border-amber-500/20"
                      )}>
                        {!q.valid && (
                          <div className="flex items-center gap-1.5 mb-1 text-amber-500 font-bold uppercase text-[10px] tracking-wider">
                            <AlertTriangle size={12} />
                            Invalid Question
                          </div>
                        )}
                        {q.explanation}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })
      )}
    </div>
  );
}

