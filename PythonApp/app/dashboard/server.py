import panel as pn
import pandas as pd

pn.extension("tabulator")

TABLE_COLUMNS = {
    "type": "Type",
    "start_date_local": "Date",
    "weather_icon": "Weather",
    "location": "Location",
    "distance_km": "Distance (km)",
    "average_speed_kmh": "Avg Speed (km/h)",
    "temperature_c": "Temp (°C)",
    "precipitation_mm": "Precipitation (mm)",
    "windspeed_kmh": "Wind (km/h)",
}


def _weather_icon(precipitation_mm, cloudcover_pct, temperature_c) -> str:
    if precipitation_mm is None:
        return "—"
    if precipitation_mm >= 1.0 and temperature_c is not None and temperature_c < 2:
        return "🌨️"
    if precipitation_mm >= 2.0:
        return "🌧️"
    if precipitation_mm >= 0.5:
        return "🌦️"
    if cloudcover_pct is None:
        return "—"
    if cloudcover_pct >= 80:
        return "☁️"
    if cloudcover_pct >= 50:
        return "⛅"
    if cloudcover_pct >= 20:
        return "🌤️"
    return "☀️"


def _build_activities_table(activities_data: pd.DataFrame) -> pn.viewable.Viewable:
    if activities_data.empty:
        return pn.pane.Str("No activity data")

    display_data = activities_data.copy()

    display_data["location"] = display_data.apply(
        lambda row: row["location_city"]
        if row["location_city"]
        else (
            f"{row['start_latlng'][0]:.2f}, {row['start_latlng'][1]:.2f}"
            if isinstance(row["start_latlng"], list) and len(row["start_latlng"]) >= 2
            else "—"
        ),
        axis=1,
    )

    display_data["weather_icon"] = display_data.apply(
        lambda row: _weather_icon(
            row.get("precipitation_mm"),
            row.get("cloudcover_pct"),
            row.get("temperature_c"),
        ),
        axis=1,
    )

    available_columns = [col for col in TABLE_COLUMNS if col in display_data.columns]
    display_data = display_data[available_columns].rename(columns=TABLE_COLUMNS)

    return pn.widgets.Tabulator(display_data, show_index=False, sizing_mode="stretch_width")


def build_dashboard(weather_data: pd.DataFrame, activities_data: pd.DataFrame) -> pn.viewable.Viewable:
    return pn.Column(
        "# CBN Dashboard",
        "## Strava Activities",
        _build_activities_table(activities_data),
    )


def save_static(dashboard: pn.viewable.Viewable, path: str = "dashboard.html") -> None:
    dashboard.save(path, embed=True)
