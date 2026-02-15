import axios from 'axios';
import config from '../config.json';
import { User } from '../stores/auth';

console.log(config.version);

export interface MyState {
  id: number;
  day: {
    date: string;
    country: {name: string; official_name: string} | null;
  },
  points: number;
  guesses_made: number;
  questions_asked: number;
  won: boolean;
}

export interface ProfileState {
  user: {
      username: string;
      created_at: string | null;
  },
  points: number;
  streak: number;
  wins: number;
  questions_asked: number;
  questions_correct: number;
  questions_incorrect: number;
  guesses_made: number;
  guesses_correct: number;
  guesses_incorrect: number;
  history: Array<MyState>;
}

const apiClient = axios.create({
  baseURL: config.apiUrl,
  withCredentials: true,   // Include credentials for cross-origin requests
  headers: {
    "Content-Type": "application/json", // Form-encoded data for auth
  },
});

const authClient = axios.create({
  baseURL: config.apiUrl,
  headers: {
    "Content-Type": "application/x-www-form-urlencoded", // Form-encoded data for auth
  },
});

apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API error:', error.response || error.message);
    if(error.status >= 500) return Promise.reject(error);

    return error.response
  }
);
// API service for the game
export const apiService = {
  async login(credentials: { username: string; password: string }) {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return await authClient.post("/login", formData);
  },
  async logout(): Promise<{success: boolean}>{
    return await apiClient.post(`${config.apiUrl}/logout`, {},
    {
    withCredentials: true
    });
  },
  async getUser() {
    const response = await axios.get(`${config.apiUrl}/users/me`, {
    withCredentials: true
    });
    return response
  },
  googleSignIn(credential: string) {
    return apiClient.post("/google-signin", { credential: credential });
  },
  register(credentials: {username: string; email: string; password: string}) {
    return apiClient.post('/register', credentials);
  },
  getGameState() {
    return apiClient.get('/countrydle/state');
  },

  askQuestion(question: string) {
    return apiClient.post('/countrydle/question', { question });
  },

  makeGuess(guess: string, country_id?: number) {
    return apiClient.post('/countrydle/guess', { guess, country_id });  // Submit a guess
  },
  getCountries() {
    return apiClient.get('/countrydle/countries');
  },

  endGame() {
    return apiClient.get('/countrydle/end/state');  // End the game and get the final result (country and explanations)
  },
  getCountrydleHistory() {
    return apiClient.get('/countrydle/statistics/history');  // End the game and get the final result (country and explanations)
  },
  async getMyHistory(): Promise<{data: Array<MyState>}> {
    return apiClient.get('/countrydle/statistics/history/me');  // End the game and get the final result (country and explanations)
  },
  updateUser(user: User) {
    return apiClient.post('/users/update', user);  // End the game and get the final result (country and explanations)
  },
  changePassword(password: string) {
    return apiClient.post('/users/change/password', { password });  // End the game and get the final result (country and explanations)
  },
  getLeaderboard() {
    return apiClient.get('/countrydle/statistics/leaderboard');
  },
  getUserProfile(username: string) {
    return apiClient.get(`/countrydle/statistics/users/${username}`);
  }
};