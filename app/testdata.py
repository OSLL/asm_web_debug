from app import app, db
from app.models import Assignment, Problem, User

from flask_migrate import upgrade

def populate():
    app.config["WTF_CSRF_ENABLED"] = False

    upgrade()

    user = User()
    user.username = "admin"
    user.set_password("admin")
    user.is_admin = True
    user.full_name = "Admin User"
    user.email = "admin@localhost"

    db.session.add(user)
    db.session.commit()

    problem = Problem()
    problem.title = "strlen"
    problem.statement = "find the length of the string!"
    problem.checker_name = "StringLengthChecker"
    problem.checker_config_json = "{}"

    db.session.add(problem)
    db.session.commit()

    assignment = Assignment()
    assignment.problem_id = problem.id
    assignment.user_id = user.id
    assignment.lti_assignment_id = "<unknown>"
    assignment.lti_callback_url = "<unknown>"
    assignment.lti_consumer_key = "<unknown>"

    db.session.add(assignment)
    db.session.commit()
