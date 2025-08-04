import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { AuthTokens, LoginCredentials, ApiError } from '@/types';
import { mockApiResponses } from './mockData';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const AUTH_URL = 'http://localhost:8000/api/token/';
const REFRESH_URL = 'http://localhost:8000/api/token/refresh';

// Development mode flag - set to true to use mock data in development
const USE_MOCK_DATA = true; // Set to false to use real API

// Rate limiting configuration
const RATE_LIMIT_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  backoffMultiplier: 2,
};

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Increased timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock API service for development
const mockApiService = {
  async get<T>(url: string): Promise<T> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const mockResponse = mockApiResponses[url as keyof typeof mockApiResponses];
    if (mockResponse) {
      return mockResponse as T;
    }
    
    // Return empty results for unknown endpoints
    return { results: [], count: 0 } as T;
  },

  async post<T>(_url: string, data?: any): Promise<T> {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Simulate successful creation
    return { 
      id: Date.now().toString(),
      ...data,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as T;
  },

  async put<T>(_url: string, data?: any): Promise<T> {
    await new Promise(resolve => setTimeout(resolve, 400));
    
    return { 
      ...data,
      updated_at: new Date().toISOString(),
    } as T;
  },

  async patch<T>(_url: string, data?: any): Promise<T> {
    await new Promise(resolve => setTimeout(resolve, 400));
    
    return { 
      ...data,
      updated_at: new Date().toISOString(),
    } as T;
  },

  async delete<T>(_url: string): Promise<T> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    return { success: true } as T;
  },

  async batch<T>(requests: Array<() => Promise<T>>): Promise<T[]> {
    const results = await Promise.allSettled(requests.map(req => req()));
    
    const fulfilled: T[] = [];
    const rejected: any[] = [];
    
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        fulfilled.push(result.value);
      } else {
        rejected.push({ index, error: result.reason });
      }
    });
    
    if (rejected.length > 0) {
      console.warn('Some batch requests failed:', rejected);
    }
    
    return fulfilled;
  },
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and rate limiting
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle rate limiting (429)
    if (error.response?.status === 429) {
      const retryCount = originalRequest._retryCount || 0;
      
      if (retryCount < RATE_LIMIT_CONFIG.maxRetries) {
        originalRequest._retryCount = retryCount + 1;
        
        // Calculate delay with exponential backoff
        const delay = RATE_LIMIT_CONFIG.retryDelay * Math.pow(RATE_LIMIT_CONFIG.backoffMultiplier, retryCount);
        
        console.warn(`Rate limited. Retrying in ${delay}ms (attempt ${retryCount + 1}/${RATE_LIMIT_CONFIG.maxRetries})`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return api(originalRequest);
      } else {
        console.error('Max retries reached for rate limiting');
        return Promise.reject({
          detail: 'Too many requests. Please try again later.',
          error: 'RATE_LIMIT_EXCEEDED',
        });
      }
    }

    // Handle authentication errors (401)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(REFRESH_URL, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication service
export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    if (USE_MOCK_DATA) {
      // Simulate successful login
      const mockTokens = {
        access: 'mock_access_token_' + Date.now(),
        refresh: 'mock_refresh_token_' + Date.now(),
      };
      
      localStorage.setItem('access_token', mockTokens.access);
      localStorage.setItem('refresh_token', mockTokens.refresh);
      
      return mockTokens;
    }

    const response = await axios.post(AUTH_URL, credentials);
    const { access, refresh } = response.data;
    
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return { access, refresh };
  },

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    if (USE_MOCK_DATA) {
      const mockTokens = {
        access: 'mock_access_token_' + Date.now(),
        refresh: refreshToken,
      };
      
      localStorage.setItem('access_token', mockTokens.access);
      return mockTokens;
    }

    const response = await axios.post(REFRESH_URL, { refresh: refreshToken });
    const { access } = response.data;
    
    localStorage.setItem('access_token', access);
    return { access, refresh: refreshToken };
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  getToken(): string | null {
    return localStorage.getItem('access_token');
  },
};

// Generic API service with enhanced error handling and mock data support
export const apiService = {
  // GET request with retry logic and mock data support
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    if (USE_MOCK_DATA) {
      return mockApiService.get<T>(url);
    }

    try {
      const response = await api.get<T>(url, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // POST request with retry logic and mock data support
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    if (USE_MOCK_DATA) {
      return mockApiService.post<T>(url, data);
    }

    try {
      const response = await api.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // PUT request with retry logic and mock data support
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    if (USE_MOCK_DATA) {
      return mockApiService.put<T>(url, data);
    }

    try {
      const response = await api.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // PATCH request with retry logic and mock data support
  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    if (USE_MOCK_DATA) {
      return mockApiService.patch<T>(url, data);
    }

    try {
      const response = await api.patch<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // DELETE request with retry logic and mock data support
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    if (USE_MOCK_DATA) {
      return mockApiService.delete<T>(url);
    }

    try {
      const response = await api.delete<T>(url, config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Batch request helper for multiple API calls
  async batch<T>(requests: Array<() => Promise<T>>): Promise<T[]> {
    if (USE_MOCK_DATA) {
      return mockApiService.batch<T>(requests);
    }

    try {
      const results = await Promise.allSettled(requests.map(req => req()));
      
      const fulfilled: T[] = [];
      const rejected: any[] = [];
      
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          fulfilled.push(result.value);
        } else {
          rejected.push({ index, error: result.reason });
        }
      });
      
      if (rejected.length > 0) {
        console.warn('Some batch requests failed:', rejected);
      }
      
      return fulfilled;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// Enhanced error handling utility
export const handleApiError = (error: any): ApiError => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data;
    
    // Handle specific HTTP status codes
    switch (status) {
      case 400:
        return {
          detail: data?.detail || 'Bad request. Please check your input.',
          error: 'BAD_REQUEST',
          details: data?.details,
        };
      case 401:
        return {
          detail: 'Authentication required. Please log in again.',
          error: 'UNAUTHORIZED',
        };
      case 403:
        return {
          detail: 'Access denied. You do not have permission to perform this action.',
          error: 'FORBIDDEN',
        };
      case 404:
        return {
          detail: 'Resource not found.',
          error: 'NOT_FOUND',
        };
      case 429:
        return {
          detail: 'Too many requests. Please try again later.',
          error: 'RATE_LIMIT_EXCEEDED',
        };
      case 500:
        return {
          detail: 'Internal server error. Please try again later.',
          error: 'INTERNAL_SERVER_ERROR',
        };
      case 502:
      case 503:
      case 504:
        return {
          detail: 'Service temporarily unavailable. Please try again later.',
          error: 'SERVICE_UNAVAILABLE',
        };
      default:
        return {
          detail: data?.detail || error.message || 'An unexpected error occurred',
          error: data?.error || 'UNKNOWN_ERROR',
          details: data?.details,
        };
    }
  }
  
  // Handle network errors
  if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
    return {
      detail: 'Network error. Please check your connection and try again.',
      error: 'NETWORK_ERROR',
    };
  }
  
  // Handle timeout errors
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return {
      detail: 'Request timeout. Please try again.',
      error: 'TIMEOUT',
    };
  }
  
  return {
    detail: error.message || 'An unexpected error occurred',
    error: 'UNKNOWN_ERROR',
  };
};

// Utility function to check if error is retryable
export const isRetryableError = (error: any): boolean => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    // Retry on 5xx errors, 429 (rate limit), and network errors
    return (status && status >= 500) || status === 429 || !error.response;
  }
  return false;
};

// Utility function to get error message for display
export const getErrorMessage = (error: any): string => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.detail) {
    return error.detail;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

// Development mode indicator
export const isDevelopmentMode = USE_MOCK_DATA;

export default api; 