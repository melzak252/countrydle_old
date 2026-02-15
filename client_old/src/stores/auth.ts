import { defineStore } from 'pinia';
import { apiService } from '../services/api';

export interface User {
    username: string;
    email: string;
}

export interface AuthState {
  user: User | null;
  isAuth: boolean;
  isGoogle: boolean;
  error: boolean;
  errorMessage: string;
}

export const useAuthStore = defineStore('auth', {
  // State section
  state: (): AuthState => ({
    user: null,
    isAuth: false,
    isGoogle: false,
    error: false,
    errorMessage: ''
  }),

  // Actions section
  actions: {
    async login(credentials: { username: string; password: string }) {        
        this.error = false;
        this.errorMessage = '';
        try {
            const response = await apiService.login(credentials);
            if(response.status !== 200) {
                this.error = true;
                this.errorMessage = response.data.detail;
                await this.logout()
                return;
            }
            this.user = response.data;
            this.isAuth = true;
            this.isGoogle = false;
        } catch(error: any) {
            this.error = true;
            this.errorMessage = error.response?.data?.detail || 'Login failed';
            await this.logout()
            return;
        }
    },
    async logout() {
        this.isAuth = false;
        this.isGoogle = false;
        this.user = null;
        await apiService.logout();
    },
    async checkAuth(): Promise<boolean> {
        const user = await this.getUser();
        if(!user) {
            this.logout();
            return false;
        }
        return true;
    },
    async getUser(): Promise<User | null> {
        this.error = false;
        this.errorMessage = '';
        try {
            const response = await apiService.getUser();
            if(response.status !== 200) {
                this.error = true;
                this.errorMessage = response.data.detail;
                return null;
            }
    
            const apiUser = response.data;
    
            if(!apiUser) {
                return null;
            }
    
            this.isAuth = true;
            this.user = apiUser;
            return apiUser;
        } catch (err: any) {
            this.error = true;
            this.errorMessage = err.response?.data?.detail || 'Failed to fetch user';
            return null;
        }
        
    },
    async googleSignIn(credential: string) {
        this.error = false;
        this.errorMessage = ''
        try {
            const response = await apiService.googleSignIn(credential);
            if(response.status !== 200) {
                this.error = true;
                this.errorMessage = response.data.detail;
                await this.logout();
                return;
            }
            this.user = response.data;
            this.isAuth = true;
            this.isGoogle = true;
        } catch (error: any) {
            this.error = true;
            this.errorMessage = error.response?.data?.detail || 'Google Sign-In failed';
            await this.logout()
        }
    },
    async updateUser(user: User) {
        this.error = false;
        this.errorMessage = '';
        try {
            const response = await apiService.updateUser(user);
            if(response.status !== 200) {
                this.error = true;
                this.errorMessage = response.data.detail;
                return response;
            }
            this.user = user;
            return response;

        } catch (error: any) {
            this.error = true;
            this.errorMessage = error.response?.data?.detail || 'Update failed';
            await this.logout()
            return error.response;
        }
    },
    async changePassword(password: string) {
        this.error = false;
        this.errorMessage = '';
        try {
            const response = await apiService.changePassword(password);
            if(response.status !== 200) {
                this.error = true;
                this.errorMessage = response.data.detail;
            }
            return response;
        } catch (error: any) {
            this.error = true;
            this.errorMessage = error.response?.data?.detail || 'Change password failed';
            return error.response;
        }
    }
  },
  persist: {
    storage: localStorage,
  },
});
