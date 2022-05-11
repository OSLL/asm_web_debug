import datetime
from flask import Blueprint, render_template
from app.core.db.manager import DBManager

dbmanager = DBManager()

class Task:
    def __init__(self):
        self.id = 0
        self.course = "course"
        self.condition = "condition" 
        self.created = datetime.datetime.now()
        self.changed = datetime.datetime.now()
        self.parameters = "Object"

class Solution:
    def __init__(self):
        self.id = 0
        self._datetime = datetime.datetime.now()
        self.feedback = "feedback"
        self.task = Task()
        self.LTI_session = "LTI session"
        self.code_id = "code_id"

solution_bp = Blueprint('solution', __name__)
bp = solution_bp

@bp.route('/solutions/<int:id>', methods=['GET', 'POST'])
def index(id):
    solution = dbmanager.get_solution(id)
    if(solution == None):
        solution = Solution()
    return render_template('pages/solution.html', data=solution)
