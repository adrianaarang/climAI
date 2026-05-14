from app.services.alert_service import AlertService
from datetime import datetime

service = AlertService()

# Los tests primeros detectaron que el servicio de alertas primero validaba el schema Pydantic 
# antes de ejecutar la lógica meteorológica (no incluian station_id, timestamp). 
# Ajustamos los datos del test para cumplir los campos obligatorios del modelo.
# Esto significa que: nuestro sistema valida datos correctamente, Pydantic está funcionando,
# el servicio no acepta registros incompletos y tenemos una validación robusta.

def test_heat_alert_triggered():

    registro = {
        "station_id": "3195",
        "timestamp": datetime.now().isoformat(),
        "temperature": 42,
        "humidity": 20,
        "wind_speed": 5,
        "precipitation": 0
    }

    result = service.evaluar_alertas(registro)

    assert len(result) > 0
# Comprobamos que se genera una alerta al poner una temperatura alta

def test_wind_alert_triggered():

    registro = {
        "station_id": "3195",
        "timestamp": datetime.now().isoformat(),
        "temperature": 25,
        "humidity": 40,
        "wind_speed": 120,
        "precipitation": 0
    }

    result = service.evaluar_alertas(registro)

    assert len(result) > 0
#Comprobamos que la validación funciona con viento extremo

def test_no_alerts():

    registro = {
        "station_id": "3195",
        "timestamp": datetime.now().isoformat(),
        "temperature": 22,
        "humidity": 50,
        "wind_speed": 10,
        "precipitation": 0
    }

    result = service.evaluar_alertas(registro)

    assert result == ["VERDE"]
#Comprobamos que salta verde, sin alertas