from typing import Optional
from flask import request
from app import redis_client

from lti import OutcomeRequest
from lti.contrib.flask import FlaskToolProvider
from oauthlib.oauth1 import RequestValidator

from app.models import ToolConsumer

PASSBACK_PARAMS = ('lis_outcome_service_url', 'lis_result_sourcedid', 'oauth_consumer_key')
ROLES_PARAM = 'roles'
TEACHER_ROLE = 'Instructor'


class LTIError(Exception): pass


class LTIRequestValidator(RequestValidator):
    @property
    def client_key_length(self):
        return 15, 30

    @property
    def nonce_length(self):
        return 20, 40

    @property
    def enforce_ssl(self):
        return False

    @property
    def timestamp_lifetime(self):
        return 600

    def get_client_secret(self, client_key, request):
        return get_secret_by_consumer_key(client_key)

    def validate_client_key(self, client_key, request):
        return get_secret_by_consumer_key(client_key) is not None

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None, access_token=None):
        redis_key = f"nonce:{timestamp}_{client_key}_{nonce}"
        if redis_client.get(redis_key):
            return False
        redis_client.setex(redis_key, self.timestamp_lifetime * 2, "1")
        return True


def get_secret_by_consumer_key(consumer_key: str) -> Optional[str]:
    tool_consumer = ToolConsumer.query.filter_by(consumer_key=consumer_key).first()
    if not tool_consumer:
        return None
    return tool_consumer.consumer_secret


def report_outcome_score(consumer_key: str, sourcedid: str, url: str, grade: float) -> None:
    consumer_secret = get_secret_by_consumer_key(consumer_key)
    if consumer_secret is None:
        raise LTIError(f"Invalid consumer {consumer_key}")

    request = OutcomeRequest(opts={
        "lis_outcome_service_url": url,
        "lis_result_sourcedid": sourcedid,
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret
    })

    response = request.post_replace_result(grade)
    if response.is_failure():
        raise LTIError(f"Failed to submit outcome: {response.description}")


def check_lti_request(tool_consumer: ToolConsumer) -> bool:
    provider = FlaskToolProvider.from_flask_request(
        secret=tool_consumer.consumer_secret,
        request=request
    )

    return provider.is_valid_request(LTIRequestValidator())
