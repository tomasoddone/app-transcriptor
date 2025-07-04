const CACHE_NAME = "transcriptor-cache-v1";
const ARCHIVOS_CACHEADOS = [
  "/",
  "/index.html",
  "/app.js",
  "/styles.css",
  "/manifest.json",
  "/icon-192.png",
  "/icon-512.png",
];

// Al instalar el Service Worker
self.addEventListener("install", (event) => {
  console.log("📦 Instalando Service Worker...");
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ARCHIVOS_CACHEADOS);
    })
  );
});

// Al activar el Service Worker
self.addEventListener("activate", (event) => {
  console.log("✅ Service Worker activado");
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
});

// Interceptar las peticiones
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return (
        cachedResponse ||
        fetch(event.request).catch(() =>
          caches.match("/index.html") // fallback para SPA
        )
      );
    })
  );
});
