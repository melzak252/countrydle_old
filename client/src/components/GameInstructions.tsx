import { useState } from 'react';
import { Info, HelpCircle, ChevronDown, ChevronUp, Languages, Trophy } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface GameInstructionsProps {
  gameName: string;
  examples: string[];
  scoring?: {
    maxPoints: number;
    details: string[];
  };
}

const GameInstructions = ({ gameName, examples, scoring }: GameInstructionsProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useTranslation();

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl mb-6 overflow-hidden shadow-lg transition-all duration-300">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 flex items-center justify-between bg-zinc-800/30 hover:bg-zinc-800/50 transition-colors"
      >
        <div className="flex items-center gap-2 text-blue-400">
          <Info size={20} />
          <h3 className="font-bold text-lg">
            {t('instructions.title')}
          </h3>
        </div>
        {isOpen ? <ChevronUp size={20} className="text-zinc-500" /> : <ChevronDown size={20} className="text-zinc-500" />}
      </button>
      
      {isOpen && (
        <div className="p-6 border-t border-zinc-800 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="space-y-6">
            <p className="text-zinc-300 leading-relaxed text-sm md:text-base">
              {t('instructions.welcome', { gameName })}
            </p>

            <div className="flex items-start gap-3 p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
              <Info size={18} className="text-blue-400 shrink-0 mt-0.5" />
              <p className="text-zinc-400 text-sm italic">
                {t('instructions.wikipedia')}
              </p>
            </div>

            <div className="flex items-start gap-3 p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
              <Languages size={18} className="text-blue-400 shrink-0 mt-0.5" />
              <p className="text-zinc-400 text-sm italic">
                {t('instructions.askAnyLanguage')}
              </p>
            </div>

            {scoring && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-yellow-500 text-xs md:text-sm font-semibold uppercase tracking-wider">
                  <Trophy size={16} />
                  {t('instructions.scoring')}
                </div>
                <div className="bg-zinc-800/30 border border-zinc-700/30 rounded-xl p-4">
                  <div className="text-2xl font-bold text-white mb-2">
                    {t('instructions.upToPoints', { maxPoints: scoring.maxPoints })}
                  </div>
                  <ul className="space-y-1">
                    {scoring.details.map((detail, index) => (
                      <li key={index} className="text-zinc-400 text-sm flex items-center gap-2">
                        <div className="w-1 h-1 rounded-full bg-zinc-600" />
                        {detail}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            <div className="space-y-3 pt-2">
              <div className="flex items-center gap-2 text-zinc-400 text-xs md:text-sm font-semibold uppercase tracking-wider">
                <HelpCircle size={16} />
                {t('instructions.examples')}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {examples.map((example, index) => (
                  <div key={index} className="bg-zinc-800/50 border border-zinc-700/50 px-4 py-2 rounded-lg text-zinc-400 text-xs md:text-sm italic">
                    "{example}"
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameInstructions;
