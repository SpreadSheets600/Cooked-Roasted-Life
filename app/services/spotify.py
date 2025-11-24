import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session


class SpotifyService:
    def __init__(self, token_info=None):
        token_info = token_info or session.get("spotify_token_info")

        if token_info:
            expires_at = token_info.get("expires_at")
            access_token = token_info.get("access_token")
            refresh_token = token_info.get("refresh_token")

            if expires_at and time.time() > (expires_at - 60) and refresh_token:
                try:
                    oauth = SpotifyOAuth(
                        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                        redirect_uri=os.getenv(
                            "SPOTIFY_REDIRECT_URI",
                            "http://localhost:8888/spotify/callback",
                        ),
                        scope=os.getenv(
                            "SPOTIFY_SCOPE",
                            "user-read-private user-read-email user-top-read user-read-recently-played",
                        ),
                        cache_path=None,
                        show_dialog=False,
                    )
                    new_tokens = oauth.refresh_access_token(refresh_token)

                    session["spotify_token_info"] = {**token_info, **new_tokens}
                    access_token = new_tokens.get("access_token", access_token)

                except Exception:
                    session.pop("spotify_token_info", None)
                    self.spotify_app = None
                    return

            self.spotify_app = spotipy.Spotify(auth=access_token)
        else:
            self.spotify_app = None

    def is_ready(self):
        return self.spotify_app is not None

    def get_roast_profile_data(self):
        if not self.is_ready():
            return {}
        data = {}

        try:
            artists_raw = self.spotify_app.current_user_top_artists(
                limit=10, time_range="long_term"
            )
            data["top_artists"] = [
                f"{a['name']} ({', '.join(a.get('genres', [])[:2])})"
                for a in artists_raw.get("items", [])
            ]
        except Exception:
            data["top_artists"] = []

        try:
            recent_raw = self.spotify_app.current_user_recently_played(limit=10)
            data["recent_tracks"] = [
                f"{i['track']['name']} by {i['track']['artists'][0]['name']}"
                for i in recent_raw.get("items", [])
            ]
        except Exception:
            data["recent_tracks"] = []

        return data
