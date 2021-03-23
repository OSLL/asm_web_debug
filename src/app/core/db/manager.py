from flask_mongoengine import MongoEngine

from app.core.db.desc import Codes
from mongoengine import connect
import json

class DBManager:
    @classmethod
    def get_codes(cls, id):
        try:
            return Codes.objects.get(_id=id).to_json()  #dates lose iso
        except:
            return None
     
    @classmethod
    def create_codes(cls, code_id, source_code, breakpoints):
    	#breakpoints accepted as request.form.get('breakpoints')
        b_p = json.loads(breakpoints)
        return Codes(_id = str(code_id), code = source_code, breakpoints = b_p).save()

    def get_codes_older_than():
    	#? since created is undefined
	    pass

    def __init__(self):
        db = connect('test', host= '127.0.0.1:27017', alias='default') #for testing exclusively 
        #'mongo' isn't a host, probably better to use flask_mongoengine to connect from init