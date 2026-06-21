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

    weatherRaw = OpenMeteoClient().get_forecast(latitude=55.68, longitude=12.57)
    weatherDataFrame = process_weather(weatherRaw)

    stravaRaw = StravaClient().get_activities()
    activitiesDataFrame = process_activities(stravaRaw)

    dashboard = build_dashboard(weatherDataFrame, activitiesDataFrame)

    if args.static:
        save_static(dashboard, path=args.output)
        print(f"Static dashboard saved to {args.output}")
    else:
        dashboard.show(title="CBN Dashboard")


if __name__ == "__main__":
    main()
