"""Application factory.

Creates and configures the Flask app, wires the database, authentication, and
route blueprints, and registers a couple of small template helpers.
"""

from datetime import date

from flask import Flask, render_template

from config import Config


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    _check_production_secrets(app)

    # Default the database into the instance folder unless overridden.
    import os

    os.makedirs(app.instance_path, exist_ok=True)
    if not app.config.get("DATABASE"):
        app.config["DATABASE"] = os.path.join(app.instance_path, "nemory.sqlite")

    from app import auth, db

    db.init_app(app)
    auth.init_app(app)

    from app import activities, assets, main

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(assets.bp)
    app.register_blueprint(activities.bp)

    _register_template_helpers(app)
    _register_error_handlers(app)

    return app


def _check_production_secrets(app: Flask) -> None:
    """Refuse to start in production while still using the dummy dev secrets.

    Enabled by NEMORY_ENV=production (see config.py). This turns a silent
    security hole — running a public server with the committed default key or
    password — into a loud startup failure.
    """
    if not app.config.get("IS_PRODUCTION"):
        return

    from config import DEV_PASSWORD, DEV_SECRET_KEY

    insecure = []
    if app.config["SECRET_KEY"] == DEV_SECRET_KEY:
        insecure.append("SECRET_KEY")
    if app.config["NEMORY_PASSWORD"] == DEV_PASSWORD:
        insecure.append("NEMORY_PASSWORD")

    if insecure:
        raise RuntimeError(
            "Refusing to start in production with default "
            f"{' and '.join(insecure)}. Set "
            f"{' and '.join(insecure)} to real secret value(s) via environment "
            "variables (see deploy/pythonanywhere_wsgi.py)."
        )


def _register_template_helpers(app: Flask) -> None:
    @app.template_filter("pretty_date")
    def pretty_date(value) -> str:
        """Render an ISO date string (or date) as e.g. 'Jun 29, 2026'."""
        if not value:
            return ""
        d = value if isinstance(value, date) else date.fromisoformat(str(value))
        return d.strftime("%b %d, %Y")

    @app.template_filter("days_until")
    def days_until(value) -> int | None:
        """Whole days from today to an ISO date (negative = overdue)."""
        if not value:
            return None
        d = value if isinstance(value, date) else date.fromisoformat(str(value))
        return (d - date.today()).days


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404
