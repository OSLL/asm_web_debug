from flask import Blueprint, render_template, redirect, request

solutions_bp = Blueprint('solutions', __name__)
bp = solutions_bp

tasks_data = [
        [0, "First", 1, 16,"Very interesting description for First task!","Very interesting examples for First task!"],
        [1, "Second", 5, 32,"Very interesting description for Second task!","Very interesting examples for Second task!"],
        [2, "Third", 3, 16,"Very interesting description for Third task!","Very interesting examples for Third task!"],
        [3, "Fourth", 2, 32,"Very interesting description for Fourth task!","Very interesting examples for Fourth task!"],
        [4, "Fifth", 4, 16,"Very interesting description for Fifth task!","Very interesting examples for Fifth task!"],
    ]

solutions_data = [
        [0, "01.12.2021", "12:40", "Success!", 3, "4365342"],
        [1, "02.12.2021", "13:56", "Error in 5 test!", 2, "3563473"],
        [2, "03.12.2021", "16:08", "Success!", 0, "2836953"],
        [3, "04.12.2021", "17:25", "Error in 2 test!", 4, "0398461"],
        [4, "05.12.2021", "19:44", "Syntax error!", 1, "6934812"],
    ]


@bp.route('/solutions', methods=['GET', 'POST'])
def index():
    return render_template('pages/solutions.html', solutions=solutions_data, tasks=tasks_data)

