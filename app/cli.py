from app import app, db
from app.models import User

import click


@app.cli.command("create-admin")
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin(username, password):
    with app.app_context():
        user = User(username=username, full_name=username, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
