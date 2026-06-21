import pandas as pd
import panel as pn
from app.dashboard.server import build_dashboard


def _make_enriched_activities():
    return pd.DataFrame([{
        "name": "Morning Run",
        "type": "Run",
        "start_date_local": pd.Timestamp("2024-06-01 08:00:00"),
        "distance_km": 10.0,
        "duration_min": 60.0,
        "average_speed_kmh": 10.0,
        "start_latlng": [55.68, 12.57],
        "location_city": "Copenhagen",
        "location_country": "Denmark",
        "temperature_c": 14.2,
        "precipitation_mm": 0.0,
        "windspeed_kmh": 12.5,
    }])


def test_build_dashboard_with_empty_data():
    weather_data = pd.DataFrame()
    activities_data = pd.DataFrame()
    dashboard = build_dashboard(weather_data, activities_data)
    assert dashboard is not None


def test_build_dashboard_with_enriched_data_returns_panel_object():
    weather_data = pd.DataFrame({
        "time": ["2024-06-01T08:00", "2024-06-01T09:00"],
        "temperature_2m": [14.2, 15.0],
    })
    activities_data = _make_enriched_activities()
    dashboard = build_dashboard(weather_data, activities_data)
    assert isinstance(dashboard, pn.viewable.Viewable)


def test_build_dashboard_table_contains_expected_columns():
    activities_data = _make_enriched_activities()
    weather_data = pd.DataFrame()
    dashboard = build_dashboard(weather_data, activities_data)

    tabulator = next(
        item for item in dashboard if isinstance(item, pn.widgets.Tabulator)
    )
    assert "Type" in tabulator.value.columns
    assert "Location" in tabulator.value.columns
    assert "Distance (km)" in tabulator.value.columns
    assert "Avg Speed (km/h)" in tabulator.value.columns
    assert "Temp (°C)" in tabulator.value.columns
    assert "Precipitation (mm)" in tabulator.value.columns
    assert "Wind (km/h)" in tabulator.value.columns
