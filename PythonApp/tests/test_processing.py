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
    }]
    df = process_activities(raw)
    assert df["distance_km"].iloc[0] == 10.0
    assert df["duration_min"].iloc[0] == 60.0


def test_process_activities_empty():
    df = process_activities([])
    assert df.empty
