/* ── app/static/js/stats.js — Estadísticas ClimAI ── */

document.addEventListener("DOMContentLoaded", () => {

  // Leemos los datos del div oculto que Jinja rellenó
  const el         = document.getElementById('stats-data');
  const labels     = JSON.parse(el.dataset.labels || '[]');
  const dataValues = JSON.parse(el.dataset.values || '[]');
  const STATS_MAX  = parseFloat(el.dataset.max    || '0');

  // Las provincias sin datos tienen null — las ponemos a 0 para la gráfica
  const datosGrafica = dataValues.map(v => v === null ? 0 : v);

  // Colores: azul para provincias con datos, gris para sin datos
  const coloresBarras = dataValues.map(v =>
    v === null ? 'rgba(90,116,153,0.3)' : 'rgba(59,130,246,0.7)'
  );
  const coloresBorde = dataValues.map(v =>
    v === null ? 'rgba(90,116,153,0.5)' : '#3b82f6'
  );

  const CHART_OPTIONS = {
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
        callbacks: {
          label: ctx => {
            const val = dataValues[ctx.dataIndex];
            return val === null ? ' Sin datos' : ` ${ctx.parsed.y}°C`;
          }
        }
      }
    },
    scales: {
      x: {
        grid:  { color: "rgba(99,179,237,0.05)" },
        ticks: {
          color: "#5a7499",
          font: { family: "'DM Mono', monospace", size: 10 },
          maxRotation: 45,
          minRotation: 45,
        },
      },
      y: {
        beginAtZero: false,
        grid:  { color: "rgba(99,179,237,0.05)" },
        ticks: {
          color: "#5a7499",
          font: { family: "'DM Mono', monospace", size: 11 },
          callback: v => `${v}°`
        }
      }
    }
  };

  let chart = null;

  function crearChart(tipo) {
    if (chart) chart.destroy();
    const ctx = document.getElementById('provinciasChart').getContext('2d');
    chart = new Chart(ctx, {
      type: tipo,
      data: {
        labels,
        datasets: [{
          label: 'Temperatura Media (°C)',
          data: datosGrafica,
          backgroundColor: tipo === 'bar'
            ? coloresBarras
            : 'rgba(59,130,246,0.08)',
          borderColor:  tipo === 'bar' ? coloresBorde : '#3b82f6',
          borderRadius: tipo === 'bar' ? 4 : 0,
          borderWidth:  tipo === 'bar' ? 0 : 2,
          pointRadius:  tipo === 'line' ? 3 : 0,
          tension:      0.4,
          fill:         tipo === 'line',
        }]
      },
      options: CHART_OPTIONS,
    });
  }

  // Iniciamos con barras
  crearChart('bar');

  // Tabs
  document.getElementById('tabBar')?.addEventListener('click', () => {
    document.getElementById('tabBar').classList.add('active');
    document.getElementById('tabLine').classList.remove('active');
    crearChart('bar');
  });

  document.getElementById('tabLine')?.addEventListener('click', () => {
    document.getElementById('tabLine').classList.add('active');
    document.getElementById('tabBar').classList.remove('active');
    crearChart('line');
  });

  // Barras de ranking en la tabla — calculadas desde JS
  document.querySelectorAll('.rank-bar').forEach(bar => {
    const temp = parseFloat(bar.dataset.temp || 0);
    const max  = parseFloat(bar.dataset.max  || 1);
    bar.style.width = max > 0 && temp > 0
      ? `${Math.round((temp / max) * 100)}%`
      : '0%';
  });

});