from flask import (
    Blueprint,
    render_template,
    request,
    current_app as app,
    redirect,
    abort,
)
from flask_login import current_user, login_user
from uuid import uuid4
import os
import subprocess

from app.core.compile_manager import CompileManager
from app.core.db.manager import DBManager
from app.core.db.utils import code_to_dict
from app.core.process_manager import UserProcess
from app.core.source_manager import SourceManager as sm
from app.core.utils.hex import hexdump
from app.response import Response


index_bp = Blueprint("index", __name__)
bp = index_bp


@bp.before_request
def check_login():
    if current_user.is_authenticated:
        app.logger.info(f"Authenticated user: {current_user.username}")
        app.logger.debug(f"{current_user.to_json()}")
        return
    else:
        if app.config["ANON_ACCESS"]:
            login_user(app.user_datastore.find_user(_id=app.config["ANON_USER_ID"]))
            app.logger.debug("Anon access to service")
            return
        else:
            abort(401, description="Not authenticated")


@bp.route("/<code_id>")
def index_id(code_id):
    if code_id not in current_user.tasks and not app.config["ANON_ACCESS"]:
        abort(404, description=f"Don't have access to code {code_id}")
    code = DBManager.get_code(code_id=code_id)
    if code:
        return render_template("pages/index.html", code=code_to_dict(code))
    else:
        return render_template("pages/index.html")


@bp.route("/save/<code_id>", methods=["POST"])
def save_code(code_id):
    source_code = request.form.get("code", "")
    breakpoints = request.form.get("breakpoints", "[]")
    arch = request.form.get("arch", "x86_64")

    DBManager.create_code(
        code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch
    )

    return Response(success_save=True)


@bp.route("/compile/<code_id>", methods=["POST"])
def compile(code_id):
    source_code = request.form.get("code", "")
    breakpoints = request.form.get("breakpoints", "[]")
    arch = request.form.get("arch", "x86_64")

    DBManager.create_code(
        code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch
    )

    try:
        sm.save_code(code_id, source_code)
    except OSError as e:
        app.logger.error(e)

    # Compiling code from file into file with same name (see ASManager.compile())
    as_flag, as_logs_stderr, as_logs_stdout = CompileManager.compile(
        sm.get_code_file_path(code_id), arch
    )
    as_logs = as_logs_stderr + as_logs_stdout

    app.logger.info(f"Compile {code_id}: success_build - {as_flag}")
    app.logger.info(f'Compile {code_id}: build_logs\n{as_logs.decode("utf-8")}')

    return Response(success_build=as_flag, build_logs=as_logs.decode("utf-8"))


@bp.route("/run/<code_id>", methods=["POST"])
def run(code_id):
    # code = sm.get_code(code_id)
    source_code = request.form.get("code", "")
    arch = request.form.get("arch", "x86_64")

    if not sm.is_code_exists(code_id):
        return Response(success_run=False, run_logs=f"Code not exists")

    bin_file = sm.get_code_file_path(code_id) + ".bin"

    if not os.path.isfile(bin_file):
        return Response(success_run=False, run_logs=f"Code not compiled")

    if arch != "x86_64":
        return Response(success_run=False, run_logs=f"Arch {arch} not supported!")

    run_result = subprocess.run(["qemu-x86_64", bin_file], capture_output=True)

    if run_result.returncode == 0:
        status = "success"
    else:
        status = run_result.returncode

    return Response(
        success_run=True,
        run_logs=f"STATUS: {status};\nstdout: {run_result.stdout};\nstderr: {run_result.stderr};\n",
    )


@bp.route("/hexview/<code_id>", methods=["GET", "POST"])
def hexview(code_id):
    error_msg = "<No code for hexview!>"
    if request.method == "POST":
        source_code = request.form.get("hexview", "")
        code = DBManager.get_code(code_id=code_id)
        if code:
            code.code = source_code
            code.save()
        return render_template(
            "pages/hexview.html", result=hexdump(source_code or error_msg)
        )
    else:
        code = DBManager.get_code(code_id=code_id)
        if code:
            return render_template(
                "pages/hexview.html", result=hexdump(code.code or error_msg)
            )
        else:
            return "No such code_id", 404
