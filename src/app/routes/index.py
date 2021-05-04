from flask import Blueprint, make_response, render_template, request, current_app, redirect, abort
from flask_login import current_user, login_user
from flask_security import MongoEngineUserDatastore
from uuid import uuid4

from app.core.asmanager import ASManager
from app.core.db.manager import DBManager
from app.core.source_manager import SourceManager as sm
from app.core.utils.debug_commands import DebugCommands
from app.core.utils.hex import hexdump


index_bp = Blueprint('index', __name__)
bp = index_bp

@bp.before_request
def check_login():
    current_app.logger.debug(current_user)
    if current_user.is_authenticated:
        current_app.logger.info(f"Authenticated user: {current_user.username}")
        pass
    else:
        if current_app.config['ANON_ACCESS']:
            login_user(current_app.user_datastore.find_user(_id=current_app.config['ANON_USER_ID']))
            current_app.logger.debug('Anon access to service')
            return
        else:
            abort(401, description="Not authenticated")


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(f"/{uuid4()}")


@bp.route('/<code_id>')
def index_id(code_id):
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
        current_app.logger.error(e)

    # Compiling code from file into file with same name (see ASManager.compile())
    as_flag, as_logs_stderr, as_logs_stdout = ASManager.compile(sm.get_code_file_path(code_id), arch)
    as_logs = as_logs_stderr + as_logs_stdout

    current_app.logger.info(f'Compile {code_id}: success_build - {as_flag}')
    current_app.logger.info(f'Compile {code_id}: build_logs\n{as_logs.decode("utf-8")}')

    return { "success_build": as_flag, "build_logs": as_logs.decode("utf-8") }


@bp.route('/run/<code_id>', methods = ["POST"])
def run(code_id):
    code = sm.get_code(code_id)
    source_code = request.form.get('code', '')
    arch =  request.form.get('arch', 'x86_64')

    return { "success_run": True, "run_logs": f"Hello world, {arch}!\n\n {code}" }


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
