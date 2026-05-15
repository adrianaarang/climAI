// app/static/js/alertas.js
// Interfaz de alertas climáticas — tiempo real, filtros, Telegram

(function () {
  "use strict";

  // ── Estado ──────────────────────────────────────────────────────────────
  let todasLasAlertas = [];
  let filtroNivel = "todos";
  let filtroTipo  = null;
  let intervaloAuto = null;
  const INTERVALO_MS = 60_000;

  // ── Meta de alertas ─────────────────────────────────────────────────────
  const ALERT_META = {
    ROJA_CALOR:      { emoji: "🌡️", label: "Calor extremo",    nivel: "ROJA"    },
    NARANJA_CALOR:   { emoji: "🌡️", label: "Calor intenso",    nivel: "NARANJA" },
    ROJA_FRIO:       { emoji: "❄️",  label: "Frío extremo",     nivel: "ROJA"    },
    NARANJA_FRIO:    { emoji: "❄️",  label: "Frío intenso",     nivel: "NARANJA" },
    ROJA_VIENTO:     { emoji: "💨",  label: "Viento muy fuerte",nivel: "ROJA"    },
    NARANJA_VIENTO:  { emoji: "💨",  label: "Viento fuerte",    nivel: "NARANJA" },
    ROJA_LLUVIA:     { emoji: "🌧️", label: "Lluvia torrencial", nivel: "ROJA"    },
    NARANJA_LLUVIA:  { emoji: "🌧️", label: "Lluvia intensa",   nivel: "NARANJA" },
    NARANJA_HUMEDAD: { emoji: "💧",  label: "Humedad alta",     nivel: "NARANJA" },
    VERDE:           { emoji: "✅",  label: "Sin alerta",       nivel: "VERDE"   },
  };

  // ── Helpers DOM ──────────────────────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const mostrarEstado = (id) => {
    ["loadingState", "errorState", "emptyState"].forEach((s) => {
      const el = $(`.${s}`) || document.getElementById(s);
      if (el) el.classList.toggle("hidden", s !== id && id !== null);
    });
    const grid = $("#alertasGrid");
    if (grid) grid.classList.toggle("hidden", id !== null);
  };

  function toast(msg, tipo = "ok") {
    const t = $("#toast");
    if (!t) return;
    t.textContent = msg;
    t.className = `toast show ${tipo}`;
    setTimeout(() => (t.className = "toast"), 3000);
  }

  // ── Carga de datos ───────────────────────────────────────────────────────
  async function cargarAlertas() {
    mostrarEstado("loadingState");
    try {
      const [resActivas, resResumen] = await Promise.all([
        fetch("/api/alertas/activas"),
        fetch("/api/alertas/resumen"),
      ]);

      if (!resActivas.ok) throw new Error(`HTTP ${resActivas.status}`);
      const dataActivas  = await resActivas.json();
      const dataResumen  = resResumen.ok ? await resResumen.json() : {};

      todasLasAlertas = dataActivas.alertas || [];

      actualizarResumen(dataResumen);
      renderAlertas();

    } catch (err) {
      console.error("[alertas] Error cargando:", err);
      mostrarEstado("errorState");
      const msg = document.getElementById("errorMsg");
      if (msg) msg.textContent = `Error: ${err.message}`;
    }
  }

  function actualizarResumen(data) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val ?? "—"; };
    set("numRoja",    data.rojas   ?? 0);
    set("numNaranja", data.naranja ?? 0);
    set("numVerde",   data.verde   ?? 0);
  }

  // ── Render ───────────────────────────────────────────────────────────────
  function renderAlertas() {
    const grid = document.getElementById("alertasGrid");
    if (!grid) return;

    let filtradas = todasLasAlertas.filter((a) => {
      if (filtroNivel !== "todos" && a.nivel_max !== filtroNivel) return false;
      if (filtroTipo && !a.alertas.some((x) => x.includes(filtroTipo))) return false;
      return true;
    });

    if (filtradas.length === 0) {
      mostrarEstado("emptyState");
      return;
    }

    mostrarEstado(null);
    grid.innerHTML = filtradas
      .map((a, i) => tarjetaHTML(a, i))
      .join("");

    // Eventos de botones notificar
    grid.querySelectorAll(".btn-notificar").forEach((btn) => {
      btn.addEventListener("click", () => {
        const datos = JSON.parse(btn.dataset.alerta || "{}");
        notificarTelegram(datos);
      });
    });
  }

  function tarjetaHTML(alerta, idx) {
    const nivel = alerta.nivel_max || "VERDE";
    const tiempo = alerta.timestamp
      ? new Date(alerta.timestamp).toLocaleString("es-ES", { hour12: false })
      : "—";

    const badgesAlertas = (alerta.alertas || [])
      .map((a) => {
        const meta = ALERT_META[a] || { emoji: "⚠️", label: a, nivel: "NARANJA" };
        return `<span class="alerta-badge ${meta.nivel}">${meta.emoji} ${meta.label}</span>`;
      })
      .join("");

    const fmt = (val, unit) =>
      val != null ? `<span class="metrica-valor">${val}${unit}</span>` : `<span class="metrica-valor" style="color:var(--text-muted)">N/D</span>`;

    const datosJson = JSON.stringify(alerta).replace(/"/g, "&quot;");

    return `
    <div class="alerta-card nivel-${nivel}" style="animation-delay:${idx * 0.05}s">
      <div class="card-top">
        <div>
          <div class="card-estacion">📍 ${alerta.station || "Estación desconocida"}</div>
          <div class="card-tiempo">${tiempo}</div>
        </div>
        <span class="nivel-badge ${nivel}">${nivel}</span>
      </div>

      <div class="card-metricas">
        <div class="metrica">
          <span class="metrica-label">🌡️ Temperatura</span>
          ${fmt(alerta.temperatura != null ? `${alerta.temperatura}` : null, "°C")}
        </div>
        <div class="metrica">
          <span class="metrica-label">💨 Viento</span>
          ${fmt(alerta.viento != null ? `${alerta.viento}` : null, " km/h")}
        </div>
        <div class="metrica">
          <span class="metrica-label">🌧️ Lluvia</span>
          ${fmt(alerta.lluvia != null ? `${alerta.lluvia}` : null, " mm")}
        </div>
        <div class="metrica">
          <span class="metrica-label">💧 Humedad</span>
          ${fmt(alerta.humedad != null ? `${alerta.humedad}` : null, "%")}
        </div>
      </div>

      <div class="card-alertas">${badgesAlertas}</div>

      <button class="btn-notificar" data-alerta="${datosJson}">
        ✈️ Notificar por Telegram
      </button>
    </div>`;
  }

  // ── Notificación Telegram ────────────────────────────────────────────────
  async function notificarTelegram(datos) {
    try {
      const resp = await fetch("/api/alertas/notificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
      });
      const res = await resp.json();
      if (res.status === "ok") {
        toast("✅ Notificación enviada por Telegram", "ok");
      } else if (res.message?.includes("Telegram")) {
        toast("⚠️ Vincula tu Telegram primero", "warn");
      } else {
        toast("❌ " + (res.message || "Error al notificar"), "error");
      }
    } catch {
      toast("❌ Error de conexión", "error");
    }
  }

  async function enviarPruebaTelegram() {
    try {
      const resp = await fetch("/api/alertas/notificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          station: "Prueba ClimAI",
          alertas: ["VERDE"],
          temperatura: 22,
          viento: 10,
          lluvia: 0,
          humedad: 55,
        }),
      });
      const res = await resp.json();
      if (res.status === "ok") {
        toast("✅ Mensaje de prueba enviado", "ok");
      } else {
        toast("⚠️ " + (res.message || "No se pudo enviar"), "warn");
      }
    } catch {
      toast("❌ Error al enviar prueba", "error");
    }
  }

  // ── Filtros ──────────────────────────────────────────────────────────────
  function initFiltros() {
    document.querySelectorAll(".filtro-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (btn.dataset.nivel !== undefined) {
          document.querySelectorAll("[data-nivel]").forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
          filtroNivel = btn.dataset.nivel;
        }
        if (btn.dataset.tipo !== undefined) {
          const activo = btn.classList.contains("active");
          document.querySelectorAll("[data-tipo]").forEach((b) => b.classList.remove("active"));
          filtroTipo = activo ? null : btn.dataset.tipo;
          if (!activo) btn.classList.add("active");
        }
        renderAlertas();
      });
    });
  }

  // ── Refresh manual ───────────────────────────────────────────────────────
  function initRefresh() {
    const btn = document.getElementById("btnRefresh");
    if (!btn) return;
    btn.addEventListener("click", () => {
      btn.classList.add("spinning");
      cargarAlertas().finally(() => {
        setTimeout(() => btn.classList.remove("spinning"), 600);
      });
    });

    const retry = document.getElementById("btnRetry");
    if (retry) retry.addEventListener("click", cargarAlertas);
  }

  // ── Auto-refresh ─────────────────────────────────────────────────────────
  function iniciarAutoRefresh() {
    if (intervaloAuto) clearInterval(intervaloAuto);
    intervaloAuto = setInterval(cargarAlertas, INTERVALO_MS);
  }

  // ── Telegram panel ───────────────────────────────────────────────────────
  function initTelegramPanel() {
    const btn = document.getElementById("btnTestTelegram");
    if (btn) btn.addEventListener("click", enviarPruebaTelegram);
  }

  // ── Init ─────────────────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", () => {
    initFiltros();
    initRefresh();
    initTelegramPanel();
    cargarAlertas();
    iniciarAutoRefresh();
  });
})();