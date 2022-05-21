import datetime 
from flask_security import RoleMixin, UserMixin 
import mongoengine as me


class Role(me.Document, RoleMixin):
    name = me.StringField(max_length=80, unique=True)
    description = me.StringField(max_length=255)


class User(me.Document, UserMixin):
    _id = me.StringField(primary_key=True)
    username = me.StringField(max_length=80)
    datetime = me.DateTimeField(default=datetime.datetime.now)
    tasks = me.DictField()
    roles = me.ListField(me.ReferenceField(Role), default=[])
    active = me.BooleanField()


class Codes(me.Document):
    _id = me.StringField(primary_key=True)
    created = me.DateTimeField(default=datetime.datetime.now)
    last_update = me.DateTimeField(default=datetime.datetime.now)     
    code = me.StringField()                  
    breakpoints = me.ListField(me.IntField())
    arch = me.StringField()
    lti_user = me.ReferenceField('LTI_sessions', dbref=True)


class Logs(me.Document):
    _id = me.StringField(primary_key=True)
    time = me.DateTimeField(default=datetime.datetime.now) 
    levelname = me.StringField()
    message = me.StringField()
    lineno = me.IntField()
    pathname = me.StringField()

    meta = {
        'indexes': ['time']
    }


class Consumers(me.Document):
    _id = me.StringField(primary_key=True)
    secret = me.StringField()
    datetime = me.DateTimeField(default=datetime.datetime.now)
    timestamps = me.ListField(blank=True)
    
class Solutions(me.Document):
    _id = me.IntField(primary_key=True)
    datetime = me.DateTimeField()
    feedback = me.StringField()
    task = me.ReferenceField('Tasks', dbref=True)
    LTI_session = me.ReferenceField('LTI_sessions', dbref=True)
    codes = me.ReferenceField('Codes', dbref=True)
    
class Tasks(me.Document):
    _id = me.IntField(primary_key=True)
    name = me.StringField(unique=True)
    description = me.StringField()
    tests = me.DictField()
    parameters = me.ReferenceField('Parameters',dbref=True)

class Parameters(me.Document):
    _id = me.IntField(primary_key=True)
    output= me.StringField()
    registry = me.ReferenceField('Registry', dbref=True)
	 
class Registry(me.Document):
    _id = me.IntField(primary_key=True)
    eax = me.StringField()
    ebx = me.StringField()
    ecx = me.StringField() 
    edx = me.StringField()
    ebp = me.StringField()
    esp = me.StringField()
    esp = me.StringField()
    edi = me.StringField()
    eip = me.StringField()
    cs = me.StringField()
    ds = me.StringField()
    es = me.StringField()
    fs = me.StringField()
    gs = me.StringField()
    ss = me.StringField()
    eflags = me.StringField()
