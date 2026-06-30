"""End-to-end checks over the main user flows via the Flask test client."""

import pytest

from app import create_app
from config import Config, DEV_PASSWORD, DEV_SECRET_KEY


def test_production_rejects_default_secret(tmp_path):
    class ProdConfig(Config):
        IS_PRODUCTION = True
        SECRET_KEY = DEV_SECRET_KEY  # still the dummy default
        NEMORY_PASSWORD = "a-real-password"
        DATABASE = str(tmp_path / "p.sqlite")

    with pytest.raises(RuntimeError):
        create_app(ProdConfig)


def test_production_rejects_default_password(tmp_path):
    class ProdConfig(Config):
        IS_PRODUCTION = True
        SECRET_KEY = "a-strong-random-key"
        NEMORY_PASSWORD = DEV_PASSWORD  # still the dummy default
        DATABASE = str(tmp_path / "p.sqlite")

    with pytest.raises(RuntimeError):
        create_app(ProdConfig)


def test_production_allows_real_secrets(tmp_path):
    class ProdConfig(Config):
        IS_PRODUCTION = True
        SECRET_KEY = "a-strong-random-key"
        NEMORY_PASSWORD = "a-real-password"
        DATABASE = str(tmp_path / "p.sqlite")

    app = create_app(ProdConfig)
    assert app.config["SECRET_KEY"] == "a-strong-random-key"


def test_login_required_redirects(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_wrong_password_rejected(client):
    resp = client.post("/login", data={"password": "nope"}, follow_redirects=True)
    assert b"Incorrect password" in resp.data


def test_home_loads_when_authenticated(auth_client):
    resp = auth_client.get("/")
    assert resp.status_code == 200
    assert b"Today" in resp.data


def test_full_activity_flow(auth_client):
    # Create an asset.
    resp = auth_client.post(
        "/assets/new", data={"name": "Generator"}, follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Generator" in resp.data

    # Create an overdue activity with a reminder on that asset (asset_id == 1).
    resp = auth_client.post(
        "/activities/new",
        data={
            "asset_id": "1",
            "title": "Oil change",
            "description": "5W30, new filter",
            "activity_date": "2020-01-01",
            "reminder_interval": "6",
            "reminder_unit": "months",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Oil change" in resp.data

    # It should surface on the home page as overdue.
    home = auth_client.get("/")
    assert b"Oil change" in home.data
    assert b"Overdue" in home.data

    # Search finds it by description.
    found = auth_client.get("/search?q=filter")
    assert b"Oil change" in found.data


def test_activity_requires_valid_date(auth_client):
    auth_client.post("/assets/new", data={"name": "House"})
    resp = auth_client.post(
        "/activities/new",
        data={"asset_id": "1", "title": "Roof", "activity_date": "not-a-date"},
        follow_redirects=True,
    )
    assert b"valid activity date" in resp.data
