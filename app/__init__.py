import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_redis import FlaskRedis
from flask_wtf.csrf import CSRFProtect

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
redis_client = FlaskRedis(app)
csrf = CSRFProtect(app)

loglevel = os.environ.get('LOGLEVEL', 'INFO').upper()

logging.basicConfig(
    level=loglevel,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

if loglevel == "DEBUG":
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def _register():
    import runner.checkers # register all checkers
    import app.models # register models
    import app.routes # register routes
    import app.cli # register cli commands

    if os.environ.get("AWI_TEST_MODE") == "1":
        logging.info("============ RUNNING IN TEST MODE! ==============")
        from app.testdata import populate
        populate()

with app.app_context():
    _register()
