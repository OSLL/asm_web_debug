from app import app, db, csrf

from flask import abort, request, url_for, redirect
from flask_login import current_user, login_user
from app.models import Assignment, Problem, ToolConsumer, User

from app.ltiutils import check_lti_request


@app.route('/lti', methods=['POST'])
@csrf.exempt # oauth messages are signed and nonced, no need for CSRF
def lti_route():
    consumer_key = request.form.get("oauth_consumer_key", "")

    tool_consumer = ToolConsumer.query.filter_by(consumer_key=consumer_key).first()
    if not tool_consumer:
        return "Invalid consumer_key", 400

    if not check_lti_request(tool_consumer):
        abort(403)

    lti_assignment_id = request.form.get("lis_result_sourcedid")
    lti_tool_consumer_guid = request.form.get("tool_consumer_instance_guid")
    lti_tool_consumer_name = request.form.get("tool_consumer_instance_name")
    lti_callback_url = request.form.get("lis_outcome_service_url")
    lti_user_id = request.form.get("user_id")
    roles = request.form.get("roles", "").split(",")
    email = request.form.get("lis_person_contact_email_primary")
    full_name = request.form.get("lis_person_name_full")
    resource_link_id = request.form.get("resource_link_id")
    resource_link_title = request.form.get("resource_link_title")
    resource_link_description = request.form.get("resource_link_description")
    context_title = request.form.get("context_title")

    tool_consumer.instance_id = lti_tool_consumer_guid
    tool_consumer.instance_name = lti_tool_consumer_name
    tool_consumer.in_use = True

    user = User.query.filter_by(tool_consumer_id=tool_consumer.id, lti_user_id=lti_user_id).first()
    if not user:
        user = User(
            tool_consumer_id=tool_consumer.id,
            lti_user_id=lti_user_id
        )
        db.session.add(user)

    if current_user.is_admin:
        user.is_admin = True

    user.email = email
    user.full_name = full_name

    db.session.commit()

    login_user(user, remember=True)

    problem = Problem.query.filter_by(tool_consumer_id=tool_consumer.id, resource_link_id=resource_link_id).first()
    if not problem:
        problem = Problem(
            title=resource_link_title,
            course_name=context_title,
            statement=resource_link_description or "",
            checker_name=None,
            tool_consumer_id=tool_consumer.id,
            resource_link_id=resource_link_id
        )
        db.session.add(problem)
        db.session.commit()

    assignment = Assignment.query.filter_by(user_id=user.id, problem_id=problem.id).first()
    if not assignment:
        assignment = Assignment(
            user_id=user.id,
            problem_id=problem.id
        )
        db.session.add(assignment)

    assignment.is_instructor = "Instructor" in roles

    assignment.lti_consumer_key = consumer_key
    assignment.lti_assignment_id = lti_assignment_id
    assignment.lti_callback_url = lti_callback_url

    db.session.commit()

    return redirect(url_for("view_assignment", assignment_id=assignment.id))
