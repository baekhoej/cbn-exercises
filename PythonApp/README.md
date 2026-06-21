# CBN Dashboard

A Python app that fetches data from external APIs, processes it, and presents it as an interactive web dashboard. Supports both live serving and static HTML export.

## Architecture

```
PythonApp/
├── app/
│   ├── apiclients/
│   │   ├── openmeteo.py    # Open-Meteo weather forecast client
│   │   └── strava.py       # Strava activities client (OAuth2)
│   ├── processing/
│   │   └── pipeline.py     # Transforms raw API data into DataFrames
│   └── dashboard/
│       └── server.py       # Panel dashboard (live or static export)
├── tests/                  # Unit tests for all three layers
├── get_strava_token.py     # One-time helper to obtain a Strava refresh token
├── main.py                 # Entry point
├── requirements.txt
└── .env.example
```

## Setup

### 1. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Fill in `.env` with your Strava API credentials (get these from [strava.com/settings/api](https://www.strava.com/settings/api)):

```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
```

### 3. Obtain a Strava refresh token

The refresh token must be obtained via OAuth with `activity:read_all` scope. Run the helper script once — it opens your browser, handles the callback, and prints the token to copy into `.env`:

```bash
.venv/bin/python get_strava_token.py
```

> Make sure `http://localhost:8765/callback` is listed as an authorized callback domain in your Strava API settings.

## Usage

### Live dashboard

```bash
.venv/bin/python main.py
```

Opens the dashboard in your browser. Weather data defaults to Copenhagen (55.68°N, 12.57°E).

### Static HTML export

```bash
.venv/bin/python main.py --static --output dashboard.html
```

Produces a self-contained `dashboard.html` with client-side interactivity (zoom, pan, hover) but no live data refresh.

## Running tests

```bash
.venv/bin/pytest tests/ -v
```

## Data sources

| Source | Auth | What it provides |
|---|---|---|
| [Open-Meteo](https://open-meteo.com/) | None (free, no key required) | Hourly weather forecast |
| [Strava](https://developers.strava.com/) | OAuth2 refresh token | Activity list (distance, duration, elevation) |


## Coding Style

- Do not use abbreviated variable names. The purpose of a variable should be readable from its name. Use snake_case as per PEP 8. For example, use `activities_data` instead of `df`, and `weather_data` instead of `weather_df`.

## Development Workflow

The development workflow for this project should follow these steps, in order:

1. Create a feature branch with name features/issue-123 (where 123 is replaced with the actual issue number)
2. Implement the feature as described
3. Run and check all relevant tests
4. Create a pull request for the issue
5. Manual review of pull request
6. Add any changes found in the review
7. Squash merge pull request into master