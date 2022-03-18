from flask import Blueprint, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
 
class Solution:
    id = 1
    task = "Task"


def getSolutionBy(id):
    #get solution by id from db
    return Solution()


solution_bp = Blueprint('solution', __name__)
bp = solution_bp

@bp.route('/solutions/<int:id>', methods=['GET', 'POST'])
def index(id):
    solution = getSolutionBy(id)
    return render_template('pages/solution.html', data=solution)