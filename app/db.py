"""SQLite access layer.

Uses the standard-library sqlite3 driver (no ORM) to keep dependencies minimal,
as required by the project philosophy. One connection is created per request and
cached on Flask's ``g``.
"""

import sqlite3
from pathlib import Path

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return the request-scoped database connection, opening it if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None) -> None:
    """Close the connection at the end of the request, if one was opened."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create tables from schema.sql (idempotent)."""
    db = get_db()
    schema = Path(current_app.root_path, "schema.sql").read_text(encoding="utf-8")
    db.executescript(schema)
    db.commit()


@click.command("init-db")
def init_db_command() -> None:
    """flask init-db -> create the database tables."""
    init_db()
    click.echo("Initialized the Nemory database.")


def init_app(app) -> None:
    """Wire database lifecycle hooks and CLI commands into the app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
