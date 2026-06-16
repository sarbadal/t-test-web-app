from flask import Blueprint, redirect, render_template, url_for, session

bp = Blueprint('home', __name__)

@bp.route('/')
def home() -> str:
    """Alternative route for the home (same as index)."""
    if not session.get("logged_in"):
        return redirect(url_for("login.login"))
    return render_template('dashboard.html', username=session.get("username"))