import math
import httpx
import logging

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


async def get_province_name(client: httpx.AsyncClient, lat: float, lon: float) -> str:
    """
    Convierte coordenadas en nombre de provincia via Nominatim.
    Limpia prefijos como 'Comunidad de', 'Provincia de', etc.
    Si falla devuelve 'madrid' como fallback.
    """
    try:
        res = await client.get(
            NOMINATIM_URL,
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 6},
            headers={"User-Agent": "climAI/1.0"}
        )
        if res.status_code == 200:
            addr = res.json().get("address", {})
            name = (addr.get("province") or addr.get("state") or "madrid").lower()

            for prefijo in [
                "comunidad de ", "comunidad foral de ", "provincia de ",
                "region de ", "región de ", "illes ", "islas ",
            ]:
                if name.startswith(prefijo):
                    name = name[len(prefijo):]
                    break
            return name
    except Exception as e:
        logger.warning(f"Nominatim falló, usando fallback: {e}")
    return "madrid"


def calcular_distancia(lat1, lon1, lat2, lon2) -> float:
    """Fórmula de Haversine — distancia en km entre dos puntos."""
    R    = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat / 2)**2 +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_coord_aemet(val: str) -> float:
    """
    Convierte coordenadas de municipios AEMET a float decimal.
    Maneja dos formatos:
      - Float directo:  "40.4168"
      - GMS con letra:  "40º32'54.45\"N"
    """
    try:
        val = val.strip()
        if 'º' not in val and "'" not in val:
            return float(val.rstrip('NnSsEeOoWw'))

        signo  = -1 if val[-1] in ('S', 'W', 's', 'w', 'O', 'o') else 1
        val    = val[:-1].strip()
        partes = val.replace('º', '|').replace("'", '|').replace('"', '|').split('|')

        grados   = float(partes[0]) if len(partes) > 0 else 0.0
        minutos  = float(partes[1]) if len(partes) > 1 else 0.0
        segundos = float(partes[2]) if len(partes) > 2 else 0.0

        return signo * (grados + minutos / 60 + segundos / 3600)
    except Exception:
        return 0.0