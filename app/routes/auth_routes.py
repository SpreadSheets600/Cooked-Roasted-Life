from . import auth_bp

import os
from spotipy.oauth2 import SpotifyOAuth
from flask import redirect, request, session, url_for, current_app


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv(
            "SPOTIFY_REDIRECT_URI", "http://localhost:8888/spotify/callback"
        ),
        scope=os.getenv(
            "SPOTIFY_SCOPE",
            "user-read-private user-read-email user-top-read user-read-recently-played",
        ),
        cache_path=None,
        show_dialog=True,
    )


@auth_bp.route("/spotify/login")
def spotify_login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

    post_auth_redirect = request.args.get("redirect") or current_app.config.get(
        "FRONTEND_ORIGIN"
    )
    if post_auth_redirect:
        session["post_auth_redirect"] = post_auth_redirect
    return redirect(auth_url)


@auth_bp.route("/spotify/callback")
def spotify_callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get("code")

    if code:
        token_info = sp_oauth.get_access_token(code)
        session["spotify_token_info"] = token_info
        session["spotify_authenticated"] = True

        try:
            import spotipy

            sp = spotipy.Spotify(auth=token_info["access_token"])
            user_info = sp.current_user()

            session["user_name"] = user_info.get("display_name") or user_info.get("id")

        except Exception:
            pass

    redirect_to = (
        session.pop("post_auth_redirect", None)
        or current_app.config.get("FRONTEND_ORIGIN")
        or request.args.get("redirect")
        or url_for("main.index")
    )
    return redirect(redirect_to)


@auth_bp.route("/spotify/logout")
def spotify_logout():
    session.pop("spotify_authenticated", None)
    session.pop("spotify_token_info", None)
    session.pop("spotify_username", None)

    redirect_to = (
        request.args.get("redirect")
        or current_app.config.get("FRONTEND_ORIGIN")
        or url_for("main.index")
    )
    return redirect(redirect_to)
