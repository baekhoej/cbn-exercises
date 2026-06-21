import pandas as pd
from app.dashboard.server import build_dashboard


def test_build_dashboard_with_empty_data():
    weather_df = pd.DataFrame()
    activities_df = pd.DataFrame()
    dashboard = build_dashboard(weather_df, activities_df)
    assert dashboard is not None
