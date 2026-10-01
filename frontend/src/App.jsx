import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import Login from './pages/Login';
import Portfolio from './pages/Portfolio';

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p>Loading...</p>;
  return user ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/portfolio" element={<Protected><Portfolio /></Protected>} />
          <Route path="*" element={<Navigate to="/portfolio" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}