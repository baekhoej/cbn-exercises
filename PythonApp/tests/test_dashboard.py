import pandas as pd
from app.dashboard.server import build_dashboard


def test_build_dashboard_with_empty_data():
    weatherDataFrame = pd.DataFrame()
    activitiesDataFrame = pd.DataFrame()
    dashboard = build_dashboard(weatherDataFrame, activitiesDataFrame)
    assert dashboard is not None
