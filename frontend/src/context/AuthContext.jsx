import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const role  = localStorage.getItem('role');
    const name  = localStorage.getItem('name');
    const uid   = localStorage.getItem('user_id');
    if (token) setUser({ token, role, name, user_id: uid });
  }, []);

  const login = (data) => {
    localStorage.setItem('token',   data.access_token);
    localStorage.setItem('role',    data.role);
    localStorage.setItem('name',    data.name);
    localStorage.setItem('user_id', data.user_id);
    setUser({ token: data.access_token, role: data.role, name: data.name, user_id: data.user_id });
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
