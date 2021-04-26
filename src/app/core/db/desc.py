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