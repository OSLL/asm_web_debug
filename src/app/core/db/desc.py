from flask_mongoengine import MongoEngine
from mongoengine import Document

db = MongoEngine() #?

import datetime 

class Codes(db.Document):
    _id = db.StringField()
    created = db.DateTimeField()
    last_update = db.DateTimeField(default=datetime.datetime.now)     
    code = db.StringField()                  
    breakpoints = db.ListField(db.IntField())   
    lti_user = db.ReferenceField('LTI_sessions', dbref = True)