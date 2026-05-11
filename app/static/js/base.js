/* ── app/static/js/base.js — Lógica compartida ── */

// Marca el nav-link activo según la ruta actual
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    if (href && href !== "/" && path.startsWith(href)) {
      link.classList.add("active");
    } else if (href === "/" && path === "/") {
      link.classList.add("active");
    }
  });
});
