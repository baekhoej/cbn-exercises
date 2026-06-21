import pandas as pd


def process_weather(raw: dict) -> pd.DataFrame:
    hourly = raw.get("hourly", {})
    return pd.DataFrame(hourly)


def process_activities(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    keep = [
        "name", "type", "start_date_local", "distance", "moving_time",
        "total_elevation_gain", "average_speed", "start_latlng",
        "location_city", "location_country",
    ]
    df = df[[c for c in keep if c in df.columns]].copy()
    for col in ["location_city", "location_country", "start_latlng"]:
        if col not in df.columns:
            df[col] = None
    df["distance_km"] = df["distance"] / 1000
    df["duration_min"] = df["moving_time"] / 60
    df["start_date_local"] = pd.to_datetime(df["start_date_local"])
    if "average_speed" in df.columns:
        df["average_speed_kmh"] = df["average_speed"] * 3.6
    return df
