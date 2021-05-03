from flask import Blueprint, abort, request, make_response, render_template, url_for, redirect 

from app.core.db.manager import DBManager

from lti.contrib.flask import FlaskToolProvider

from app.core.utils.lti_validator import LTIRequestValidator
from app.core.db.desc import Consumers, User

from flask import current_app as app

import flask_login
from flask_security.datastore import UserDatastore

lti_bp = Blueprint('lti', __name__ )
bp = lti_bp

def check_request(request):
    provider = FlaskToolProvider.from_flask_request(
        secret = request.args.get('oauth_consumer_key', None),
        request = request
    )

    return provider.is_valid_request(LTIRequestValidator())

@bp.route('/lti', methods=['POST'])
def lti_route():
    if check_request(request):
        temporary_user_params = request.form
        user_id = temporary_user_params.get('user_id')
        username = temporary_user_params.get('ext_user_username')
        if DBManager.get_user(user_id) == None:
            app.user_datastore.create_user(_id = user_id, username = username)
            flask_login.login_user(User.objects.get(_id=user_id))
        else:
            flask_login.login_user(User.objects.get(_id=user_id))
        return redirect('/')

    else:
        abort(403)