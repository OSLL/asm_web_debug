from flask import request

from app.core.db.manager import DBManager

PASSBACK_PARAMS = ('lis_outcome_service_url', 'lis_result_sourcedid', 'oauth_consumer_key')

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