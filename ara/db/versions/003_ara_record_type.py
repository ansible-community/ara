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
