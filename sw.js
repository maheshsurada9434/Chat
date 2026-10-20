// Vault Messenger service worker: app shell offline, network-first for the page.
const V = 'vault-chat-v3';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== V).map(x => caches.delete(x)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin) return; // never touch Supabase or CDN traffic
  e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(V).then(c => c.put(r, cp)); return res; }).catch(() => caches.match(r).then(m => m || caches.match('index.html'))));
});

self.addEventListener('push', e => {
  let d = {}; try { d = e.data.json(); } catch {}
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    if (cs.some(c => c.visibilityState === 'visible')) return; // the app shows its own pop-up
    return self.registration.showNotification(d.title || 'Vault Messenger', { body: d.body || 'New message', icon: 'icons/icon-192.png', badge: 'icons/icon-192.png', tag: d.thread || 'vm', data: { thread: d.thread } });
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close(); const thread = e.notification.data && e.notification.data.thread;
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    const c = cs[0]; if (c) { c.focus(); c.postMessage({ thread }); return; }
    return self.clients.openWindow('./');
  }));
});
