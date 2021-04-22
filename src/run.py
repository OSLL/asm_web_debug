from flask import Flask, flash
import os

from app.routes.index import index_bp
from app.core.source_manager import SourceManager

from config import ConfigManager

from flask_mongoengine import MongoEngine

from flask_security import Security, MongoEngineUserDatastore
from app.core.db.desc import Role, User
import flask_login

def create_app():
    app = Flask(__name__)

    # register blueprints
    app.register_blueprint(index_bp)

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

    @login_manager.user_loader
    def load_user(user_id):
        return User.objects.get(_id=user_id)

    @app.before_first_request
    def create_user():
        user_datastore.create_user(_id='first_user')
        user_datastore.create_user(_id='second_user')
    
        user = user_datastore.find_user(_id='first_user')
        flask_login.login_user(user, remember=True)
        current = flask_login.current_user

        flash('Authentication status: {}'.format(current.is_authenticated))
        flash('Logged in as {}'.format(current.get_id()))


    run_app(app)