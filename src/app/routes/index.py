from flask import Blueprint, make_response, render_template, request, current_app as app, redirect, abort
from flask_login import current_user, login_user
from flask_security import MongoEngineUserDatastore
from uuid import uuid4
import os
import subprocess

from app.core.asmanager import ASManager
from app.core.db.manager import DBManager
from app.core.source_manager import SourceManager as sm
from app.core.utils.debug_commands import DebugCommands
from app.core.utils.hex import hexdump

from app.core.db.manager import DBManager

from app.core.process_manager import QemuUserProcess
from app.core.source_manager import SourceManager
from app.core.asmanager import ASManager


index_bp = Blueprint('index', __name__)
bp = index_bp

@bp.before_request
def check_login():
    if current_user.is_authenticated:
        app.logger.info(f"Authenticated user: {current_user.username}")
        app.logger.debug(f"{current_user.to_json()}")
        return
    else:
        if app.config['ANON_ACCESS']:
            login_user(app.user_datastore.find_user(_id=app.config['ANON_USER_ID']))
            app.logger.debug('Anon access to service')
            return
        else:
            abort(401, description="Not authenticated")


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(f"/{uuid4()}")


@bp.route('/<code_id>')
def index_id(code_id):
    if code_id not in current_user.tasks and not app.config['ANON_ACCESS']:
        abort(404, description=f"Don't have access to code {code_id}")
    code = DBManager.get_code(code_id=code_id)
    if code:
        return render_template('index.html', txt_code=code.code)
    else:
        return render_template('index.html', txt_code='; Put your code here.')


@bp.route('/save/<code_id>', methods = ["POST"])
def save_code(code_id):
    source_code = request.form.get('code', '')
    breakpoints = request.form.get('breakpoints', '[]')
    arch =  request.form.get('arch', 'x86_64')

    DBManager.create_code(code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch)
    
    return { "success_save" : True }


@bp.route('/compile/<code_id>', methods = ["POST"])
def compile(code_id):
    source_code = request.form.get('code', '')
    breakpoints = request.form.get('breakpoints', '[]')
    arch =  request.form.get('arch', 'x86_64')

    DBManager.create_code(code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch)

    try:
        sm.save_code(code_id, source_code)
    except OSError as e:
        app.logger.error(e)

    # Compiling code from file into file with same name (see ASManager.compile())
    as_flag, as_logs_stderr, as_logs_stdout = ASManager.compile(sm.get_code_file_path(code_id), arch)
    as_logs = as_logs_stderr + as_logs_stdout

    app.logger.info(f'Compile {code_id}: success_build - {as_flag}')
    app.logger.info(f'Compile {code_id}: build_logs\n{as_logs.decode("utf-8")}')

    return { "success_build": as_flag, "build_logs": as_logs.decode("utf-8") }


@bp.route('/run/<code_id>', methods = ["POST"])
def run(code_id):
    code = sm.get_code(code_id)
    source_code = request.form.get('code', '')
    arch =  request.form.get('arch', 'x86_64')

    if not sm.is_code_exists(code_id):
        return { "success_run": False, "run_logs": f"Code not exists" }

    bin_file = sm.get_code_file_path(code_id) + ".bin"

    if not os.path.isfile(bin_file):
        return { "success_run": False, "run_logs": f"Code not compiled" }
    qproc = QemuUserProcess(bin_file, arch)
    qproc.add_process(code_id, bin_file, arch)
    qproc.run(code_id)

    rsuccess = True
    if qproc.get_pids(code_id)[0] == -1:
        rsuccess = False
        rlog = "Target executable was not run"
    else:
        rlog = "Exit code: {0}".format(qproc.get_status(code_id))

    if qproc.get_status(code_id) != 0:
        rsuccess = False

    return { "success_run": rsuccess, "run_logs": rlog }


@bp.route('/hexview/<code_id>', methods = ["GET", "POST"])
def hexview(code_id):
    error_msg = '<No code for hexview!>'
    if request.method == "POST":
        source_code = request.form.get('hexview', '')
        code = DBManager.get_code(code_id=code_id)
        if code:
            code.code = source_code
            code.save()
        return render_template('hexview.html', result=hexdump(source_code or error_msg))
    else:
        code = DBManager.get_code(code_id=code_id)
        if code:
            return render_template('hexview.html', result=hexdump(code.code or error_msg))
        else:
            return 'No such code_id', 404


@bp.route('/debug/<code_id>', methods = ["POST"])
def debug(code_id):
    command = request.form.get('debug_command', '')
    for e in DebugCommands:
        if command == e.value:
            return e.name + ' ' + str(code_id)
    return f'No debug such debug command: {command}', 404
