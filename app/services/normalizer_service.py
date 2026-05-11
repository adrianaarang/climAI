from datetime import datetime


def normalize_weather_data(raw_data: dict) -> dict:

    # Normaliza un registro de AEMET.

    return {
        "station_id": raw_data.get("idema"),
        "Zone": raw_data.get("ubi"),
        "temperature": raw_data.get("ta"),
        "temp_min": raw_data.get("tamin"),
        "temp_max": raw_data.get("tamax"),
        "humidity": raw_data.get("hr"),
        "precipitation": raw_data.get("prec"),
        "wind_speed": raw_data.get("vv"),

        "timestamp": datetime.strptime(
            raw_data["fint"],
            "%Y-%m-%dT%H:%M:%S%z"
        ),

        "source": "aemet"
    }


def normalize_aemet_response(api_response: list[dict]) -> list[dict]:

    #Normaliza todos los registros recibidos de AEMET.


    return [
        normalize_weather_data(item)
        for item in api_response
    ]
