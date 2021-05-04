from flask import Blueprint, abort, request, make_response, render_template, url_for, redirect 

from app.core.db.manager import DBManager

from app.core.lti_core.lti_validator import LTIRequestValidator
from app.core.lti_core.lti_utils import extract_passback_params, get_custom_params
from app.core.lti_core.check_request import check_request
from app.core.db.desc import Consumers, User

from flask import current_app as app
import flask_login
from flask_security.datastore import UserDatastore
from uuid import uuid4


lti_bp = Blueprint('lti', __name__ )
bp = lti_bp


@bp.route('/lti', methods=['POST'])
def lti_route():
    app.logger.debug('checking')
    if check_request(request):
        temporary_user_params = request.form
        username = temporary_user_params.get('ext_user_username')
        user_id = f"{username}_{temporary_user_params.get('tool_consumer_instance_guid', '')}"
        params_for_passback = extract_passback_params(temporary_user_params)
        custom_params = get_custom_params(temporary_user_params)

        task_id = custom_params.get('task_id',
            f"{temporary_user_params.get('user_id')}-{temporary_user_params.get('resource_link_id')}")
        #task_id = str(uuid4())  # change in future

        user = DBManager.get_user(user_id)
        if user:
            user.tasks[task_id] = { 'passback': params_for_passback }
            user.save()
        else:
            app.user_datastore.create_user(_id=user_id, username=username,
                tasks={ task_id: {'passback': params_for_passback} })

        flask_login.login_user(User.objects.get(_id=user_id), remember=True)
        app.logger.debug(flask_login.current_user.username)
        return redirect(url_for('index.index_id', code_id=task_id))
    else:
        abort(404)