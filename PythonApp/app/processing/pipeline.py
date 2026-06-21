import pandas as pd


def process_weather(raw: dict) -> pd.DataFrame:
    hourly = raw.get("hourly", {})
    return pd.DataFrame(hourly)


def process_activities(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    activities_data = pd.DataFrame(raw)
    keep = [
        "name", "type", "start_date_local", "distance", "moving_time",
        "total_elevation_gain", "average_speed", "start_latlng",
        "location_city", "location_country",
    ]
    activities_data = activities_data[[c for c in keep if c in activities_data.columns]].copy()
    for col in ["location_city", "location_country", "start_latlng"]:
        if col not in activities_data.columns:
            activities_data[col] = None
    activities_data["distance_km"] = activities_data["distance"] / 1000
    activities_data["duration_min"] = activities_data["moving_time"] / 60
    activities_data["start_date_local"] = pd.to_datetime(activities_data["start_date_local"])
    if "average_speed" in activities_data.columns:
        activities_data["average_speed_kmh"] = activities_data["average_speed"] * 3.6
    return activities_data
