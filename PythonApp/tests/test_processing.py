from unittest.mock import MagicMock
from app.processing.pipeline import process_weather, process_activities, enrich_with_weather


def test_process_weather_returns_dataframe():
    raw = {"hourly": {"time": ["2024-01-01T00:00"], "temperature_2m": [3.5]}}
    weather_data = process_weather(raw)
    assert "temperature_2m" in weather_data.columns
    assert len(weather_data) == 1


def test_process_activities_computes_km():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 10000, "moving_time": 3600, "total_elevation_gain": 50,
        "average_speed": 2.778, "start_latlng": [55.68, 12.57],
        "location_city": "Copenhagen", "location_country": "Denmark",
    }]
    activities_data = process_activities(raw)
    assert activities_data["distance_km"].iloc[0] == 10.0
    assert activities_data["duration_min"].iloc[0] == 60.0


def test_process_activities_empty():
    activities_data = process_activities([])
    assert activities_data.empty


def test_process_activities_speed_converted_to_kmh():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 10000, "moving_time": 3600, "average_speed": 2.778,
        "start_latlng": [55.68, 12.57],
    }]
    activities_data = process_activities(raw)
    assert abs(activities_data["average_speed_kmh"].iloc[0] - 10.0) < 0.01


def test_process_activities_preserves_latlng():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 5000, "moving_time": 1800, "average_speed": 2.778,
        "start_latlng": [55.68, 12.57],
    }]
    activities_data = process_activities(raw)
    assert activities_data["start_latlng"].iloc[0] == [55.68, 12.57]


def test_process_activities_preserves_location_fields():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 5000, "moving_time": 1800,
        "location_city": "Copenhagen", "location_country": "Denmark",
    }]
    activities_data = process_activities(raw)
    assert activities_data["location_city"].iloc[0] == "Copenhagen"
    assert activities_data["location_country"].iloc[0] == "Denmark"


def test_process_activities_missing_location_fields_are_none():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 5000, "moving_time": 1800,
    }]
    activities_data = process_activities(raw)
    assert activities_data["location_city"].iloc[0] is None
    assert activities_data["location_country"].iloc[0] is None
    assert activities_data["start_latlng"].iloc[0] is None


def test_process_activities_indoor_no_latlng():
    raw = [{
        "name": "Indoor Ride", "type": "VirtualRide",
        "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 20000, "moving_time": 2400, "average_speed": 8.33,
    }]
    activities_data = process_activities(raw)
    assert not activities_data.empty
    assert activities_data["start_latlng"].iloc[0] is None


def _make_weather_response():
    return {
        "hourly": {
            "time": ["2024-06-01T07:00", "2024-06-01T08:00", "2024-06-01T09:00"],
            "temperature_2m": [11.0, 14.2, 17.5],
            "precipitation": [0.2, 0.0, 0.5],
            "windspeed_10m": [8.0, 12.5, 20.0],
        }
    }


def test_enrich_with_weather_adds_columns():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-06-01T08:00:00Z",
        "distance": 10000, "moving_time": 3600, "average_speed": 2.778,
        "start_latlng": [55.68, 12.57],
    }]
    activities_data = process_activities(raw)
    mock_client = MagicMock()
    mock_client.get_historical_weather.return_value = _make_weather_response()

    enriched = enrich_with_weather(activities_data, mock_client)

    # activity starts at 08:00 — matches index 1
    assert enriched["temperature_c"].iloc[0] == 14.2
    assert enriched["windspeed_kmh"].iloc[0] == 12.5
    assert enriched["precipitation_mm"].iloc[0] == 0.0


def test_enrich_with_weather_matches_nearest_hour():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-06-01T08:45:00Z",
        "distance": 10000, "moving_time": 3600, "average_speed": 2.778,
        "start_latlng": [55.68, 12.57],
    }]
    activities_data = process_activities(raw)
    mock_client = MagicMock()
    mock_client.get_historical_weather.return_value = _make_weather_response()

    enriched = enrich_with_weather(activities_data, mock_client)

    # 08:45 is closer to 09:00 (index 2, temp=17.5) than 08:00 (index 1, temp=14.2)
    assert enriched["temperature_c"].iloc[0] == 17.5


def test_enrich_with_weather_skips_indoor_activities():
    raw = [{
        "name": "Indoor Ride", "type": "VirtualRide",
        "start_date_local": "2024-06-01T08:00:00Z",
        "distance": 20000, "moving_time": 2400, "average_speed": 8.33,
    }]
    activities_data = process_activities(raw)
    mock_client = MagicMock()

    enriched = enrich_with_weather(activities_data, mock_client)

    mock_client.get_historical_weather.assert_not_called()
    assert enriched["temperature_c"].iloc[0] is None
    assert enriched["precipitation_mm"].iloc[0] is None
    assert enriched["windspeed_kmh"].iloc[0] is None


def test_enrich_with_weather_calls_api_once_per_outdoor_activity():
    raw = [
        {
            "name": "Morning Run", "type": "Run", "start_date_local": "2024-06-01T08:00:00Z",
            "distance": 10000, "moving_time": 3600, "average_speed": 2.778,
            "start_latlng": [55.68, 12.57],
        },
        {
            "name": "Indoor Ride", "type": "VirtualRide", "start_date_local": "2024-06-01T10:00:00Z",
            "distance": 20000, "moving_time": 2400, "average_speed": 8.33,
        },
        {
            "name": "Evening Run", "type": "Run", "start_date_local": "2024-06-01T18:00:00Z",
            "distance": 5000, "moving_time": 1800, "average_speed": 2.778,
            "start_latlng": [55.70, 12.60],
        },
    ]
    activities_data = process_activities(raw)
    mock_client = MagicMock()
    mock_client.get_historical_weather.return_value = _make_weather_response()

    enrich_with_weather(activities_data, mock_client)

    assert mock_client.get_historical_weather.call_count == 2
