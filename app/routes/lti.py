from app import app

from flask import abort, request, make_response, render_template, url_for, redirect
from itsdangerous import json

from app.core.db.manager import DBManager

from app.core.lti_core.lti_validator import LTIRequestValidator
from app.core.lti_core.lti_utils import extract_passback_params, get_custom_params, get_role
from app.core.lti_core.check_request import check_request
from app.core.db.desc import Code, Consumers, User

import flask_login


@app.route('/lti', methods=['POST'])
def lti_route():
    if check_request(request):
        temporary_user_params = request.form
        username = temporary_user_params.get('ext_user_username')
        user_id = f"{username}_{temporary_user_params.get('tool_consumer_instance_guid', '')}"
        params_for_passback = extract_passback_params(temporary_user_params)
        custom_params = get_custom_params(temporary_user_params)
        role = get_role(temporary_user_params)

        problem_id = custom_params.get("problem_id", "").strip()
        code_id = f"{user_id}--{problem_id}"

        user = DBManager.get_user(user_id)

        if not user:
            user = User(_id=user_id, username=username)
        user.is_admin = role == "teacher"
        user.save()

        flask_login.login_user(User.objects.get(_id=user_id), remember=True)

        code = DBManager.get_code(code_id)
        if not code:
            code = Code(_id=code_id, owner=user)
        code.problem = DBManager.get_problem(problem_id)
        code.passback_params = json.dumps(params_for_passback)
        code.save()

        return redirect(url_for('codes.index_id', code_id=code_id))
    else:
        abort(404)
