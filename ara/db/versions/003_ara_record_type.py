"""ara_record type

Revision ID: 2a0c6b92010a
Revises: e8e78fd08bf2
Create Date: 2016-11-19 09:48:49.231279

"""
# flake8: noqa
# revision identifiers, used by Alembic.
revision = '2a0c6b92010a'
down_revision = 'e8e78fd08bf2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('data', sa.Column('type', sa.String(length=255), nullable=True))
    ### end Alembic commands ###


def downgrade():
    op.drop_column('data', 'type')
    ### end Alembic commands ###
