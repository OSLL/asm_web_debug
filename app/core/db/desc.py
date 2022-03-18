import datetime
from email.policy import default
from sqlite3 import Timestamp
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


class Problem(me.Document):
    _id = me.StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    title = me.StringField(max_length=256)
    statement = me.StringField()
    checker_name = me.StringField()
    checker_config = me.StringField(default="{}")

    def __str__(self):
        return str(self.title)


class Code(me.Document):
    _id = me.StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    created = me.DateTimeField(default=datetime.datetime.now)
    last_update = me.DateTimeField(default=datetime.datetime.now)
    code = me.StringField(default="")
    arch = me.StringField(default="x86_64")
    owner = me.ReferenceField(User)
    problem = me.ReferenceField(Problem)
    passback_params = me.StringField()


class Submission(me.Document):
    _id = me.StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    user = me.ReferenceField(User)
    problem = me.ReferenceField(Problem)
    arch = me.StringField()
    code = me.StringField()
    is_correct = me.BooleanField()
    comment = me.StringField()
    timestamp = me.DateTimeField(default=datetime.datetime.now)


class Consumers(me.Document):
    _id = me.StringField(primary_key=True)
    secret = me.StringField()
    datetime = me.DateTimeField(default=datetime.datetime.now)
    timestamps = me.ListField(blank=True)
