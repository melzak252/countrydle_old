import { useEffect, useState } from 'react';
import { useWojewodztwaGameStore } from '../stores/gameStore';
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';
import QuestionInput from '../components/QuestionInput';
import History from '../components/History';
import GuessInput from '../components/GuessInput';
import WojewodztwaMap from '../components/WojewodztwaMap';
import GameInstructions from '../components/GameInstructions';
import { Loader2, ChevronDown, ChevronUp, Map as MapIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function WojewodztwaGamePage() {
  const { 
    gameState, 
    questions, 
    guesses, 
    entities: wojewodztwa, 
    correctEntity: correctWojewodztwo,
    isLoading, 
    fetchGameState, 
    fetchEntities: fetchWojewodztwa, 
    askQuestion, 
    makeGuess
  } = useWojewodztwaGameStore();

  const { isAuthenticated, isLoading: isAuthLoading } = useAuthStore();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isMapOpen, setIsMapOpen] = useState(true);

  useEffect(() => {
    if (!isAuthLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, isAuthLoading, navigate]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchGameState();
      fetchWojewodztwa();
    }
  }, [isAuthenticated, fetchGameState, fetchWojewodztwa]);

  if (isAuthLoading || (!gameState && isLoading)) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <Loader2 className="animate-spin text-blue-500" size={48} />
      </div>
    );
  }

  if (!gameState) return null;

  return (
    <div className="max-w-6xl mx-auto pb-20 px-4">
      <div className="text-center mb-6">
        <h2 className="text-2xl md:text-4xl font-bold mb-1 md:mb-2 bg-gradient-to-r from-red-500 to-white text-transparent bg-clip-text">
          {t('wojewodztwaPage.title')}
        </h2>
        <p className="text-xs md:text-sm text-zinc-400">{t('gamePage.date', { date: useWojewodztwaGameStore.getState().dailyDate })}</p>
      </div>

      <GameInstructions 
        gameName={t('wojewodztwaPage.title')}
        examples={t('wojewodztwaPage.examples', { returnObjects: true }) as string[]}
        scoring={{
          maxPoints: 450,
          details: t('wojewodztwaPage.scoringDetails', { returnObjects: true }) as string[]
        }}
      />

      {/* Collapsible Map Section */}
      <div className="mb-6 md:mb-8 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-lg">
        <button 
          onClick={() => setIsMapOpen(!isMapOpen)}
          className="w-full p-3 md:p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
        >
          <div className="flex items-center gap-2">
            <MapIcon className="text-red-500 w-[18px] h-[18px] md:w-[20px] md:h-[20px]" />
            <span className="font-bold text-base md:text-lg">{t('wojewodztwaPage.map')}</span>
          </div>
          {isMapOpen ? <ChevronUp className="w-[18px] h-[18px] md:w-[20px] md:h-[20px]" /> : <ChevronDown className="w-[18px] h-[18px] md:w-[20px] md:h-[20px]" />}
        </button>
        
        {isMapOpen && (
          <div className="p-0 animate-in fade-in slide-in-from-top-4 duration-300">
             <WojewodztwaMap correctWojewodztwoName={correctWojewodztwo?.nazwa} />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8">
        <div className="lg:col-span-8 space-y-6 md:space-y-8">
            {gameState.is_game_over && (
              <div className={`text-center p-6 md:p-8 rounded-xl ${gameState.won ? 'bg-green-900/20 border border-green-500/50' : 'bg-red-900/20 border border-red-500/50'}`}>
                <h2 className="text-3xl md:text-4xl font-bold mb-3 md:mb-4">
                  {gameState.won ? t('wojewodztwaPage.won') : t('wojewodztwaPage.gameOver')}
                </h2>
                <p className="text-lg md:text-xl mb-3 md:mb-4">
                  {gameState.won 
                    ? t('wojewodztwaPage.wonMessage')
                    : t('wojewodztwaPage.lostMessage')}
                </p>
                 {(correctWojewodztwo || guesses.find(g => g.answer)?.guess) && (
                    <p className="text-base md:text-lg">{t('wojewodztwaPage.answer')} <span className="font-bold">{correctWojewodztwo?.nazwa || guesses.find(g => g.answer)?.guess}</span></p>
                 )}
              </div>
            )}


            {!gameState.is_game_over && (
              <div className="space-y-6">
                <QuestionInput 
                  onAsk={askQuestion} 
                  isLoading={isLoading} 
                  remainingQuestions={gameState.remaining_questions} 
                  placeholder={t('wojewodztwaPage.askPlaceholder', { count: gameState.remaining_questions })}
                />
                
                <GuessInput 
                  countries={wojewodztwa} 
                  onGuess={async (id, name) => makeGuess(name, id)} 
                  isLoading={isLoading} 
                  remainingGuesses={gameState.remaining_guesses} 
                  placeholder={t('wojewodztwaPage.guessPlaceholder', { count: gameState.remaining_guesses })}
                />
              </div>
            )}

            <div>
               <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold">{t('wojewodztwaPage.history')}</h3>
                  <span className="text-sm text-zinc-500">{t('wojewodztwaPage.questionsAsked', { count: questions.length })}</span>
               </div>
               <History questions={questions} isGameOver={gameState.is_game_over} />
            </div>
        </div>

        <div className="lg:col-span-4 space-y-4 md:space-y-6">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 md:p-6 shadow-md">
               <h3 className="font-bold text-zinc-400 uppercase tracking-wider mb-4 text-[10px] md:text-sm">{t('wojewodztwaPage.status')}</h3>
               <div className="grid grid-cols-2 gap-3 md:gap-4">
                  <div className="text-center p-2 md:p-3 bg-zinc-800/50 rounded-lg">
                    <div className="text-xl md:text-2xl font-bold text-blue-500 mb-0.5 md:mb-1">
                      {gameState.remaining_questions}
                    </div>
                    <div className="text-[10px] md:text-xs text-zinc-500 uppercase leading-tight">{t('wojewodztwaPage.questionsLeft')}</div>
                  </div>
                  <div className="text-center p-2 md:p-3 bg-zinc-800/50 rounded-lg">
                    <div className="text-xl md:text-2xl font-bold text-teal-500 mb-0.5 md:mb-1">
                      {gameState.remaining_guesses}
                    </div>
                    <div className="text-[10px] md:text-xs text-zinc-500 uppercase leading-tight">{t('wojewodztwaPage.guessesLeft')}</div>
                  </div>
               </div>
            </div>

            {guesses.length > 0 && (
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 md:p-6 shadow-md">
                    <h3 className="font-bold text-zinc-400 uppercase tracking-wider mb-4 text-[10px] md:text-sm">{t('wojewodztwaPage.yourGuesses')}</h3>
                    <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1 custom-scrollbar">
                        {guesses.map((g) => (
                            <div key={g.id} className={`flex items-center justify-between p-2 md:p-3 rounded-lg border ${g.answer ? 'bg-green-900/20 border-green-500/50 text-green-400' : 'bg-red-900/20 border-red-500/50 text-red-400'} text-sm md:text-base`}>
                                <span className="font-medium truncate mr-2">{g.guess}</span>
                                {g.answer ? <span className="text-green-500 shrink-0 text-xs md:text-sm font-bold">{t('wojewodztwaPage.correct')}</span> : <span className="text-red-500 shrink-0 text-xs md:text-sm font-bold">{t('wojewodztwaPage.incorrect')}</span>}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>

      </div>
    </div>
  );
}
