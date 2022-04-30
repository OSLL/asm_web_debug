import os

class Config:
    TEMPLATE_FOLDER = 'templates'
    STATIC_FOLDER = 'static'
    CODES_FOLDER = '../codes/'
    ENVIRONMENT_FOLDER = '../environment'
    ARCHS = ("x86_64", "avr5")
    REDIS_URL = "redis://redis:6379/0"
    SECRET_KEY = ''
    RUNNER_API = "http://runner/runner_api"
    MAX_GRADE = 100
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def load_data_from_env(cls):
        # flask secret
        cls.SECRET_KEY = os.environ.get('AWI_SECRET_KEY', '')

        # postgres connection string
        postgres_password = os.environ.get("POSTGRES_PASSWORD", "")
        cls.SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{postgres_password}@postgres/postgres"


Config.load_data_from_env()
