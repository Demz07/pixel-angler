/* Pixel Angler service worker - cache-first, full offline play */
const CACHE = 'pixel-angler-v1';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});
self.addEventListener('activate', e => { e.waitUntil(clients.claim()); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit ||
      fetch(e.request).then(res => {
        const cp = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, cp));
        return res;
      }).catch(() => caches.match('./index.html'))
    )
  );
});
