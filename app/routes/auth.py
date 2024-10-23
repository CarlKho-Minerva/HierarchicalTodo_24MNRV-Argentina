"""Authentication routes for the Medieval Todo List application."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from typing import Union
from app.models.user import User
from app import db

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, redirect]:
    """
    Handle user registration.

    Returns:
        Union[str, redirect]: Either the registration page or a redirect
        to the login page on successful registration
    """
    if current_user.is_authenticated:
        return redirect(url_for("todos.index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([username, email, password]):
            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, redirect]:
    """
    Handle user login.

    Returns:
        Union[str, redirect]: Either the login page or a redirect
        to the next page on successful login
    """
    if current_user.is_authenticated:
        return redirect(url_for("todos.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        if not all([username, password]):
            flash("Please fill in all fields.", "error")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        login_user(user, remember=remember)
        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("todos.index")
        return redirect(next_page)

    return render_template("login.html")


@bp.route("/logout")
def logout() -> redirect:
    """
    Handle user logout.

    Returns:
        redirect: Redirect to the login page
    """
    logout_user()
    return redirect(url_for("auth.login"))
