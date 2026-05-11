/* app/static/js/weather_province.js */

// Centroides aproximados por nombre de provincia (clave en minúsculas sin acento)
const PROVINCE_COORDS = {
  "álava":                    [42.85, -2.68],
  "albacete":                 [39.00, -1.86],
  "alicante":                 [38.35, -0.48],
  "almería":                  [37.00, -2.17],
  "asturias":                 [43.36, -5.86],
  "ávila":                    [40.66, -4.69],
  "badajoz":                  [38.88, -6.97],
  "barcelona":                [41.39,  2.17],
  "burgos":                   [42.34, -3.70],
  "cáceres":                  [39.47, -6.37],
  "cádiz":                    [36.52, -6.29],
  "cantabria":                [43.18, -3.99],
  "castellón":                [39.99, -0.05],
  "ciudad real":              [38.99, -3.92],
  "córdoba":                  [37.89, -4.78],
  "cuenca":                   [40.07, -2.14],
  "girona":                   [41.98,  2.82],
  "granada":                  [37.18, -3.60],
  "guadalajara":              [40.63, -3.16],
  "guipúzcoa":                [43.31, -2.00],
  "huelva":                   [37.26, -6.95],
  "huesca":                   [42.14, -0.41],
  "islas baleares":           [39.57,  2.65],
  "jaén":                     [37.77, -3.79],
  "la coruña":                [43.37, -8.40],
  "la rioja":                 [42.29, -2.45],
  "las palmas":               [28.10,-15.41],
  "león":                     [42.60, -5.57],
  "lleida":                   [41.62,  0.62],
  "lugo":                     [43.01, -7.56],
  "madrid":                   [40.42, -3.70],
  "málaga":                   [36.72, -4.42],
  "murcia":                   [37.98, -1.13],
  "navarra":                  [42.69, -1.64],
  "ourense":                  [42.34, -7.86],
  "palencia":                 [42.01, -4.53],
  "pontevedra":               [42.43, -8.65],
  "salamanca":                [40.97, -5.66],
  "santa cruz de tenerife":   [28.46,-16.25],
  "segovia":                  [40.95, -4.12],
  "sevilla":                  [37.39, -5.99],
  "soria":                    [41.76, -2.47],
  "tarragona":                [41.12,  1.25],
  "teruel":                   [40.34, -1.11],
  "toledo":                   [39.86, -4.02],
  "valencia":                 [39.47, -0.38],
  "valladolid":               [41.65, -4.72],
  "vizcaya":                  [43.26, -2.93],
  "zamora":                   [41.50, -5.74],
  "zaragoza":                 [41.65, -0.89],
};

// Normaliza el nombre para buscar en el diccionario
function normalizar(str) {
  return str
    .toLowerCase()
    .normalize("NFD")                        // separa letras de tildes
    .replace(/[\u0300-\u036f]/g, "")         // elimina las tildes
    .trim();
}

function buscarCoordenadas(nombre) {
  const clave = normalizar(nombre);

  // Búsqueda exacta primero (sin tildes)
  for (const [k, v] of Object.entries(PROVINCE_COORDS)) {
    if (normalizar(k) === clave) return v;
  }

  // Búsqueda parcial como fallback
  for (const [k, v] of Object.entries(PROVINCE_COORDS)) {
    if (normalizar(k).includes(clave) || clave.includes(normalizar(k))) return v;
  }

  return null;
}

document.addEventListener("DOMContentLoaded", async () => {
  const selector = document.getElementById("provinceSelector");
  const btn      = document.getElementById("btnSearchProv");

  // ── Cargar lista de provincias desde la BD ──────────────────────────────────
  async function loadProvinces() {
    try {
      const res  = await fetch("/api/provinces");
      const data = await res.json();

      selector.innerHTML = '<option value="">Selecciona una provincia...</option>';
      data.forEach(p => {
        const opt = document.createElement("option");
        opt.value        = p.name;   // guardamos el nombre, no el id
        opt.textContent  = p.name;
        opt.style.color  = "black";
        selector.appendChild(opt);
      });
    } catch {
      selector.innerHTML = '<option value="">Error al conectar con la base de datos</option>';
    }
  }

  // ── Al pulsar "Consultar" ───────────────────────────────────────────────────
  btn.addEventListener("click", () => {
    const nombre = selector.value;
    if (!nombre) return;

    const coords = buscarCoordenadas(nombre);
    if (!coords) {
      alert(`No se encontraron coordenadas para "${nombre}". Comprueba que la provincia está en el listado.`);
      return;
    }

    const [lat, lon] = coords;
    // Redirigimos al index pasando lat/lon y el nombre de la ciudad como parámetros
    window.location.href = `/?lat=${lat}&lon=${lon}&ciudad=${encodeURIComponent(nombre)}`;
  });

  loadProvinces();
});