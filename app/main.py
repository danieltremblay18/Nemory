"""Home and search routes.

The home page deliberately shows only three things (per the spec): overdue
reminders, upcoming reminders within the configured window, and recent activities.
"""

from datetime import date, timedelta

from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    send_from_directory,
)

from app.auth import login_required
from app.db import get_db

bp = Blueprint("main", __name__)


@bp.route("/sw.js")
def service_worker():
    """Serve the service worker from the root so its scope covers the whole app."""
    response = send_from_directory(current_app.static_folder, "sw.js")
    response.headers["Cache-Control"] = "no-cache"
    return response


# Shared SELECT so overdue/upcoming/recent rows all expose the asset name.
_ACTIVITY_SELECT = """
    SELECT act.*, a.name AS asset_name
    FROM activities act
    JOIN assets a ON a.id = act.asset_id
"""


@bp.route("/")
@login_required
def home():
    db = get_db()
    today = date.today().isoformat()
    horizon = (
        date.today()
        + timedelta(days=current_app.config["UPCOMING_WINDOW_DAYS"])
    ).isoformat()

    overdue = db.execute(
        _ACTIVITY_SELECT
        + """
        WHERE act.next_reminder_date IS NOT NULL AND act.next_reminder_date < ?
        ORDER BY act.next_reminder_date ASC
        """,
        (today,),
    ).fetchall()

    upcoming = db.execute(
        _ACTIVITY_SELECT
        + """
        WHERE act.next_reminder_date IS NOT NULL
          AND act.next_reminder_date >= ?
          AND act.next_reminder_date <= ?
        ORDER BY act.next_reminder_date ASC
        """,
        (today, horizon),
    ).fetchall()

    recent = db.execute(
        _ACTIVITY_SELECT
        + " ORDER BY act.activity_date DESC, act.id DESC LIMIT 10"
    ).fetchall()

    return render_template(
        "home.html",
        overdue=overdue,
        upcoming=upcoming,
        recent=recent,
        today=date.today(),
    )


@bp.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        like = f"%{query}%"
        results = (
            get_db()
            .execute(
                _ACTIVITY_SELECT
                + """
                WHERE a.name LIKE ? COLLATE NOCASE
                   OR act.title LIKE ? COLLATE NOCASE
                   OR act.description LIKE ? COLLATE NOCASE
                ORDER BY act.activity_date DESC, act.id DESC
                """,
                (like, like, like),
            )
            .fetchall()
        )
    return render_template("search.html", query=query, results=results)
