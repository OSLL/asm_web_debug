from flask import Blueprint, render_template, redirect, request
from app.core.db.manager import DBManager
from flask_security import roles_accepted

solutions_bp = Blueprint('solutions', __name__)
bp = solutions_bp
amount = 5

@bp.route('/solutions', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def index():
    pages = int(len(DBManager.get_all_solutions())/amount)+1

    data = []
    task_id = -1
    page = 0

    if request.args.get('task_id'):
        try:
            task_id = int(request.args.get('task_id'))
        except ValueError:
            task_id = -1
    if request.args.get('page'):
        try:
            page = int(request.args.get('page'))
            if page < 0:
                page = 0
        except ValueError:
            page = 0

    data = DBManager.get_solutions(page=page, amount=amount, task_id=task_id)

    return render_template('pages/solutions.html', solutions=data, cur_page=page, pages=pages, task_id=task_id)
