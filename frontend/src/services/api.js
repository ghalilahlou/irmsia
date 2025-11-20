import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Health check
  health: () => apiClient.get('/health'),

  // Authentication
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  refreshToken: () => apiClient.post('/auth/refresh'),

  // File upload
  uploadFile: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post('/upload/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },

  uploadFiles: (files, onProgress) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    return apiClient.post('/upload/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },

  // Analysis
  getAnalyses: (filters = {}) => apiClient.get('/analysis', { params: filters }),
  getAnalysis: (id) => apiClient.get(`/analysis/${id}`),
  startAnalysis: (data) => apiClient.post('/analysis/start', data),
  cancelAnalysis: (id) => apiClient.post(`/analysis/${id}/cancel`),
  getAnalysisStatus: (id) => apiClient.get(`/analysis/${id}/status`),
  getAnalysisResult: (id) => apiClient.get(`/analysis/${id}/result`),
  getAnalysisMetrics: (id) => apiClient.get(`/analysis/${id}/metrics`),

  // Models
  getModels: () => apiClient.get('/models'),
  getModelInfo: (modelId) => apiClient.get(`/models/${modelId}`),
  updateModel: (modelId, data) => apiClient.put(`/models/${modelId}`, data),

  // Reports
  getReports: (filters = {}) => apiClient.get('/reports', { params: filters }),
  getReport: (id) => apiClient.get(`/reports/${id}`),
  generateReport: (analysisId, options = {}) => 
    apiClient.post(`/reports/generate`, { analysisId, ...options }),
  downloadReport: (id, format = 'pdf') => 
    apiClient.get(`/reports/${id}/download`, { 
      params: { format },
      responseType: 'blob'
    }),

  // 3D Viewer
  getVolumeData: (analysisId) => apiClient.get(`/viewer/${analysisId}/volume`),
  getSegmentationData: (analysisId) => apiClient.get(`/viewer/${analysisId}/segmentation`),
  exportScene: (analysisId, format) => 
    apiClient.post(`/viewer/${analysisId}/export`, { format }),

  // Settings
  getSettings: () => apiClient.get('/settings'),
  updateSettings: (settings) => apiClient.put('/settings', settings),

  // Users
  getProfile: () => apiClient.get('/users/profile'),
  updateProfile: (data) => apiClient.put('/users/profile', data),
  changePassword: (data) => apiClient.put('/users/password', data),

  // Notifications
  getNotifications: () => apiClient.get('/notifications'),
  markNotificationAsRead: (id) => apiClient.put(`/notifications/${id}/read`),
  markAllNotificationsAsRead: () => apiClient.put('/notifications/read-all'),

  // Statistics
  getStatistics: (period = 'week') => apiClient.get('/statistics', { params: { period } }),
  getAnalytics: (filters = {}) => apiClient.get('/analytics', { params: filters }),
};

// WebSocket connection for real-time updates
export const createWebSocket = (token) => {
  const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
  const ws = new WebSocket(`${wsUrl}?token=${token}`);

  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  return ws;
};

// File validation helpers
export const validateFile = (file) => {
  const maxSize = 100 * 1024 * 1024; // 100MB
  const allowedTypes = [
    'image/dicom',
    'application/dicom',
    'application/octet-stream',
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/bmp',
    'image/tiff',
  ];

  const allowedExtensions = [
    '.dcm',
    '.nii',
    '.nii.gz',
    '.mha',
    '.mhd',
    '.png',
    '.jpg',
    '.jpeg',
    '.bmp',
    '.tiff',
  ];

  const errors = [];

  // Check file size
  if (file.size > maxSize) {
    errors.push(`Le fichier ${file.name} est trop volumineux (max 100MB)`);
  }

  // Check file type
  const hasValidType = allowedTypes.includes(file.type) ||
    allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

  if (!hasValidType) {
    errors.push(`Le format de fichier ${file.name} n'est pas supporté`);
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Error handling
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return `Erreur de validation: ${data.message || 'Données invalides'}`;
      case 401:
        return 'Session expirée. Veuillez vous reconnecter.';
      case 403:
        return 'Accès refusé. Vous n\'avez pas les permissions nécessaires.';
      case 404:
        return 'Ressource non trouvée.';
      case 413:
        return 'Fichier trop volumineux. Taille maximale: 100MB.';
      case 422:
        return `Erreur de validation: ${data.detail || 'Données invalides'}`;
      case 500:
        return 'Erreur serveur. Veuillez réessayer plus tard.';
      default:
        return `Erreur ${status}: ${data.message || 'Une erreur est survenue'}`;
    }
  } else if (error.request) {
    // Network error
    return 'Erreur de connexion. Vérifiez votre connexion internet.';
  } else {
    // Other error
    return error.message || 'Une erreur inattendue est survenue';
  }
};

export default api; 