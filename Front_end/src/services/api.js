// src/services/api.js - VERSION SIMPLIFIÉE
// Use 'localhost' so cookies (session cookie set on login) are included correctly
export const API_BASE_URL = 'http://localhost:5000';

async function apiFetch(endpoint, options = {}) {
  const defaultOptions = {
    credentials: 'include', // ⭐ TOUJOURS 'include' pour les sessions
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...defaultOptions,
    ...options
  });

  if (response.status === 401) {
    // Rediriger vers login si non authentifié
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: (endpoint) => apiFetch(endpoint, { method: 'GET' }),
  post: (endpoint, data) => apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  put: (endpoint, data) => apiFetch(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  delete: (endpoint) => apiFetch(endpoint, { method: 'DELETE' })
};