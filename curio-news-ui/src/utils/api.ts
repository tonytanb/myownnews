import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add cache-busting parameter to all requests
apiClient.interceptors.request.use((config) => {
  if (config.url) {
    const separator = config.url.includes('?') ? '&' : '?';
    config.url = `${config.url}${separator}_t=${Date.now()}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const api = {
  async getBootstrap() {
    const response = await apiClient.get('/bootstrap');
    return response.data;
  },

  async generateFresh(payload?: any) {
    const response = await apiClient.post('/generate-fresh', payload);
    return response.data;
  },
};

export default apiClient;
