from flask import Blueprint, make_response, render_template, request

from app.core.utils.debug_commands import DebugCommands

from app.core.utils.hex import hexdump


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
	return render_template('hexview.html', result=hexdump(request.form.to_dict()['hexview'])) 

  
@bp.route('/debug', methods = ["POST"])
def debug():
    command = request.form.get('debug_command', '')
    for e in DebugCommands:
        if command == e.value:
            return e.name
    return f'No debug such debug command: {command}', 404