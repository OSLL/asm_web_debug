from flask import Flask, flash
import flask_login
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore
import os

from app.core.db.desc import Role, User
from app.core.logging.log_settings import logging_init
from app.core.source_manager import SourceManager
from app.routes.index import index_bp
from app.routes.logs import log_bp
from app.routes.lti import lti_bp

from config import ConfigManager
from app.core.db.manager import DBManager

def create_app():
    app = Flask(__name__)

    # register blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(lti_bp)

    # load config
    runmode = os.environ.get('RUNMODE')
    app.config.from_object(ConfigManager.get_config(runmode))

    # setup app folders
    app.template_folder = app.config['TEMPLATE_FOLDER']
    app.static_folder = app.config['STATIC_FOLDER']

    return app


def run_app(app):
    # init SourceManager 
    SourceManager.init(app.config['CODES_FOLDER'])

    # run app
    app.run(host=app.config['HOST'], port=app.config['PORT'])


if __name__ == "__main__":
    app = create_app()
    db = MongoEngine(app)
    user_datastore = MongoEngineUserDatastore(db, User, Role)    
    security = Security(app, user_datastore)
    login_manager = flask_login.LoginManager(app)

    app.user_datastore = user_datastore
    app.security = security
    app.login_manager = login_manager

    DBManager.create_lti_consumer(app.config['LTI_KEY'], app.config['LTI_SECRET'])
    logging_init(app)

    @login_manager.user_loader
    def load_user(user_id):
        try: 
            return User.objects.get(_id=user_id)
        except User.DoesNotExist:
            return None

    run_app(app)