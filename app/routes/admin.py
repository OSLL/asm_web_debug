from flask import abort, current_app
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.mongoengine import ModelView
from flask_login import current_user

from app.core.db.desc import Codes, User

class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        abort(403)



class AdminIndex(AdminIndexView):
    @expose("/")
    def index(self):
        if current_user.is_authenticated and current_user.is_admin:
            return super().index()
        abort(403)

def init_admin(app):
    app.admin = Admin(app, name="ASM Web Debug", template_mode="bootstrap4", index_view=AdminIndex())
    app.admin.add_view(ProtectedModelView(User, endpoint="admin_users", url="users"))
    app.admin.add_view(ProtectedModelView(Codes, endpoint="admin_codes", url="codes"))
