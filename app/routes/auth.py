from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from app.core.db.manager import DBManager


bp = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    error = ""
    if form.validate_on_submit():
        user = DBManager.get_user_by_username_and_password(form.username.data, form.password.data)
        if user is not None:
            login_user(user)
            return redirect(url_for("welcome.index"))
        error = "Invalid username or password"
    return render_template("pages/login.html", form=form, error=error)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("welcome.index"))
