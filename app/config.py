import logging
from os import environ as os_environ

from app.core.lti_core.lti_utils import parse_consumer_info


class Config:
    TEMPLATE_FOLDER = 'templates'
    STATIC_FOLDER = 'static'
    CODES_FOLDER = '../codes/'
    ENVIRONMENT_FOLDER = '../environment'
    ARCHS = ('x86_64',)
    MONGODB_SETTINGS = {
        'db': 'database',
        'host': 'mongo',
        'port': 27017
    }
    SECRET_KEY = ''
    LTI_CONSUMERS = {}
    RUNNER_API = "http://runner/runner_api"

    @classmethod
    def load_data_from_env(cls):
        # consumers
        consumer_keys = os_environ.get('AWI_CONSUMER_KEYS', '')
        consumer_secrets = os_environ.get('AWI_CONSUMER_SECRETS', '')
        cls.LTI_CONSUMERS = parse_consumer_info(consumer_keys, consumer_secrets)

        # flask secret
        cls.SECRET_KEY = os_environ.get('AWI_SECRET_KEY', '')


Config.load_data_from_env()
