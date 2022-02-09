from crypt import methods
import json
import logging
from flask import Blueprint, render_template, request, current_app as app, redirect, abort
from flask_login import current_user
import requests

from app.core.db.desc import Submission
from app.core.db.manager import DBManager
from app.core.db.utils import code_to_dict
from app.core.utils.hex import hexdump
from app.response import Response



bp = Blueprint('codes', __name__)

@bp.before_request
def check_login():
    if current_user.is_authenticated:
        app.logger.info(f"Authenticated user: {current_user.username}")
        app.logger.debug(f"{current_user.to_json()}")
    else:
        abort(403, description="Not authenticated")


@bp.route('/<code_id>')
def index_id(code_id):
    code = DBManager.get_code(code_id=code_id)
    if code:
        checker_name = ""
        if code.problem:
            checker_name = code.problem.checker_name
        ide_init = f"IDE({json.dumps(checker_name)});"
        return render_template(
            'pages/ide.html',
            code=code_to_dict(code),
            problem=code.problem,
            ide_init=ide_init
        )
    else:
        return render_template('pages/ide.html')


@bp.route("/submit/<code_id>", methods=["POST"])
def submit_code(code_id):
    code = DBManager.get_code(code_id)
    if code is None or code.problem is None or code.arch not in app.config["ARCHS"]:
        return { "error": "invalid code" }

    api_endpoint = app.config["RUNNER_API"] + "/check"

    result = requests.post(api_endpoint, json={
        "checker_name": code.problem.checker_name,
        "arch": code.arch,
        "source_code": code.code,
        "config": json.loads(code.problem.checker_config)
    })

    if result.status_code != 200:
        logging.error("runner api returned invalid response code")
        return {
            "is_correct": False,
            "comment": "Internal server error"
        }

    result = result.json()
    is_correct = result["ok"]

    if not is_correct:
        error_type = result["error_type"]
        if error_type == "DoesNotCompileError":
            error_message = "Compilation error"
        elif error_type == "WrongAnswerError":
            error_message = "Wrong answer"
        elif error_type == "SignalledError":
            error_message = "Unexpected signal received"
        comment = f"{error_message}: {result['message']}"
    else:
        comment = "Solution accepted"


    submission = Submission(
        user=code.owner,
        problem=code.problem,
        arch=code.arch,
        code=code.code,
        is_correct=is_correct,
        comment=comment
    )

    submission.save()

    return {
        "is_correct": is_correct,
        "comment": comment
    }


@bp.route('/save/<code_id>', methods = ["POST"])
def save_code(code_id):
    source_code = request.form.get('code', '')
    arch = request.form.get('arch', 'x86_64')

    DBManager.create_code(code_id=code_id, source_code=source_code, arch=arch)

    return Response(success_save=True)


@bp.route('/hexview/<code_id>', methods = ["GET", "POST"])
def hexview(code_id):
    error_msg = '<No code for hexview!>'
    if request.method == "POST":
        source_code = request.form.get('hexview', '')
        code = DBManager.get_code(code_id=code_id)
        if code:
            code.code = source_code
            code.save()
        return render_template('pages/hexview.html', result=hexdump(source_code or error_msg))
    else:
        code = DBManager.get_code(code_id=code_id)
        if code:
            return render_template('pages/hexview.html', result=hexdump(code.code or error_msg))
        else:
            return 'No such code_id', 404
