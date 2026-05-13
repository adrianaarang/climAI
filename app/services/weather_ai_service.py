import joblib
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WeatherAIService:
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.model_path = BASE_DIR / "ml_models" / "modelo_clima.pkl"
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                logger.info("Modelo IA cargado correctamente.")
            else:
                logger.error(f"No se encontro el modelo en {self.model_path}")
        except Exception as e:
            logger.error(f"Error al cargar el archivo .pkl: {e}")

    def obtener_prediccion(self, temp: float, humedad: float) -> dict:
        if self.model is None:
            return {"temperatura": "--", "tendencia": "IA no disponible"}
        try:
            hora_actual = datetime.now().hour
            input_data = np.array([[temp, humedad, hora_actual]])
            prediccion = self.model.predict(input_data)[0]
            diff = prediccion - temp
            if diff > 0.5:
                tendencia = "En ascenso"
            elif diff < -0.5:
                tendencia = "En descenso"
            else:
                tendencia = "Estable"
            return {"temperatura": round(float(prediccion), 1), "tendencia": tendencia}
        except Exception as e:
            logger.error(f"Error en la prediccion de IA: {e}")
            return {"temperatura": "--", "tendencia": "Error de calculo"}
# app/services/weather_ai_service.py

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WeatherAIService:
    """
    Servicio de IA — carga el modelo .pkl una sola vez y expone dos métodos:
    - obtener_prediccion()        → temperatura actual + tendencia (para el hero)
    - obtener_prediccion_futura() → ajuste IA sobre los 5 días de AEMET (para las cards)
    """

    def __init__(self):
        # Subimos tres niveles desde services/ hasta la raíz del proyecto
        BASE_DIR         = Path(__file__).resolve().parent.parent.parent
        self.model_path  = BASE_DIR / "ml_models" / "modelo_clima.pkl"
        self.model       = None
        self._load_model()

    def _load_model(self):
        """Carga el .pkl al arrancar. Si no existe o falla, el servicio sigue funcionando sin IA."""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                logger.info(f"Modelo IA cargado desde {self.model_path}")
            else:
                logger.error(f"No se encontró el modelo en {self.model_path}")
        except Exception as e:
            logger.error(f"Error al cargar el .pkl: {e}")

    def obtener_prediccion(self, temp: float, humedad: float) -> dict:
        """
        Predicción puntual para el momento actual.
        Recibe temp y humedad de la estación AEMET más cercana
        y devuelve la temperatura ajustada por IA y su tendencia.
        Lo usa el hero card de prediccion_ia.html.
        """
        if self.model is None:
            return {"temperatura": "--", "tendencia": "IA no disponible"}

        try:
            hora_actual = datetime.now().hour
            # El modelo espera [temp, humedad, hora] — mismo orden que en train_ia.py
            input_data  = np.array([[temp, humedad, hora_actual]])
            prediccion  = self.model.predict(input_data)[0]

            # Calculamos si la temperatura va a subir, bajar o quedarse igual
            diff = prediccion - temp
            if diff > 0.5:
                tendencia = "En ascenso"
            elif diff < -0.5:
                tendencia = "En descenso"
            else:
                tendencia = "Estable"

            return {
                "temperatura": round(float(prediccion), 1),
                "tendencia":   tendencia
            }

        except Exception as e:
            logger.error(f"Error en predicción puntual: {e}")
            return {"temperatura": "--", "tendencia": "Error de cálculo"}

    def obtener_prediccion_futura(self, pronostico_dias: list) -> list:
        """
        Ajusta con IA el pronóstico de los 5 días que devuelve AEMET.
        Recibe la lista pronostico_dias de weather_service y añade
        temp_ia y tendencia a cada día.
        Lo usan las day-cards de prediccion_ia.html.
        """
        if self.model is None:
            # Si no hay modelo devolvemos los días sin ajuste para no romper la UI
            return [
                {**dia, "temp_ia": dia.get("temp_max", "--"), "tendencia": "IA no disponible"}
                for dia in pronostico_dias
            ]

        resultado = []
        for dia in pronostico_dias:
            try:
                # El modelo fue entrenado con humedad y presion — ajusta según tu train_ia.py
                input_data = pd.DataFrame([{
                    "humedad": dia.get("prob_lluvia", 50),  # usamos prob_lluvia como proxy
                    "presion": 1013,                         # presión estándar si no tenemos dato
                }])

                prediccion = self.model.predict(input_data)[0]
                temp_max   = dia.get("temp_max", 0)

                # Calculamos corrección respecto a la temp máxima del día
                diff = float(prediccion) - float(temp_max) if temp_max != "—" else 0
                if diff > 0.5:
                    tendencia = "En ascenso"
                elif diff < -0.5:
                    tendencia = "En descenso"
                else:
                    tendencia = "Estable"

                resultado.append({
                    **dia,                                    # conservamos fecha, temp_max, etc.
                    "temp_ia":   round(float(prediccion), 1),
                    "tendencia": tendencia,
                    "confianza": "95%"
                })

            except Exception as e:
                logger.error(f"Error procesando día {dia.get('fecha')}: {e}")
                # Si un día falla, lo añadimos sin ajuste para no perder el resto
                resultado.append({**dia, "temp_ia": dia.get("temp_max", "--"), "tendencia": "—"})

        return resultado
