"""Activity routes: create, view, edit, delete.

An activity records something that happened to an asset and, optionally, when it
should happen again. The next reminder date is always derived — never entered by
hand — via the reminders service.
"""

from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db
from app.services.reminders import VALID_UNITS, compute_next_reminder_date

bp = Blueprint("activities", __name__, url_prefix="/activities")

# Seed suggestions shown before the journal has built up its own history. Once an
# activity is saved, its title joins the list automatically (see _title_suggestions).
PREDEFINED_TITLES = (
    "Changement d'huile",
    "Inspection",
    "Remplacement de filtre",
    "Nettoyage",
    "Vérification de la batterie",
    "Hivernage",
    "Entretien",
)


def get_activity_or_404(activity_id: int):
    activity = (
        get_db()
        .execute(
            """
            SELECT act.*, a.name AS asset_name
            FROM activities act
            JOIN assets a ON a.id = act.asset_id
            WHERE act.id = ?
            """,
            (activity_id,),
        )
        .fetchone()
    )
    if activity is None:
        abort(404, f"Activity {activity_id} does not exist.")
    return activity


def _all_assets():
    return (
        get_db()
        .execute("SELECT id, name FROM assets ORDER BY name COLLATE NOCASE")
        .fetchall()
    )


def _title_suggestions():
    """Distinct titles already used, merged with the predefined seeds.

    This is what makes a new title 'stick': once saved, it shows up here for
    every future activity. Returns a case-insensitively sorted list of strings.
    """
    used = [
        row["title"]
        for row in get_db()
        .execute("SELECT DISTINCT title FROM activities")
        .fetchall()
    ]
    seen = {title.casefold() for title in used}
    extras = [t for t in PREDEFINED_TITLES if t.casefold() not in seen]
    return sorted(used + extras, key=str.casefold)


def _parse_form(form):
    """Validate and normalize the activity form.

    Returns ``(values, error)`` where ``values`` is a dict ready for SQL and
    ``error`` is a user-facing message or ``None``.
    """
    asset_id = form.get("asset_id", type=int)
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    activity_date_raw = form.get("activity_date", "").strip()
    interval_raw = form.get("reminder_interval", "").strip()
    unit = form.get("reminder_unit", "").strip() or None

    if not asset_id:
        return None, "Veuillez choisir un bien."
    if not title:
        return None, "Le titre est obligatoire."
    try:
        activity_date = date.fromisoformat(activity_date_raw)
    except ValueError:
        return None, "Une date d'activité valide est requise."

    interval = None
    if interval_raw:
        try:
            interval = int(interval_raw)
        except ValueError:
            return None, "L'intervalle de rappel doit être un nombre entier."
        if interval <= 0:
            return None, "L'intervalle de rappel doit être supérieur à zéro."
        if unit not in VALID_UNITS:
            return None, "Veuillez choisir une unité de rappel."
    else:
        unit = None  # no interval -> no reminder

    next_reminder = compute_next_reminder_date(activity_date, interval, unit)

    return (
        {
            "asset_id": asset_id,
            "title": title,
            "description": description,
            "activity_date": activity_date.isoformat(),
            "reminder_interval": interval,
            "reminder_unit": unit,
            "next_reminder_date": next_reminder.isoformat()
            if next_reminder
            else None,
        },
        None,
    )


@bp.route("/new", methods=("GET", "POST"))
@login_required
def create():
    assets = _all_assets()
    if not assets:
        flash("Créez d'abord un bien.")
        return redirect(url_for("assets.create"))

    if request.method == "POST":
        values, error = _parse_form(request.form)
        if error:
            flash(error)
            return render_template(
                "activities/form.html",
                activity=request.form,
                assets=assets,
                units=VALID_UNITS,
                title_suggestions=_title_suggestions(),
            )
        db = get_db()
        cur = db.execute(
            """
            INSERT INTO activities
                (asset_id, title, description, activity_date,
                 reminder_interval, reminder_unit, next_reminder_date)
            VALUES (:asset_id, :title, :description, :activity_date,
                    :reminder_interval, :reminder_unit, :next_reminder_date)
            """,
            values,
        )
        db.commit()
        flash("Activité enregistrée.")
        return redirect(url_for("activities.detail", activity_id=cur.lastrowid))

    # Pre-select an asset and default the date to today for a fast (<30s) entry.
    prefill = {
        "asset_id": request.args.get("asset_id", type=int),
        "activity_date": date.today().isoformat(),
    }
    return render_template(
        "activities/form.html",
        activity=prefill,
        assets=assets,
        units=VALID_UNITS,
        title_suggestions=_title_suggestions(),
    )


@bp.route("/<int:activity_id>")
@login_required
def detail(activity_id: int):
    activity = get_activity_or_404(activity_id)
    return render_template("activities/detail.html", activity=activity)


@bp.route("/<int:activity_id>/edit", methods=("GET", "POST"))
@login_required
def edit(activity_id: int):
    activity = get_activity_or_404(activity_id)
    assets = _all_assets()

    if request.method == "POST":
        values, error = _parse_form(request.form)
        if error:
            flash(error)
            return render_template(
                "activities/form.html",
                activity=request.form,
                assets=assets,
                units=VALID_UNITS,
                title_suggestions=_title_suggestions(),
            )
        db = get_db()
        db.execute(
            """
            UPDATE activities SET
                asset_id = :asset_id,
                title = :title,
                description = :description,
                activity_date = :activity_date,
                reminder_interval = :reminder_interval,
                reminder_unit = :reminder_unit,
                next_reminder_date = :next_reminder_date,
                updated_at = datetime('now')
            WHERE id = :id
            """,
            {**values, "id": activity_id},
        )
        db.commit()
        flash("Activité mise à jour.")
        return redirect(url_for("activities.detail", activity_id=activity_id))

    return render_template(
        "activities/form.html",
        activity=activity,
        assets=assets,
        units=VALID_UNITS,
        title_suggestions=_title_suggestions(),
    )


@bp.route("/<int:activity_id>/delete", methods=("POST",))
@login_required
def delete(activity_id: int):
    activity = get_activity_or_404(activity_id)
    db = get_db()
    db.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
    db.commit()
    flash("Activité supprimée.")
    return redirect(url_for("assets.detail", asset_id=activity["asset_id"]))
