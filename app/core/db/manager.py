import json
import datetime
import logging
from typing import Optional

from flask import current_app
from flask_mongoengine import MongoEngine
from pymongo import DESCENDING, ASCENDING
from passlib.hash import pbkdf2_sha256

from app.core.db.desc import Code, Problem, User, Logs, Consumers


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

    #### log ####

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(_id=user_id)
        except User.DoesNotExist:
            current_app.logger.debug(f'User not found: {user_id}')
            return None

    @staticmethod
    def add_log(log_id, time, lineno, pathname, levelname, message):
        return Logs(_id=log_id, time=time, lineno=lineno, pathname=pathname, levelname=levelname, message=message).save()._id

    @staticmethod
    def get_all_logs():
        return Logs.objects.all()

    @staticmethod
    def get_log_by_id(log_id):
        try:
            log = Logs.objects.get(_id=log_id)
            return log
        except Logs.DoesNotExist:
            current_app.logger.debug(f'Log not found: {log_id}')
            return None

    @staticmethod
    def get_filter_logs(query={}, limit=None, offset=None, sort=None, order=None):
        logs = Logs.objects(**query).order_by('-time')
        count = logs.count()
        if limit is not None and offset is not None:
            logs = logs.skip(offset).limit(limit)
        if sort:
            logs = logs.order_by(f"{'-' if order == 'asc' else '+'}{sort}")
        return logs, count


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

