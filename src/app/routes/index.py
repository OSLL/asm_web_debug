from flask import Blueprint, make_response, render_template, request, current_app
from uuid import uuid4

from app.core.utils.debug_commands import DebugCommands
from app.core.source_manager import SourceManager


index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/compile', methods = ["POST"])
def compile():
    scc = SourceManager(current_app.config['CODES_DIR'])

    source_code = request.form.get('code', '')
    
    try:
        scc.save_code(str(uuid4()), source_code)
    except OSError as e:
        print(e)

    return request.form.to_dict()


@bp.route('/debug', methods = ["POST"])
def debug():
    command = request.form.get('debug_command', '')
    for e in DebugCommands:
        if command == e.value:
            return e.name
    return f'No debug such debug command: {command}', 404
