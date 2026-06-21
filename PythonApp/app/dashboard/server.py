import panel as pn
import pandas as pd
import hvplot.pandas  # registers .hvplot accessor on DataFrames

pn.extension()


def build_dashboard(weather_df: pd.DataFrame, activities_df: pd.DataFrame) -> pn.viewable.Viewable:
    weather_plot = weather_df.hvplot.line(
        x="time", y="temperature_2m", title="Temperature forecast (°C)", responsive=True
    ) if not weather_df.empty else pn.pane.Str("No weather data")

    activities_plot = activities_df.hvplot.bar(
        x="start_date_local", y="distance_km", title="Activity distances (km)", responsive=True
    ) if not activities_df.empty else pn.pane.Str("No activity data")

    return pn.Column(
        "# CBN Dashboard",
        "## Weather",
        weather_plot,
        "## Strava Activities",
        activities_plot,
    )


def save_static(dashboard: pn.viewable.Viewable, path: str = "dashboard.html") -> None:
    dashboard.save(path, embed=True)
