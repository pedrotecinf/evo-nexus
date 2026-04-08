const API = import.meta.env.DEV ? 'http://localhost:8080' : '';

export const api = {
  get: async (path: string) => {
    const res = await fetch(`${API}/api${path}`, { credentials: 'include' });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  },
  getRaw: async (path: string) => {
    const res = await fetch(`${API}/api${path}`, { credentials: 'include' });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.text();
  },
  post: async (path: string, body?: unknown) => {
    const res = await fetch(`${API}/api${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  },
  put: async (path: string, body?: unknown) => {
    const res = await fetch(`${API}/api${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  },
  delete: async (path: string) => {
    const res = await fetch(`${API}/api${path}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  },
};
