import datetime
from unittest.mock import patch, MagicMock, call
import pytest
from app.apiclients.openmeteo import OpenMeteoClient


def test_get_forecast_returns_json():
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": {"time": [], "temperature_2m": []}}
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response):
        result = OpenMeteoClient().get_forecast(55.68, 12.57)
    assert "hourly" in result


def test_get_historical_weather_sends_correct_params():
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": {}}
    date = datetime.date(2024, 6, 1)
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response) as mock_get:
        OpenMeteoClient().get_historical_weather(55.68, 12.57, date)
    _, kwargs = mock_get.call_args
    params = kwargs["params"]
    assert params["latitude"] == 55.68
    assert params["longitude"] == 12.57
    assert params["start_date"] == "2024-06-01"
    assert params["end_date"] == "2024-06-01"
    assert "temperature_2m" in params["hourly"]
    assert "precipitation" in params["hourly"]
    assert "windspeed_10m" in params["hourly"]
    assert "cloudcover" in params["hourly"]


def test_get_historical_weather_returns_hourly_fields():
    hourly = {
        "time": ["2024-06-01T00:00", "2024-06-01T01:00"],
        "temperature_2m": [14.2, 13.8],
        "precipitation": [0.0, 0.1],
        "windspeed_10m": [8.5, 9.0],
    }
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": hourly}
    date = datetime.date(2024, 6, 1)
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response):
        result = OpenMeteoClient().get_historical_weather(55.68, 12.57, date)
    assert result["hourly"]["temperature_2m"] == [14.2, 13.8]
    assert result["hourly"]["precipitation"] == [0.0, 0.1]
    assert result["hourly"]["windspeed_10m"] == [8.5, 9.0]


def test_get_historical_weather_propagates_http_errors():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("503 Service Unavailable")
    date = datetime.date(2024, 6, 1)
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response):
        with pytest.raises(Exception, match="503"):
            OpenMeteoClient().get_historical_weather(55.68, 12.57, date)
