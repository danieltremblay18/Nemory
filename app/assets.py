"""Asset routes: list, create, view, rename, delete.

An asset is intentionally just a name (see the project philosophy: no serial
number, purchase date, price, or accounting).
"""

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
        name = request.form.get("name", "").strip()
        if not name:
            flash("Le nom est obligatoire.")
            return render_template("assets/form.html", asset=None)
        db = get_db()
        cur = db.execute("INSERT INTO assets (name) VALUES (?)", (name,))
        db.commit()
        return redirect(url_for("assets.detail", asset_id=cur.lastrowid))
    return render_template("assets/form.html", asset=None)


@bp.route("/<int:asset_id>/edit", methods=("GET", "POST"))
@login_required
def edit(asset_id: int):
    asset = get_asset_or_404(asset_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Le nom est obligatoire.")
            return render_template("assets/form.html", asset=asset)
        db = get_db()
        db.execute(
            "UPDATE assets SET name = ?, updated_at = datetime('now') WHERE id = ?",
            (name, asset_id),
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
