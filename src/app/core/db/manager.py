from flask_mongoengine import MongoEngine

from app.core.db.desc import Codes 
import datetime 
import json

class DBManager:

    @classmethod
    def get_codes(cls, id):
        try:
            cd = Codes.objects.get(_id=id)
            return cd.to_json()  #?dates lose iso, format during return/better way 
        except Codes.DoesNotExist:
            return None
        #? not exhaustive, get_or_404 - ?
     
    @classmethod
    def create_codes(cls, code_id, source_code, breakpoints):
    	#breakpoints accepted as request.form.get('breakpoints') 
        b_p = json.loads(breakpoints)
        try:
            Codes.objects.insert(Codes(_id = str(code_id), created = datetime.datetime.now, code = source_code, breakpoints = b_p ))
        except:
            Codes.objects(_id=str(code_id)).update_one(last_update = datetime.datetime.now, code = source_code, breakpoints = b_p)
    
    @classmethod
    def get_codes_older_than(cls, days):
    	return Codes.objects(created__lte = (datetime.datetime.now() - datetime.timedelta(days=days))).to_json()
	    