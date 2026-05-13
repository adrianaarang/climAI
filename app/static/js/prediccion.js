// static/js/prediccion.js

// ── Helpers ────────────────────────────────────────────────────────────────────

function getIcon(estado, esNoche, precipitacion) {
  // Si es de noche siempre luna, independientemente del estado
  if (esNoche) return '🌙';

  const e = (estado || '').toLowerCase();
  if (e.includes('tormenta'))                        return '⛈️';
  if (e.includes('lluvia') || precipitacion > 5)     return '🌧️';
  if (e.includes('chubascos') || precipitacion > 0)  return '🌦️';
  if (e.includes('nieve'))                           return '❄️';
  if (e.includes('niebla'))                          return '🌫️';
  if (e.includes('nuboso') || e.includes('cubierto'))return '☁️';
  if (e.includes('nubes'))                           return '⛅';
  return '☀️';
}

function getTendenciaColor(tendencia) {
  // Color del badge de tendencia según si sube, baja o está estable
  if (tendencia === 'En ascenso')  return 'var(--amber)';
  if (tendencia === 'En descenso') return 'var(--cyan)';
  return 'var(--green)';
}

function formatFecha(fechaStr) {
  // "2025-05-14" → "mié"
  const d = new Date(fechaStr + 'T00:00:00');
  return d.toLocaleDateString('es-ES', { weekday: 'short' });
}

function show(id) { document.getElementById(id).style.display = 'block'; }
function hide(id) { document.getElementById(id).style.display = 'none'; }


// ── Renders ────────────────────────────────────────────────────────────────────

function renderHero(datos, lat, lon) {
  // Cabecera: ciudad, estación, temperatura actual y badge de IA
  document.getElementById('city-name').textContent      = datos.ciudad_buscada  ?? 'Tu ubicación';
  document.getElementById('station-name').textContent   = datos.estacion_nombre ?? '—';
  document.getElementById('coords-display').textContent =
    `${lat.toFixed(4)}° N · ${Math.abs(lon).toFixed(4)}° O`;
  document.getElementById('temp-now').textContent       = `${datos.temperatura ?? '—'}°`;
  document.getElementById('weather-icon').textContent   =
    getIcon('', datos.es_noche, datos.precipitacion);

  // Badge IA: muestra la temperatura ajustada por el modelo y su tendencia
  const ia = datos.pronostico_ia;
  document.getElementById('ia-badge').textContent = ia
    ? `IA · ${ia.temperatura}° · ${ia.tendencia}`
    : 'IA · no disponible';
}

function renderMetrics(datos) {
  // Grid de 4 métricas debajo del hero
  const items = [
    { label: 'Humedad',       value: `${datos.humedad       ?? '—'}%`    },
    { label: 'Viento',        value: `${datos.viento        ?? '—'} km/h`},
    { label: 'Precipitación', value: `${datos.precipitacion ?? 0} mm`    },
    { label: 'Estado',        value:  datos.es_noche ? 'Noche' : 'Día'   },
  ];

  document.getElementById('metrics-grid').innerHTML = items.map(i => `
    <div class="metric-box">
      <div class="metric-label">${i.label}</div>
      <div class="metric-value">${i.value}</div>
    </div>
  `).join('');
}

function renderDays(dias) {
  // Cards de los próximos 5 días con corrección IA
  if (!dias?.length) {
    document.getElementById('days-grid').innerHTML =
      '<p style="color:var(--muted);font-size:0.8rem;">Sin pronóstico disponible</p>';
    return;
  }

  document.getElementById('days-grid').innerHTML = dias.map((d, i) => `
    <div class="day-card ${i === 0 ? 'today' : ''}">
      <div class="day-name">${i === 0 ? 'Hoy' : formatFecha(d.fecha)}</div>
      <div class="day-icon">${getIcon(d.estado, false, d.prob_lluvia)}</div>

      <div class="day-temp-max">${d.temp_max ?? '—'}°</div>
      <div class="day-temp-min">${d.temp_min ?? '—'}°</div>

      <!-- Temperatura ajustada por el modelo .pkl -->
      <div class="day-ia">IA · ${d.temp_ia ?? '—'}°</div>

      <!-- Tendencia: En ascenso / Estable / En descenso -->
      <div class="day-tendencia" style="color:${getTendenciaColor(d.tendencia)};">
        ${d.tendencia ?? '—'}
      </div>
    </div>
  `).join('');
}

function renderChart(dias) {
  // Barras de probabilidad de lluvia por día
  if (!dias?.length) {
    document.getElementById('bar-chart').innerHTML =
      '<p style="color:var(--muted);font-size:0.8rem;">Sin datos</p>';
    return;
  }

  document.getElementById('bar-chart').innerHTML = dias.map((d, i) => {
    const prob  = d.prob_lluvia ?? 0;
    const h     = Math.max(4, prob * 0.65);
    const color = prob > 60 ? '#38bdf8'
                : prob > 30 ? 'rgba(56,189,248,0.5)'
                :             'rgba(34,197,94,0.5)';
    return `
      <div class="bar-wrap">
        <span class="bar-pct">${prob}%</span>
        <div class="bar" style="height:${h}px; background:${color};"></div>
        <span class="bar-day">${i === 0 ? 'Hoy' : formatFecha(d.fecha)}</span>
      </div>
    `;
  }).join('');
}


// ── Init ───────────────────────────────────────────────────────────────────────

async function init() {
  show('loading-screen');
  hide('prediccion-view');
  hide('error-screen');

  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      const { latitude: lat, longitude: lon } = coords;

      try {
        const res = await fetch(`/api/v1/predict?lat=${lat}&lon=${lon}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const datos = await res.json();

        // El endpoint devuelve error:true si AEMET o la BD fallaron
        if (datos.error) throw new Error(datos.mensaje);

        // Todo OK — rellenamos cada sección de la vista
        renderHero(datos, lat, lon);
        renderMetrics(datos);
        renderDays(datos.pronostico_dias);
        renderChart(datos.pronostico_dias);

        // Timestamp de última actualización
        document.getElementById('updated-at').textContent =
          `actualizado ${new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit', minute: '2-digit'
          })}`;

        hide('loading-screen');
        show('prediccion-view');

      } catch (err) {
        console.error('[prediccion]', err);
        hide('loading-screen');
        document.getElementById('error-msg').textContent = `Error: ${err.message}`;
        show('error-screen');
      }
    },

    // El usuario denegó el permiso de ubicación
    () => {
      hide('loading-screen');
      document.getElementById('error-msg').textContent =
        'Permiso de ubicación denegado. Actívalo en tu navegador e inténtalo de nuevo.';
      show('error-screen');
    }
  );

  document.getElementById('refresh-btn')?.addEventListener('click', () => location.reload());
}

init();