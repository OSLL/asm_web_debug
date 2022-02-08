import json
from flask import Blueprint, render_template, request, current_app as app, redirect, abort
from flask_login import current_user

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


@bp.route('/save/<code_id>', methods = ["POST"])
def save_code(code_id):
    source_code = request.form.get('code', '')
    breakpoints = request.form.get('breakpoints', '[]')
    arch =  request.form.get('arch', 'x86_64')

    DBManager.create_code(code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch)

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
