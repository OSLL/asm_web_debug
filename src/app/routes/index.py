from flask import Blueprint, make_response, render_template, request

import os

from app.core.utils.debug_commands import DebugCommands

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
    # Writing code string to a temporary file
    if not os.path.exists(tmp_dir):
         os.mkdir(tmp_dir)
    tmpfd = open(tmp_dir + tmp_name + ".s", "w")
    if tmpfd == None:
        return request.form.to_dict()
    tmpfd.write(request.form["code"])
    tmpfd.close()

    # Compiling code from temporary file into temporary file with same name (see as_manager.compile())
    arch = "x86_64"

    as_flag, as_logs_stderr, as_logs_stdout = as_manager.compile(tmp_dir + tmp_name + ".s",
								 tmp_dir + tmp_name + ".o",
								 arch)
    logs_as = as_logs_stderr + as_logs_stdout

    ld_flag, ld_logs_stderr, ld_logs_stdout = as_manager.link(as_manager.object_filename,
							      tmp_dir + tmp_name + ".out",
							      arch)
    logs_ld = ld_logs_stderr + ld_logs_stdout

    logs = logs_as + logs_ld

    # Cleaning up
    os.unlink(tmp_dir + tmp_name + ".s")

    return { "success_build": as_flag and ld_flag, "build_logs": logs }


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
