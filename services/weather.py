import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude, longitude):
    """Consulta dados meteorológicos públicos do Open-Meteo."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,precipitation,rain,showers,weather_code",
        "timezone": "America/Sao_Paulo",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=8)
    response.raise_for_status()
    payload = response.json()

    current = payload.get("current")
    if not isinstance(current, dict):
        raise ValueError("Resposta climática inesperada.")

    return {
        "fonte": "Open-Meteo",
        "latitude": latitude,
        "longitude": longitude,
        "horario": current.get("time"),
        "temperatura_c": current.get("temperature_2m"),
        "precipitacao_mm": current.get("precipitation"),
        "chuva_mm": current.get("rain"),
        "codigo_tempo": current.get("weather_code"),
        "observacao": "Dados meteorológicos não representam confirmação de alagamento.",
    }
