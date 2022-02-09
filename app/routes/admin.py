from flask import abort, current_app
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.form import SecureForm
from flask_admin.contrib.mongoengine import ModelView
from flask_login import current_user
from wtforms.fields import PasswordField, SelectField

from app.core.db.desc import Code, Problem, Submission, User

class ProtectedModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


class ArchSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "choices": current_app.config["ARCHS"]})


class CheckerSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "choices": list(current_app.config["CHECKERS"])})


class UserView(ProtectedModelView):
    column_exclude_list = ["password", "tasks"]
    form_excluded_columns = ["password"]

    form_extra_fields = {
        "new_password": PasswordField("New password", description="if you want to update user's password, type it here")
    }

    def __init__(self):
        super().__init__(User, endpoint="admin_users", url="users")

    def on_model_change(self, form, model, is_created):
        if form.new_password.data:
            model.set_password(form.new_password.data)
        return super().on_model_change(form, model, is_created)


class CodeView(ProtectedModelView):
    column_exclude_list = ["code"]
    form_overrides = { "arch": ArchSelectField }

    def __init__(self):
        super().__init__(Code, endpoint="admin_codes", url="codes")


class ProblemView(ProtectedModelView):
    column_exclude_list = ["statement", "checker_config"]
    form_overrides = { "checker_name": CheckerSelectField }

    def __init__(self):
        super().__init__(Problem, endpoint="admin_problems", url="problems")


class SubmissionView(ProtectedModelView):
    column_exclude_list = ["code"]
    form_overrides = { "arch": ArchSelectField }

    def __init__(self):
        super().__init__(Submission, endpoint="admin_submissions", url="submissions")


class AdminIndex(AdminIndexView):
    @expose("/")
    def index(self):
        if current_user.is_authenticated and current_user.is_admin:
            return super().index()
        abort(403)


def init_admin(app):
    app.admin = Admin(app, template_mode="bootstrap4", index_view=AdminIndex())
    app.admin.add_views(UserView(), CodeView(), ProblemView(), SubmissionView())
