import datetime 
from flask import current_app
from flask_mongoengine import MongoEngine
from pymongo import DESCENDING, ASCENDING
import json

from app.core.db.desc import Codes, User, Logs, Consumers, Tasks, Solutions

class DBManager:

    #### code ####

    @staticmethod
    def get_code(code_id):
        try:
            return Codes.objects.get(_id=code_id)
        except Codes.DoesNotExist:
            current_app.logger.debug(f'Code not found: {code_id}')
            return None
     
    @staticmethod
    def create_code(code_id, source_code, breakpoints, arch):
        #breakpoints accepted as request.form.get('breakpoints') 
        b_p = json.loads(breakpoints)
        code_obj = Codes.objects(_id=code_id).first()
        if code_obj:
            code_obj.last_update = datetime.datetime.now()
            code_obj.code = source_code
            code_obj.breakpoints = b_p
            code_obj.arch = arch
            code_obj.save()
        else:
            code_obj = Codes(_id=code_id, code=source_code, breakpoints=b_p, arch=arch)
            code_obj.save()

    @staticmethod
    def get_codes_older_than(days):
        return Codes.objects(created__lte=(datetime.datetime.now()-datetime.timedelta(days=days))).to_json()
    
    @staticmethod
    def create_task(task_id, task_name, task_description, task_tests):
        task_obj = Tasks.objects(_id=task_id).first()
        if task_obj:
            task_obj.name = task_name
            task_obj.description = task_description
            task_obj.tests = task_tests
            task_obj.save()
        else:
            task_obj = Tasks(_id=task_id, name=task_name, description=task_description, tests=task_tests)
            task_obj.save()
            
    @staticmethod
    def get_task(task_id):
        try:
            return Tasks.objects.get(_id=task_id)
        except Tasks.DoesNotExist:
            current_app.logger.debug(f'Task not found: {task_id}')
            return None

    @staticmethod
    def get_all_tasks():
        return Tasks.objects.all()
    
    @staticmethod
    def delete_task(task_id):
        try:
            return Tasks.objects(_id=task_id).delete()
        except Tasks.DoesNotExist:
            current_app.logger.debug(f'Task not found: {task_id}')
            return None
    
    ### solutions ###
    
    @staticmethod
    def delete_solution(solution_id):
        try:
            return Solutions.objects(_id=solution_id).delete()
        except Solution.DoesNotExist:
            current_app.logger.debug(f'Solution not found: {solution_id}')
            return None


    @staticmethod
    def create_solution(solution_id, datetime, feedback, task, LTI_session, codes):
        solution_obj = Solutions.objects(_id=solution_id).first()
        if solution_obj:
            solution_obj.datetime = datetime
            solution_obj.feedback = feedback
            solution_obj.task = task
            #solution_obj.LTI_session = LTI_session
            solution_obj.codes = codes
            solution_obj.save()
        else:
            solution_obj = Solutions(_id=solution_id, datetime=datetime, feedback=feedback, codes=codes)
            solution_obj.save() 

    @staticmethod
    def get_solution(solution_id):
        try:
            return Solutions.objects.get(_id=solution_id)
        except Solutions.DoesNotExist:
            current_app.logger.debug(f'Solution not found: {solution_id}')
            return None
    
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
