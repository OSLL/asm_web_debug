from app import app

from lti import OutcomeRequest

PASSBACK_PARAMS = ('lis_outcome_service_url', 'lis_result_sourcedid', 'oauth_consumer_key')
ROLES_PARAM = 'roles'
TEACHER_ROLE = 'Instructor'


class LTIError(Exception): pass


def report_outcome_score(consumer_key: str, sourcedid: str, url: str, grade: float) -> None:
    consumer_secret = app.config["LTI_CONSUMERS"].get(consumer_key)
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
