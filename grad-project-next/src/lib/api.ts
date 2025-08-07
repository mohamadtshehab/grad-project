import axios from 'axios';
import { 
  User, 
  Book, 
  Character, 
  Relationship, 
  LoginCredentials, 
  RegisterCredentials,
  ApiResponse 
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<ApiResponse<User>> => {
    const response = await api.post('/auth/login/', credentials);
    return response.data;
  },
  
  register: async (credentials: RegisterCredentials): Promise<ApiResponse<User>> => {
    const response = await api.post('/auth/register/', credentials);
    return response.data;
  },
  
  logout: async (): Promise<void> => {
    await api.post('/auth/logout/');
    localStorage.removeItem('token');
  },
  
  forgotPassword: async (email: string): Promise<ApiResponse<{ message: string }>> => {
    const response = await api.post('/auth/forgot-password/', { email });
    return response.data;
  },
  
  resetPassword: async (token: string, password: string): Promise<ApiResponse<{ message: string }>> => {
    const response = await api.post('/auth/reset-password/', { token, password });
    return response.data;
  },
};

// Books API
export const booksApi = {
  getUserBooks: async (): Promise<ApiResponse<Book[]>> => {
    const response = await api.get('/books/');
    return response.data;
  },
  
  getBook: async (id: string): Promise<ApiResponse<Book>> => {
    const response = await api.get(`/books/${id}/`);
    return response.data;
  },
  
  uploadBook: async (file: File, isPublic: boolean): Promise<ApiResponse<Book>> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_public', isPublic.toString());
    
    const response = await api.post('/books/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  deleteBook: async (id: string): Promise<ApiResponse<{ message: string }>> => {
    const response = await api.delete(`/books/${id}/`);
    return response.data;
  },
  
  getPublicBooks: async (): Promise<ApiResponse<Book[]>> => {
    const response = await api.get('/books/public/');
    return response.data;
  },
};

// Characters API
export const charactersApi = {
  getBookCharacters: async (bookId: string): Promise<ApiResponse<Character[]>> => {
    const response = await api.get(`/books/${bookId}/characters/`);
    return response.data;
  },
  
  getCharacter: async (bookId: string, characterId: string): Promise<ApiResponse<Character>> => {
    const response = await api.get(`/books/${bookId}/characters/${characterId}/`);
    return response.data;
  },
};

// Relationships API
export const relationshipsApi = {
  getBookRelationships: async (bookId: string): Promise<ApiResponse<Relationship[]>> => {
    const response = await api.get(`/books/${bookId}/relationships/`);
    return response.data;
  },
};

// User API
export const userApi = {
  getProfile: async (): Promise<ApiResponse<User>> => {
    const response = await api.get('/user/profile/');
    return response.data;
  },
  
  updateProfile: async (data: Partial<User>): Promise<ApiResponse<User>> => {
    const response = await api.put('/user/profile/', data);
    return response.data;
  },
  
  changePassword: async (oldPassword: string, newPassword: string): Promise<ApiResponse<{ message: string }>> => {
    const response = await api.post('/user/change-password/', { old_password: oldPassword, new_password: newPassword });
    return response.data;
  },
  
  deleteAccount: async (): Promise<ApiResponse<{ message: string }>> => {
    const response = await api.delete('/user/account/');
    return response.data;
  },
};

export default api; 