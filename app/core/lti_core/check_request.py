import logging

from flask import current_app
from app.core.db.manager import DBManager
from app.core.lti_core.lti_validator import LTIRequestValidator
from lti.contrib.flask import FlaskToolProvider


def check_request(request):
    provider = FlaskToolProvider.from_flask_request(
        secret = DBManager.get_secret(request.values.get('oauth_consumer_key', None)),
        request = request
    )
    current_app.logger.info(vars(provider))
    current_app.logger.info(request.values)

    return provider.is_valid_request(LTIRequestValidator())
