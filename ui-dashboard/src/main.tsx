/**
 * @file      : main.tsx
 * @summary   :
 * @author    : Charles Best <cbest@nvidia.com>
 * @created   : 2023-12-14
 * @copywrite : 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * @exports   : main
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// 1. Get the root element and create the React root ONCE.
const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

// 2. BYPASS KEYCLOAK FOR VM TESTING
// Instead of waiting for authentication, we just immediately render the dashboard.
console.log("[VM Bypass] Skipping Keycloak auth. Booting directly to App.");

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);