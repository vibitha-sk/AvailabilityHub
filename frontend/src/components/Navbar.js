import React from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from '../authConfig';
import './Navbar.css';

export default function Navbar() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const user = accounts[0];

  const handleLogin = () => instance.loginRedirect(loginRequest);
  const handleLogout = () => instance.logoutRedirect({ postLogoutRedirectUri: '/login' });

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="navbar-icon">🛍️</span>
        <span className="navbar-title">Product Availability Tracker</span>
      </div>
      <div className="navbar-actions">
        {isAuthenticated ? (
          <>
            <span className="navbar-user">👤 {user?.name || user?.username}</span>
            <button className="btn btn-outline" onClick={handleLogout}>Sign Out</button>
          </>
        ) : (
          <button className="btn btn-primary" onClick={handleLogin}>Sign In</button>
        )}
      </div>
    </nav>
  );
}
