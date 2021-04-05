import mongoengine as me
import datetime 


class Codes(me.Document):
    _id = me.StringField()
    created = me.DateTimeField(default=datetime.datetime.now)
    last_update = me.DateTimeField(default=datetime.datetime.now)     
    code = me.StringField()                  
    breakpoints = me.ListField(me.IntField())
    arch = me.StringField()
    lti_user = me.ReferenceField('LTI_sessions', dbref=True)