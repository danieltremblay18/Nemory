// Register the service worker so Nemory is installable and works offline.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .catch((err) => console.warn("Service worker registration failed:", err));
  });
}
