import React from 'react';
import ReactDOM from 'react-dom/client';
import { MsalProvider } from '@azure/msal-react';
import { PublicClientApplication } from '@azure/msal-browser';
import { msalConfig } from './authConfig';
import App from './App';
import './index.css';

const msalInstance = new PublicClientApplication(msalConfig);

// Initialize MSAL and process any redirect response BEFORE rendering
msalInstance.initialize().then(async () => {
  // If returning from a login redirect, this exchanges the code for tokens
  const response = await msalInstance.handleRedirectPromise();
  if (response) {
    msalInstance.setActiveAccount(response.account);
  }

  // Only render after MSAL is fully ready
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </React.StrictMode>
  );
});
