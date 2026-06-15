from flask import Blueprint, render_template, request, session, redirect, url_for

from ..services import UserService

bp = Blueprint("login", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            user = UserService.authenticate_user(username, password)
            if user:
                session["logged_in"] = True
                session["user_id"] = user.id
                session["username"] = user.username
                session["is_admin"] = user.is_admin
                return redirect(url_for("home.home"))

        return render_template("password_incorrect.html")
    return render_template("password_form.html")