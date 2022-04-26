from app import app, db
from app.models import User

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
    consumer_key, consumer_secret = list(app.config["LTI_CONSUMERS"].items())[0]
    return render_template("pages/admin/lms.html",
        tool_url=f"{request.url_root}lti",
        consumer_key=consumer_key,
        consumer_secret=consumer_secret
    )
