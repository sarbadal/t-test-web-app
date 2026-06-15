from flask import Blueprint, redirect, render_template, url_for, session

bp = Blueprint('readme', __name__)

@bp.route('/readme', methods=['GET'])
def readme() -> str:
    """Alternative route for the home (same as index)."""
    if not session.get("logged_in"):
        return redirect(url_for("login.login"))
    return render_template('readme.html')