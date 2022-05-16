from datetime import datetime
from app import app, db, csrf

from flask import request

from app.models import DebugSession


@app.route("/internal/debug_session_info", methods=["POST"])
@csrf.exempt
def debug_session_info():
    data = request.json
    obj = DebugSession.query.get(data["id"]) if "id" in data else None
    if not obj:
        obj = DebugSession()

    obj.user_id = data["user_id"]
    obj.assignment_id = data["assignment_id"]
    obj.source_code = data["source_code"]
    obj.arch = data["arch"]
    obj.started_at = datetime.fromtimestamp(data["started_at"])
    obj.finished_at = datetime.fromtimestamp(data["finished_at"]) if "finished_at" in data else None
    obj.cpu_time_used = data.get("cpu_time_used")
    obj.memory_used = data.get("memory_used")
    obj.is_interactive = True

    if obj.finished_at:
        obj.real_time_used = (obj.finished_at - obj.started_at).total_seconds()
    else:
        obj.real_time_used = (datetime.now() - obj.started_at).total_seconds()

    db.session.add(obj)
    db.session.commit()

    return { "id": obj.id }

