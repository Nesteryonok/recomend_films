const CACHE_NAME = 'kinonavigator-v2';
const urlsToCache = [
  '/',
  '/index.html',
  '/logo192.png',
  '/logo512.png',
  '/favicon.ico'
];

// Установка
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Кэширование ресурсов...');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Активация
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('Удаление старого кэша:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      self.clients.claim()
    ])
  );
});

// Перехват запросов
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Если есть в кэше — возвращаем его
        if (response) {
          return response;
        }
        // Иначе — запрашиваем с сервера
        return fetch(event.request).then(
          (response) => {
            // Кэшируем ответ для будущих запросов
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
      .catch(() => {
        // Fallback для офлайн-режима
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
      })
  );
});