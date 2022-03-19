from app import app

from app.core.lti_core.lti_validator import LTIRequestValidator
from lti.contrib.flask import FlaskToolProvider


def check_request(request):
    consumer_key = request.values.get('oauth_consumer_key', None)
    consumer_secret = app.config["LTI_CONSUMERS"].get(consumer_key)
    provider = FlaskToolProvider.from_flask_request(
        secret = consumer_secret,
        request = request
    )

    return provider.is_valid_request(LTIRequestValidator())
