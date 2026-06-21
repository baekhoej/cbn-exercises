import argparse
from dotenv import load_dotenv

load_dotenv()

from app.apiclients.openmeteo import OpenMeteoClient
from app.apiclients.strava import StravaClient
from app.processing.pipeline import process_weather, process_activities
from app.dashboard.server import build_dashboard, save_static


def main():
    parser = argparse.ArgumentParser(description="CBN Dashboard")
    parser.add_argument("--static", action="store_true", help="Export static HTML instead of serving live")
    parser.add_argument("--output", default="dashboard.html", help="Output path for static export")
    args = parser.parse_args()

    weather_raw = OpenMeteoClient().get_forecast(latitude=55.68, longitude=12.57)
    weather_df = process_weather(weather_raw)

    strava_raw = StravaClient().get_activities()
    activities_df = process_activities(strava_raw)

    dashboard = build_dashboard(weather_df, activities_df)

    if args.static:
        save_static(dashboard, path=args.output)
        print(f"Static dashboard saved to {args.output}")
    else:
        dashboard.show(title="CBN Dashboard")


if __name__ == "__main__":
    main()
