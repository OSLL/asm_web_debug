from flask import Flask

from app.routes.index import index_bp
from app.core.utils.debug_commands import DebugCommands 

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.register_blueprint(index_bp)


app.config['DEBUG_COMMANDS'] = DebugCommands
app.config['CODES_DIR'] = '../codes/'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
