import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface Post {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_name: string;
  created_at: string;
}

export interface PostCreate {
  title: string;
  content: string;
}

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // 投稿一覧を取得
  async getPosts(): Promise<Post[]> {
    try {
      const response = await axios.get(`${this.baseURL}/posts`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch posts:', error);
      throw error;
    }
  }

  // 投稿を作成
  async createPost(postData: PostCreate): Promise<Post> {
    try {
      const response = await axios.post(`${this.baseURL}/posts`, postData);
      return response.data;
    } catch (error) {
      console.error('Failed to create post:', error);
      throw error;
    }
  }

  // 投稿を更新
  async updatePost(id: number, postData: Partial<PostCreate>): Promise<Post> {
    try {
      const response = await axios.put(`${this.baseURL}/posts/${id}`, postData);
      return response.data;
    } catch (error) {
      console.error('Failed to update post:', error);
      throw error;
    }
  }

  // 投稿を削除
  async deletePost(id: number): Promise<void> {
    try {
      await axios.delete(`${this.baseURL}/posts/${id}`);
    } catch (error) {
      console.error('Failed to delete post:', error);
      throw error;
    }
  }

  // ヘルスチェック
  async healthCheck(): Promise<any> {
    try {
      const response = await axios.get(`${this.baseURL}/health`);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();

