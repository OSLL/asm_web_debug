from flask import Blueprint, render_template, redirect, request

tasks_bp = Blueprint('tasks', __name__)
bp = tasks_bp

tasks_data = [
        [0, "First", 1, 16,"Very interesting description for First task!","Very interesting examples for First task!"],
        [1, "Second", 5, 32,"Very interesting description for Second task!","Very interesting examples for Second task!"],
        [2, "Third", 3, 16,"Very interesting description for Third task!","Very interesting examples for Third task!"],
        [3, "Fourth", 2, 32,"Very interesting description for Fourth task!","Very interesting examples for Fourth task!"],
        [4, "Fifth", 4, 16,"Very interesting description for Fifth task!","Very interesting examples for Fifth task!"],
    ]


@bp.route('/tasks', methods=['GET', 'POST'])
def index():
    return render_template('pages/tasks.html', data=tasks_data)


@bp.route('/tasks/remove/<id>', methods=['GET', 'POST'])
def remove(id):
    x=0
    for i in tasks_data:
        if i[0]==int(id):
            tasks_data.pop(x)
        else:
            x+=1
    return redirect('/tasks')


@bp.route('/tasks/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    tasks_data[int(id)][1]=request.form.get("edit_name")
    tasks_data[int(id)][2] = request.form.get("edit_difficulty")
    tasks_data[int(id)][4] = request.form.get("edit_description")
    tasks_data[int(id)][5] = request.form.get("edit_examples")
    return redirect('/tasks')


@bp.route('/tasks/add', methods=['GET', 'POST'])
def add():
    max = 0
    for i in tasks_data:
        if i[0] >max:
            max=i[0]
    tasks_data.append([max+1,
                       request.form.get("edit_name"),
                       request.form.get("edit_difficulty"),
                       0,
                       request.form.get("edit_description"),
                       request.form.get("edit_examples")])
    return redirect('/tasks')
