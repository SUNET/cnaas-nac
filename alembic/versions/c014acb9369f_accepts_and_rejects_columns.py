"""accepts and rejects columns

Revision ID: c014acb9369f
Revises: 4843367789e9
Create Date: 2022-11-07 13:37:59.487725

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c014acb9369f'
down_revision = '4843367789e9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("raduserinfo", sa.Column(
        'accepts', postgresql.BIGINT(), autoincrement=False, nullable=False, server_default="0"))
    op.add_column("raduserinfo", sa.Column(
        'rejects', postgresql.BIGINT(), autoincrement=False, nullable=False, server_default="0"))


def downgrade():
    op.drop_column("raduserinfo", "accepts")
    op.drop_column("raduserinfo", "rejects")
