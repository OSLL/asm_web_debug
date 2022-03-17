import logging
import os
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine(app)
login_manager = LoginManager(app)

logging.basicConfig(level="DEBUG")

def _register():
    import runner.checkers # register all checkers
    import app.routes # register routes
    import app.cli # register cli commands

_register()
