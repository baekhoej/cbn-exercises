import pandas as pd


def process_weather(raw: dict) -> pd.DataFrame:
    hourly = raw.get("hourly", {})
    return pd.DataFrame(hourly)


def process_activities(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    activitiesDataFrame = pd.DataFrame(raw)
    keep = [
        "name", "type", "start_date_local", "distance", "moving_time",
        "total_elevation_gain", "average_speed", "start_latlng",
        "location_city", "location_country",
    ]
    activitiesDataFrame = activitiesDataFrame[[c for c in keep if c in activitiesDataFrame.columns]].copy()
    for col in ["location_city", "location_country", "start_latlng"]:
        if col not in activitiesDataFrame.columns:
            activitiesDataFrame[col] = None
    activitiesDataFrame["distance_km"] = activitiesDataFrame["distance"] / 1000
    activitiesDataFrame["duration_min"] = activitiesDataFrame["moving_time"] / 60
    activitiesDataFrame["start_date_local"] = pd.to_datetime(activitiesDataFrame["start_date_local"])
    if "average_speed" in activitiesDataFrame.columns:
        activitiesDataFrame["average_speed_kmh"] = activitiesDataFrame["average_speed"] * 3.6
    return activitiesDataFrame
