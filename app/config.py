import os


def parse_lti_consumer_info(key_str, secret_str):
    keys = key_str.split(',')
    secrets = secret_str.split(',')

    if len(keys) != len(secrets):
        raise Exception(f"len(consumer_keys) != len(consumer_secrets): '{key_str}' vs '{secret_str}'")

    return { key: secret for key, secret in zip(keys, secrets) }


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
    MAX_GRADE = 100
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def load_data_from_env(cls):
        # consumers
        consumer_keys = os.environ.get('AWI_CONSUMER_KEYS', '')
        consumer_secrets = os.environ.get('AWI_CONSUMER_SECRETS', '')
        cls.LTI_CONSUMERS = parse_lti_consumer_info(consumer_keys, consumer_secrets)

        # flask secret
        cls.SECRET_KEY = os.environ.get('AWI_SECRET_KEY', '')

        # postgres connection string
        postgres_password = os.environ.get("POSTGRES_PASSWORD", "")
        cls.SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{postgres_password}@postgres/postgres"


Config.load_data_from_env()
