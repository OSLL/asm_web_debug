from flask import Blueprint, render_template, redirect, request
from flask_security import roles_accepted

tasks_bp = Blueprint('tasks', __name__)
bp = tasks_bp

tasks_data = [
        [0, "First", 1, 16,"Very interesting description for First task!", [["a","1"],["b","2"],["c","3"]], [["a","1"],["b","2"],["c","3"]]],
        [1, "Second", 5, 32,"Very interesting description for Second task!", [["a","1"],["b","2"],["c","3"]], [["a","1"],["b","2"],["c","3"]]],
        [2, "Third", 3, 16,"Very interesting description for Third task!", [["a","1"],["b","2"],["c","3"]], [["a","1"],["b","2"],["c","3"]]],
        [3, "Fourth", 2, 32,"Very interesting description for Fourth task!", [["a","1"],["b","2"],["c","3"]], [["a","1"],["b","2"],["c","3"]]],
        [4, "Fifth", 4, 16,"Very interesting description for Fifth task!", [["a","1"],["b","2"],["c","3"]], [["a","1"],["b","2"],["c","3"]]],
    ]


@bp.route('/tasks', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def index():
    return render_template('pages/tasks.html', data=tasks_data)


@bp.route('/tasks/remove/<id>', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def remove(id):
    x=0
    for i in tasks_data:
        if i[0]==int(id):
            tasks_data.pop(x)
        else:
            x+=1
    return redirect('/tasks')



@bp.route('/tasks/edit/', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def edit():
    task_id=request.args.get("id")
    registers_bef=request.args.get("registers").split(",")
    stack_bef = request.args.get("stack").split(",")
    registers=[]
    stack = []
    for i in range(int(len(registers_bef)/2)):
        if registers_bef[i*2]!="":
            registers.append([registers_bef[i*2],registers_bef[i*2+1]])
    for i in range(int(len(stack_bef)/2)):
        if stack_bef[i*2]!="":
            stack.append([stack_bef[i*2],stack_bef[i*2+1]])
    x = 0
    for i in tasks_data:
        if i[0] == int(task_id):
            break;
        else:
            x += 1
    tasks_data[x][1]=request.form.get("edit_name")
    tasks_data[x][2] = request.form.get("edit_difficulty")
    tasks_data[x][4] = request.form.get("edit_description")
    tasks_data[x][5] = registers
    tasks_data[x][6] = stack
    return redirect('/tasks')


@bp.route('/tasks/add/', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def add():
    max = 0
    for i in tasks_data:
        if i[0] >max:
            max=i[0]
            
    registers_bef = request.args.get("registers").split(",")
    stack_bef = request.args.get("stack").split(",")
    registers = []
    stack = []
    for i in range(int(len(registers_bef) / 2)):
        if registers_bef[i * 2] != "":
            registers.append([registers_bef[i * 2], registers_bef[i * 2 + 1]])
    for i in range(int(len(stack_bef) / 2)):
        if stack_bef[i * 2] != "":
            stack.append([stack_bef[i * 2], stack_bef[i * 2 + 1]])

    tasks_data.append([max+1,
                       request.form.get("edit_name"),
                       request.form.get("edit_difficulty"),
                       0,
                       request.form.get("edit_description"),registers,stack])
    return redirect('/tasks')

