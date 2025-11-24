from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("spotify_token"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return wrapper
