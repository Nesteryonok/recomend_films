import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

// Регистрация сервис-воркера для PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker зарегистрирован: ', registration.scope);
      })
      .catch(error => {
        console.log('Ошибка регистрации ServiceWorker: ', error);
      });
  });
}

const rootElement = document.getElementById('root');
const root = createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);