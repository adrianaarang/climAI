import os
import math
import httpx        # Para hacer peticiones HTTP asíncronas (a AEMET y Nominatim)
import json
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import Province, Station, Record
from app.services.weather_ai_service import WeatherAIService

logger = logging.getLogger(__name__)

# URL de AEMET para obtener todas las observaciones meteorológicas en tiempo real
AEMET_BASE = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
# URL de Nominatim (OpenStreetMap) para convertir coordenadas en nombre de lugar
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


class WeatherAPIService:
    """
    Servicio principal de clima. Dado un par de coordenadas (lat, lon):
    1. Averigua en qué provincia estás
    2. Descarga datos de todas las estaciones de AEMET
    3. Encuentra la estación más cercana a ti
    4. Guarda la estación y su registro en la base de datos
    5. Genera una predicción con IA
    6. Devuelve todo junto como un diccionario
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # Sesión de base de datos, se inyecta desde el router
        self.api_key = os.getenv("AEMET_API_KEY")  # Clave de AEMET desde el .env
        self.headers = {"api_key": self.api_key, "cache-control": "no-cache"}
        self.ai = WeatherAIService()  # Servicio de IA para el pronóstico


    async def obtener_clima_por_coordenadas(self, lat: float, lon: float) -> Optional[dict]:
        """
        Método orquestador: llama a todos los pasos en orden.
        Si algo falla en cualquier paso, devuelve None.
        """
        # Abrimos un cliente HTTP que reutilizamos para todas las peticiones externas
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            try:
                # PASO 1: Convertir coordenadas en nombre de provincia
                p_name = await self._get_province_name(client, lat, lon)

                # PASO 2: Buscar esa provincia en nuestra base de datos
                provincia_db = await self._get_province_from_db(p_name)
                if not provincia_db:
                    logger.error("Error crítico: No hay provincias cargadas en la BD.")
                    return None

                # PASO 3: Descargar todas las observaciones de AEMET
                observaciones = await self._fetch_aemet_data(client)
                if not observaciones:
                    return None

                # PASO 4: De todas las estaciones, encontrar la más cercana al usuario
                est_aemet, dist = self._find_nearest_station(lat, lon, observaciones)
                if not est_aemet:
                    return None

                # PASO 5: Guardar la estación en BD si no existe ya (upsert manual)
                estacion_db = await self._ensure_station_exists(est_aemet, provincia_db.province_id)

                # PASO 6: Guardar el registro meteorológico actual de esa estación
                nuevo_registro = await self._save_record(est_aemet, estacion_db.station_id)
                if not nuevo_registro:
                    return None

                # PASO 7: Pedir a la IA una predicción basada en temperatura y humedad
                pronostico = self.ai.obtener_prediccion(
                    temp=nuevo_registro.temperature,
                    humedad=nuevo_registro.humidity
                )

                # PASO 8: Formatear el histórico de las últimas 24h de esa estación
                hist_data = self._format_history(observaciones, est_aemet["idema"])

                # PASO 9: Devolver todo junto al endpoint que lo pidió
                return {
                    "temperatura": nuevo_registro.temperature,
                    "humedad": nuevo_registro.humidity,
                    "viento": nuevo_registro.wind,
                    "precipitacion": nuevo_registro.rain,
                    "estacion_nombre": estacion_db.name,
                    "ciudad_buscada": provincia_db.name,
                    "es_noche": not (7 <= datetime.now().hour <= 21),  # True si es de noche
                    "pronostico_ia": pronostico,
                    "historico": hist_data,
                }

            except Exception as e:
                logger.exception(f"Fallo inesperado en WeatherAPIService: {e}")
                return None


    # -------------------------------------------------------------------------
    # MÉTODOS PRIVADOS (cada uno hace una sola cosa)
    # -------------------------------------------------------------------------

    async def _get_province_name(self, client: httpx.AsyncClient, lat: float, lon: float) -> str:
        """
        Llama a Nominatim con las coordenadas y devuelve el nombre de la provincia
        en minúsculas y sin prefijos como 'Comunidad de', 'Provincia de', etc.
        Si falla, devuelve 'madrid' como fallback.
        """
        try:
            res = await client.get(
                NOMINATIM_URL,
                params={"lat": lat, "lon": lon, "format": "json", "zoom": 6},
                headers={"User-Agent": "climAI/1.0"}
            )
            if res.status_code == 200:
                addr = res.json().get("address", {})
                # Nominatim puede devolver el nombre en 'province' o 'state'
                name = (addr.get("province") or addr.get("state") or "madrid").lower()

                # Nominatim a veces devuelve "Comunidad de Madrid", "Provincia de Sevilla", etc.
                # Los limpiamos para que coincidan con lo que tenemos en la BD
                for prefijo in [
                    "comunidad de ",
                    "comunidad foral de ",
                    "provincia de ",
                    "region de ",
                    "región de ",
                    "illes ",
                    "islas ",
                ]:
                    if name.startswith(prefijo):
                        name = name[len(prefijo):]  # Quitamos el prefijo
                        break
                return name
        except Exception as e:
            logger.warning(f"Nominatim falló, usando fallback: {e}")
        return "madrid"


    async def _get_province_from_db(self, name: str) -> Optional[Province]:
        """
        Busca una provincia en la BD por nombre (búsqueda parcial, sin distinguir mayúsculas).
        Si no la encuentra, intenta con 'madrid' como fallback.
        Si tampoco encuentra madrid, devuelve None (la BD está vacía).
        """
        stmt = select(Province).where(Province.name.ilike(f"%{name}%"))
        result = await self.db.execute(stmt)
        prov = result.scalar_one_or_none()

        if not prov and name != "madrid":
            logger.warning(f"No se encontró la provincia '{name}', usando Madrid como fallback.")
            return await self._get_province_from_db("madrid")

        if not prov:
            logger.error("No se encontró la provincia en la base de datos (ni siquiera Madrid).")
        return prov


    async def _fetch_aemet_data(self, client: httpx.AsyncClient) -> Optional[List[Dict]]:
        """
        Descarga las observaciones de todas las estaciones de AEMET.
        AEMET funciona en dos pasos:
          1. Pides la URL → te devuelve otra URL con los datos reales
          2. Pides esa segunda URL → te devuelve el JSON con todas las observaciones
        Reintenta hasta 3 veces si hay error.
        """
        for intento in range(3):
            try:
                # Primer paso: obtenemos la URL de los datos
                r_meta = await client.get(AEMET_BASE, headers=self.headers)
                r_meta.raise_for_status()
                url_datos = r_meta.json().get("datos")

                if url_datos:
                    await asyncio.sleep(0.5)  # Esperamos un poco para no saturar la API
                    # Segundo paso: descargamos los datos reales
                    r_datos = await client.get(url_datos)
                    # AEMET devuelve los datos en latin-1, no en UTF-8
                    return json.loads(r_datos.content.decode("latin-1", errors="replace"))
            except Exception as e:
                logger.warning(f"Reintento AEMET {intento+1}/3 debido a: {e}")
                await asyncio.sleep(1)
        return None


    def _find_nearest_station(self, lat: float, lon: float, obs: List[Dict]) -> tuple:
        """
        Recorre todas las observaciones de AEMET y devuelve la estación
        cuyas coordenadas estén más cerca de las coordenadas del usuario.
        Devuelve una tupla (estacion, distancia_en_km).
        """
        est_min, dist_min = None, float("inf")
        for o in obs:
            try:
                d = self._calcular_distancia(lat, lon, float(o["lat"]), float(o["lon"]))
                if d < dist_min:
                    dist_min, est_min = d, o
            except:
                continue  # Si una observación tiene datos malformados, la saltamos
        return est_min, dist_min


    def _calcular_distancia(self, lat1, lon1, lat2, lon2):
        """
        Fórmula de Haversine: calcula la distancia en km entre dos puntos
        de la Tierra dadas sus coordenadas. Tiene en cuenta la curvatura terrestre.
        """
        R = 6371.0  # Radio de la Tierra en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2)**2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


    async def _ensure_station_exists(self, est: Dict, prov_id: int) -> Station:
        """
        Comprueba si la estación ya existe en la BD (por su código 'idema').
        Si no existe, la crea. Así evitamos duplicados.
        Es un patrón 'get or create'.
        """
        idema = est["idema"]  # Código único de estación de AEMET
        stmt = select(Station).where(Station.idema == idema)
        result = await self.db.execute(stmt)
        estacion_db = result.scalar_one_or_none()

        if not estacion_db:
            estacion_db = Station(
                idema=idema,
                name=est.get("ubi", "Desconocida"),  # 'ubi' es el nombre de la ubicación en AEMET
                latitude=float(est["lat"]),
                longitude=float(est["lon"]),
                province_id=prov_id
            )
            self.db.add(estacion_db)
            await self.db.flush()  # flush para obtener el ID sin hacer commit todavía
        return estacion_db


    async def _save_record(self, est: Dict, station_id: int) -> Optional[Record]:
        """
        Guarda un nuevo registro meteorológico en la BD con los datos actuales
        de la estación: temperatura, humedad, viento y precipitación.
        Si algo falla, hace rollback para no dejar la BD en un estado inconsistente.
        """
        try:
            nuevo = Record(
                timestamp=datetime.now(),
                temperature=float(est.get("ta") or 0),    # 'ta' = temperatura del aire
                humidity=float(est.get("hr") or 0),        # 'hr' = humedad relativa
                wind=float(est.get("vv") or 0),            # 'vv' = velocidad del viento
                rain=float(est.get("prec") or 0.0),        # 'prec' = precipitación
                station_id=station_id
            )
            self.db.add(nuevo)
            await self.db.commit()
            return nuevo
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al guardar registro: {e}")
            return None


    def _format_history(self, observaciones: List[Dict], idema: str) -> Dict:
        """
        De todas las observaciones de AEMET, filtra solo las de nuestra estación
        y devuelve las últimas 24 entradas formateadas para pintar una gráfica en el frontend.
        Devuelve listas paralelas: horas, temperaturas, humedades y precipitaciones.
        """
        # Filtramos solo las observaciones de nuestra estación
        regs = [o for o in observaciones if o.get("idema") == idema]
        # Ordenamos por fecha/hora ('fint' = fecha de la observación)
        regs.sort(key=lambda x: x.get("fint", ""))

        hist = {"horas": [], "temperature": [], "humidity": [], "precipitation": []}
        for r in regs[-24:]:  # Solo las últimas 24 observaciones
            fint = r.get("fint", "")
            # 'fint' tiene formato "2024-01-15T12:00:00" → extraemos solo "12:00"
            hist["horas"].append(fint.split("T")[-1][:5] if "T" in fint else "--")
            hist["temperature"].append(float(r.get("ta") or r.get("temp") or 0))
            hist["humidity"].append(float(r.get("hr") or 0))
            hist["precipitation"].append(float(r.get("prec") or 0.0))
        return hist


# Función de entrada pública que usan los routers
# Crea una instancia del servicio y llama al método principal
async def obtener_clima_cercano(lat: float, lon: float, db: AsyncSession) -> Optional[dict]:
    service = WeatherAPIService(db)
    return await service.obtener_clima_por_coordenadas(lat, lon)