"""Application configuration.

Values come from environment variables (loaded from a local .env in development
via python-dotenv). Keep this module free of any Flask import so it stays trivial
to test and reason about.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Dummy defaults — safe to commit, used only for zero-setup local development.
# The production guard in create_app() refuses to start if these are still in use
# on a server (NEMORY_ENV=production). They are NOT secret.
DEV_SECRET_KEY = "dev-only-insecure-key"
DEV_PASSWORD = "nemory"


class Config:
    """Base configuration shared by every environment."""

    # The defaults below let the app run locally with zero setup. In production
    # (e.g. PythonAnywhere) ALWAYS override SECRET_KEY and NEMORY_PASSWORD via
    # environment variables — never rely on these defaults on a public server.
    SECRET_KEY = os.environ.get("SECRET_KEY", DEV_SECRET_KEY)

    # Plain-text single-user password from the environment. It is hashed once at
    # startup (see auth.py) so the hash never needs to be stored anywhere.
    NEMORY_PASSWORD = os.environ.get("NEMORY_PASSWORD", DEV_PASSWORD)

    # Set NEMORY_ENV=production on a real server to enable the secret-safety guard.
    IS_PRODUCTION = os.environ.get("NEMORY_ENV", "").lower() == "production"

    # SQLite database lives in the Flask instance folder by default.
    DATABASE = os.environ.get("DATABASE")

    # How far ahead the home page looks for "upcoming" reminders.
    UPCOMING_WINDOW_DAYS = 30

    # Keep the session reasonably long-lived for a personal app.
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30  # 30 days, in seconds
