import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function AuthPage() {
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'student',
    company_name: '',
    department: '',
    cgpa: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handle = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const endpoint = tab === 'login' ? '/auth/login' : '/auth/register';
      const payload =
        tab === 'login'
          ? { email: form.email, password: form.password }
          : { ...form, cgpa: form.cgpa ? parseFloat(form.cgpa) : null };
      const { data } = await api.post(endpoint, payload);
      login(data);
      navigate(data.role === 'student' ? '/student' : data.role === 'recruiter' ? '/recruiter' : '/admin');
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card fade-in">
        <div className="auth-logo">
          <div className="auth-logo-icon">🎯</div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--color-text)' }}>TalentMatch AI</h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Next-Gen Campus Placement & Resume Screening
          </p>
        </div>

        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${tab === 'login' ? 'active' : ''}`}
            onClick={() => setTab('login')}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`auth-tab ${tab === 'register' ? 'active' : ''}`}
            onClick={() => setTab('register')}
          >
            Create Account
          </button>
        </div>

        {error && <div className="auth-error">⚠️ {error}</div>}

        <form onSubmit={submit}>
          {tab === 'register' && (
            <>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  name="name"
                  className="form-input"
                  placeholder="e.g. Priya Sharma"
                  value={form.name}
                  onChange={handle}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Role</label>
                <select name="role" className="form-select" value={form.role} onChange={handle}>
                  <option value="student">🎓 Student / Candidate</option>
                  <option value="recruiter">🏢 Corporate Recruiter</option>
                </select>
              </div>

              {form.role === 'student' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label className="form-label">Department</label>
                    <input
                      name="department"
                      className="form-input"
                      placeholder="e.g. Computer Science"
                      value={form.department}
                      onChange={handle}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">CGPA</label>
                    <input
                      name="cgpa"
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      className="form-input"
                      placeholder="e.g. 8.7"
                      value={form.cgpa}
                      onChange={handle}
                    />
                  </div>
                </div>
              )}

              {form.role === 'recruiter' && (
                <div className="form-group">
                  <label className="form-label">Company Name</label>
                  <input
                    name="company_name"
                    className="form-input"
                    placeholder="e.g. TCS, Zoho, Infosys, HCL"
                    value={form.company_name}
                    onChange={handle}
                    required
                  />
                </div>
              )}
            </>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              name="email"
              type="email"
              className="form-input"
              placeholder="you@domain.com"
              value={form.email}
              onChange={handle}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              name="password"
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={form.password}
              onChange={handle}
              required
              minLength={6}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full btn-lg"
            disabled={loading}
            style={{ marginTop: '0.75rem' }}
          >
            {loading ? 'Authenticating...' : tab === 'login' ? 'Sign In →' : 'Create Account →'}
          </button>
        </form>
      </div>
    </div>
  );
}
