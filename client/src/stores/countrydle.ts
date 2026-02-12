import { defineStore } from 'pinia';
import { apiService } from '../services/api';

export interface Question {
  original_question: string;
  question: string;
  answer: boolean | null;
  valid: boolean;
  explanation?: string;
}

export interface Country { 
  name: string;
  official_name: string;
}

export interface GameState {
  questionsHistory: Array<Question>;
  guessHistory: Array<{
    guess: string;
    answer: boolean | null;
  }>;
  selectedCountries: Array<string>;
  remainingQuestions: number;
  remainingGuesses: number;
  isGameOver: boolean;
  won: boolean;
  correctCountry: Country | null;
  questionLimitReached: boolean;
  guessLimitReached: boolean;
  loading: boolean;
  error: string | null;
  gameDate: string;
  countrydleHistory: Array<{
    date: string;
    country: Country;
  }>;
  countriesCount: Array<{
    name: string;
    count: number;
    last: string;
  }>;
  leaderboard: Array<{
    username: string;
    points: number;
    streak: number;
    wins: number;
  }>;
  points: number;
}

export const useCountrydleStore = defineStore('countrydle', {
  // State section
  state: (): GameState => ({
    questionsHistory: [] as Array<Question>,
    selectedCountries: [] as Array<string>,
    guessHistory: [] as Array<{ guess: string; answer: boolean | null; }>,
    remainingQuestions: 10,
    remainingGuesses: 3,
    isGameOver: false,
    won: false,
    correctCountry: null,  
    questionLimitReached: false,
    guessLimitReached: false, 
    loading: false,  
    error: null,  
    gameDate: '',
    countrydleHistory: [],
    countriesCount: [],
    leaderboard: [],
    points: 0,
  }),

  // Actions section
  actions: {
    async loadGameState() {
      this.resetCorrect();

      const today = new Date().toISOString().split('T')[0];  
      if (this.gameDate !== today)   
        this.resetState()



      this.loading = true;
      try {
        const response = await apiService.getGameState();  
        this.questionsHistory = response.data.questions;
        this.guessHistory = response.data.guesses;
        this.remainingQuestions = response.data.state.remaining_questions;
        this.remainingGuesses = response.data.state.remaining_guesses;
        this.isGameOver = response.data.state.is_game_over;
        this.won = response.data.state.won;
        this.gameDate = response.data.date;

        if(this.isGameOver) this.endGame()
      } catch (err) {
        this.error = 'Failed to load the game state.';
        this.resetState();
      } finally {
        this.loading = false;
      }
    },

    async askQuestion(question: string) {
      if (this.remainingQuestions <= 0 || this.isGameOver) return;

      this.loading = true;
      try {
        const response = await apiService.askQuestion(question);  
        this.questionsHistory.push({ ...response.data });
        this.remainingQuestions--;
      } catch (err) {
        this.error = 'Failed to ask the question.';
      } finally {
        this.loading = false;
      }
    },
    async makeGuess(guess: string, country_id?: number) {
      if (this.remainingGuesses <= 0 || this.isGameOver) return;

      this.loading = true;
      try {
        const response = await apiService.makeGuess(guess, country_id);  
        this.guessHistory.push({ guess, answer: response.data.answer });
        this.remainingGuesses--;

        if (response.data.answer || this.remainingGuesses <= 0) {
          await this.endGame();
        }
      } catch (err) {
        this.error = 'Failed to submit the guess.';
      } finally {
        this.loading = false;
      }
    },

    async endGame() {
      this.loading = true;
      try {
        const response = await apiService.endGame();  
        this.correctCountry = response.data.country;
        this.questionsHistory = response.data.questions;
        this.guessHistory = response.data.guesses;
        this.remainingQuestions = response.data.state.remaining_questions;
        this.remainingGuesses = response.data.state.remaining_guesses;
        this.isGameOver = response.data.state.is_game_over;
        this.won = response.data.state.won;
        this.points = response.data.state.points;
      } catch (err) {
        this.error = 'Failed to end the game.';
      } finally {
        this.loading = false;
      }
    },
    handleCountryClick(countryName: string) {
      const index = this.selectedCountries.indexOf(countryName);
      if (index === -1) {
        this.selectedCountries.push(countryName);
        return true;
      } else {
        this.selectedCountries.splice(index, 1);
        return false;
      }
    },
    resetState() {
      this.questionsHistory = [];
      this.guessHistory = [];
      this.selectedCountries = [];
      this.remainingQuestions = 10;
      this.remainingGuesses = 3;
      this.isGameOver = false;
      this.won = false;
      this.correctCountry = null;
      this.points = 0;
    },
    resetCorrect() {
      this.isGameOver = false;
      this.won = false;
      this.correctCountry = null;
    },
    async getCountrydleHistory() {
      this.loading = true;
      try {
        const response = await apiService.getCountrydleHistory();
        this.countrydleHistory = response.data.daily_countries;
        this.countriesCount = response.data.countries_count;
      } catch (err) {
        this.error = 'Failed to load the countrydle history.';
      } finally {
        this.loading = false;
      }
    },
    async getLeaderboard() {
      this.loading = true;
      try {
        const response = await apiService.getLeaderboard();
        this.leaderboard = response.data;
      } catch (err) {
        this.error = 'Failed to load the leaderboard.';
      } finally {
        this.loading = false;
      }
    }
  },

  persist: {
    storage: localStorage,
  },
});
