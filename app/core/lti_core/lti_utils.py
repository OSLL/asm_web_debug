import json
from sqlite3 import InternalError
from flask import request
from lti import OutcomeRequest

from app.core.db.manager import DBManager

PASSBACK_PARAMS = ('lis_outcome_service_url', 'lis_result_sourcedid', 'oauth_consumer_key')
CUSTOM_PARAM_PREFIX = 'custom_'
ROLES_PARAM = 'roles'
TEACHER_ROLE = 'Instructor'


class LTIError(Exception): pass


# methods for parsing LTI-launch parameters

def extract_passback_params(data):
    params = {}
    for param_key in PASSBACK_PARAMS:
        if param_key in data:
            params[param_key] = data[param_key]
        else:
            raise KeyError("{} doesn't include {}. Must inslude: {}".format(data, param_key, PASSBACK_PARAMS))
    return params


def get_custom_params(data):
    return { key[len(CUSTOM_PARAM_PREFIX):]: data[key] for key in data if key.startswith(CUSTOM_PARAM_PREFIX) }


def get_role(data, default_role='user'):
    #TODO: add collections w/admins
    try:
        if TEACHER_ROLE in data.get(ROLES_PARAM, '').split(','):
            return 'teacher'
        else:
            return default_role
    except:
        return default_role


def report_outcome_score(passback_params: str | dict, score: float) -> None:
    if type(passback_params) is not dict:
        passback_params = json.loads(passback_params)

    consumer_key = passback_params["oauth_consumer_key"]
    consumer_secret = DBManager.get_secret(consumer_key)
    if consumer_secret is None:
        raise LTIError(f"Invalid consumer {consumer_key}")

    request = OutcomeRequest(opts={
        "lis_outcome_service_url": passback_params["lis_outcome_service_url"],
        "lis_result_sourcedid": passback_params["lis_result_sourcedid"],
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret
    })

    response = request.post_replace_result(score)
    if response.is_failure():
        raise LTIError(f"Failed to submit outcome: {response.description}")


# methods for working w/consumers

def create_consumers(consumer_dict):
    for key, secret in consumer_dict.items():
        DBManager.create_lti_consumer(key, secret)


def parse_consumer_info(key_str, secret_str):
    keys = key_str.split(',')
    secrets = secret_str.split(',')

    if len(keys) != len(secrets):
        raise Exception(f"len(consumer_keys) != len(consumer_secrets): '{key_str}' vs '{secret_str}'")

    return { key: secret for key, secret in zip(keys, secrets) }
