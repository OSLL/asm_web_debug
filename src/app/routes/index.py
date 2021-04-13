from flask import Blueprint, make_response, render_template, request, current_app, redirect
from uuid import uuid4

import subprocess

from app.core.utils.debug_commands import DebugCommands
from app.core.utils.hex import hexdump

from app.core.source_manager import SourceManager
from app.core.asmanager import ASManager
from app.core.debug_manager import DebugManager
from app.core.emulation_manager import EmulationManager


index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(f"/{uuid4()}")

@bp.route('/compile/<uuid:code_id>', methods = ["POST"])
def compile(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])
    source_code = request.form.get('code', '')
    arch = request.form.get('arch', 'x86_64')

    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)

    # Compiling code from temporary file into temporary file with same name (see ASManager.compile())

    as_flag, as_logs_stderr, as_logs_stdout = ASManager.compile(scc.get_code_file_path(code_id),
								 scc.get_code_file_path(code_id) + ".o",
								 arch)
    logs_as = as_logs_stderr + as_logs_stdout
    ld_flag, ld_logs_stderr, ld_logs_stdout = ASManager.link(ASManager.object_filename,
							      scc.get_code_file_path(code_id) + ".out",
							      arch)
    logs_ld = ld_logs_stderr + ld_logs_stdout

    logs = logs_as + logs_ld

    return { "success_build": as_flag and ld_flag, "build_logs": logs.decode("utf-8") }


@bp.route('/<uuid:code_id>')
def index_id(code_id):
    source_code = ''
    scc = SourceManager(current_app.config['CODES_FOLDER'])

    if not scc.is_code_exists(code_id):
        return render_template('index.html', txt_code='default code and new user id')

    try:
        source_code = scc.get_code(code_id)
    except OSError as e:
        print(e)
        return render_template('index.html', txt_code='default code and new user id')

    return render_template('index.html', txt_code=source_code)


@bp.route('/save/<uuid:code_id>', methods = ["POST"])
def save_code(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])

    source_code = request.form.get('code', '')
    arch = request.form.get('arch', 'x86_64')

    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)
        return { "success_save" : False }

    return { "success_save" : True }


@bp.route('/run/<uuid:code_id>', methods = ["POST"])
def run(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])
    source_code = request.form.get('code', '')
    arch = request.form.get('arch', 'x86_64')

    run_inst = EmulationManager.run_exec(scc.get_code_file_path(code_id) + ".out", arch, code_id)
    if run_inst != None:
        gdb_res = DebugManager.run_and_attach(run_inst, arch)

    return { "success_run": bool(run_inst) }


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
