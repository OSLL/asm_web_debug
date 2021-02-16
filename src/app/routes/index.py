from flask import Blueprint, make_response, render_template, request

index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index', methods = ["POST", "GET"])
def index():
    if request.method == 'POST':
        return request.form.to_dict()
    return render_template('index.html')