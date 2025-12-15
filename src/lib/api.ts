// API configuration for Flask backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

// Generic API client
export const apiClient = {
  get: async (endpoint: string, options?: RequestInit) => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  },

  post: async (endpoint: string, data?: any, options?: RequestInit) => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  },

  put: async (endpoint: string, data?: any, options?: RequestInit) => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  },

  delete: async (endpoint: string, options?: RequestInit) => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  },
};

// Auth API
export const authAPI = {
  register: (userData: any) => apiClient.post('/auth/register', userData),
  login: (credentials: any) => apiClient.post('/auth/login', credentials),
  getProfile: () => apiClient.get('/auth/profile'),
};

// Studies API
export const studiesAPI = {
  getStudies: (params?: any) => {
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
    return apiClient.get(`/studies${queryString}`);
  },
  getStudy: (studyId: string) => apiClient.get(`/studies/${studyId}`),
  createStudy: (studyData: any) => apiClient.post('/studies', studyData),
  applyToStudy: (studyId: string, applicationData?: any) => 
    apiClient.post(`/studies/${studyId}/apply`, applicationData),
  getStudyApplications: (studyId: string) =>
    apiClient.get(`/studies/${studyId}/applications`),
  getStudyParticipants: (studyId: string) =>
    apiClient.get(`/studies/${studyId}/participants`),
};

// Matching API
export const matchingAPI = {
  getMatchedParticipants: (studyId: string) => 
    apiClient.get(`/matching/participants/${studyId}`),
  getMatchedStudies: () => 
    apiClient.post(`/matching/studies`),
};

// Messages API
export const messagesAPI = {
  getMessages: (params?: any) => {
    const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
    return apiClient.get(`/messages/${queryString}`);
  },
  sendMessage: (messageData: any) => apiClient.post('/messages', messageData),
  getConversations: () => apiClient.get('/messages/conversations'),
  markAsRead: (messageId: string) => 
    apiClient.put(`/messages/${messageId}/read`),
};

// Participants API
export const participantsAPI = {
  getProfile: () => apiClient.get('/participants/profile'),
  updateProfile: (profileData: any) => 
    apiClient.put('/participants/profile', profileData),
  getApplications: () => apiClient.get('/participants/applications'),
  getParticipations: () => apiClient.get('/participants/participations'),
};

// Researchers API
export const researchersAPI = {
  getProfile: () => apiClient.get('/researchers/profile'),
  updateProfile: (profileData: any) => 
    apiClient.put('/researchers/profile', profileData),
};