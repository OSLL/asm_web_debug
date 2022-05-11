from flask import Blueprint, render_template, current_app
from flask_security import roles_accepted
from os.path import isfile
from json import dumps as json_dumps

debug_bp = Blueprint('debug', __name__)
bp = debug_bp


@bp.route('/build', methods=['GET'])
@roles_accepted('teacher', 'admin')
def debug_page():
    return render_template('pages/build_info.html', build_info=load_debug_file(current_app.config['BUILD_FILE']))


def load_debug_file(path):
    def parse_debug_file(str_list):
        config = {}
        for string in str_list:
            current_app.logger.error(string)
            key, value = string.strip().split('=', 1)
            config[key] = value
        return config
        
    if isfile(path):
        with open(path, 'r') as file:
            return json_dumps(parse_debug_file(file.readlines()), sort_keys=True, indent=4)
    else:
        return 'No debug file'
