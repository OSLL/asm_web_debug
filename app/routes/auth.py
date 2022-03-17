from app import app, login_manager

from flask import redirect, render_template, url_for
from flask_login import login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from app.core.db.manager import DBManager


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


@login_manager.user_loader
def load_user(user_id):
    return DBManager.get_user(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    error = ""
    if form.validate_on_submit():
        user = DBManager.get_user_by_username_and_password(form.username.data, form.password.data)
        if user is not None:
            login_user(user)
            return redirect(url_for("index"))
        error = "Invalid username or password"
    return render_template("pages/login.html", form=form, error=error)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
