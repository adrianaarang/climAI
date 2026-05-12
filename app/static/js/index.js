/* ── app/static/js/index.js — Dashboard ClimAI ── */

// ─── ICONO VISUAL ───────────────────────────────────────────────
function actualizarIconoVisual(data) {
    const container = document.getElementById("weather-icon-container");
    const sun = document.getElementById("sun-icon");
    if (!container || !sun) return;

    container.querySelectorAll(".cloud, .rain-drops").forEach(el => el.remove());
    sun.className = "sun";

    if (data.es_noche) sun.classList.add("is-night");

    const temp = Math.round(data.temperatura ?? 0);
    if (temp <= 12)       sun.classList.add("temp-cold");
    else if (temp >= 28) sun.classList.add("temp-hot");

    const lluvia = data.precipitacion || 0;
    if (lluvia > 0)             crearNube(container, true);
    else if (data.humedad > 75) crearNube(container, false);
}

function crearNube(parent, conLluvia) {
    const cloud = document.createElement("div");
    cloud.className = "cloud";
    if (conLluvia) {
        const drops = document.createElement("div");
        drops.className = "rain-drops";
        for (let i = 0; i < 3; i++) {
            const d = document.createElement("div");
            d.className = "drop";
            d.style.left = (20 + i * 25) + "px";
            d.style.animationDelay = (i * 0.2) + "s";
            drops.appendChild(d);
        }
        cloud.appendChild(drops);
    }
    parent.appendChild(cloud);
}

// ─── CHART.JS ────────────────────────────────────────────────────
let climaChart = null;
let datosCache = { horas: [], temps: [], humedads: [], lluvias: [] };

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: "#111f35",
            borderColor: "rgba(99,179,237,0.15)",
            borderWidth: 1,
            titleColor: "#5a7499",
            bodyColor: "#e8f0fe",
            padding: 10,
            cornerRadius: 8,
        },
    },
    scales: {
        x: {
            grid:  { color: "rgba(99,179,237,0.05)" },
            ticks: { color: "#5a7499", font: { family: "'DM Mono', monospace", size: 11 } },
        },
        y: {
            suggestedMax: 1,
            grid:  { color: "rgba(99,179,237,0.05)" },
            ticks: { color: "#5a7499", font: { family: "'DM Mono', monospace", size: 11 } },
        },
    },
};

function crearGrafica(canvas, labels, datasets) {
    if (climaChart) climaChart.destroy();
    climaChart = new Chart(canvas, {
        type: "line",
        data: { labels, datasets },
        options: CHART_DEFAULTS,
    });
}

function datasetBase(label, data, color) {
    return {
        label,
        data,
        borderColor: color,
        backgroundColor: color.replace(")", ", 0.08)").replace("rgb", "rgba"),
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.4,
        fill: true,
    };
}

function cargarGraficaTemp() {
    const canvas = document.getElementById("climaChart");
    if (!canvas || !datosCache.temps.length) return;
    crearGrafica(canvas, datosCache.horas,
        [datasetBase("Temperatura (°C)", datosCache.temps, "rgb(59,130,246)")]);
}

function cargarGraficaHumedad() {
    const canvas = document.getElementById("climaChart");
    if (!canvas || !datosCache.humedads.length) return;
    crearGrafica(canvas, datosCache.horas,
        [datasetBase("Humedad (%)", datosCache.humedads, "rgb(56,189,248)")]);
}

function cargarGraficaLluvia() {
    const canvas = document.getElementById("climaChart");
    if (!canvas || !datosCache.lluvias.length) return;
    crearGrafica(canvas, datosCache.horas,
        [datasetBase("Lluvia (mm)", datosCache.lluvias, "rgb(14,165,233)")]);
}

// ─── HELPERS UI ──────────────────────────────────────────────────
function setStatus(ok) {
    const dot = document.getElementById("statusDot");
    if (!dot) return;
    dot.style.background = ok ? "#22c55e" : "#ef4444";
    dot.style.boxShadow  = ok
        ? "0 0 10px rgba(34,197,94,0.5)"
        : "0 0 10px rgba(239,68,68,0.5)";
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function refrescarGraficaActiva() {
    if (document.getElementById("tabHumedad")?.classList.contains("active")) {
        cargarGraficaHumedad();
    } else if (document.getElementById("tabLluvia")?.classList.contains("active")) {
        cargarGraficaLluvia();
    } else {
        cargarGraficaTemp();
    }
}

function leerParamsURL() {
    const params = new URLSearchParams(window.location.search);
    const lat    = params.get("lat");
    const lon    = params.get("lon");
    const ciudad = params.get("ciudad");
    if (lat && lon) {
        return { lat: parseFloat(lat), lon: parseFloat(lon), ciudad };
    }
    return null;
}

// ─── FETCH CLIMA ─────────────────────────────────────────────────
async function actualizarClima() {
    setText("updatedAt", "Localizando...");
    const paramsURL = leerParamsURL();

    if (paramsURL) {
        const { lat, lon, ciudad } = paramsURL;
        if (ciudad) {
            setText("mainTitle", `${ciudad} · Tiempo Real`);
            setText("cityName",  ciudad);
        }
        await fetchYActualizar(lat, lon);
    } else {
        if (!navigator.geolocation) {
            setText("updatedAt", "GPS no soportado");
            return;
        }
        navigator.geolocation.getCurrentPosition(
            async ({ coords: { latitude, longitude } }) => {
                await fetchYActualizar(latitude, longitude);
            },
            () => setText("updatedAt", "Permiso de ubicación denegado")
        );
    }
}

async function fetchYActualizar(latitude, longitude) {
    try {
        const res  = await fetch(`/api/clima?lat=${latitude}&lon=${longitude}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? "Error de servidor");

        // Datos actuales
        setText("temperature", `${Math.round(data.temperatura)}°`);
        setText("humidity",    `${data.humedad}%`);
        setText("wind",        `${data.viento} km/h`);
        setText("rain",        data.precipitacion > 0 ? `${data.precipitacion} mm` : "Sin lluvia");
        setText("stationName", data.estacion_nombre || "Estación AEMET");

        // 🤖 ACTUALIZAR PRONÓSTICO IA
        if (data.pronostico_ia) {
            setText("pred-temp", `${data.pronostico_ia.temperatura}°C`);
            setText("trend-text", data.pronostico_ia.tendencia);
            
            const trendIcon = document.getElementById("trend-icon");
            if (trendIcon) {
                const tend = data.pronostico_ia.tendencia.toLowerCase();
                if (tend.includes("ascenso")) {
                    trendIcon.textContent = "↑";
                    trendIcon.style.color = "#ff5f5f";
                } else if (tend.includes("descenso")) {
                    trendIcon.textContent = "↓";
                    trendIcon.style.color = "#5fb8ff";
                } else {
                    trendIcon.textContent = "→";
                    trendIcon.style.color = "#888";
                }
            }
        }

        if (!leerParamsURL()) {
            setText("cityName",  data.ciudad_buscada || "Tu Ubicación");
            setText("mainTitle", `${data.ciudad_buscada || "Clima"} · Tiempo Real`);
        }

        const horaActual = new Date().toLocaleTimeString("es-ES", {
            hour: "2-digit", minute: "2-digit",
        });
        setText("updatedAt", `Actualizado a las ${horaActual}`);

        if (data.historico) {
            datosCache.horas     = data.historico.horas;
            datosCache.temps     = data.historico.temperature;
            datosCache.humedads = data.historico.humidity;
            datosCache.lluvias  = data.historico.precipitation;
            refrescarGraficaActiva();
        }

        actualizarIconoVisual(data);
        setStatus(true);

    } catch (err) {
        console.error(err);
        setText("updatedAt", "Error de conexión");
        setStatus(false);
    }
}

// ─── INIT ─────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    actualizarClima();
    document.getElementById("refreshBtn")?.addEventListener("click", actualizarClima);

    const tabs = {
        "tabTemp": cargarGraficaTemp,
        "tabHumedad": cargarGraficaHumedad,
        "tabLluvia": cargarGraficaLluvia
    };

    Object.keys(tabs).forEach(tabId => {
        const el = document.getElementById(tabId);
        el?.addEventListener("click", () => {
            Object.keys(tabs).forEach(id => document.getElementById(id)?.classList.remove("active"));
            el.classList.add("active");
            tabs[tabId]();
        });
    });
});