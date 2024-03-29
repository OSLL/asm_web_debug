from flask import current_app
from oauthlib.oauth1 import RequestValidator

from app.core.db.desc import Consumers
from app.core.db.manager import DBManager


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

    def get_client_secret(self, client_key, request):
        return DBManager.get_secret(client_key)

    def validate_client_key(self, client_key, request):
        return DBManager.is_key_valid(client_key)

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None, access_token=None):
        if not DBManager.has_timestamp_and_nonce(client_key, timestamp, nonce):
            DBManager.add_timestamp_and_nonce(client_key, timestamp, nonce)
            current_app.logger.debug('timestamp and nonce are valid!')
            return True
        else:
            current_app.logger.error('timestamp and nonce are invalid!')
            return False


    @property
    def dummy_client(self):
        return 'dummy_client'
