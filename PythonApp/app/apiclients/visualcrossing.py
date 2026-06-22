import datetime
import os
import time
import requests


class VisualCrossingClient:
    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

    def __init__(self):
        self._api_key = os.environ["VISUAL_CROSSING_API_KEY"]

    def get_historical_weather(self, latitude: float, longitude: float, date: datetime.date, retries: int = 3) -> dict:
        date_str = date.strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/{latitude},{longitude}/{date_str}/{date_str}"
        params = {
            "unitGroup": "metric",
            "include": "hours",
            "elements": "datetime,temp,precip,windspeed,cloudcover",
            "key": self._api_key,
            "contentType": "json",
        }
        last_error: Exception
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return self._to_openmeteo_format(response.json(), date_str)
            except Exception as error:
                last_error = error
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        raise last_error

    def _to_openmeteo_format(self, raw: dict, date_str: str) -> dict:
        hours = raw["days"][0]["hours"]
        return {"hourly": {
            "time": [f"{date_str}T{h['datetime'][:5]}" for h in hours],
            "temperature_2m": [h["temp"] for h in hours],
            "precipitation": [h["precip"] for h in hours],
            "windspeed_10m": [h["windspeed"] for h in hours],
            "cloudcover": [h["cloudcover"] for h in hours],
        }}
