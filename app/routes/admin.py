from app import app, db

from flask import abort
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms.fields import PasswordField, SelectField, TextAreaField

from app.models import Problem, Submission, User, Assignment
from runner.checkerlib import Checker

class ProtectedModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


class ArchSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "choices": app.config["ARCHS"]})


class CheckerSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "choices": list(Checker._all_checkers)})


class UserView(ProtectedModelView):
    column_exclude_list = ["password_hash", "lti_tool_consumer_guid", "lti_user_id"]
    form_excluded_columns = ["password_hash", "assignments"]

    form_extra_fields = {
        "new_password": PasswordField("New password", description="if you want to update user's password, type it here")
    }

    def __init__(self):
        super().__init__(User, db.session, endpoint="admin_users", url="users")

    def on_model_change(self, form, model, is_created):
        if form.new_password.data:
            model.set_password(form.new_password.data)
        return super().on_model_change(form, model, is_created)


class AssignmentView(ProtectedModelView):
    column_exclude_list = ["source_code", "arch", "lti_assignment_id", "lti_callback_url"]
    form_excluded_columns = ["submissions"]
    form_overrides = {
        "arch": ArchSelectField,
        "source_code": TextAreaField
    }

    def __init__(self):
        super().__init__(Assignment, db.session, endpoint="admin_codes", url="assignments")


class ProblemView(ProtectedModelView):
    column_exclude_list = ["statement", "checker_config_json"]
    form_excluded_columns = ["assignments"]
    form_overrides = {
        "checker_name": CheckerSelectField,
        "statement": TextAreaField
    }

    def __init__(self):
        super().__init__(Problem, db.session, endpoint="admin_problems", url="problems")


class SubmissionView(ProtectedModelView):
    column_exclude_list = ["source_code"]
    form_overrides = {
        "arch": ArchSelectField,
        "source_code": TextAreaField
    }

    def __init__(self):
        super().__init__(Submission, db.session, endpoint="admin_submissions", url="submissions")


class AdminIndex(AdminIndexView):
    @expose("/")
    def index(self):
        if current_user.is_authenticated and current_user.is_admin:
            return super().index()
        abort(403)


admin = Admin(app, template_mode="bootstrap4", index_view=AdminIndex())
admin.add_views(UserView(), ProblemView(), AssignmentView(), SubmissionView())
