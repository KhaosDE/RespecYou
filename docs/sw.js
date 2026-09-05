const CACHE = 'respecyou-ios-1.4';
const SHELL = [
  './',
  './index.html',
  './manifest.json',
  './assets/fonts/PressStart2P-Regular.ttf',
  './assets/fonts/VT323-Regular.ttf',
  './icons/icon-180.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
];
// App-Code/Manifest immer frisch vom Netz holen (Updates sollen sofort ankommen);
// nur bei Netzfehler (offline) auf den Cache zurückfallen.
const NETWORK_FIRST = /\.html$|manifest\.json$|sw\.js$|\/$/;

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (NETWORK_FIRST.test(url.pathname)) {
    e.respondWith(
      fetch(e.request)
        .then((res) => { if (res.ok) caches.open(CACHE).then((c) => c.put(e.request, res.clone())); return res; })
        .catch(() => caches.match(e.request))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then((cached) => {
      const network = fetch(e.request)
        .then((res) => {
          if (res.ok) caches.open(CACHE).then((c) => c.put(e.request, res.clone()));
          return res;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
