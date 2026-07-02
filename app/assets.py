"""Asset routes: list, create, view, rename, delete."""

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

bp = Blueprint("assets", __name__, url_prefix="/assets")


def _parse_asset_form(form):
    """Validate and normalize the asset form.

    Returns ``(values, error)`` where ``values`` is a dict ready for SQL and
    ``error`` is a user-facing message or ``None``.
    """
    name = form.get("name", "").strip()
    if not name:
        return None, "Le nom est obligatoire."

    notes = form.get("notes", "").strip()
    supplier = form.get("supplier", "").strip()
    contact = form.get("contact", "").strip()

    year = None
    year_raw = form.get("year", "").strip()
    if year_raw:
        try:
            year = int(year_raw)
        except ValueError:
            return None, "L'année doit être un nombre entier."
        if not (1900 <= year <= 2100):
            return None, "L'année doit être comprise entre 1900 et 2100."

    return {"name": name, "notes": notes, "supplier": supplier, "contact": contact, "year": year}, None


def get_asset_or_404(asset_id: int):
    asset = (
        get_db()
        .execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
        .fetchone()
    )
    if asset is None:
        abort(404, f"Asset {asset_id} does not exist.")
    return asset


@bp.route("/")
@login_required
def index():
    assets = (
        get_db()
        .execute(
            """
            SELECT a.*, COUNT(act.id) AS activity_count
            FROM assets a
            LEFT JOIN activities act ON act.asset_id = a.id
            GROUP BY a.id
            ORDER BY a.name COLLATE NOCASE
            """
        )
        .fetchall()
    )
    return render_template("assets/index.html", assets=assets)


@bp.route("/<int:asset_id>")
@login_required
def detail(asset_id: int):
    asset = get_asset_or_404(asset_id)
    activities = (
        get_db()
        .execute(
            """
            SELECT act.*, a.name AS asset_name
            FROM activities act
            JOIN assets a ON a.id = act.asset_id
            WHERE act.asset_id = ?
            ORDER BY act.activity_date DESC, act.id DESC
            """,
            (asset_id,),
        )
        .fetchall()
    )
    return render_template(
        "assets/detail.html", asset=asset, activities=activities
    )


@bp.route("/new", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        values, error = _parse_asset_form(request.form)
        if error:
            flash(error)
            return render_template("assets/form.html", asset=request.form)
        db = get_db()
        cur = db.execute(
            """
            INSERT INTO assets (name, notes, supplier, contact, year)
            VALUES (:name, :notes, :supplier, :contact, :year)
            """,
            values,
        )
        db.commit()
        return redirect(url_for("assets.detail", asset_id=cur.lastrowid))
    return render_template("assets/form.html", asset=None)


@bp.route("/<int:asset_id>/edit", methods=("GET", "POST"))
@login_required
def edit(asset_id: int):
    asset = get_asset_or_404(asset_id)
    if request.method == "POST":
        values, error = _parse_asset_form(request.form)
        if error:
            flash(error)
            return render_template("assets/form.html", asset=request.form)
        db = get_db()
        db.execute(
            """
            UPDATE assets SET
                name = :name,
                notes = :notes,
                supplier = :supplier,
                contact = :contact,
                year = :year,
                updated_at = datetime('now')
            WHERE id = :id
            """,
            {**values, "id": asset_id},
        )
        db.commit()
        return redirect(url_for("assets.detail", asset_id=asset_id))
    return render_template("assets/form.html", asset=asset)


@bp.route("/<int:asset_id>/delete", methods=("POST",))
@login_required
def delete(asset_id: int):
    get_asset_or_404(asset_id)
    db = get_db()
    db.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    db.commit()
    flash("Bien supprimé.")
    return redirect(url_for("assets.index"))
