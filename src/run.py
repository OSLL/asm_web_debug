from flask import Flask

from app.routes.index import index_bp

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.register_blueprint(index_bp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
