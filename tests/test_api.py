from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
#Esto crea un navegador falso para hacer como hariamos en Postman (GET...)

def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200
# Comprueba que FastAPI arranca, la ruta existe y el servidor responde

def test_weather_endpoint_exists():

    response = client.get("/api/clima/")

    assert response.status_code == 200
# Simula una petición REAL a nuestro endpoint. Comprueba que la ruta existe y FastApi llega

def test_create_invalid_weather_record():

    response = client.post(
        "/api/clima/",
        json={}
    )

    assert response.status_code == 405
#Demuestra que nuestra API bloquea metodos no permitidos cuando alguien usa el método incorrecto.