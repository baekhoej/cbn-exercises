import pandas as pd
from app.dashboard.server import build_dashboard


def test_build_dashboard_with_empty_data():
    weather_data = pd.DataFrame()
    activities_data = pd.DataFrame()
    dashboard = build_dashboard(weather_data, activities_data)
    assert dashboard is not None
