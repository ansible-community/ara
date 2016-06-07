#   Copyright Red Hat, Inc. All Rights Reserved.
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
#

import logging

from cliff.lister import Lister
from cliff.show import ShowOne
from cliff.command import Command
from ara import models
from ara.models import db
from ara.fields import Field

LIST_FIELDS = (
    Field('ID'),
    Field('Path'),
    Field('Time Start'),
    Field('Duration'),
    Field('Complete'),
)

SHOW_FIELDS = (
    Field('ID'),
    Field('Path'),
    Field('Time Start'),
    Field('Time End'),
    Field('Duration'),
    Field('Complete'),
)


class PlaybookList(Lister):
    """Returns a list of playbooks"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookList, self).get_parser(prog_name)
        parser.add_argument(
            '--incomplete', '-I',
            action='store_true',
            help='Only show incomplete playbook runs',
        )
        parser.add_argument(
            '--complete', '-C',
            action='store_true',
            help='Only show incomplete playbook runs',
        )
        return parser

    def take_action(self, args):
        playbooks = (models.Playbook.query
                     .order_by(models.Playbook.time_start))

        if args.incomplete:
            playbooks = playbooks.filter_by(complete=False)
        if args.complete:
            playbooks = playbooks.filter_by(complete=True)

        return [[field.name for field in LIST_FIELDS],
                [[field(playbook) for field in LIST_FIELDS]
                 for playbook in playbooks]]


class PlaybookShow(ShowOne):
    """Show details of a playbook"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookShow, self).get_parser(prog_name)
        parser.add_argument(
            'playbook_id',
            metavar='<playbook-id>',
            help='Playbook to show',
        )
        return parser

    def take_action(self, args):
        playbook = models.Playbook.query.get(args.playbook_id)
        if playbook is None:
            raise RuntimeError('Playbook %s could not be found' %
                               args.playbook_id)
        return [[field.name for field in SHOW_FIELDS],
                [field(playbook) for field in SHOW_FIELDS]]


class PlaybookDelete(Command):
    """Delete playbooks from the database."""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookDelete, self).get_parser(prog_name)
        parser.add_argument(
            '--ignore-errors', '-i',
            action='store_true',
            help='Do not exit if a playbook cannot be found')
        parser.add_argument(
            '--incomplete', '-I',
            action='store_true',
            help='Delete all incomplete playbook runs',
        )
        parser.add_argument(
            'playbook_id',
            nargs='*',
            metavar='<playbook-id>',
            help='Playbook(s) to delete',
        )
        return parser

    def take_action(self, args):
        if not args.playbook_id and not args.incomplete:
            raise RuntimeError('Nothing to delete')

        if args.playbook_id and args.incomplete:
            raise RuntimeError('You may not use --incomplete with '
                               'a list of playbooks')

        if args.incomplete:
            pids = (playbook.id for playbook in
                    models.Playbook.query.filter_by(complete=False))
        else:
            pids = []
            for pid in args.playbook_id:
                res = models.Playbook.query.get(pid)
                if res is None:
                    if args.ignore_errors:
                        self.log.warning('Playbook %s does not exist '
                                         '(ignoring)' % pid)
                    else:
                        raise RuntimeError('Playbook %s does not exist' % pid)
                else:
                    pids.append(pid)

        for pid in pids:
            self.log.warning('deleting playbook %s', pid)
            playbook = models.Playbook.query.get(pid)
            db.session.delete(playbook)

        db.session.commit()
