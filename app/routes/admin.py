from app import app, db
from app.models import Assignment, Problem, ToolConsumer, User, DebugSession

import secrets
import json
import functools
from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import InputRequired
from markdown import markdown
from sqlalchemy.orm import joinedload

from runner.checkerlib import Checker


def admin_required(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return wrapped


def check_problem_access(problem: Problem) -> None:
    if not current_user.is_authenticated:
        abort(403)
    if current_user.is_admin:
        return
    assignment = Assignment.query.filter_by(problem_id=problem.id, user_id=current_user.id).first()
    if not assignment or not assignment.is_instructor:
        abort(403)


@app.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("pages/admin/users.html", users=users)


@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_users"))


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
def admin_problem_edit(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    check_problem_access(problem)
    form = ProblemForm(obj=problem)

    if form.validate_on_submit():
        form.populate_obj(problem)
        db.session.commit()
        return redirect(request.args.get("next", url_for("admin_problems")))

    checker_docs = {}
    for name, checker in Checker._all_checkers.items():
        html = ""
        if checker.__doc__:
            html = markdown(checker.__doc__)
        checker_docs[name] = html

    return render_template("pages/admin/problem_edit.html", form=form, checker_docs_json=json.dumps(checker_docs), problem=problem)


@app.route("/admin/problem/<int:problem_id>/submissions")
def admin_problem_submissions(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    check_problem_access(problem)
    assignments = Assignment.query \
        .filter_by(problem_id=problem.id) \
        .options(joinedload(Assignment.user)) \
        .all()
    return render_template("pages/admin/problem_submissions.html", assignments=assignments, problem=problem)


@app.route("/admin/problem/<int:problem_id>/delete", methods=["POST"])
@admin_required
def admin_problem_delete(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    db.session.delete(problem)
    db.session.commit()
    return redirect(url_for("admin_problems"))


@app.route("/admin/debug_sessions")
@admin_required
def admin_debug_sessions():
    debug_sessions = DebugSession.query \
        .options(joinedload(DebugSession.user)) \
        .all()
    return render_template("pages/admin/debug_sessions.html", debug_sessions=debug_sessions)
