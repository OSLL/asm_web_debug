from flask import Blueprint, make_response, render_template, request, current_app, redirect
from uuid import uuid4
import os
import subprocess

from app.core.utils.debug_commands import DebugCommands
from app.core.utils.hex import hexdump

from app.core.db.manager import DBManager

from app.core.process_manager import QemuUserProcess
from app.core.source_manager import SourceManager
from app.core.asmanager import ASManager


index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(f"/{uuid4()}")


@bp.route('/<code_id>')
def index_id(code_id):

    scc = SourceManager(current_app.config['CODES_FOLDER'])
    code = None

    if scc.is_code_exists(code_id):
        code = scc.get_code(code_id) #DBManager.get_code(code_id=code_id)

    if code:
        return render_template('index.html', txt_code=code)
    else:
        return render_template('index.html', txt_code='; Put your code here.')


@bp.route('/save/<code_id>', methods = ["POST"])
def save_code(code_id):
    source_code = request.form.get('code', '')
    breakpoints = request.form.get('breakpoints', '[]')
    arch =  request.form.get('arch', 'x86_64')


    scc = SourceManager(current_app.config['CODES_FOLDER'])

    source_code = request.form.get('code', '')
    breakpoints = request.form.get('breakpoints', '[]')
    arch =  request.form.get('arch', 'x86_64')


    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)

    #DBManager.create_code(code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch)
    
    return { "success_save" : True }


@bp.route('/compile/<code_id>', methods = ["POST"])
def compile(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])

    source_code = request.form.get('code', '')
    breakpoints = request.form.get('breakpoints', '[]')
    arch =  request.form.get('arch', 'x86_64')

    #DBManager.create_code(code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch)

    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)

    # Compiling code from file into file with same name (see ASManager.compile())
    as_flag, as_logs_stderr, as_logs_stdout = ASManager.compile(scc.get_code_file_path(code_id), arch)
    as_logs = as_logs_stderr + as_logs_stdout

    return { "success_build": as_flag, "build_logs": as_logs.decode("utf-8") }


@bp.route('/run/<code_id>', methods = ["POST"])
def run(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])
    source_code = request.form.get('code', '')
    arch =  request.form.get('arch', 'x86_64')


    if not scc.is_code_exists(code_id):
        return { "success_run": False, "run_logs": f"Code not exists" }


    bin_file = scc.get_code_file_path(code_id) + ".bin"

    if not os.path.isfile(bin_file):
        return { "success_run": False, "run_logs": f"Code not compiled" }

    if arch != "x86_64":
        return { "success_run": False, "run_logs": f"Arch {arch} not supported!" }

    run_result = subprocess.run(["./environment/qemu-x86_64", bin_file], capture_output = True)

    if run_result.returncode == 0:
        status = 'success'
    else:
        status = run_result.returncode

    return { "success_run": True, "run_logs": f"STATUS: {status};\nstdout: {run_result.stdout};\nstderr: {run_result.stderr};\n" }


@bp.route('/hexview/<code_id>', methods = ["POST"])
def hexview(code_id):
	return render_template('hexview.html', result=hexdump(request.form.get('hexview', ''))) 

  
@bp.route('/debug/<code_id>', methods = ["POST"])
def debug(code_id):
    command = request.form.get('debug_command', '')
    for e in DebugCommands:
        if command == e.value:
            return e.name + ' ' + str(code_id)
    return f'No debug such debug command: {command}', 404
