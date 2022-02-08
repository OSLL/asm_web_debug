import datetime
from email.policy import default
import uuid
import mongoengine as me
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256


class User(me.Document, UserMixin):
    _id = me.StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    username = me.StringField(unique=True, max_length=80)
    password = me.StringField()
    datetime = me.DateTimeField(default=datetime.datetime.now)
    tasks = me.DictField()
    is_admin = me.BooleanField(default=False)

    def get_id(self) -> str:
        return str(self._id)

    def set_password(self, password: str) -> None:
        self.password = pbkdf2_sha256.hash(password)

    def __str__(self):
        return str(self.username)


class Codes(me.Document):
    _id = me.StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    created = me.DateTimeField(default=datetime.datetime.now)
    last_update = me.DateTimeField(default=datetime.datetime.now)
    code = me.StringField()
    breakpoints = me.ListField(me.IntField())
    arch = me.StringField()
    owner = me.ReferenceField(User)


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
