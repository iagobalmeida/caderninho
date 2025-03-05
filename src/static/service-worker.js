const CACHE_NAME = "pwa-cache-v1";
const urlsToCache = [
  "/",
  "/app",
  "/static/manifest.json",
  "/static/style.css",
  "/static/tabler.min.css",
  "/static/logo.svg",
  "/static/imgs/Phone-Customization--Streamline-Brooklyn.png",
  "/static/imgs/Projection--Streamline-Brooklyn.png",
  "/static/imgs/Too-Busy-2--Streamline-Brooklyn.png",
  "/static/favicon/android-chrome-192x192.png",
  "/static/favicon/android-chrome-512x512.png",
  "/static/favicon/favicon.ico"
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
