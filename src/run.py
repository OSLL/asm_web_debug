from flask import Flask, current_app

from app.routes.index import index_bp
from config import config

import os

runmode = os.environ.get('RUNMODE') #'default' doesn't appear necessary when there is default value in sh
app = Flask(__name__) 
app.register_blueprint(index_bp)

app.config.from_object(config.get(runmode))

app.template_folder = app.config['TEMPLATE_FOLDER']
app.static_folder = app.config['STATIC_FOLDER']


if __name__ == "__main__":
    app.run()