const API_BASE = '/api';

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('af_token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(API_BASE + path, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    // Staff password change required — redirect
    if (res.status === 403 && data.must_change_password) {
      window.location.href = '/admin/change-password.html';
      return null;
    }
    throw { status: res.status, message: data.error || 'Request failed', data };
  }
  return data;
}

const api = {
  get: (path) => apiFetch(path),
  post: (path, body) => apiFetch(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => apiFetch(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: (path) => apiFetch(path, { method: 'DELETE' }),
};

window.api = api;
