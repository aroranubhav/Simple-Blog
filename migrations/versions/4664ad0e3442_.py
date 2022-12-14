"""empty message

Revision ID: 4664ad0e3442
Revises: db8a687cf95a
Create Date: 2022-10-19 16:14:08.869665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4664ad0e3442'
down_revision = 'db8a687cf95a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_name', sa.String(length=20), nullable=False))
    op.create_unique_constraint(None, 'users', ['user_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'user_name')
    # ### end Alembic commands ###
