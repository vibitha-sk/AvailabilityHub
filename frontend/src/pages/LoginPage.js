import React from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { Navigate } from 'react-router-dom';
import { loginRequest } from '../authConfig';
import './LoginPage.css';

export default function LoginPage() {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  if (isAuthenticated) return <Navigate to="/" replace />;

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-icon">🛍️</div>
        <h1 className="login-title">Product Availability Tracker</h1>
        <p className="login-subtitle">
          Track your favourite products and get notified the moment your size is back in stock.
        </p>
        <button
          className="login-btn"
          onClick={() => instance.loginRedirect(loginRequest)}
        >
          <img
            src="https://learn.microsoft.com/en-us/azure/active-directory/develop/media/howto-add-branding-in-apps/ms-symbollockup_mssymbol_19.svg"
            alt="Microsoft"
            className="ms-logo"
          />
          Sign in with Microsoft
        </button>
        <p className="login-note">Powered by Azure Entra ID</p>
      </div>
    </div>
  );
}
