from flask import Blueprint, make_response, render_template, request, current_app, redirect
from uuid import uuid4

from app.core.utils.debug_commands import DebugCommands
from app.core.utils.hex import hexdump

from app.core.db.manager import DBManager

from app.core.source_manager import SourceManager
from app.core.asmanager import ASManager


index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(f"/{uuid4()}")


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
    arch =  request.form.get('arch', 'x86_64')

    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)
        return { "success_save" : False }

    return { "success_save" : True }


@bp.route('/compile/<uuid:code_id>', methods = ["POST"])
def compile(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])
    source_code = request.form.get('code', '')

    #?testing saving to db 
    DBManager.create_codes(code_id = code_id, source_code = source_code, breakpoints = request.form.get('breakpoints'))
    print(DBManager.get_codes('some_id_that_exists'))
    print(DBManager.get_codes_older_than(2))

    arch =  request.form.get('arch', 'x86_64')


    try:
        scc.save_code(code_id, source_code)
    except OSError as e:
        print(e)

    # Compiling code from file into file with same name (see ASManager.compile())
    as_flag, as_logs_stderr, as_logs_stdout = ASManager.compile(scc.get_code_file_path(code_id), arch)
    as_logs = as_logs_stderr + as_logs_stdout

    return { "success_build": as_flag, "build_logs": as_logs.decode("utf-8") }


@bp.route('/run/<uuid:code_id>', methods = ["POST"])
def run(code_id):
    scc = SourceManager(current_app.config['CODES_FOLDER'])
    source_code = request.form.get('code', '')
    arch =  request.form.get('arch', 'x86_64')

    return { "success_run": True, "run_logs": f"Hello world, {arch}!" }


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
