/**
 * Service Worker untuk Trading Platform Modern
 * Development-friendly dengan cache control
 */
const CACHE_NAME = 'trading-platform-v1.0.0';
const CACHE_VERSION = '1.0.0';

// Files to cache for offline functionality
const STATIC_CACHE_URLS = [
  '/',
  '/pages/index.html',
  '/pages/fundamental.html',
  '/pages/sentiment.html',
  '/pages/trading.html',
  '/pages/notifications.html',
  '/manifest.json',
  // CSS files
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.datatables.net/1.13.7/css/dataTables.bootstrap5.min.css',
  // JS files
  'https://code.jquery.com/jquery-3.7.1.min.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
  'https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js',
  'https://cdn.datatables.net/1.13.7/js/dataTables.bootstrap5.min.js',
  'https://cdn.socket.io/4.7.2/socket.io.min.js'
];

// API endpoints to cache (with short TTL)
const API_CACHE_URLS = [
  '/api/v1/health',
  '/api/v1/security/status'
];

// Development mode flag
const IS_DEVELOPMENT = true; // Set to false in production

// Install event
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip external requests (except CDN)
  if (url.origin !== location.origin && !isCDNRequest(url)) {
    return;
  }
  
  // Development mode: Skip caching for API requests
  if (IS_DEVELOPMENT && url.pathname.startsWith('/api/')) {
    console.log('Service Worker: Development mode - skipping API cache');
    return;
  }
  
  event.respondWith(
    handleRequest(request)
  );
});

// Handle different types of requests
async function handleRequest(request) {
  const url = new URL(request.url);
  
  try {
    // Static files (HTML, CSS, JS, images)
    if (isStaticFile(url)) {
      return await handleStaticFile(request);
    }
    
    // API requests
    if (url.pathname.startsWith('/api/')) {
      return await handleAPIRequest(request);
    }
    
    // Default: try cache first, then network
    return await handleDefaultRequest(request);
    
  } catch (error) {
    console.error('Service Worker: Request handling error', error);
    return new Response('Service Worker Error', { status: 500 });
  }
}

// Handle static files
async function handleStaticFile(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    console.log('Service Worker: Serving from cache', request.url);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Service Worker: Network error for static file', error);
    return new Response('Offline - Static file not available', { status: 503 });
  }
}

// Handle API requests
async function handleAPIRequest(request) {
  const url = new URL(request.url);
  
  // Development mode: always fetch from network
  if (IS_DEVELOPMENT) {
    try {
      return await fetch(request);
    } catch (error) {
      console.error('Service Worker: API request failed', error);
      return new Response('API unavailable', { status: 503 });
    }
  }
  
  // Production mode: cache API responses
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    // Check if cache is still valid (5 minutes for API)
    const cacheTime = cachedResponse.headers.get('sw-cache-time');
    if (cacheTime && Date.now() - parseInt(cacheTime) < 5 * 60 * 1000) {
      return cachedResponse;
    }
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      // Add cache timestamp
      const responseClone = networkResponse.clone();
      responseClone.headers.set('sw-cache-time', Date.now().toString());
      cache.put(request, responseClone);
    }
    return networkResponse;
  } catch (error) {
    // Return cached response if available
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response('API unavailable', { status: 503 });
  }
}

// Handle default requests
async function handleDefaultRequest(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

// Helper functions
function isCDNRequest(url) {
  const cdnHosts = [
    'cdn.jsdelivr.net',
    'code.jquery.com',
    'cdn.datatables.net',
    'cdn.socket.io'
  ];
  return cdnHosts.some(host => url.hostname.includes(host));
}

function isStaticFile(url) {
  const staticExtensions = ['.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'];
  return staticExtensions.some(ext => url.pathname.endsWith(ext));
}

// Message handling for cache control
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'CLEAR_CACHE':
      clearCache();
      break;
      
    case 'UPDATE_CACHE':
      updateCache();
      break;
      
    case 'GET_CACHE_STATUS':
      getCacheStatus().then(status => {
        event.ports[0].postMessage(status);
      });
      break;
      
    default:
      console.log('Service Worker: Unknown message type', type);
  }
});

// Clear cache
async function clearCache() {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
  console.log('Service Worker: Cache cleared');
}

// Update cache
async function updateCache() {
  const cache = await caches.open(CACHE_NAME);
  await cache.addAll(STATIC_CACHE_URLS);
  console.log('Service Worker: Cache updated');
}

// Get cache status
async function getCacheStatus() {
  const cacheNames = await caches.keys();
  const cacheStatus = {};
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    cacheStatus[cacheName] = {
      size: keys.length,
      urls: keys.map(request => request.url)
    };
  }
  
  return {
    version: CACHE_VERSION,
    caches: cacheStatus,
    isDevelopment: IS_DEVELOPMENT
  };
}

// Background sync (for future use)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  console.log('Service Worker: Background sync');
  // Implement background sync logic here
}

// Push notifications (for future use)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/icon-72x72.png',
      tag: data.tag || 'trading-notification',
      data: data.data
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
});

console.log('Service Worker: Loaded successfully');
