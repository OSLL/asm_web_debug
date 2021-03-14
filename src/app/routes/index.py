from flask import Blueprint, make_response, render_template, request, current_app
from uuid import uuid4

import os

from app.core.utils.debug_commands import DebugCommands
from app.core.source_manager import SourceManager

from app.core.utils.hex import hexdump

from app.core.as_manager import as_manager

# Constants
tmp_dir = "./tmp/"
tmp_name = "as_tmp"


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
    arch =  request.form.get('arch', 'x86_64')
    code_id = str(uuid4())

    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)

    # Compiling code from file into file with same name (see as_manager.compile())
    as_flag, as_logs_stderr, as_logs_stdout = as_manager.compile(scc.get_code_file_path(code_id), arch)
    as_logs = as_logs_stderr + as_logs_stdout

    return { "success_build": as_flag, "build_logs": as_logs.decode("utf-8") }


@bp.route('/hexview', methods = ["POST"])
def hexview():
	return render_template('hexview.html', result=hexdump(request.form.get('hexview', '')))


@bp.route('/debug', methods = ["POST"])
def debug():
    command = request.form.get('debug_command', '')
    for e in DebugCommands:
        if command == e.value:
            return e.name
    return f'No debug such debug command: {command}', 404
