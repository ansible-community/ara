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

"""Initial Revision

Revision ID: da9459a1f71c
Revises: None
Create Date: 2016-11-01 17:52:04.170217

"""
# flake8: noqa
# revision identifiers, used by Alembic.
revision = 'da9459a1f71c'
down_revision = None

import ara
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('file_contents',
    sa.Column('id', sa.String(length=40), nullable=False),
    sa.Column('content', ara.models.CompressedText((2 ** 32) - 1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('playbooks',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('path', sa.String(255), nullable=True),
    sa.Column('time_start', sa.DateTime(), nullable=True),
    sa.Column('time_end', sa.DateTime(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('files',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('playbook_id', sa.String(length=36), nullable=True),
    sa.Column('path', sa.String(length=255), nullable=True),
    sa.Column('content_id', sa.String(length=40), nullable=True),
    sa.Column('is_playbook', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['content_id'], ['file_contents.id'], ),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('playbook_id', 'path')
    )
    op.create_table('hosts',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('playbook_id', sa.String(length=36), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('playbook_id', 'name')
    )
    op.create_index(op.f('ix_hosts_name'), 'hosts', ['name'], unique=False)
    op.create_table('plays',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('playbook_id', sa.String(length=36), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('sortkey', sa.Integer(), nullable=True),
    sa.Column('time_start', sa.DateTime(), nullable=True),
    sa.Column('time_end', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('host_facts',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('host_id', sa.String(length=36), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('values', sa.Text(length=16777215), nullable=True),
    sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stats',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('playbook_id', sa.String(length=36), nullable=True),
    sa.Column('host_id', sa.String(length=36), nullable=True),
    sa.Column('changed', sa.Integer(), nullable=True),
    sa.Column('failed', sa.Integer(), nullable=True),
    sa.Column('ok', sa.Integer(), nullable=True),
    sa.Column('skipped', sa.Integer(), nullable=True),
    sa.Column('unreachable', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tasks',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('playbook_id', sa.String(length=36), nullable=True),
    sa.Column('play_id', sa.String(length=36), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('sortkey', sa.Integer(), nullable=True),
    sa.Column('action', sa.Text(), nullable=True),
    sa.Column('is_handler', sa.Boolean(), nullable=True),
    sa.Column('file_id', sa.String(length=36), nullable=True),
    sa.Column('lineno', sa.Integer(), nullable=True),
    sa.Column('time_start', sa.DateTime(), nullable=True),
    sa.Column('time_end', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['play_id'], ['plays.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_results',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('task_id', sa.String(length=36), nullable=True),
    sa.Column('host_id', sa.String(length=36), nullable=True),
    sa.Column('status', sa.Enum('ok', 'failed', 'skipped', 'unreachable'), nullable=True),
    sa.Column('changed', sa.Boolean(), nullable=True),
    sa.Column('failed', sa.Boolean(), nullable=True),
    sa.Column('skipped', sa.Boolean(), nullable=True),
    sa.Column('unreachable', sa.Boolean(), nullable=True),
    sa.Column('ignore_errors', sa.Boolean(), nullable=True),
    sa.Column('result', ara.models.CompressedText((2 ** 32) - 1), nullable=True),
    sa.Column('time_start', sa.DateTime(), nullable=True),
    sa.Column('time_end', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    # This is the initial revision, there is no such thing as a downgrade.
    pass
