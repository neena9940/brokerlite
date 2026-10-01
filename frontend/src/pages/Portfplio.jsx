import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();               // stop the browser's default page reload
    try {
      await login(email, password);
      navigate('/portfolio');         // success -> dashboard
    } catch {
      setError('Invalid credentials'); // deliberately generic, same as the backend
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>BrokerLite</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required />
      <button type="submit">Log in</button>
    </form>
  );
}