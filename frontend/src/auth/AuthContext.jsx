import { createContext, useContext, useEffect, useState } from 'react';
import { api, setTokens } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // on app load: if a refresh token exists, try to silently restore the session
    api('/portfolio')
      .then(r => (r.ok ? setUser({ authed: true }) : null))
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const res = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error('Invalid credentials');
    
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    setUser({ authed: true });
  }

  return (
    <AuthContext.Provider value={{ user, loading, login }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);