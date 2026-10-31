import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ links }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
  }, []);

  const changeTheme = (t) => {
    setTheme(t);
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('theme', t);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userInitial = user?.name ? user.name.charAt(0).toUpperCase() : 'U';

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🎯</div>
        <div>
          <div className="sidebar-logo-text">TalentMatch AI</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>CAMPUS PLACEMENT</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/admin' || to === '/student' || to === '/recruiter'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span style={{ fontSize: '1.1rem', width: 22, textAlign: 'center' }}>{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        {/* Live Theme Switcher */}
        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem', letterSpacing: '0.05em' }}>
          Theme
        </div>
        <div className="theme-switcher-box">
          <button
            type="button"
            className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
            onClick={() => changeTheme('light')}
            title="Clean Light Theme (Stripe/Linear)"
          >
            ☀️ Light
          </button>
          <button
            type="button"
            className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
            onClick={() => changeTheme('dark')}
            title="Midnight Dark Theme"
          >
            🌙 Dark
          </button>
          <button
            type="button"
            className={`theme-btn ${theme === 'cyber' ? 'active' : ''}`}
            onClick={() => changeTheme('cyber')}
            title="Cyber Emerald Theme"
          >
            🔮 Cyber
          </button>
        </div>

        <div className="user-profile-badge">
          <div className="user-avatar">{userInitial}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-text)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.name || 'User'}
            </div>
            <div style={{ fontSize: '0.725rem', color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>
              {user?.role}
            </div>
          </div>
          <span className="fit-badge fit-high" style={{ fontSize: '0.65rem', padding: '0.15rem 0.45rem' }}>
            ONLINE
          </span>
        </div>

        <button
          onClick={handleLogout}
          className="btn btn-outline btn-sm"
          style={{ width: '100%', justifyContent: 'center' }}
        >
          Sign Out
        </button>
      </div>
    </aside>
  );
}
