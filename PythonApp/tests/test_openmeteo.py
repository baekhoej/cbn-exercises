import datetime
from unittest.mock import patch, MagicMock
import pytest
from app.apiclients.openmeteo import OpenMeteoClient, MAX_PAST_DAYS

RECENT_DATE = datetime.date.today() - datetime.timedelta(days=5)
OLD_DATE = datetime.date.today() - datetime.timedelta(days=MAX_PAST_DAYS + 1)


def test_get_forecast_returns_json():
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": {"time": [], "temperature_2m": []}}
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response):
        result = OpenMeteoClient().get_forecast(55.68, 12.57)
    assert "hourly" in result


def test_get_historical_weather_sends_correct_params():
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": {}}
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response) as mock_get:
        OpenMeteoClient().get_historical_weather(55.68, 12.57, RECENT_DATE)
    _, kwargs = mock_get.call_args
    params = kwargs["params"]
    assert params["latitude"] == 55.68
    assert params["longitude"] == 12.57
    assert params["past_days"] == (datetime.date.today() - RECENT_DATE).days + 1
    assert params["forecast_days"] == 0
    assert "temperature_2m" in params["hourly"]
    assert "precipitation" in params["hourly"]
    assert "windspeed_10m" in params["hourly"]
    assert "cloudcover" in params["hourly"]


def test_get_historical_weather_uses_forecast_api_url():
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": {}}
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response) as mock_get:
        OpenMeteoClient().get_historical_weather(55.68, 12.57, RECENT_DATE)
    url = mock_get.call_args[0][0]
    assert "api.open-meteo.com" in url
    assert "archive" not in url


def test_get_historical_weather_returns_hourly_fields():
    hourly = {
        "time": ["2026-06-16T00:00", "2026-06-16T01:00"],
        "temperature_2m": [14.2, 13.8],
        "precipitation": [0.0, 0.1],
        "windspeed_10m": [8.5, 9.0],
    }
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": hourly}
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response):
        result = OpenMeteoClient().get_historical_weather(55.68, 12.57, RECENT_DATE)
    assert result["hourly"]["temperature_2m"] == [14.2, 13.8]
    assert result["hourly"]["precipitation"] == [0.0, 0.1]
    assert result["hourly"]["windspeed_10m"] == [8.5, 9.0]


def test_get_historical_weather_raises_value_error_for_old_dates():
    with patch("app.apiclients.openmeteo.requests.get") as mock_get:
        with pytest.raises(ValueError, match="beyond the"):
            OpenMeteoClient().get_historical_weather(55.68, 12.57, OLD_DATE)
    mock_get.assert_not_called()


def test_get_historical_weather_propagates_http_errors():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("503 Service Unavailable")
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response):
        with patch("app.apiclients.openmeteo.time.sleep"):
            with pytest.raises(Exception, match="503"):
                OpenMeteoClient().get_historical_weather(55.68, 12.57, RECENT_DATE)


def test_get_historical_weather_retries_on_failure():
    good_response = MagicMock()
    good_response.json.return_value = {"hourly": {}}
    with patch("app.apiclients.openmeteo.requests.get", side_effect=[Exception("timeout"), good_response]) as mock_get:
        with patch("app.apiclients.openmeteo.time.sleep"):
            OpenMeteoClient().get_historical_weather(55.68, 12.57, RECENT_DATE)
    assert mock_get.call_count == 2


def test_get_historical_weather_raises_after_all_retries_exhausted():
    with patch("app.apiclients.openmeteo.requests.get", side_effect=Exception("timeout")) as mock_get:
        with patch("app.apiclients.openmeteo.time.sleep"):
            with pytest.raises(Exception, match="timeout"):
                OpenMeteoClient().get_historical_weather(55.68, 12.57, RECENT_DATE, retries=3)
    assert mock_get.call_count == 3
