import { create } from 'zustand';
import type { GameState, Question, Guess } from '../types';
import { gameService, powiatService, usStateService, wojewodztwoService } from '../services/api';

interface GameData {
  gameState: GameState | null;
  questions: Question[];
  guesses: Guess[];
  entities: any[]; // General entities (countries, powiaty, etc.)
  correctEntity: any | null;
  dailyDate: string | null;
  selectedEntityNames: string[];
  isLoading: boolean;
  error: string | null;
}

interface GameActions {
  fetchGameState: () => Promise<void>;
  fetchEntities: () => Promise<void>;
  askQuestion: (questionText: string) => Promise<void>;
  makeGuess: (guessText: string, entityId?: number) => Promise<void>;
  resetGame: () => void;
  toggleEntitySelection: (name: string) => void;
  clearSelection: () => void;
}

// Factory to create stores for different game types
const createGameStore = (gameType: 'country' | 'powiaty' | 'us_states' | 'wojewodztwa') => {
  const service = {
    country: gameService,
    powiaty: powiatService,
    us_states: usStateService,
    wojewodztwa: wojewodztwoService
  }[gameType];

  return create<GameData & GameActions>((set, get) => ({
    gameState: null,
    questions: [],
    guesses: [],
    entities: [],
    correctEntity: null,
    dailyDate: null,
    selectedEntityNames: [],
    isLoading: false,
    error: null,

    fetchGameState: async () => {
      set({ isLoading: true, error: null });
      try {
        const data = await service.getState(); 
        
        set({
          gameState: data.state,
          questions: data.questions,
          guesses: data.guesses,
          dailyDate: data.date,
          correctEntity: data.country || data.powiat || data.us_state || data.wojewodztwo || null,
          isLoading: false,
        });
      } catch (e: any) {
        console.error(e);
        set({ error: e.message || 'Failed to load game state', isLoading: false });
      }
    },

    fetchEntities: async () => {
      try {
        let entities = [];
        if (gameType === 'country') entities = await gameService.getCountries();
        else if (gameType === 'powiaty') entities = await powiatService.getPowiaty();
        else if (gameType === 'us_states') entities = await usStateService.getStates();
        else if (gameType === 'wojewodztwa') entities = await wojewodztwoService.getWojewodztwa();
        
        set({ entities });
      } catch (e) {
        console.error(e);
      }
    },

    askQuestion: async (questionText: string) => {
      set({ isLoading: true, error: null });
      try {
        await service.askQuestion(questionText);
        await get().fetchGameState();
      } catch (e: any) {
         console.error(e);
         if (e.response?.status === 400 && e.response?.data?.detail?.includes("over")) {
             await get().fetchGameState();
         } else {
             set({ error: e.response?.data?.detail || 'Failed to ask question', isLoading: false });
         }
      }
    },

    makeGuess: async (guessText: string, entityId?: number) => {
      set({ isLoading: true, error: null });
      try {
        await service.makeGuess(guessText, entityId);
        await get().fetchGameState();
      } catch (e: any) {
          console.error(e);
          if (e.response?.status === 400 && e.response?.data?.detail?.includes("over")) {
              await get().fetchGameState();
          } else {
              set({ error: e.response?.data?.detail || 'Failed to make guess', isLoading: false });
          }
      }
    },
    
    resetGame: () => set({ 
        gameState: null, 
        questions: [], 
        guesses: [], 
        selectedEntityNames: [], 
        correctEntity: null, 
        error: null 
    }),
    
    toggleEntitySelection: (name: string) => {
      const { selectedEntityNames } = get();
      if (selectedEntityNames.includes(name)) {
        set({ selectedEntityNames: selectedEntityNames.filter(n => n !== name) });
        return;
      }
      set({ selectedEntityNames: [...selectedEntityNames, name] });
    },
    
    clearSelection: () => set({ selectedEntityNames: [] })
  }));
};

// Export specialized stores
export const useCountryGameStore = createGameStore('country');
export const usePowiatyGameStore = createGameStore('powiaty');
export const useUSStatesGameStore = createGameStore('us_states');
export const useWojewodztwaGameStore = createGameStore('wojewodztwa');

// Default export for backward compatibility (pointing to country store)
export const useGameStore = useCountryGameStore;
