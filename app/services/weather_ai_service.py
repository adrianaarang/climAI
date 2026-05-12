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
