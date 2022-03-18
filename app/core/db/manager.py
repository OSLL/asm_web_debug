import datetime
import logging
from typing import Optional

from pymongo import DESCENDING, ASCENDING
from passlib.hash import pbkdf2_sha256

from app.core.db.desc import Code, Problem, Submission, User, Consumers


class DBManager:

    @staticmethod
    def get_user_by_username_and_password(username: str, password: str) -> Optional[User]:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if pbkdf2_sha256.verify(password, user.password):
            return user

    @staticmethod
    def get_problem(problem_id):
        try:
            return Problem.objects.get(_id=problem_id)
        except Problem.DoesNotExist:
            return None

    #### code ####

    @staticmethod
    def get_code(code_id):
        try:
            return Code.objects.get(_id=code_id)
        except Code.DoesNotExist:
            return None

    @staticmethod
    def get_submission(submission_id):
        try:
            return Submission.objects.get(_id=submission_id)
        except Submission.DoesNotExist:
            return None

    @staticmethod
    def create_code(code_id, source_code, arch):
        code_obj = Code.objects(_id=code_id).first()
        if code_obj:
            code_obj.last_update = datetime.datetime.now()
            code_obj.code = source_code
            code_obj.arch = arch
            code_obj.save()
        else:
            code_obj = Code(_id=code_id, code=source_code, arch=arch)
            code_obj.save()

    @staticmethod
    def get_codes_older_than(days):
        return Code.objects(created__lte=(datetime.datetime.now()-datetime.timedelta(days=days))).to_json()

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(_id=user_id)
        except User.DoesNotExist:
            logging.debug(f'User not found: {user_id}')
            return None

    #### lti ####

    @staticmethod
    def get_secret(key):
        try:
            return Consumers.objects.get(_id = key).secret
        except Consumers.DoesNotExist:
            return None

    @staticmethod
    def is_key_valid(key):
        try:
            Consumers.objects.get(_id = key)
            return True
        except Consumers.DoesNotExist:
            return False

    @staticmethod
    def add_timestamp_and_nonce(id_key, timestamp, nonce):
        try:
            consumer_obj = Consumers.objects.get(_id = id_key)
            consumer_obj.timestamps.append([timestamp, nonce])
            consumer_obj.save()
        except Consumers.DoesNotExist:
            pass

    @staticmethod
    def has_timestamp_and_nonce(id_key, timestamp, nonce):
        try:
            consumer_obj = Consumers.objects.get(_id = id_key)
            if (timestamp, nonce) in consumer_obj.timestamps:
                return True
        except Consumers.DoesNotExist:
            return False

    @staticmethod
    def create_lti_consumer(id_key, secret_key, timestamp_and_nonce = []):
        return Consumers(_id = id_key, secret = secret_key, timestamps = timestamp_and_nonce).save()

