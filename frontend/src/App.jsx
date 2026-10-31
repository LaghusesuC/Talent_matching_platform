import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuth } from './context/AuthContext';
import AuthPage from './pages/AuthPage';
import StudentDashboard from './pages/StudentDashboard';
import RecruiterDashboard from './pages/RecruiterDashboard';
import AdminDashboard from './pages/AdminDashboard';

function ProtectedRoute({ role, children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const { user } = useAuth();

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--color-surface)',
            color: 'var(--color-text)',
            border: '1px solid var(--border-color)',
            boxShadow: 'var(--shadow-card)',
            borderRadius: '10px',
            fontSize: '0.9rem',
            fontWeight: 500,
          },
        }}
      />
      <Routes>
        <Route path="/login" element={
          user ? <Navigate to={`/${user.role}`} /> : <AuthPage />
        } />

        <Route path="/student/*" element={
          <ProtectedRoute role="student"><StudentDashboard /></ProtectedRoute>
        } />

        <Route path="/recruiter/*" element={
          <ProtectedRoute role="recruiter"><RecruiterDashboard /></ProtectedRoute>
        } />

        <Route path="/admin/*" element={
          <ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>
        } />

        <Route path="/" element={
          user ? <Navigate to={`/${user.role}`} /> : <Navigate to="/login" />
        } />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </>
  );
}
