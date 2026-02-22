import { useEffect, useState } from 'react';
import { useGameStore } from '../stores/gameStore';
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';
import QuestionInput from '../components/QuestionInput';
import History from '../components/History';
import GuessInput from '../components/GuessInput';
import MapBox from '../components/MapBox';
import GameInstructions from '../components/GameInstructions';
import { Loader2, ChevronDown, ChevronUp, Map as MapIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function GamePage() {
  const { 
    gameState, 
    questions, 
    guesses, 
    entities: countries, 
    correctEntity: correctCountry,
    isLoading, 
    fetchGameState, 
    fetchEntities: fetchCountries, 
    askQuestion, 
    makeGuess 
  } = useGameStore();
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
      fetchCountries();
    }
  }, [isAuthenticated, fetchGameState, fetchCountries]);

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
        <h2 className="text-3xl font-bold mb-2">{t('gamePage.title')}</h2>
        <p className="text-zinc-400">{t('gamePage.date', { date: useGameStore.getState().dailyDate })}</p>
      </div>

      <GameInstructions 
        gameName="Countrydle"
        examples={t('gamePage.examples', { returnObjects: true }) as string[]}
        scoring={{
          maxPoints: 2000,
          details: t('gamePage.scoringDetails', { returnObjects: true }) as string[]
        }}
      />

      {/* Collapsible Map Section */}
      <div className="mb-8 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-lg">
        <button 
          onClick={() => setIsMapOpen(!isMapOpen)}
          className="w-full p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
        >
          <div className="flex items-center gap-2">
            <MapIcon size={20} className="text-blue-500" />
            <span className="font-bold text-lg">{t('gamePage.map')}</span>
          </div>
          {isMapOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
        
        {isMapOpen && (
          <div className="p-0 animate-in fade-in slide-in-from-top-4 duration-300">
             <MapBox correctCountryName={correctCountry?.name} />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Main Column: Inputs & History (8 cols) */}
        <div className="lg:col-span-8 space-y-8">
            {gameState.is_game_over && (
              <div className={`text-center p-8 rounded-xl ${gameState.won ? 'bg-green-900/20 border border-green-500/50' : 'bg-red-900/20 border border-red-500/50'}`}>
                <h2 className="text-4xl font-bold mb-4">
                  {gameState.won ? t('gamePage.won') : t('gamePage.gameOver')}
                </h2>
                <p className="text-xl mb-4">
                  {gameState.won 
                    ? t('gamePage.wonMessage')
                    : t('gamePage.lostMessage')}
                </p>
                 {(correctCountry || guesses.find(g => g.answer)?.guess) && (
                    <p className="text-lg">{t('gamePage.answer')} <span className="font-bold">{correctCountry?.name || guesses.find(g => g.answer)?.guess}</span></p>
                 )}
              </div>
            )}

            {!gameState.is_game_over && (
              <div className="space-y-6">
                <QuestionInput 
                  onAsk={askQuestion} 
                  isLoading={isLoading} 
                  remainingQuestions={gameState.remaining_questions} 
                  placeholder={t('gamePage.askPlaceholder', { count: gameState.remaining_questions })}
                />
                
                <GuessInput 
                  countries={countries} 
                  onGuess={async (id, name) => makeGuess(name, id)} 
                  isLoading={isLoading} 
                  remainingGuesses={gameState.remaining_guesses} 
                  placeholder={t('gamePage.guessPlaceholder', { count: gameState.remaining_guesses })}
                />
              </div>
            )}

            <div>
               <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold">{t('gamePage.history')}</h3>
                  <span className="text-sm text-zinc-500">{t('gamePage.questionsAsked', { count: questions.length })}</span>
               </div>
               <History questions={questions} isGameOver={gameState.is_game_over} />
            </div>
        </div>

        {/* Side Column: Stats & Guesses (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
               <h3 className="font-bold text-zinc-400 uppercase tracking-wider mb-4 text-sm">{t('gamePage.status')}</h3>
               <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-zinc-800/50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-500 mb-1">
                      {gameState.remaining_questions}
                    </div>
                    <div className="text-xs text-zinc-500 uppercase">{t('gamePage.questionsLeft')}</div>
                  </div>
                  <div className="text-center p-3 bg-zinc-800/50 rounded-lg">
                    <div className="text-2xl font-bold text-teal-500 mb-1">
                      {gameState.remaining_guesses}
                    </div>
                    <div className="text-xs text-zinc-500 uppercase">{t('gamePage.guessesLeft')}</div>
                  </div>
               </div>
            </div>

            {guesses.length > 0 && (
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                    <h3 className="font-bold text-zinc-400 uppercase tracking-wider mb-4 text-sm">{t('gamePage.yourGuesses')}</h3>
                    <div className="space-y-2">
                        {guesses.map((g) => (
                            <div key={g.id} className={`flex items-center justify-between p-3 rounded-lg border ${g.answer ? 'bg-green-900/20 border-green-500/50 text-green-400' : 'bg-red-900/20 border-red-500/50 text-red-400'}`}>
                                <span className="font-medium">{g.guess}</span>
                                {g.answer ? <span className="text-green-500">{t('gamePage.correct')}</span> : <span className="text-red-500">{t('gamePage.incorrect')}</span>}
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
