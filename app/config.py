import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    "Configuration Shared Accross The Application"

    # Flask
    PORT = int(os.getenv("PORT", 8888))
    SECRET_KEY = os.getenv("SECRET_KEY", "SuperDuperSecretKey")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///roastmytaste.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    # Spotify API
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv(
        "SPOTIFY_REDIRECT_URI", "http://localhost:5000/callback"
    )
    SPOTIFY_SCOPE = os.getenv(
        "SPOTIFY_SCOPE",
        "user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private",
    )

    # Valorant API
    HENRIK_API_KEY = os.getenv("HENRIK_API_KEY")

    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
