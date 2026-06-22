import datetime
import os
from unittest.mock import patch, MagicMock
import pytest
from app.apiclients.visualcrossing import VisualCrossingClient

DATE = datetime.date(2024, 6, 15)
DATE_STR = "2024-06-15"


def _make_client():
    with patch.dict(os.environ, {"VISUAL_CROSSING_API_KEY": "test-key"}):
        return VisualCrossingClient()


def _make_raw_response():
    return {
        "days": [{
            "datetime": DATE_STR,
            "hours": [
                {"datetime": "00:00:00", "temp": 11.0, "precip": 0.0, "windspeed": 8.0, "cloudcover": 20.0},
                {"datetime": "08:00:00", "temp": 14.2, "precip": 0.5, "windspeed": 12.0, "cloudcover": 60.0},
                {"datetime": "16:00:00", "temp": 17.5, "precip": 2.0, "windspeed": 15.0, "cloudcover": 90.0},
            ],
        }]
    }


def test_sends_correct_url_and_params():
    mock_response = MagicMock()
    mock_response.json.return_value = _make_raw_response()
    client = _make_client()
    with patch("app.apiclients.visualcrossing.requests.get", return_value=mock_response) as mock_get:
        client.get_historical_weather(55.68, 12.57, DATE)
    url, kwargs = mock_get.call_args[0][0], mock_get.call_args[1]
    params = kwargs["params"]
    assert "55.68,12.57" in url
    assert DATE_STR in url
    assert params["unitGroup"] == "metric"
    assert params["key"] == "test-key"
    assert "temp" in params["elements"]
    assert "precip" in params["elements"]
    assert "windspeed" in params["elements"]
    assert "cloudcover" in params["elements"]


def test_normalises_response_to_openmeteo_format():
    mock_response = MagicMock()
    mock_response.json.return_value = _make_raw_response()
    client = _make_client()
    with patch("app.apiclients.visualcrossing.requests.get", return_value=mock_response):
        result = client.get_historical_weather(55.68, 12.57, DATE)
    hourly = result["hourly"]
    assert hourly["time"] == ["2024-06-15T00:00", "2024-06-15T08:00", "2024-06-15T16:00"]
    assert hourly["temperature_2m"] == [11.0, 14.2, 17.5]
    assert hourly["precipitation"] == [0.0, 0.5, 2.0]
    assert hourly["windspeed_10m"] == [8.0, 12.0, 15.0]
    assert hourly["cloudcover"] == [20.0, 60.0, 90.0]


def test_retries_on_failure():
    good_response = MagicMock()
    good_response.json.return_value = _make_raw_response()
    client = _make_client()
    with patch("app.apiclients.visualcrossing.requests.get",
               side_effect=[Exception("timeout"), good_response]) as mock_get:
        with patch("app.apiclients.visualcrossing.time.sleep"):
            client.get_historical_weather(55.68, 12.57, DATE)
    assert mock_get.call_count == 2


def test_raises_after_all_retries_exhausted():
    client = _make_client()
    with patch("app.apiclients.visualcrossing.requests.get", side_effect=Exception("timeout")) as mock_get:
        with patch("app.apiclients.visualcrossing.time.sleep"):
            with pytest.raises(Exception, match="timeout"):
                client.get_historical_weather(55.68, 12.57, DATE, retries=3)
    assert mock_get.call_count == 3


def test_raises_if_api_key_missing():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("VISUAL_CROSSING_API_KEY", None)
        with pytest.raises(KeyError):
            VisualCrossingClient()
