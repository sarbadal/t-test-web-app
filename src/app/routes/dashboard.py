from flask import Blueprint, redirect, url_for, session

from . import index

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
def dashboard() -> str:
    """Alternative route for the dashboard (same as index)."""
    if not session.get("logged_in"):
        return redirect(url_for("login.login"))
    return index.home()