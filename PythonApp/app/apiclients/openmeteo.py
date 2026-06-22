import datetime
import time
import requests

MAX_PAST_DAYS = 92


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

    def get_historical_weather(self, latitude: float, longitude: float, date: datetime.date, retries: int = 3, timeout: int = 30) -> dict:
        days_ago = (datetime.date.today() - date).days
        if days_ago > MAX_PAST_DAYS:
            raise ValueError(f"Date {date} is {days_ago} days ago, beyond the {MAX_PAST_DAYS}-day limit")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "past_days": days_ago + 1,
            "forecast_days": 0,
            "hourly": "temperature_2m,precipitation,windspeed_10m,cloudcover",
        }
        last_error: Exception
        for attempt in range(retries):
            try:
                response = requests.get(self.BASE_URL, params=params, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except Exception as error:
                last_error = error
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        raise last_error
