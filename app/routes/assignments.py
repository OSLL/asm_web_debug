import logging
from urllib.parse import urlencode

import requests
import yaml
from app import app, db
from app.ltiutils import report_outcome_score
from app.models import Assignment, Submission
from flask import abort, make_response, render_template, request
from flask_login import current_user
from markdown import markdown
from sqlalchemy import desc


def check_assignment_access(assignment: Assignment) -> None:
    if not current_user.is_authenticated:
        abort(403, description="Not authenticated")
    if current_user.is_admin or assignment.user_id == current_user.id:
        return
    current_user_assignment = Assignment.query.filter_by(user_id=current_user.id, problem_id=assignment.problem_id).first()
    if current_user_assignment and current_user_assignment.is_instructor:
        return
    abort(403)


def get_assignment(assignment_id) -> Assignment:
    assignment = Assignment.query.get_or_404(assignment_id)
    check_assignment_access(assignment)
    return assignment


@app.route('/assignment/<int:assignment_id>')
def view_assignment(assignment_id):
    assignment = get_assignment(assignment_id)

    checker = assignment.problem.get_checker()
    sample_test = checker.sample_test if checker else ""
    return render_template(
        'pages/ide.html',
        assignment=assignment,
        problem=assignment.problem,
        sample_test=sample_test,
        markdown_statement=markdown(assignment.problem.statement or "")
    )


@app.route("/assignment/<int:assignment_id>/submit", methods=["POST"])
def submit_code(assignment_id):
    assignment = get_assignment(assignment_id)

    api_endpoint = app.config["RUNNER_API"] + "/check"

    result = requests.post(api_endpoint, json={
        "arch": assignment.arch,
        "source_code": assignment.source_code,
        "checker_name": assignment.problem.checker_name,
        "config": yaml.safe_load(assignment.problem.checker_config)
    })

    if result.status_code != 200:
        logging.error("runner api returned invalid response code")
        return {
            "is_correct": False,
            "comment": "Internal server error"
        }

    result = result.json()
    is_correct = result["ok"]

    if not is_correct:
        score = 0
        error_type = result["error_type"]
        if error_type == "DoesNotCompileError":
            error_message = "Compilation error"
        elif error_type == "WrongAnswerError":
            error_message = "Wrong answer"
        elif error_type == "SignalledError":
            error_message = "Unexpected signal received"
        else:
            error_message = error_type
        comment = f"{error_message}: {result['message']}"
    else:
        score = app.config["MAX_GRADE"]
        comment = "Solution accepted"

    if score > assignment.grade:
        assignment.grade = score

    if assignment.lti_assignment_id:
        report_outcome_score(
            assignment.lti_consumer_key,
            assignment.lti_assignment_id,
            assignment.lti_callback_url,
            assignment.grade / app.config["MAX_GRADE"]
        )

    submission = Submission(
        assignment_id=assignment.id,
        source_code=assignment.source_code,
        arch=assignment.arch,
        grade=score,
        comment=comment
    )

    db.session.add(submission)
    db.session.commit()

    return {
        "is_correct": is_correct,
        "submission_grade": score,
        "assignment_grade": assignment.grade,
        "comment": comment
    }


@app.route('/assignment/<int:assignment_id>/save', methods=["POST"])
def save_code(assignment_id):
    assignment = get_assignment(assignment_id)

    source_code = request.form.get("code", "")

    assignment.source_code = source_code
    assignment.arch = assignment.problem.arch
    db.session.commit()

    return {"success_save": True}


@app.route("/assignment/<int:assignment_id>/submissions")
def view_submissions(assignment_id):
    assignment = get_assignment(assignment_id)
    submissions = Submission.query.filter_by(assignment_id=assignment.id).order_by(desc(Submission.submitted_at)).all()
    return render_template("pages/submissions.html", submissions=submissions)


@app.route("/submission/<int:submission_id>/source")
def view_source_code(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    check_assignment_access(submission.assignment)

    response = make_response(submission.source_code, 200)
    response.mimetype = "text/plain"
    return response


@app.route("/assignment/<int:assignment_id>/websocket")
def websocket(assignment_id):
    assignment = get_assignment(assignment_id)

    params = {
        "user_id": str(current_user.id),
        "assignment_id": str(assignment.id),
        "checker_name": assignment.problem.checker_name,
        "arch": assignment.problem.arch
    }

    response = make_response()
    response.headers["X-Accel-Redirect"] = f"/runner_api/websocket?{urlencode(params)}"
    return response
