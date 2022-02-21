from flask import Blueprint, render_template

welcome_bp = Blueprint('welcome', __name__)
bp = welcome_bp


@bp.route('/')
@bp.route('/index')
@bp.route('/welcome')
def index():
    return render_template('pages/welcome.html')


@bp.route("/_health")
def health_check():
    return "ok"
