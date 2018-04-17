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

"""ansible_metadata

Revision ID: 5716083d63f5
Revises: 22aa8072d705
Create Date: 2017-05-02 13:34:41.150156

"""
# flake8: noqa
# revision identifiers, used by Alembic.
revision = '5716083d63f5'
down_revision = '22aa8072d705'

from ara import models
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('playbooks', sa.Column('options', models.CompressedData((2 ** 32) - 1), nullable=True))
    op.add_column('tasks', sa.Column('tags', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('tasks', 'tags')
    op.drop_column('playbooks', 'options')
    # ### end Alembic commands ###
