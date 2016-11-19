"""ara_record data

Revision ID: e8e78fd08bf2
Revises: da9459a1f71c
Create Date: 2016-11-01 18:02:38.685998

"""
# flake8: noqa
# revision identifiers, used by Alembic.
revision = 'e8e78fd08bf2'
down_revision = 'da9459a1f71c'

import ara
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('data',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('playbook_id', sa.String(length=36), nullable=True),
    sa.Column('key', sa.String(length=255), nullable=True),
    sa.Column('value', ara.models.CompressedText((2 ** 32) - 1), nullable=True),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('playbook_id', 'key')
    )
    ### end Alembic commands ###


def downgrade():
    op.drop_table('data')
    ### end Alembic commands ###
