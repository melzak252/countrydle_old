import { create } from 'zustand';
import type { GameState, Question, Guess, CountryDisplay } from '../types';
import { gameService } from '../services/api';
``

interface GameStore {
  gameState: GameState | null;
  questions: Question[];
  guesses: Guess[];
  countries: CountryDisplay[];
  correctCountry: CountryDisplay | null; // For end state
  dailyCountryDate: string | null;
  selectedCountries: string[]; // Names of countries selected on map
  isLoading: boolean;
  error: string | null;
  
  fetchGameState: () => Promise<void>;
  fetchCountries: () => Promise<void>;
  askQuestion: (questionText: string) => Promise<void>;
  makeGuess: (guessText: string, countryId?: number) => Promise<void>;
  resetGame: () => void;
  toggleCountrySelection: (countryName: string) => void;
  clearSelection: () => void;
}

export const useGameStore = create<GameStore>((set, get) => ({
  gameState: null,
  questions: [],
  guesses: [],
  countries: [],
  correctCountry: null,
  dailyCountryDate: null,
  selectedCountries: [],
  isLoading: false,
  error: null,

  fetchGameState: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await gameService.getState();
      
      set({
        gameState: data.state,
        questions: data.questions,
        guesses: data.guesses,
        dailyCountryDate: data.date,
        correctCountry: data.country || null,
        isLoading: false,
      });
    } catch (e: any) {
      console.error(e);
      set({ error: e.message || 'Failed to load game state', isLoading: false });
    }
  },

  fetchCountries: async () => {
    try {
      const countries = await gameService.getCountries();
      set({ countries });
    } catch (e) {
      console.error(e);
    }
  },

  askQuestion: async (questionText: string) => {
    set({ isLoading: true, error: null });
    try {
      await gameService.askQuestion(questionText);
      
      // Update local state optimistically or re-fetch
      // Re-fetching is safer to ensure sync with backend logic (remaining questions etc)
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

  makeGuess: async (guessText: string, countryId?: number) => {
    set({ isLoading: true, error: null });
    try {
      await gameService.makeGuess(guessText, countryId);
      
       // Re-fetch to update state (win/loss/remaining)
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
  
  resetGame: () => set({ gameState: null, questions: [], guesses: [], selectedCountries: [], correctCountry: null, error: null }),
  
  toggleCountrySelection: (countryName: string) => {
    const { selectedCountries } = get();
    if (selectedCountries.includes(countryName)) {
      set({ selectedCountries: selectedCountries.filter(c => c !== countryName) });
      return;
    }
    console.log('Toggling selection for', countryName);
    set({ selectedCountries: [...selectedCountries, countryName] });
  },
  
  clearSelection: () => set({ selectedCountries: [] })
}));
