import axios from 'axios';

// Vite proxy configuration forwards /api/ to http://localhost:8000/
const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * Upload resume and get parsed text/fields
   * @param {File} file 
   */
  parseResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await client.post('/parse-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Run the full end-to-end analysis (caching enabled)
   * @param {File} file 
   * @param {string} jobDescription 
   */
  runFullAnalysis: async (file, jobDescription) => {
    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_description', jobDescription);
    const response = await client.post('/full-analysis', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // Large timeout for fresh model inference & SHAP computations
    });
    return response.data;
  },

  /**
   * Fetch past analyses stored in the SQLite database
   */
  getHistory: async () => {
    const response = await client.get('/history');
    return response.data;
  },

  /**
   * Check backend health status
   */
  checkHealth: async () => {
    const response = await client.get('/health');
    return response.data;
  }
};

export default api;
