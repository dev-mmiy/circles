import axios from 'axios'

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API types
export interface Post {
  id: number
  title: string
  content: string
  group_id: number
  created_at: string
}

export interface PostCreate {
  title: string
  content: string
  group_id: number
}

export interface HealthCheck {
  status: string
  message: string
}

// API functions
export const apiService = {
  // Health check
  async getHealth(): Promise<HealthCheck> {
    const response = await api.get('/health')
    return response.data
  },

  // Posts
  async getPosts(): Promise<Post[]> {
    const response = await api.get('/api/posts')
    return response.data
  },

  async getPost(id: number): Promise<Post> {
    const response = await api.get(`/api/posts/${id}`)
    return response.data
  },

  async createPost(post: PostCreate): Promise<Post> {
    const response = await api.post('/api/posts', post)
    return response.data
  },

  // Status
  async getStatus(): Promise<HealthCheck> {
    const response = await api.get('/api/status')
    return response.data
  },
}

export default api
