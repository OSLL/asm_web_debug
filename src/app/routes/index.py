from flask import Blueprint, make_response, render_template

index_bp = Blueprint('index', __name__)
bp = index_bp


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', text="Button not pressed")

@bp.route('/index/<string:text>')
def index_deb(text):
    return render_template('index.html', text = text + ' pressed')

@bp.route('/run_code')
def run_code():
    return render_template('index.html', text="Button 'Run' pressed")

@bp.route('/debug')
def debug():
    return render_template('index.html', text="Button 'Debug' pressed")

@bp.route('/compile')
def compile():
    return render_template('index.html', text="Button 'Compile' pressed")

@bp.route('/hex_view')
def hex_view():
    return render_template('hex_view.html', text="Button 'Open binary in HEX view' pressed")
    
@bp.route('/check')
def check():
    return render_template('index.html', text="Button 'Check' pressed")

@bp.route('/solutions')
def solutions():
    return render_template('solutions.html')

@bp.route('/solutions/<int:id>')
def solution(id):
    return render_template('solution.html', id=id)

