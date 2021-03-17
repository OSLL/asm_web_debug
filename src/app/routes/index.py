from flask import Blueprint, make_response, render_template, request, current_app, redirect
from uuid import uuid4

import os

from app.core.utils.debug_commands import DebugCommands
from app.core.source_manager import SourceManager

from app.core.utils.hex import hexdump

from app.core.asmanager import ASManager


index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(f"/{uuid4()}")


@bp.route('/<uuid:code_id>')
def index_id(code_id):
    return render_template('index.html', txt_code=code_id)


@bp.route('/compile/<uuid:code_id>', methods = ["POST"])
def compile(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])

    source_code = request.form.get('code', '')
    arch =  request.form.get('arch', 'x86_64')

    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)

    # Compiling code from file into file with same name (see ASManager.compile())
    as_flag, as_logs_stderr, as_logs_stdout = ASManager.compile(scc.get_code_file_path(code_id), arch)
    as_logs = as_logs_stderr + as_logs_stdout

    return { "success_build": as_flag, "build_logs": as_logs.decode("utf-8") }


@bp.route('/hexview/<uuid:code_id>', methods = ["POST"])
def hexview(code_id):
	return render_template('hexview.html', result=hexdump(request.form.get('hexview', ''))) 

  
@bp.route('/debug/<uuid:code_id>', methods = ["POST"])
def debug(code_id):
    command = request.form.get('debug_command', '')
    for e in DebugCommands:
        if command == e.value:
            return e.name + ' ' + str(code_id)
    return f'No debug such debug command: {command}', 404
