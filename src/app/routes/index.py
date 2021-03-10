from flask import Blueprint, make_response, render_template, request, current_app, app

from app.core.utils.debug_commands import DebugCommands
from app.core.SourceCodeContainer import SourceCodeContainer
import random


scc = SourceCodeContainer('../solutions/')
index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/compile', methods = ["POST"])
def compile():
    source_code = request.form.get('code', '')
    
    try:
        scc.save_solution(random.randint(1, 100000), source_code)
    except (OSError, FileExistsError) as e:
        print(e)

    return request.form.to_dict()


@bp.route('/debug', methods = ["POST"])
def debug():
    command = request.form.get('debug_command', '')
    for e in DebugCommands:
        if command == e.value:
            return e.name
    return f'No debug such debug command: {command}', 404
