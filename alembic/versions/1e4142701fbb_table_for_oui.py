"""Table for OUI

Revision ID: 1e4142701fbb
Revises: e76a7f120db0
Create Date: 2019-11-25 14:36:33.114792

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import Sequence, CreateSequence

# revision identifiers, used by Alembic.
revision = '1e4142701fbb'
down_revision = 'e76a7f120db0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(CreateSequence(Sequence('device_oui_id_seq')))
    op.create_table('device_oui',
                    sa.Column('id', sa.Integer(), autoincrement=True,
                              nullable=True),
                    sa.Column('oui', sa.TEXT(), autoincrement=False,
                              nullable=False),
                    sa.Column('vlan', sa.TEXT(), autoincrement=False,
                              nullable=True),
                    sa.Column('description', sa.TEXT(), autoincrement=False,
                              nullable=True),
                    sa.PrimaryKeyConstraint('id', name='device_oui_pkey'))
    op.alter_column('device_oui', 'id', nullable=False,
                    server_default=sa.text("nextval('device_oui_id_seq'::regclass)"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('device_oui')
    # ### end Alembic commands ###
