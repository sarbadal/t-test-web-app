from flask import Blueprint, redirect, session, url_for
from datetime import datetime

bp = Blueprint('make_session', __name__)


@bp.before_request
def make_session():
    session.permanent = True
    session.modified = True

    now = datetime.now()
    last_activity = session.get("last_activity")

    if last_activity:
        last_activity = datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")
        if now - last_activity > bp.permanent_session_lifetime:
            session.clear()
            return redirect(url_for("login.login")) # redirect to login page

    session["last_activity"] = now.strftime("%Y-%m-%d %H:%M:%S")