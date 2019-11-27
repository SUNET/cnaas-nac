"""Table for NAS ports

Revision ID: e76a7f120db0
Revises: 6c431b45dfe0
Create Date: 2019-11-21 08:42:10.566995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, Sequence


# revision identifiers, used by Alembic.
revision = 'e76a7f120db0'
down_revision = '538170dfe877'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(CreateSequence(Sequence('nas_port_id_seq')))
    op.create_table('nas_port',
                    sa.Column('id', sa.Integer(), autoincrement=True,
                              nullable=False),
                    sa.Column('username', sa.Unicode(length=64),
                              nullable=False),
                    sa.Column('nas_identifier', sa.Unicode(length=64),
                              nullable=True),
                    sa.Column('nas_port_id', sa.Unicode(length=64),
                              nullable=True),
                    sa.Column('calling_station_id', sa.Unicode(length=64),
                              nullable=True),
                    sa.Column('called_station_id', sa.Unicode(length=64),
                              nullable=True))
    op.alter_column('nas_port', 'id', nullable=False,
                    server_default=sa.text("nextval('nas_port_id_seq'::regclass)"))


def downgrade():
    op.drop_table('nas_port')
