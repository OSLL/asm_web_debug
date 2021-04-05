from flask_mongoengine import MongoEngine
import datetime 
import json

from app.core.db.desc import Codes 


class DBManager:

    @staticmethod
    def get_code(code_id):
        try:
            return Codes.objects.get(_id=code_id)
        except Codes.DoesNotExist:
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
	    