import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface User {
  account_id: number;
  nickname: string;
  first_name: string;
  last_name: string;
  primary_condition: string;
  privacy_level: string;
  share_medical_info: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nickname: string;
  first_name?: string;
  last_name?: string;
  primary_condition?: string;
  conditions?: Record<string, any>;
  medications?: Record<string, any>;
  emergency_contact?: Record<string, any>;
  privacy_level?: string;
  share_medical_info?: boolean;
  accessibility_needs?: Record<string, any>;
  timezone?: string;
  language?: string;
  country?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token: string;
  user: User;
}

class AuthService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // 現在のユーザー情報を取得
  async getCurrentUser(): Promise<User> {
    try {
      const response = await axios.get(`${this.baseURL}/auth/me`);
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  }

  // ログイン
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      // 実際のログインAPIを呼び出し
      const response = await axios.post(`${this.baseURL}/auth/login`, credentials);
      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  // ユーザー登録
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      // 実際の登録APIを呼び出し
      const response = await axios.post(`${this.baseURL}/auth/register`, userData);
      return response.data;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  // ログアウト
  async logout(): Promise<void> {
    try {
      // トークンをクリア
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }

  // トークンリフレッシュ
  async refreshToken(): Promise<AuthResponse> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await axios.post(`${this.baseURL}/auth/refresh`, {
        refresh_token: refreshToken
      });
      
      // 新しいトークンを保存
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      
      return response.data;
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw error;
    }
  }

  // 認証状態をチェック
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  // 保存されたユーザー情報を取得
  getStoredUser(): User | null {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Failed to parse stored user:', error);
      return null;
    }
  }

  // ユーザー情報を保存
  storeUser(user: User): void {
    localStorage.setItem('user', JSON.stringify(user));
  }

  // トークンを保存
  storeTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }
}

export const authService = new AuthService();

