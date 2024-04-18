const CACHE_NAME = 'version-1';
const urlsToCache = [  ];

self.addEventListener('install', (event) => {
    // Service worker installed
    console.log('Service Worker: Installed');
});

self.addEventListener('fetch', (event) => {
    // Intercept fetch requests and do nothing, just pass the fetch through
    event.respondWith(fetch(event.request));
});

self.addEventListener('activate', (event) => {
    // Service worker activated
    console.log('Service Worker: Activated');
    // Clean up old caches if necessary, not needed if you have no previous version of caches
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if(cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Removing old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});