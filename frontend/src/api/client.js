let accessToken = null;   // in-memory only: XSS can't steal what isn't in localStorage

export function setTokens(access, refresh) {
  accessToken = access;
  localStorage.setItem('refresh_token', refresh);  // refresh survives page reload
}

export async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...options.headers,
    },
  });

  // Transparent refresh: if the access token expired (15 min), get a new one
  // using the refresh token and retry the ORIGINAL request once.
  if (res.status === 401 && !path.startsWith('/auth/')) {
    if (await refresh()) {
      return api(path, options);        // retry once with the fresh token
    }
    logout();                            // refresh failed too -> back to login
  }
  return res;
}

async function refresh() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;
  const res = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  accessToken = data.access_token;       // slide the new access token into memory
  return true;
}

export function logout() {
  accessToken = null;
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}