import os
import requests


TOKEN_URL = "https://www.strava.com/oauth/token"
BASE_URL = "https://www.strava.com/api/v3"


class StravaClient:
    def __init__(self):
        self.client_id = os.environ["STRAVA_CLIENT_ID"]
        self.client_secret = os.environ["STRAVA_CLIENT_SECRET"]
        self.refresh_token = os.environ["STRAVA_REFRESH_TOKEN"]
        self._access_token: str | None = None

    def _refresh_access_token(self) -> str:
        response = requests.post(TOKEN_URL, data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }, timeout=10)
        if not response.ok:
            raise RuntimeError(f"Strava token refresh failed: {response.status_code} {response.text}")
        self._access_token = response.json()["access_token"]
        return self._access_token

    def _headers(self) -> dict:
        token = self._access_token or self._refresh_access_token()
        return {"Authorization": f"Bearer {token}"}

    def get_activities(self, per_page: int = 30, page: int = 1) -> list[dict]:
        response = requests.get(
            f"{BASE_URL}/athlete/activities",
            headers=self._headers(),
            params={"per_page": per_page, "page": page},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
