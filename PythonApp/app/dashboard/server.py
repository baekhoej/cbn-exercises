import panel as pn
import pandas as pd
import hvplot.pandas  # registers .hvplot accessor on DataFrames

pn.extension("tabulator")

TABLE_COLUMNS = {
    "type": "Type",
    "location": "Location",
    "distance_km": "Distance (km)",
    "average_speed_kmh": "Avg Speed (km/h)",
    "temperature_c": "Temp (°C)",
    "precipitation_mm": "Precipitation (mm)",
    "windspeed_kmh": "Wind (km/h)",
}


def _build_activities_table(activities_data: pd.DataFrame) -> pn.viewable.Viewable:
    if activities_data.empty:
        return pn.pane.Str("No activity data")

    display_data = activities_data.copy()

    display_data["location"] = display_data.apply(
        lambda row: row["location_city"]
        if row["location_city"]
        else (
            f"{row['start_latlng'][0]:.2f}, {row['start_latlng'][1]:.2f}"
            if isinstance(row["start_latlng"], list)
            else "—"
        ),
        axis=1,
    )

    available_columns = [col for col in TABLE_COLUMNS if col in display_data.columns]
    display_data = display_data[available_columns].rename(columns=TABLE_COLUMNS)

    return pn.widgets.Tabulator(display_data, show_index=False, sizing_mode="stretch_width")


def build_dashboard(weather_data: pd.DataFrame, activities_data: pd.DataFrame) -> pn.viewable.Viewable:
    weather_plot = weather_data.hvplot.line(
        x="time", y="temperature_2m", title="Temperature forecast (°C)", responsive=True
    ) if not weather_data.empty else pn.pane.Str("No weather data")

    activities_plot = activities_data.hvplot.bar(
        x="start_date_local", y="distance_km", title="Activity distances (km)", responsive=True
    ) if not activities_data.empty else pn.pane.Str("No activity data")

    return pn.Column(
        "# CBN Dashboard",
        "## Weather",
        weather_plot,
        "## Strava Activities",
        _build_activities_table(activities_data),
        activities_plot,
    )


def save_static(dashboard: pn.viewable.Viewable, path: str = "dashboard.html") -> None:
    dashboard.save(path, embed=True)
