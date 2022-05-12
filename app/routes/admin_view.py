from flask import Blueprint, render_template, request
from flask_security import roles_accepted
import subprocess

adminview_bp = Blueprint('admin_view', __name__)
bp = adminview_bp

def top():
    return subprocess.run(['top', 'b', '-n', '1'], capture_output=True, text=True)

@bp.route('/admin_view', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def index():
    if request.args.get('updated'):
        return top().stdout
    return render_template('pages/admin_view.html', data=top().stdout)
