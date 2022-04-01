from app import app, login_manager

from flask import redirect, render_template, url_for, abort
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    return User.query.get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    error = ""
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("index"))
        error = "Invalid username or password"
    return render_template("pages/login.html", form=form, error=error)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/require_admin")
def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)
    return "ok"
