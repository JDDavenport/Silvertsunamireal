import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LandingPage } from './views/LandingPage';
import { Onboarding } from './views/Onboarding';
import { Dashboard } from './views/Dashboard';
import { CheckoutResult } from './views/CheckoutResult';

const GOOGLE_CLIENT_ID = "238142947257-25pcmqi9vuamd1ntaoihbj8n9v7skt3s.apps.googleusercontent.com";

function AppRoutes() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <Routes>
      <Route 
        path="/" 
        element={isAuthenticated ? <Navigate to="/dashboard" /> : <LandingPage />} 
      />
      <Route 
        path="/onboarding" 
        element={isAuthenticated ? <Onboarding /> : <Navigate to="/" />} 
      />
      <Route 
        path="/dashboard/*" 
        element={isAuthenticated ? <Dashboard /> : <Navigate to="/" />} 
      />
      <Route path="/checkout" element={<CheckoutResult />} />
    </Routes>
  );
}

function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#1e293b',
                color: '#fff',
                border: '1px solid #334155'
              },
              success: {
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#1e293b'
                }
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#1e293b'
                }
              }
            }}
          />
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
