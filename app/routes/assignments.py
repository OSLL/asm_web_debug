from app import app, db

import json
import logging
from flask import make_response, render_template, request, abort
from flask_login import current_user
import requests
from urllib.parse import urlencode
from sqlalchemy import desc

from app.core.lti_core.lti_utils import report_outcome_score
from app.core.utils.hex import hexdump
from app.models import Assignment, Submission


def check_assignment_access(assignment: Assignment) -> None:
    if not current_user.is_authenticated:
        abort(403, description="Not authenticated")
    if current_user.is_admin:
        return
    if assignment.user_id != current_user.id:
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
        sample_test=sample_test
    )


@app.route("/assignment/<int:assignment_id>/submit", methods=["POST"])
def submit_code(assignment_id):
    assignment = get_assignment(assignment_id)

    api_endpoint = app.config["RUNNER_API"] + "/check"

    result = requests.post(api_endpoint, json={
        "arch": assignment.arch,
        "source_code": assignment.source_code,
        "checker_name": assignment.problem.checker_name,
        "config": json.loads(assignment.problem.checker_config_json)
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
    arch = request.form.get("arch", "x86_64")

    if arch not in app.config["ARCHS"]:
        abort(403)

    assignment.source_code = source_code
    assignment.arch = arch
    db.session.commit()

    return {"success_save": True}


@app.route('/assignment/<int:assignment_id>/hexview', methods=["GET", "POST"])
def hexview(assignment_id):
    assignment = get_assignment(assignment_id)
    return render_template('pages/hexview.html', result=hexdump(assignment.source_code))


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
        "checker_name": assignment.problem.checker_name
    }

    response = make_response()
    response.headers["X-Accel-Redirect"] = f"/runner_api/websocket?{urlencode(params)}"
    return response
