from unittest.mock import patch, MagicMock
from app.apiclients.openmeteo import OpenMeteoClient


def test_get_forecast_returns_json():
    mock_response = MagicMock()
    mock_response.json.return_value = {"hourly": {"time": [], "temperature_2m": []}}
    with patch("app.apiclients.openmeteo.requests.get", return_value=mock_response):
        result = OpenMeteoClient().get_forecast(55.68, 12.57)
    assert "hourly" in result
