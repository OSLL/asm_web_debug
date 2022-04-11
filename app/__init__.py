import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_redis import FlaskRedis

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
redis_client = FlaskRedis(app)

logging.basicConfig(
    level=logging.os.environ.get('LOGLEVEL', 'INFO').upper(),
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def _register():
    import runner.checkers # register all checkers
    import app.models # register models
    import app.routes # register routes
    import app.cli # register cli commands

_register()
