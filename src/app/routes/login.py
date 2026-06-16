import secrets

from flask import Blueprint, current_app, render_template, request, session, redirect, url_for

from ..services import UserService

bp = Blueprint("login", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_mode = request.form.get("login_mode", "password")

        if login_mode == "guest":
            guest_username = "guest"
            user = UserService.get_user_by_username(guest_username)
            if not user:
                try:
                    user = UserService.create_user(
                        username=guest_username,
                        password=secrets.token_urlsafe(24),
                        is_admin=False,
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    current_app.logger.warning("Guest user creation race or failure: %s", exc)
                    user = UserService.get_user_by_username(guest_username)

            if user and user.is_active:
                session["logged_in"] = True
                session["user_id"] = user.id
                session["username"] = user.username
                session["is_admin"] = user.is_admin
                return redirect(url_for("home.home"))

            return render_template("password_incorrect.html")

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