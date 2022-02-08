import os

from flask import Flask, abort
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
import waitress

from app.core.db.desc import User
from app.core.logging.log_settings import logging_init
from app.core.lti_core.lti_utils import create_consumers
from app.routes.admin import init_admin
from app.routes.debug import debug_bp
from app.routes.codes import bp as codes_bp
from app.routes.logs import log_bp
from app.routes.lti import lti_bp
from app.routes.welcome import welcome_bp
from app.routes.auth import bp as auth_bp
from app.config import ConfigManager


def create_app():
    app = Flask(__name__)

    # load config
    runmode = os.environ.get('RUNMODE')
    app.config.from_object(ConfigManager.get_config(runmode))

    app.db = MongoEngine(app)
    init_admin(app)

    # register blueprints
    app.register_blueprint(codes_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(lti_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(welcome_bp)
    app.register_blueprint(auth_bp)

    # setup app folders
    app.template_folder = app.config['TEMPLATE_FOLDER']
    app.static_folder = app.config['STATIC_FOLDER']

    app.login_manager = LoginManager(app)

    @app.login_manager.user_loader
    def load_user(user_id):
        try:
            return User.objects.get(_id=user_id)
        except User.DoesNotExist:
            return None

    return app


def run_app(app):
    # init logging
    logging_init(app)

    # init lti consumers
    create_consumers(app.config['LTI_CONSUMERS'])

    # run app
    if app.config["DEBUG"]:
        app.run(host=app.config['HOST'], port=app.config['PORT'])
    else:
        waitress.serve(app, host=app.config['HOST'], port=app.config['PORT'])


def main():
    app = create_app()
    run_app(app)
