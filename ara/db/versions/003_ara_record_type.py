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
