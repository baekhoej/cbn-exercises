import requests


class OpenMeteoClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def get_forecast(self, latitude: float, longitude: float, variables: list[str] | None = None) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(variables or ["temperature_2m", "precipitation", "windspeed_10m"]),
        }
        response = requests.get(self.BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
