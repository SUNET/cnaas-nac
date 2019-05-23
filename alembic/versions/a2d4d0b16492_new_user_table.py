"""New user table

Revision ID: a2d4d0b16492
Revises: 
Create Date: 2019-05-23 13:28:53.324525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2d4d0b16492'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.Unicode(length=255), nullable=False),
    sa.Column('description', sa.Unicode(length=255), nullable=True),
    sa.Column('attributes', sa.Unicode(length=1024), nullable=True),
    sa.Column('user', sa.Boolean, nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
