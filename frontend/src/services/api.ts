import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { 
  LoginCredentials, 
  AuthTokens, 
  ApiError
} from '@/types';
import { mockApiResponses } from './mockData';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Debug logging to check the API URL
console.log('API_BASE_URL:', API_BASE_URL);
console.log('Environment variables:', import.meta.env);
const RATE_LIMIT_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000,
  backoffMultiplier: 2,
};

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});



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
          status: 429,
        });
      }
    }

    // Handle token refresh (401)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
              try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            const response = await axios.post('/api/token/refresh/', {
              refresh: refreshToken,
            });
            
            const { access } = response.data;
            localStorage.setItem('access_token', access);
            
            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access}`;
            return api(originalRequest);
          }
        } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// API Service class
export class ApiService {
  // Authentication
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    try {
      const response = await axios.post('/api/token/', credentials);
      const { access, refresh } = response.data;
      
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      return { access, refresh };
    } catch (error) {
      console.error('Login failed:', error);
      throw error; // Don't fallback to mock for authentication
    }
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    try {
      const response = await axios.post('/api/token/refresh/', {
        refresh: refreshToken,
      });
      
      const { access } = response.data;
      localStorage.setItem('access_token', access);
      
      return { access, refresh: refreshToken };
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw error;
    }
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // Mock data fallback method
  private getMockDataFallback(url: string): any {
    // Check if we have mock data for this endpoint
    const mockKey = Object.keys(mockApiResponses).find(key => {
      // Remove query parameters for matching
      const cleanUrl = url.split('?')[0];
      return cleanUrl.includes(key);
    });
    
    if (mockKey && mockKey in mockApiResponses) {
      console.log(`Mock data fallback triggered for: ${url} -> ${mockKey}`);
      let mockData = mockApiResponses[mockKey as keyof typeof mockApiResponses];
      
      // Apply filtering for stock alerts if needed
      if (mockKey === '/stock-alerts/' && url.includes('?')) {
        mockData = this.filterMockStockAlerts(mockData, url);
      }
      
      return mockData;
    }
    return null;
  }

  // Filter mock stock alerts based on query parameters
  private filterMockStockAlerts(mockData: any, url: string): any {
    const urlParams = new URLSearchParams(url.split('?')[1]);
    const alertType = urlParams.get('alert_type');
    const severity = urlParams.get('severity');
    const isResolved = urlParams.get('is_resolved');
    
    let filteredResults = mockData.results;
    
    if (alertType && alertType !== '') {
      filteredResults = filteredResults.filter((alert: any) => alert.alert_type === alertType);
    }
    
    if (severity && severity !== '') {
      filteredResults = filteredResults.filter((alert: any) => alert.severity === severity);
    }
    
    if (isResolved !== null) {
      const resolved = isResolved === 'true';
      filteredResults = filteredResults.filter((alert: any) => alert.is_resolved === resolved);
    }
    
    return {
      ...mockData,
      results: filteredResults,
      count: filteredResults.length
    };
  }

  // Generic API methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      // Clean up empty parameters from query string
      if (config?.params) {
        const cleanParams: any = {};
        Object.entries(config.params).forEach(([key, value]) => {
          if (value !== '' && value !== null && value !== undefined) {
            cleanParams[key] = value;
          }
        });
        config.params = cleanParams;
      }
      
      const response = await api.get<T>(url, config);
      return response.data;
    } catch (error) {
      console.error(`GET ${url} failed:`, error);
      
      // Fallback to mock data for specific endpoints
      const mockData = this.getMockDataFallback(url);
      if (mockData) {
        console.log(`Using mock data for ${url}`);
        return mockData as T;
      }
      
      throw handleApiError(error);
    }
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await api.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      console.error(`POST ${url} failed:`, error);
      throw handleApiError(error);
    }
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await api.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      console.error(`PUT ${url} failed:`, error);
      throw handleApiError(error);
    }
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await api.patch<T>(url, data, config);
      return response.data;
    } catch (error) {
      console.error(`PATCH ${url} failed:`, error);
      throw handleApiError(error);
    }
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await api.delete<T>(url, config);
      return response.data;
    } catch (error) {
      console.error(`DELETE ${url} failed:`, error);
      throw handleApiError(error);
    }
  }

  async batch<T>(requests: Array<() => Promise<T>>): Promise<T[]> {
    try {
      return await Promise.all(requests.map(req => req()));
    } catch (error) {
      console.error('Batch request failed:', error);
      throw handleApiError(error);
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Error handling utilities
export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    if (status === 400) {
      return {
        detail: data.detail || 'Bad request. Please check your input.',
        details: data,
        status,
      };
    } else if (status === 401) {
      return {
        detail: 'Authentication required. Please log in.',
        status,
      };
    } else if (status === 403) {
      return {
        detail: 'You do not have permission to perform this action.',
        status,
      };
    } else if (status === 404) {
      return {
        detail: 'The requested resource was not found.',
        status,
      };
    } else if (status === 429) {
      return {
        detail: 'Too many requests. Please try again later.',
        status,
      };
    } else if (status >= 500) {
      return {
        detail: 'Server error. Please try again later.',
        status,
      };
    } else {
      return {
        detail: data.detail || 'An unexpected error occurred.',
        details: data,
        status,
      };
    }
  } else if (error.request) {
    // Request was made but no response received
    return {
      detail: 'Network error. Please check your connection.',
      status: 0,
    };
  } else {
    // Something else happened
    return {
      detail: error.message || 'An unexpected error occurred.',
      status: 0,
    };
  }
};

export const isRetryableError = (error: any): boolean => {
  const status = error.response?.status;
  return status === 429 || status >= 500;
};

export const getErrorMessage = (error: any): string => {
  const apiError = handleApiError(error);
  return apiError.detail || 'An error occurred';
}; 