from datetime import datetime, timedelta
from flask import Blueprint, make_response, render_template, request, current_app, abort
from flask_security import roles_accepted
from uuid import uuid4
from urllib.parse import unquote

from app.core.db.manager import DBManager


log_bp = Blueprint('logs', __name__, url_prefix='/logs')
bp = log_bp


@bp.route('/', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def logs_page():
    return render_template('pages/logs.html')


@bp.route('/<log_id>', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def log_page(log_id):
    log = DBManager.get_log_by_id(log_id)
    if log:
        return render_template('pages/log.html', log=log)
    else:
        current_app.logger.debug(f'No such log_id {log_id}')
        abort(404)


@bp.route('/get_filtered', methods=['GET', 'POST'])
@roles_accepted('teacher', 'admin')
def filter_logs():
    try:
        pathname = unquote(request.args.get('pathname', ''))
        message = request.args.get('message', None)
        levelname = request.args.get('levelname', None)
        time = request.args.get('time', None)
        limit = request.args.get('limit', None)
        offset = request.args.get('offset', None)
        sort = request.args.get('sort', None)
        order = request.args.get('order', None)

        query = {}

        if time:
            try:
                time = datetime.strptime(time, "%Y-%m-%d")
            except:
                pass
            else: 
                query["time__gte"] = time
                query["time__lte"] = time + timedelta(days=1)
        if pathname:
            query["pathname"] = pathname
        if levelname:
            query["levelname"] = levelname
        if message:
            query["message"] = {'$regex': "{}".format(message), '$options': "$i"}

        logs, count = DBManager().get_filter_logs(query=query, limit=int(limit), offset=int(offset), sort=sort, order=order)

        response = {
            'total': count,
            'rows':[{
                    "_id": ob._id,
                    "time": str(ob.time),
                    "levelname": ob.levelname,
                    "message": ob.message,
                    "lineno": ob.lineno,
                    "pathname": ob.pathname
                } for ob in logs]
        }
    except Exception as e:
        current_app.logger.error(e)
        abort(400)
    else:
        return response
