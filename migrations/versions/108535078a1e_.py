"""empty message

Revision ID: 108535078a1e
Revises: 969e0e899721
Create Date: 2022-04-30 10:11:44.631707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '108535078a1e'
down_revision = '969e0e899721'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('problem', sa.Column('arch', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('problem', 'arch')
    # ### end Alembic commands ###