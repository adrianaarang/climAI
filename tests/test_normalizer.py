from datetime import datetime

from app.services.normalizer_service import (
    normalize_weather_data,
    normalize_aemet_response
)


def test_normalize_weather_data():
    raw_data = {
        "idema": "3195",
        "ubi": "Madrid-Retiro",
        "ta": 25.4,
        "tamin": 18.0,
        "tamax": 30.0,
        "hr": 45,
        "prec": 0.0,
        "vv": 12.5,
        "fint": "2026-05-11T12:00:00+0000"
    }

    result = normalize_weather_data(raw_data)

    assert result["station_id"] == "3195"
    assert result["zone"] == "Madrid-Retiro"
    assert result["temperature"] == 25.4
    assert result["humidity"] == 45
    assert isinstance(result["timestamp"], datetime)
    assert result["source"] == "aemet"



def test_normalize_aemet_response():
    api_response = [
        {
            "idema": "1",
            "ubi": "Madrid",
            "ta": 20,
            "tamin": 15,
            "tamax": 25,
            "hr": 50,
            "prec": 0,
            "vv": 10,
            "fint": "2026-05-11T12:00:00+0000"
        },
        {
            "idema": "2",
            "ubi": "Barcelona",
            "ta": 22,
            "tamin": 17,
            "tamax": 28,
            "hr": 60,
            "prec": 1,
            "vv": 8,
            "fint": "2026-05-11T12:00:00+0000"
        }
    ]

    result = normalize_aemet_response(api_response)

    assert len(result) == 2
    assert result[0]["station_id"] == "1"
    assert result[1]["zone"] == "Barcelona"