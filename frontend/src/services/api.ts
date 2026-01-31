import axios from 'axios';
import type {
  Session,
  Persona,
  Provider,
  SimulationStatus,
  SessionFormData,
  PersonaFormData,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sessions
export const sessionsApi = {
  list: async (): Promise<{ sessions: Session[]; total: number }> => {
    const response = await api.get('/sessions');
    return response.data;
  },

  get: async (id: string): Promise<Session> => {
    const response = await api.get(`/sessions/${id}`);
    return response.data;
  },

  create: async (data: SessionFormData): Promise<Session> => {
    const response = await api.post('/sessions', data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/sessions/${id}`);
  },
};

// Personas
export const personasApi = {
  list: async (): Promise<{ personas: Persona[]; total: number }> => {
    const response = await api.get('/personas');
    return response.data;
  },

  get: async (id: string): Promise<Persona> => {
    const response = await api.get(`/personas/${id}`);
    return response.data;
  },

  create: async (data: PersonaFormData): Promise<Persona> => {
    const response = await api.post('/personas', data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/personas/${id}`);
  },
};

// Providers
export const providersApi = {
  list: async (): Promise<{ providers: Provider[] }> => {
    const response = await api.get('/providers');
    return response.data;
  },

  test: async (providerName: string): Promise<{ status: string; message: string }> => {
    const response = await api.post(`/providers/${providerName}/test`);
    return response.data;
  },

  getModels: async (providerName: string): Promise<{ models: Provider['models'] }> => {
    const response = await api.get(`/providers/${providerName}/models`);
    return response.data;
  },
};

// Simulation
export const simulationApi = {
  start: async (sessionId: string): Promise<{ status: string; session_id: string }> => {
    const response = await api.post('/simulation/start', { session_id: sessionId });
    return response.data;
  },

  stop: async (sessionId: string): Promise<{ status: string }> => {
    const response = await api.post('/simulation/stop', null, {
      params: { session_id: sessionId },
    });
    return response.data;
  },

  getStatus: async (sessionId: string): Promise<SimulationStatus> => {
    const response = await api.get(`/simulation/status/${sessionId}`);
    return response.data;
  },

  // Create an EventSource for SSE streaming
  createEventSource: (sessionId: string): EventSource => {
    return new EventSource(`/api/simulation/stream/${sessionId}`);
  },
};

// Export/Import
export const exportApi = {
  exportSession: async (sessionId: string): Promise<Blob> => {
    const response = await api.get(`/export/${sessionId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  importSession: async (file: File): Promise<{ session_id: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/export/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getMarkdownReport: async (sessionId: string): Promise<string> => {
    const response = await api.get(`/export/report/${sessionId}/md`);
    return response.data;
  },

  getPdfReport: async (sessionId: string): Promise<Blob> => {
    const response = await api.get(`/export/report/${sessionId}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default api;
