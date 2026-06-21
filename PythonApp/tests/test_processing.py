from app.processing.pipeline import process_weather, process_activities


def test_process_weather_returns_dataframe():
    raw = {"hourly": {"time": ["2024-01-01T00:00"], "temperature_2m": [3.5]}}
    df = process_weather(raw)
    assert "temperature_2m" in df.columns
    assert len(df) == 1


def test_process_activities_computes_km():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 10000, "moving_time": 3600, "total_elevation_gain": 50,
        "average_speed": 2.778, "start_latlng": [55.68, 12.57],
        "location_city": "Copenhagen", "location_country": "Denmark",
    }]
    df = process_activities(raw)
    assert df["distance_km"].iloc[0] == 10.0
    assert df["duration_min"].iloc[0] == 60.0


def test_process_activities_empty():
    df = process_activities([])
    assert df.empty


def test_process_activities_speed_converted_to_kmh():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 10000, "moving_time": 3600, "average_speed": 2.778,
        "start_latlng": [55.68, 12.57],
    }]
    df = process_activities(raw)
    assert abs(df["average_speed_kmh"].iloc[0] - 10.0) < 0.01


def test_process_activities_preserves_latlng():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 5000, "moving_time": 1800, "average_speed": 2.778,
        "start_latlng": [55.68, 12.57],
    }]
    df = process_activities(raw)
    assert df["start_latlng"].iloc[0] == [55.68, 12.57]


def test_process_activities_preserves_location_fields():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 5000, "moving_time": 1800,
        "location_city": "Copenhagen", "location_country": "Denmark",
    }]
    df = process_activities(raw)
    assert df["location_city"].iloc[0] == "Copenhagen"
    assert df["location_country"].iloc[0] == "Denmark"


def test_process_activities_missing_location_fields_are_none():
    raw = [{
        "name": "Run", "type": "Run", "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 5000, "moving_time": 1800,
    }]
    df = process_activities(raw)
    assert df["location_city"].iloc[0] is None
    assert df["location_country"].iloc[0] is None
    assert df["start_latlng"].iloc[0] is None


def test_process_activities_indoor_no_latlng():
    raw = [{
        "name": "Indoor Ride", "type": "VirtualRide",
        "start_date_local": "2024-01-01T08:00:00Z",
        "distance": 20000, "moving_time": 2400, "average_speed": 8.33,
    }]
    df = process_activities(raw)
    assert not df.empty
    assert df["start_latlng"].iloc[0] is None
