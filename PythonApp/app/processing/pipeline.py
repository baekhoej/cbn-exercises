import datetime

import pandas as pd


def process_weather(raw: dict) -> pd.DataFrame:
    hourly = raw.get("hourly", {})
    return pd.DataFrame(hourly)


def process_activities(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    activities_data = pd.DataFrame(raw)
    if "visibility" in activities_data.columns:
        activities_data = activities_data[activities_data["visibility"] != "only_me"]
    if activities_data.empty:
        return pd.DataFrame()
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


def enrich_with_weather(activities_data: pd.DataFrame, openmeteo_client, fallback_client=None) -> pd.DataFrame:
    enriched = activities_data.copy()
    enriched["temperature_c"] = None
    enriched["precipitation_mm"] = None
    enriched["windspeed_kmh"] = None
    enriched["cloudcover_pct"] = None

    for index, activity in enriched.iterrows():
        coords = activity["start_latlng"]
        if not isinstance(coords, list) or len(coords) < 2:
            continue

        lat, lon = coords[0], coords[1]
        activity_date = activity["start_date_local"].date()
        primary_kwargs = {"retries": 1, "timeout": 5} if fallback_client else {}
        try:
            historical_weather = openmeteo_client.get_historical_weather(lat, lon, activity_date, **primary_kwargs)
        except ValueError:
            continue
        except Exception:
            if fallback_client is None:
                continue
            try:
                historical_weather = fallback_client.get_historical_weather(lat, lon, activity_date)
            except Exception:
                continue

        hourly = historical_weather.get("hourly", {})
        times = pd.to_datetime(hourly.get("time", []))
        if len(times) == 0:
            continue

        closest_index = (times - activity["start_date_local"].tz_localize(None)).to_series().abs().argmin()
        enriched.at[index, "temperature_c"] = hourly["temperature_2m"][closest_index]
        enriched.at[index, "precipitation_mm"] = hourly["precipitation"][closest_index]
        enriched.at[index, "windspeed_kmh"] = hourly["windspeed_10m"][closest_index]
        enriched.at[index, "cloudcover_pct"] = hourly["cloudcover"][closest_index]

    return enriched
