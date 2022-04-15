import os

from flask import Flask, abort
import flask_login
from flask_mongoengine import MongoEngine
from flask_security import Security, MongoEngineUserDatastore
import waitress

from app.core.db.desc import Role, User
from app.core.logging.log_settings import logging_init
from app.core.lti_core.lti_utils import create_consumers
from app.routes.debug import debug_bp
from app.routes.index import index_bp
from app.routes.logs import log_bp
from app.routes.lti import lti_bp
from app.routes.welcome import welcome_bp
from app.routes.solution import solution_bp
from app.routes.tasks import tasks_bp
from app.routes.solutions import solutions_bp
from app.config import ConfigManager


def create_app():
    app = Flask(__name__)

    # register blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(lti_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(welcome_bp)
    app.register_blueprint(solution_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(solutions_bp)

    # load config
    runmode = os.environ.get('RUNMODE')
    app.config.from_object(ConfigManager.get_config(runmode))

    # setup app folders
    app.template_folder = app.config['TEMPLATE_FOLDER']
    app.static_folder = app.config['STATIC_FOLDER']

    db = MongoEngine(app)
    app.user_datastore = MongoEngineUserDatastore(db, User, Role)
    app.security = Security(app, app.user_datastore)
    app.login_manager = flask_login.LoginManager(app)

    # TODO: do smth with role_requiered and etc
    app.security.unauthorized_handler(lambda fn=None, params=None: abort(404))

    @app.before_first_request
    def init_roles_and_user():
        if app.config['ANON_ACCESS']:
            app.user_datastore.create_user(_id=app.config['ANON_USER_ID'], username='anon_username')
        for role in app.config['USER_ROLES']:
            if not app.user_datastore.find_role(role):
                app.user_datastore.create_role(name=role)

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
