import datetime
from tokenize import String

from flask import Blueprint, render_template, redirect, request
#from app.core.db.manager import get_solution
class Task:
    def __init__(self):
        self.id = 1
        self.course = "course"
        self.condition = "condition" 
        self.created = datetime.datetime.now()
        self.changed = datetime.datetime.now()
        self.parameters = "Object"

class Solution:
    def __init__(self):
        self.id = 1
        self._datetime = datetime.datetime.now()
        self.feedback = "feedback"
        self.task = Task()
        self.LTI_session = "LTI session"
    # def __init__(self, solution):
    #     self.id = solution._id
    #     self.datetime = solution.datetime
    #     self.feedback = solution.feedback
    #     self.task = solution.task
    #     self.LTI_session = solution.LTI_session


def getSolutionBy(id):
    #get solution by id from db
    #return Solution(get_solution(id))
    return Solution()


solution_bp = Blueprint('solution', __name__)
bp = solution_bp

@bp.route('/solutions/<int:id>', methods=['GET', 'POST'])
def index(id):
    solution = getSolutionBy(id)
    return render_template('pages/solution.html', data=solution)