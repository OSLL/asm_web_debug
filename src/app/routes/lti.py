from flask import Blueprint, abort, request, make_response, render_template, url_for, redirect 

from app.core.db.manager import DBManager

from lti.contrib.flask import FlaskToolProvider

from app.core.utils.lti_validator import LTIRequestValidator
from app.core.db.desc import Consumers

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
        return redirect('/')

    else:
        abort(403)