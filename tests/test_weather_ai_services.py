from unittest.mock import MagicMock

from app.services.weather_ai_service import WeatherAIService

#Hacemos mock para probar solo nuestra logica, no necesitamos cargar el modelo real
#Asi va mas rápido

def test_obtener_prediccion():
    service = WeatherAIService()

    mock_model = MagicMock()
    mock_model.predict.return_value = [30.0]

    service.model = mock_model

    result = service.obtener_prediccion(
        temp=25,
        humedad=40
    )

    assert result["temperatura"] == 30.0
    assert result["tendencia"] == "En ascenso"