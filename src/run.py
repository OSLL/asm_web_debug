from flask import Flask

from app.routes.index import index_bp
import config

import os

runmode = os.environ['runmode']

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.register_blueprint(index_bp)

app.config.from_object("{}.{}".format('config', runmode))
app.config['ARCHS'] = ['x86', 'arm','avr']


if __name__ == "__main__":
    app.run()