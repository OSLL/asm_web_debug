from app import app, redis_client

from oauthlib.oauth1 import RequestValidator


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
        return app.config["LTI_CONSUMERS"].get(client_key)

    def validate_client_key(self, client_key, request):
        return client_key in app.config["LTI_CONSUMERS"]

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None, access_token=None):
        redis_key = f"nonce:{timestamp}_{client_key}_{nonce}"
        if redis_client.get(redis_key):
            return False
        redis_client.setex(redis_key, self.timestamp_lifetime * 2, "1")
        return True
