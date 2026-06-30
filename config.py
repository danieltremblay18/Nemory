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


class Config:
    """Base configuration shared by every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")

    # Plain-text single-user password from the environment. It is hashed once at
    # startup (see auth.py) so the hash never needs to be stored anywhere.
    NEMORY_PASSWORD = os.environ.get("NEMORY_PASSWORD", "nemory")

    # SQLite database lives in the Flask instance folder by default.
    DATABASE = os.environ.get("DATABASE")

    # How far ahead the home page looks for "upcoming" reminders.
    UPCOMING_WINDOW_DAYS = 30

    # Keep the session reasonably long-lived for a personal app.
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30  # 30 days, in seconds
