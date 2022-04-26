from app import app, db
from app.models import Problem, ToolConsumer, User

import secrets
import json
import functools
from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import InputRequired
from markdown import markdown

from runner.checkerlib import Checker


def admin_required(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return wrapped


@app.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("pages/admin/users.html", users=users)


@app.route("/admin/lms")
@admin_required
def admin_lms():
    tool_consumer = ToolConsumer.query.filter_by(in_use=False).first()
    if not tool_consumer:
        tool_consumer = ToolConsumer(
            consumer_key=secrets.token_hex(8),
            consumer_secret=secrets.token_urlsafe(),
            in_use=False
        )
        db.session.add(tool_consumer)
        db.session.commit()

    proto = request.headers.get("X-Forwarded-Proto", "http")
    tool_url = f"{proto}://{request.host}/lti"

    tool_consumers = ToolConsumer.query.filter_by(in_use=True).all()

    return render_template("pages/admin/lms.html",
        tool_url=tool_url,
        consumer_key=tool_consumer.consumer_key,
        consumer_secret=tool_consumer.consumer_secret,
        tool_consumers=tool_consumers
    )


@app.route("/admin/problems")
@admin_required
def admin_problems():
    problems = Problem.query.all()
    return render_template("pages/admin/problems.html", problems=problems)


class ProblemForm(FlaskForm):
    title = StringField(validators=[InputRequired()])
    course_name = StringField()
    statement = TextAreaField()
    checker_name = SelectField(choices=list(Checker._all_checkers))
    checker_config = TextAreaField()


@app.route("/admin/problem/<int:problem_id>", methods=["GET", "POST"])
@admin_required
def admin_problem_edit(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    form = ProblemForm(obj=problem)

    if form.validate_on_submit():
        form.populate_obj(problem)
        db.session.commit()
        return redirect(url_for("admin_problems"))

    checker_docs = {}
    for name, checker in Checker._all_checkers.items():
        html = ""
        if checker.__doc__:
            html = markdown(checker.__doc__)
        checker_docs[name] = html

    return render_template("pages/admin/problem_edit.html", form=form, checker_docs_json=json.dumps(checker_docs))
