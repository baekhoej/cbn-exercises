"""
One-time helper to obtain a Strava refresh token with activity:read_all scope.

Usage:
    python get_strava_token.py

You will need STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in your .env file.
"""

import http.server
import threading
import webbrowser
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8765/callback"
SCOPE = "activity:read_all"

auth_code: str | None = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = parse_qs(urlparse(self.path).query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Authorization successful. You can close this tab.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h2>Missing code parameter.</h2>")

    def log_message(self, format, *args):
        pass  # suppress request logging


def main():
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=force"
        f"&scope={SCOPE}"
    )

    server = http.server.HTTPServer(("localhost", 8765), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    print("Opening Strava authorization in your browser...")
    print(f"If it doesn't open, visit:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    thread.join(timeout=120)

    if not auth_code:
        print("No authorization code received within 2 minutes. Aborting.")
        return

    response = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
    }, timeout=10)
    response.raise_for_status()

    tokens = response.json()
    refresh_token = tokens["refresh_token"]
    athlete = tokens.get("athlete", {})

    print(f"\nAuthorized as: {athlete.get('firstname', '')} {athlete.get('lastname', '')}")
    print(f"\nAdd this to your .env file:")
    print(f"STRAVA_REFRESH_TOKEN={refresh_token}")


if __name__ == "__main__":
    main()
