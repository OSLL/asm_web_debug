from flask import Blueprint, render_template, redirect, request
from flask_security import roles_accepted

solutions_bp = Blueprint('solutions', __name__)
bp = solutions_bp

solutions_data = [
        [0, 2, "01.12.2021 12:40", "bdc8ef8c-0a37-4ebb-99a1-bcadc01d6cea", "4365342"],
        [1, 3, "02.12.2021 13:56", "04fae989-0fb9-44b1-81f4-4556a6986d10", "3563473"],
        [2, 4, "03.12.2021 16:08", "ac0ecae9-ab15-4d5b-a034-0ab9f9b9bc08", "2836953"],
        [3, 2, "04.12.2021 17:25", "4de69ad8-3df3-472d-9999-f4d50912923d", "0398461"],
        [4, 3, "05.12.2021 19:44", "0863a42f-51c7-4b78-8a50-939ec2a02f1e", "6934812"],
    ]


@bp.route('/solutions', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def index():
    task_id=-1
    if request.args.get('task_id'):
        task_id=int(request.args.get('task_id'))
    return render_template('pages/solutions.html', solutions=solutions_data, id=task_id)
