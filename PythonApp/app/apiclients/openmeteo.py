import datetime
import time
import requests


class OpenMeteoClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def get_forecast(self, latitude: float, longitude: float, variables: list[str] | None = None) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(variables or ["temperature_2m", "precipitation", "windspeed_10m"]),
        }
        response = requests.get(self.BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_historical_weather(self, latitude: float, longitude: float, date: datetime.date, retries: int = 3) -> dict:
        date_str = date.strftime("%Y-%m-%d")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_str,
            "end_date": date_str,
            "hourly": "temperature_2m,precipitation,windspeed_10m,cloudcover",
        }
        last_error: Exception
        for attempt in range(retries):
            try:
                response = requests.get(self.ARCHIVE_URL, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as error:
                last_error = error
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        raise last_error
