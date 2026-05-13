# app/api/v1/endpoints/predict.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.weather_service import obtener_clima_cercano
from app.services.weather_ai_service import WeatherAIService

router = APIRouter(tags=["prediccion"])


@router.get("/predict")
async def predict(
    lat: float = Query(..., description="Latitud del navegador"),
    lon: float = Query(..., description="Longitud del navegador"),
    db: AsyncSession = Depends(get_db),
):
    """
    Orquesta los dos servicios independientes:
    - weather_service    → AEMET (datos actuales + pronóstico 5 días)
    - weather_ai_service → modelo .pkl (predicción puntual + ajuste 5 días)

    URL: GET /api/v1/predict?lat=40.41&lon=-3.70
    """

    # SERVICIO 1: AEMET
    # Obtiene datos actuales de la estación más cercana
    # y el pronóstico de los próximos 5 días por municipio
    datos = await obtener_clima_cercano(lat, lon, db)

    if not datos:
        return {
            "error":   True,
            "mensaje": "No se pudieron obtener datos de AEMET. Inténtalo de nuevo."
        }

    # SERVICIO 2: IA
    # Instanciamos el servicio — el modelo .pkl se carga una sola vez en __init__
    ai = WeatherAIService()

    # Predicción puntual: temp + humedad actuales → temperatura ajustada + tendencia
    # Esto va al hero card (el número grande con "En ascenso / Estable / En descenso")
    pronostico_ia = ai.obtener_prediccion(
        temp=datos["temperatura"],
        humedad=datos["humedad"]
    )

    # Predicción futura: ajusta con IA cada uno de los 5 días de AEMET
    # Esto va a las day-cards del pronóstico semanal
    pronostico_dias = ai.obtener_prediccion_futura(datos["pronostico_dias"])

    # Devolvemos todo junto al frontend
    return {
        "error": False,

        # ── Condiciones actuales (estación AEMET más cercana) ────────
        "temperatura":     datos["temperatura"],      # °C en tiempo real
        "humedad":         datos["humedad"],          # % humedad relativa
        "viento":          datos["viento"],           # km/h
        "precipitacion":   datos["precipitacion"],   # mm

        # ── Ubicación ────────────────────────────────────────────────
        "estacion_nombre": datos["estacion_nombre"],  # nombre de la estación AEMET
        "ciudad_buscada":  datos["ciudad_buscada"],   # provincia detectada por Nominatim
        "es_noche":        datos["es_noche"],          # True si hora fuera de 7-21h

        # ── Predicción IA puntual ─────────────────────────────────────
        # { temperatura: 22.3, tendencia: "En ascenso" }
        # Lo usa el hero card para mostrar la corrección del modelo
        "pronostico_ia":   pronostico_ia,

        # ── Pronóstico 5 días ajustado por IA ────────────────────────
        # Lista de 5 dicts: { fecha, temp_max, temp_min, prob_lluvia,
        #                     estado, temp_ia, tendencia, confianza }
        # Lo usan las day-cards del pronóstico semanal
        "pronostico_dias": pronostico_dias,
    }
def _load_model(self):
    print(f">> Buscando modelo en: {self.model_path}")
    print(f">> Existe: {self.model_path.exists()}")
    try:
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            print(">> Modelo cargado OK")
        else:
            logger.error(f"No se encontró el modelo en {self.model_path}")
    except Exception as e:
        logger.error(f"Error al cargar el .pkl: {e}")
