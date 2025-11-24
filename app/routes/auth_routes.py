from . import auth_bp
from ..models.database import db, User

import os
import requests
from spotipy.oauth2 import SpotifyOAuth
from flask import redirect, request, session, url_for, current_app


def get_google_provider_cfg():
    return requests.get(current_app.config["GOOGLE_DISCOVERY_URL"]).json()


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


# Google OAuth
@auth_bp.route("/google/login")
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    redirect_uri = url_for("auth.google_callback", _external=True)

    params = {
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "response_type": "code",
    }

    import urllib.parse

    auth_url = f"{authorization_endpoint}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


@auth_bp.route("/google/callback")
def google_callback():
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = (
        current_app.config["GOOGLE_CLIENT_ID"],
        {},
        {
            "code": code,
            "client_id": current_app.config["GOOGLE_CLIENT_ID"],
            "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
            "redirect_uri": url_for("auth.google_callback", _external=True),
            "grant_type": "authorization_code",
        },
    )

    token_response = requests.post(token_endpoint, data=body)
    tokens = token_response.json()

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    userinfo_response = requests.get(userinfo_endpoint, headers=headers)
    userinfo = userinfo_response.json()

    user = User.query.filter_by(google_id=userinfo["sub"]).first()

    if not user:
        user = User(
            google_id=userinfo["sub"],
            email=userinfo["email"],
            name=userinfo.get("name"),
            picture=userinfo.get("picture"),
        )
        db.session.add(user)
    else:
        user.picture = userinfo.get("picture")

    db.session.commit()

    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_email"] = user.email
    session["user_picture"] = user.get_avatar()

    return redirect(url_for("main.index"))


@auth_bp.route("/google/logout")
def google_logout():
    session.clear()

    return redirect(url_for("main.index"))


# Spotify OAuth
@auth_bp.route("/spotify/login")
def spotify_login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

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

            session["spotify_username"] = user_info.get(
                "display_name"
            ) or user_info.get("id")

        except:
            pass

    return redirect(url_for("main.index"))


@auth_bp.route("/spotify/logout")
def spotify_logout():
    session.pop("spotify_token_info", None)
    session.pop("spotify_authenticated", None)
    session.pop("spotify_username", None)

    return redirect(url_for("main.index"))
