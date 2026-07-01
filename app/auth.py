"""Single-user password authentication (Version 1).

There is no user table: the app has exactly one user. The password comes from the
NEMORY_PASSWORD environment variable and is hashed once at startup, so only the
hash is ever held in memory. Login state is kept in the signed session cookie.
"""

import functools

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__)


def init_app(app) -> None:
    """Pre-compute the password hash and expose it on the app."""
    app.config["PASSWORD_HASH"] = generate_password_hash(
        app.config["NEMORY_PASSWORD"]
    )


@bp.before_app_request
def load_logged_in_state() -> None:
    """Make ``g.authenticated`` available to every view and template."""
    g.authenticated = session.get("authenticated", False)


def login_required(view):
    """Redirect to the login page for any anonymous request."""

    @functools.wraps(view)
    def wrapped(**kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)

    return wrapped


@bp.route("/login", methods=("GET", "POST"))
def login():
    if session.get("authenticated"):
        return redirect(url_for("main.home"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if check_password_hash(current_app.config["PASSWORD_HASH"], password):
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            return redirect(request.args.get("next") or url_for("main.home"))
        flash("Mot de passe incorrect.")

    return render_template("auth/login.html")


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
