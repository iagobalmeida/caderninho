const CACHE_NAME = "pwa-cache-v1";
const urlsToCache = [
  "/",
  "/app",
  "/static/manifest.json",
  "/static/favicon/android-chrome-192x192.png",
  "/static/favicon/android-chrome-512x512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    }).catch(ex => {
        console.error(ex);
    })
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    }).catch(ex => {
        console.error(ex);
    })
  );
});
