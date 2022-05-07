import logging
from flask import Blueprint, render_template, request, current_app as app, redirect, abort
from flask_login import current_user, login_user
from uuid import uuid4
import os
import subprocess

from app.core.db.manager import DBManager
from app.core.db.utils import code_to_dict
from app.core.utils.hex import hexdump
from app.response import Response



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


@bp.route('/<code_id>')
def index_id(code_id):
    if code_id not in current_user.tasks and not app.config['ANON_ACCESS']:
        abort(404, description=f"Don't have access to code {code_id}")
    code = DBManager.get_code(code_id=code_id)
    if code:
        return render_template('pages/index.html', code=code_to_dict(code))
    else:
        return render_template('pages/index.html')


@bp.route('/save/<code_id>', methods = ["POST"])
def save_code(code_id):
    source_code = request.form.get('code', '')
    breakpoints = request.form.get('breakpoints', '[]')
    arch =  request.form.get('arch', 'x86_64')

    DBManager.create_code(code_id=code_id, source_code=source_code, breakpoints=breakpoints, arch=arch)

    return Response(success_save=True)


@bp.route('/savesolution/<code_id>', methods = ["POST"])
def save_solution(code_id):
    _datetime = datetime.datetime.now()
    feedback = request.form.get('feedback', '')
    task_id = request.form.get('task', '')
    LTI_session = request.form.get('LTI_session:', '')
    if task_id == 'test':
        DBManager.create_task('1', 'First', 'test', {'A': 'B'})
        task_id = '1'
    task = DBManager.get_task(task_id)
    code = DBManager.get_code(code_id)

    DBManager.create_solution(solution_id=code_id, datetime=_datetime, feedback=feedback, task=task, LTI_session=LTI_session, codes=code)

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
