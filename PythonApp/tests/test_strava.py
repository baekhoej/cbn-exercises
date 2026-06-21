from unittest.mock import patch, MagicMock
from app.apiclients.strava import StravaClient
import os


def test_get_activities_returns_list(monkeypatch):
    monkeypatch.setenv("STRAVA_CLIENT_ID", "id")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret")
    monkeypatch.setenv("STRAVA_REFRESH_TOKEN", "token")

    token_response = MagicMock()
    token_response.json.return_value = {"access_token": "abc"}

    activities_response = MagicMock()
    activities_response.json.return_value = [{"name": "Morning Run", "type": "Run", "distance": 5000}]

    with patch("app.apiclients.strava.requests.post", return_value=token_response), \
         patch("app.apiclients.strava.requests.get", return_value=activities_response):
        result = StravaClient().get_activities()

    assert isinstance(result, list)
    assert result[0]["name"] == "Morning Run"
