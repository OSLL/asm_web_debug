from flask import Blueprint, make_response, render_template, request

index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/compile', methods = ["POST"])
def compile():
    return request.form.to_dict()

@bp.route('/hexview', methods = ["POST"])
def hexview():
    return render_template('hexview.html', result = request.form.to_dict())
