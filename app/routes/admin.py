import secrets
from app import app, db
from app.models import ToolConsumer, User

import functools
from flask import abort, render_template, request
from flask_login import current_user


def admin_required(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return wrapped


@app.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("pages/admin/users.html", users=users)


@app.route("/admin/lms")
@admin_required
def admin_lms():
    tool_consumer = ToolConsumer.query.filter_by(in_use=False).first()
    if not tool_consumer:
        tool_consumer = ToolConsumer(
            consumer_key=secrets.token_hex(8),
            consumer_secret=secrets.token_urlsafe(),
            in_use=False
        )
        db.session.add(tool_consumer)
        db.session.commit()

    proto = request.headers.get("X-Forwarded-Proto", "http")
    tool_url = f"{proto}://{request.host}/lti"

    tool_consumers = ToolConsumer.query.filter_by(in_use=True).all()

    return render_template("pages/admin/lms.html",
        tool_url=tool_url,
        consumer_key=tool_consumer.consumer_key,
        consumer_secret=tool_consumer.consumer_secret,
        tool_consumers=tool_consumers
    )
