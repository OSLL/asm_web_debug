from flask import request

from app.core.db.manager import DBManager

PASSBACK_PARAMS = ('lis_outcome_service_url', 'lis_result_sourcedid', 'oauth_consumer_key')
CUSTOM_PARAM_PREFIX = 'custom_'
ROLES_PARAM = 'roles'
TEACHER_ROLE = 'Instructor'

def extract_passback_params(data):
    params = {}
    for param_key in PASSBACK_PARAMS:
        if param_key in data:
            params[param_key] = data[param_key]
        else:
            raise KeyError("{} doesn't include {}. Must inslude: {}".format(data, param_key, PASSBACK_PARAMS))
    return params


def create_consumers(consumer_dict):
    for key, secret in consumer_dict.items():
        DBManager.create_lti_consumer(key, secret)


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