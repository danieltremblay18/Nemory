import tempfile
from pathlib import Path

import pytest

from app import create_app
from app.db import init_db
from config import Config


@pytest.fixture
def app():
    tmp = tempfile.TemporaryDirectory()
    db_path = Path(tmp.name, "test.sqlite")

    class TestConfig(Config):
        TESTING = True
        SECRET_KEY = "test"
        NEMORY_PASSWORD = "secret"
        DATABASE = str(db_path)
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)
    with app.app_context():
        init_db()

    yield app
    tmp.cleanup()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app):
    """A client that has already logged in."""
    client = app.test_client()
    client.post("/login", data={"password": "secret"})
    return client
