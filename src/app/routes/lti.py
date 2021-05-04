from flask import Blueprint, abort, request, make_response, render_template, url_for, redirect 

from app.core.db.manager import DBManager

from app.core.lti_core.lti_validator import LTIRequestValidator
from app.core.lti_core.lti_utils import extract_passback_params
from app.core.lti_core.check_request import check_request
from app.core.db.desc import Consumers, User

from flask import current_app as app
from uuid import uuid4

import flask_login
from flask_security.datastore import UserDatastore

lti_bp = Blueprint('lti', __name__ )
bp = lti_bp

@bp.route('/lti', methods=['POST'])
def lti_route():
    if check_request(request):
        temporary_user_params = request.form
        user_id = temporary_user_params.get('user_id')
        username = temporary_user_params.get('ext_user_username')
        params_for_passback = extract_passback_params(temporary_user_params)

        if DBManager.get_user(user_id) == None:
            app.user_datastore.create_user(_id = user_id, username = username, tasks = {str(uuid4()): {'passback': params_for_passback }})
            flask_login.login_user(User.objects.get(_id=user_id))
        else:
            flask_login.login_user(User.objects.get(_id=user_id))

        return redirect('/')
    else:
        abort(403)