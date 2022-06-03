from flask import Blueprint, render_template, redirect, request
from flask_security import roles_accepted
from app.core.db.manager import DBManager

tasks_bp = Blueprint('tasks', __name__)
bp = tasks_bp

dbmanager = DBManager()

@bp.route('/tasks', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def index():
    return render_template('pages/tasks.html', tasks=dbmanager.get_all_tasks())


@bp.route('/tasks/remove/<id>', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def remove(id):
    dbmanager.delete_task(id)
    return redirect('/tasks')



@bp.route('/tasks/edit/', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def edit():
    task_id=request.args.get("id")
    registers_bef=request.args.get("registers").split(",")
    stack_bef = request.args.get("stack").split(",")
    task_name = request.form.get("edit_name")
    task_difficulty = request.form.get("edit_difficulty")
    tasks_description = request.form.get("edit_description")
    registers = {}
    stack = {}
    for i in range(int(len(registers_bef)/2)):
        if registers_bef[i*2]!="":
            registers[registers_bef[i * 2]] = registers_bef[i * 2 + 1]
    for i in range(int(len(stack_bef)/2)):
        if stack_bef[i*2]!="":
            stack[stack_bef[i * 2]] = stack_bef[i * 2 + 1]
    task = dbmanager.get_task(task_id)
    dbmanager.create_task(task_id, task_name, tasks_description, task_difficulty, task.success, registers, stack)
    return redirect('/tasks')


@bp.route('/tasks/add/', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def add():
    max_id = 0
    for task in dbmanager.get_all_tasks():
        if task._id > max_id:
            max_id = task._id

    registers_bef = request.args.get("registers").split(",")
    stack_bef = request.args.get("stack").split(",")
    registers = {}
    stack = {}
    for i in range(int(len(registers_bef) / 2)):
        if registers_bef[i * 2] != "":
            registers[registers_bef[i * 2]] = registers_bef[i * 2 + 1]
    for i in range(int(len(stack_bef) / 2)):
        if stack_bef[i * 2] != "":
            stack[stack_bef[i * 2]] = stack_bef[i * 2 + 1]

    dbmanager.create_task(max_id + 1, request.form.get("edit_name"), request.form.get("edit_description"), request.form.get("edit_difficulty"), 0, registers, stack)
    return redirect('/tasks')

@bp.route('/tasks/<id>', methods=['GET'])
def get_task(id):
    task_dict = {}
    task = dbmanager.get_task(id)
    task_dict['_id'] = task._id
    task_dict['name'] = task.name
    task_dict['description'] = task.description
    task_dict['difficulty'] = task.difficulty
    task_dict['success'] = task.success
    task_dict['registers'] = task.registers
    task_dict['stack'] = task.stack
    return task_dict
