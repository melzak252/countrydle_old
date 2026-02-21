import { Info, HelpCircle } from 'lucide-react';

interface GameInstructionsProps {
  gameName: string;
  examples: string[];
  isPolish?: boolean;
}

const GameInstructions = ({ gameName, examples, isPolish }: GameInstructionsProps) => {
  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
      <div className="flex items-center gap-2 mb-4 text-blue-400">
        <Info size={20} />
        <h3 className="font-bold text-lg">
          {isPolish ? 'Informacja o grze' : 'Game Information'}
        </h3>
      </div>
      
      <p className="text-zinc-300 mb-4 leading-relaxed text-sm md:text-base">
        {isPolish 
          ? `Witaj w ${gameName}! Gra jest obecnie w fazie rozwoju, więc przepraszamy za ewentualne błędy AI w odpowiedziach. Staramy się stale ulepszać jakość rozgrywki.`
          : `Welcome to ${gameName}! This game is currently in development, so we apologize for any potential AI mistakes in the answers. We are constantly working to improve the experience.`}
      </p>

      <div className="space-y-3">
        <div className="flex items-center gap-2 text-zinc-400 text-xs md:text-sm font-semibold uppercase tracking-wider">
          <HelpCircle size={16} />
          {isPolish ? 'Przykładowe pytania:' : 'Example questions:'}
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
  );
};

export default GameInstructions;
