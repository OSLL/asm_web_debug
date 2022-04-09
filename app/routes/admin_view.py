from flask import Blueprint, render_template

adminview_bp = Blueprint('admin_view', __name__)
bp = adminview_bp

@bp.route('/admin_view', methods=['GET', 'POST'])
def index():
    # here should be a function, which return system information to some var
    return render_template('pages/admin_view.html', data=[])