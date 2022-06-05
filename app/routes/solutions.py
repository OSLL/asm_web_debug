import math

from flask import Blueprint, render_template, redirect, request
from app.core.db.manager import DBManager
from flask_security import roles_accepted

solutions_bp = Blueprint('solutions', __name__)
bp = solutions_bp

@bp.route('/solutions', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def index():
    data = []
    task_id = -1
    page = 0
    amount = 5
    from_date = ""
    to_date = ""
    date_sort = 0
    passed = 0

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
    if request.args.get('amount'):
        try:
            amount = int(request.args.get('amount'))
            if amount < 5:
                amount = 5
        except ValueError:
            amount = 5
    if request.args.get('from_date'):
        from_date = request.args.get('from_date')
    if request.args.get('to_date'):
        to_date = request.args.get('to_date')
    current_app.logger.debug(from_date)
    current_app.logger.debug(to_date)
    if request.args.get('date_sort'):
        try:
            date_sort = int(request.args.get('date_sort'))
            if date_sort != 1 and date_sort != -1:
                date_sort = 0
        except ValueError:
            date_sort = 0
    if request.args.get('passed'):
        try:
            passed = int(request.args.get('passed'))
            if passed != 1 and passed != -1:
                passed = 0
        except ValueError:
            passed = 0
    data, k = DBManager.get_solutions(page=page, amount=amount, task_id=task_id,
                                from_date=from_date, to_date=to_date, date_sort=date_sort, passed=passed)
    pages = math.ceil(k/amount)
    return render_template('pages/solutions.html', solutions=data, cur_page=page, pages=pages, amount=amount, task_id=task_id,
                                from_date=from_date, to_date=to_date, date_sort=date_sort, passed=passed)
