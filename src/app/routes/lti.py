from flask import Blueprint, abort, request, make_response, render_template, url_for, redirect 

from app.core.db.manager import DBManager

from lti.contrib.flask import FlaskToolProvider
from lti.tool_provider import ToolProvider

from app.core.utils.lti_validator import LTIRequestValidator
from app.core.db.desc import Consumers

lti_bp = Blueprint('lti', __name__, url_prefix='/lti')
bp = lti_bp

def check_request(request_info):
    """
    :request_info: dict - must include ('headers', 'data', 'secret', 'url') 
    """
    #provider = FlaskToolProvider.from_flask_request(
    #    secret = request.args.get('oauth_consumer_key', None),
    #    request = request
    #)
    provider = ToolProvider.from_unpacked_request(
        secret=request_info.get('secret', None),
        params=request_info.get('data', {}),
        headers=request_info.get('headers', {}),
        url=request_info.get('url', '')
        )

    return provider.is_valid_request(LTIRequestValidator())

@bp.route('/', methods=['POST'], strict_slashes=False)
def lti_route():
    params = request.form
    consumer_key = params.get('oauth_consumer_key', '')
    consumer_secret = DBManager.get_secret(consumer_key)
    request_info = dict( 
        headers=dict(request.headers),
        data=params,
        url=request.url,
        secret=consumer_secret
    )

    if check_request(request_info):
        return redirect('/')

    else:
        #403
        return request.form 