"""Table for NAS ports

Revision ID: e76a7f120db0
Revises: 6c431b45dfe0
Create Date: 2019-11-21 08:42:10.566995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e76a7f120db0'
down_revision = '6c431b45dfe0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('nas_port',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('username', sa.Unicode(length=64), nullable=False),
                    sa.Column('nas_port', sa.Unicode(length=64), nullable=True))


def downgrade():
    op.drop_table('nas_port')
