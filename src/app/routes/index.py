from flask import Blueprint, make_response, render_template, request, current_app

from app.core.utils.debug_commands import DebugCommands
from app.core.SourceCodeContainer import SourceCodeContainer


index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/compile', methods = ["POST"])
def compile():
    scc = SourceCodeContainer(current_app.config['SOLUTIONS_DIT'])
    next(scc.gen_free_uid())

    source_code = request.form.get('code', '')
    
    try:
        scc.save_solution(next(scc.gen_free_uid()), source_code)
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
