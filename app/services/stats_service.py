# app/services/stats_service.py
import os
import math
import httpx
import json
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import Record, Province

logger = logging.getLogger(__name__)

AEMET_BASE = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"

CAPITALES = {
    "álava":       (42.8467, -2.6726),
    "albacete":    (38.9942, -1.8585),
    "alicante":    (38.3452, -0.4815),
    "almería":     (36.8340, -2.4637),
    "asturias":    (43.3614, -5.8593),
    "ávila":       (40.6565, -4.6812),
    "badajoz":     (38.8794, -6.9706),
    "barcelona":   (41.3851,  2.1734),
    "burgos":      (42.3440, -3.6970),
    "cáceres":     (39.4753, -6.3724),
    "cádiz":       (36.5271, -6.2886),
    "cantabria":   (43.4623, -3.8099),
    "castellón":   (39.9864, -0.0513),
    "ciudad real": (38.9848, -3.9274),
    "córdoba":     (37.8882, -4.7794),
    "cuenca":      (40.0704, -2.1374),
    "girona":      (41.9794,  2.8214),
    "granada":     (37.1773, -3.5986),
    "guadalajara": (40.6321, -3.1661),
    "guipúzcoa":   (43.3128, -1.9753),
    "huelva":      (37.2614, -6.9447),
    "huesca":      (42.1401, -0.4089),
    "islas baleares":(39.5696,  2.6502),  
    "illes balears": (39.5696,  2.6502),   
    "baleares":      (39.5696,  2.6502),  
    "jaén":        (37.7796, -3.7849),
    "a coruña":   (43.3713, -8.3960),
    "la rioja":    (42.4650, -2.4489),
    "las palmas":  (28.1235,-15.4363),
    "león":        (42.5987, -5.5671),
    "lleida":      (41.6176,  0.6200),
    "lugo":        (43.0097, -7.5567),
    "madrid":      (40.4168, -3.7038),
    "málaga":      (36.7213, -4.4214),
    "murcia":      (37.9922, -1.1307),
    "navarra":     (42.6954, -1.6761),
    "ourense":     (42.3359, -7.8639),
    "palencia":    (42.0096, -4.5288),
    "pontevedra":  (42.4336, -8.6475),
    "salamanca":   (40.9701, -5.6635),
    "santa cruz de tenerife":(28.4636,-16.2518),
    "segovia":     (40.9429, -4.1088),
    "sevilla":     (37.3891, -5.9845),
    "soria":       (41.7640, -2.4686),
    "tarragona":   (41.1189,  1.2445),
    "teruel":      (40.3456, -1.1065),
    "toledo":      (39.8628, -4.0273),
    "valencia":    (39.4699, -0.3763),
    "valladolid":  (41.6523, -4.7245),
    "vizcaya":     (43.2630, -2.9350),
    "zamora":      (41.5036, -5.7449),
    "zaragoza":    (41.6488, -0.8891),
    "ceuta":       (35.8894, -5.3198),
    "melilla":     (35.2923, -2.9381),
}


class StatsService:

    def __init__(self, db: AsyncSession):
        self.db      = db
        self.api_key = os.getenv("AEMET_API_KEY")
        self.headers = {"api_key": self.api_key, "cache-control": "no-cache"}

    async def obtener_stats(self) -> dict:
        try:
            # Descargamos todas las observaciones de AEMET una sola vez
            observaciones = await self._fetch_observaciones()

            # Sacamos todas las provincias de la BD
            result     = await self.db.execute(select(Province).order_by(Province.name))
            provincias = result.scalars().all()

            labels_provincias  = []
            temp_por_provincia = []

            for prov in provincias:
                nombre = prov.name.lower().strip()
                coords = CAPITALES.get(nombre)

                if coords and observaciones:
                    # Buscamos la estación AEMET más cercana a la capital
                    est = self._estacion_mas_cercana(coords[0], coords[1], observaciones)
                    temp = float(est.get("ta") or 0) if est else None
                else:
                    temp = None

                labels_provincias.append(prov.name.capitalize())
                temp_por_provincia.append(round(temp, 1) if temp is not None else None)

            # Ordenamos de mayor a menor temperatura
            pares = sorted(
                zip(labels_provincias, temp_por_provincia),
                key=lambda x: x[1] if x[1] is not None else float('-inf'),
                reverse=True
            )
            labels_provincias  = [p[0] for p in pares]
            temp_por_provincia = [p[1] for p in pares]

            # Extremos
            con_datos           = [(l, t) for l, t in pares if t is not None]
            provincia_top_calor = con_datos[0][0]  if con_datos else "—"
            temp_max_provincia  = con_datos[0][1]  if con_datos else 0
            provincia_top_frio  = con_datos[-1][0] if con_datos else "—"
            temp_min_provincia  = con_datos[-1][1] if con_datos else 0

            # Media y máxima de los datos reales
            temps_reales   = [t for t in temp_por_provincia if t is not None]
            media_nacional = round(sum(temps_reales) / len(temps_reales), 1) if temps_reales else 0
            max_historica  = max(temps_reales) if temps_reales else 0

            # Correlación desde BD
            registros   = await self.db.execute(select(Record.temperature, Record.humidity))
            datos       = registros.all()
            correlacion = self._calcular_correlacion(datos)

            return {
                "media_nacional":       media_nacional,
                "max_historica":        max_historica,
                "provincia_top_calor":  provincia_top_calor,
                "temp_max_provincia":   temp_max_provincia,
                "provincia_top_frio":   provincia_top_frio,
                "temp_min_provincia":   temp_min_provincia,
                "correlacion_hum_temp": correlacion,
                "labels_provincias":    labels_provincias,
                "temp_por_provincia":   temp_por_provincia,
            }

        except Exception as e:
            logger.error(f"Error calculando stats: {e}")
            return {
                "media_nacional":       0,
                "max_historica":        0,
                "provincia_top_calor":  "—",
                "temp_max_provincia":   0,
                "provincia_top_frio":   "—",
                "temp_min_provincia":   0,
                "correlacion_hum_temp": "—",
                "labels_provincias":    [],
                "temp_por_provincia":   [],
            }

    async def _fetch_observaciones(self):
        """Descarga todas las observaciones de AEMET en tiempo real."""
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                r = await client.get(AEMET_BASE, headers=self.headers)
                r.raise_for_status()
                url = r.json().get("datos")
                if url:
                    await asyncio.sleep(0.5)
                    r2 = await client.get(url)
                    return json.loads(r2.content.decode("latin-1", errors="replace"))
        except Exception as e:
            logger.warning(f"Error descargando observaciones AEMET: {e}")
        return []

    def _estacion_mas_cercana(self, lat, lon, obs):
        """Devuelve la observación de la estación más cercana a lat/lon."""
        est_min, dist_min = None, float("inf")
        for o in obs:
            try:
                d = self._distancia(lat, lon, float(o["lat"]), float(o["lon"]))
                if d < dist_min:
                    dist_min, est_min = d, o
            except:
                continue
        return est_min

    def _distancia(self, lat1, lon1, lat2, lon2):
        """Haversine."""
        R    = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a    = (math.sin(dlat/2)**2 +
                math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def _calcular_correlacion(self, datos):
        if len(datos) < 2:
            return "—"
        try:
            temps  = [d[0] for d in datos]
            humeds = [d[1] for d in datos]
            n      = len(temps)
            mean_t = sum(temps) / n
            mean_h = sum(humeds) / n
            num    = sum((t - mean_t) * (h - mean_h) for t, h in zip(temps, humeds))
            den_t  = sum((t - mean_t)**2 for t in temps)**0.5
            den_h  = sum((h - mean_h)**2 for h in humeds)**0.5
            if den_t == 0 or den_h == 0:
                return "—"
            return round(num / (den_t * den_h), 2)
        except:
            return "—"