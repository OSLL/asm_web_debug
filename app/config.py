import logging
from os import environ as os_environ

from app.core.lti_core.lti_utils import parse_consumer_info


class Config(object):
    HOST = '0.0.0.0'
    PORT = '5000'
    TEMPLATE_FOLDER = 'templates'
    STATIC_FOLDER = 'static'
    CODES_FOLDER = '../codes/'
    ENVIRONMENT_FOLDER = '../environment'
    BUILD_FILE = '../DEBUG'
    ARCHS = ('x86_64',)
    MONGODB_SETTINGS = {
        'db': 'database',
        'host': '127.0.0.1',
        'port': 27017
    }
    SECRET_KEY = ''
    DEBUG = True
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


class DeployConfig(Config):
    MONGODB_SETTINGS = {
        'db': 'database',
        'host': 'mongo',
        'port': 27017
    }
    DEBUG = False
    PORT = '80'


class TestConfig(DeployConfig):
    DEBUG = True


class DefaultConfig(Config):
    pass


class ConfigManager:

    config = {
        'default': DefaultConfig,
        'deploy': DeployConfig,
        'test': TestConfig
    }

    @classmethod
    def get_config(cls, config_type):
        if config_type in cls.config:
            config = cls.config[config_type]
        else:
            logging.warn(f"No such config: '{config_type}'. Using default config")
            config = cls.config['default']

        try:
            config.load_data_from_env()
        except Exception as e:
            print(str(e))
            return None
        return config
