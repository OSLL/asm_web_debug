import logging

from app.core.db.manager import DBManager
from app.core.lti_core.lti_validator import LTIRequestValidator
from lti.contrib.flask import FlaskToolProvider


def check_request(request):
    provider = FlaskToolProvider.from_flask_request(
        secret = DBManager.get_secret(request.values.get('oauth_consumer_key', None)),
        request = request
    )

    return provider.is_valid_request(LTIRequestValidator())
