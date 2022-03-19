from app import app, db

from flask import abort, request, url_for, redirect
from itsdangerous import json
from app.models import Assignment, User

from app.core.lti_core.check_request import check_request

import flask_login


@app.route('/lti', methods=['POST'])
def lti_route():
    if not check_request(request):
        abort(403)

    consumer_key = request.form.get("oauth_consumer_key")
    lti_assignment_id = request.form.get("lis_result_sourcedid")
    lti_tool_consumer_guid = request.form.get("tool_consumer_instance_guid")
    lti_callback_url = request.form.get("lis_outcome_service_url")
    lti_user_id = request.form.get("user_id")
    roles = request.form.get("roles", "").split(",")
    email = request.form.get("lis_person_contact_email_primary")
    full_name = request.form.get("lis_person_name_full")

    try:
        problem_id = int(request.form.get("custom_problem_id", "").strip())
    except ValueError:
        return "Invalid custom_problem_id param, should be an integer", 400

    user = User.query.filter_by(lti_tool_consumer_guid=lti_tool_consumer_guid, lti_user_id=lti_user_id).first()
    if not user:
        user = User(
            lti_tool_consumer_guid=lti_tool_consumer_guid,
            lti_user_id=lti_user_id
        )
        db.session.add(user)

    user.is_admin = "Instructor" in roles
    user.email = email
    user.full_name = full_name

    db.session.commit()

    flask_login.login_user(user, remember=True)

    assignment = Assignment.query.filter_by(user_id=user.id, problem_id=problem_id).first()
    if not assignment:
        assignment = Assignment(
            user_id=user.id,
            problem_id=problem_id
        )
        db.session.add(assignment)

    assignment.lti_consumer_key = consumer_key
    assignment.lti_assignment_id = lti_assignment_id
    assignment.lti_callback_url = lti_callback_url

    db.session.commit()

    return redirect(url_for("view_assignment", assignment_id=assignment.id))
