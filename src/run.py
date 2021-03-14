from flask import Flask

from app.routes.index import index_bp
from config import config

import os

runmode = os.environ.get('RUNMODE')
app = Flask(__name__) 
app.register_blueprint(index_bp)


app.config.from_object(config.get(runmode))

app.template_folder = app.config['TEMPLATE_FOLDER']
app.static_folder = app.config['STATIC_FOLDER']
app.config['CODES_DIR'] = '../codes/'


if __name__ == "__main__":
    app.run()