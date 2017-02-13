#   Copyright 2017 Red Hat, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""ansible_version

Revision ID: 22aa8072d705
Revises: 2a0c6b92010a
Create Date: 2017-02-12 20:00:04.269622

"""
# flake8: noqa
# revision identifiers, used by Alembic.
revision = '22aa8072d705'
down_revision = '2a0c6b92010a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('playbooks', sa.Column('ansible_version', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('playbooks', 'ansible_version')
    # ### end Alembic commands ###
