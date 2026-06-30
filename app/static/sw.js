// Minimal service worker: precache the app shell, serve static assets
// cache-first, and fall back to the network for everything else (dynamic pages
// that require authentication should always hit the server).

const CACHE = "nemory-v1";
const SHELL = ["/static/css/style.css", "/static/js/app.js", "/static/icons/icon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  // Cache-first for static assets; network-first otherwise.
  if (request.url.includes("/static/")) {
    event.respondWith(
      caches.match(request).then((cached) => cached || fetch(request))
    );
  }
});
