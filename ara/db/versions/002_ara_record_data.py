#  Copyright (c) 2018 Red Hat, Inc.
#
#  This file is part of ARA Records Ansible.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

"""ara_record data

Revision ID: e8e78fd08bf2
Revises: da9459a1f71c
Create Date: 2016-11-01 18:02:38.685998

"""
# flake8: noqa
# revision identifiers, used by Alembic.
revision = 'e8e78fd08bf2'
down_revision = 'da9459a1f71c'

from ara import models
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('data',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('playbook_id', sa.String(length=36), nullable=True),
    sa.Column('key', sa.String(length=255), nullable=True),
    sa.Column('value', models.CompressedData((2 ** 32) - 1), nullable=True),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('playbook_id', 'key')
    )
    ### end Alembic commands ###


def downgrade():
    op.drop_table('data')
    ### end Alembic commands ###
