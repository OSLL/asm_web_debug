from app.core.lti_core.lti_validator import LTIRequestValidator
from lti.contrib.flask import FlaskToolProvider


def check_request(request):
    provider = FlaskToolProvider.from_flask_request(
        secret=request.args.get("oauth_consumer_key", None), request=request
    )

    return provider.is_valid_request(LTIRequestValidator())
