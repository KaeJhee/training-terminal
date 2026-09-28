/* Repeat-visit cache. HTML is network-first so a new deploy shows up.
   Vendor files and the Pyodide CDN are cache-first. */
const CACHE = 'ghost-training-v4.0.5';
const PRECACHE = [
  './',
  './index.html',
  './content-bundle.js',
  './pyodide-worker.js',
  './favicon.ico',
  './favicon.svg',
  './favicon-32x32.png',
  './apple-touch-icon.png',
  './og.png',
  './vendor/fonts/fonts.css',
  './vendor/fonts/dm-mono-400.woff2',
  './vendor/fonts/dm-mono-500.woff2',
  './vendor/fonts/dm-sans-latin.woff2',
  './vendor/xterm/xterm.css',
  './vendor/xterm/xterm.js',
  './vendor/xterm/addon-fit.js',
  './vendor/sql.js/sql-wasm.js',
  './vendor/sql.js/sql-wasm.wasm',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

function isHtml(request, url) {
  return request.mode === 'navigate' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/');
}

async function networkFirst(request) {
  const cache = await caches.open(CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (_) {
    const cached = await cache.match(request) || await cache.match('./index.html');
    if (cached) return cached;
    throw _;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  const fresh = await fetch(request);
  if (fresh && (fresh.ok || fresh.type === 'opaque')) {
    try { cache.put(request, fresh.clone()); } catch (_) {}
  }
  return fresh;
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin === self.location.origin) {
    event.respondWith(isHtml(request, url) ? networkFirst(request) : cacheFirst(request));
    return;
  }
  if (url.hostname === 'cdn.jsdelivr.net') {
    event.respondWith(cacheFirst(request));
  }
});
