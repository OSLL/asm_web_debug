from flask import Flask
import os

from app.routes.index import index_bp
from config import ConfigManager


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
    app.run(host=app.config['HOST'], port=app.config['PORT'])


if __name__ == "__main__":
    app = create_app()
    run_app(app)