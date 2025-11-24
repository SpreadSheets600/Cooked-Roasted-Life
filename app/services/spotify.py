import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session


class SpotifyService:
    def __init__(self, token_info=None):
        token_info = token_info or session.get("spotify_token_info")

        if token_info:
            self.spotify_app = spotipy.Spotify(auth=token_info["access_token"])

        else:
            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

            if not client_id or not client_secret:
                self.spotify_app = None
                return

            self.spotify_app = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=os.getenv(
                        "SPOTIFY_REDIRECT_URI", "http://localhost:8888/spotify/callback"
                    ),
                    scope=os.getenv(
                        "SPOTIFY_SCOPE",
                        "user-read-private user-read-email user-top-read user-read-recently-played",
                    ),
                )
            )

    def is_ready(self):
        return self.spotify_app is not None

    def get_roast_profile_data(self):
        if not self.is_ready():
            return {}
        try:
            artists_raw = self.spotify_app.current_user_top_artists(
                limit=10, time_range="long_term"
            )
            top_artists = [
                f"{a['name']} ({', '.join(a['genres'][:2])})"
                for a in artists_raw.get("items", [])
            ]
            recent_raw = self.spotify_app.current_user_recently_played(limit=10)
            recent_tracks = [
                f"{i['track']['name']} by {i['track']['artists'][0]['name']}"
                for i in recent_raw.get("items", [])
            ]
            return {"top_artists": top_artists, "recent_tracks": recent_tracks}
        except Exception:
            return {}
