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
import six

from cliff.lister import Lister
from cliff.show import ShowOne
from ara import app, db, models, utils


class PlaybookList(Lister):
    """Returns a list of playbooks"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(PlaybookList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        playbooks = models.Playbook.query.all()

        fields = (
            ('ID',),
            ('Path',),
            ('Time Start',),
            ('Time End',),
        )

        return ([field[0] for field in fields],
                [[utils.get_field_attr(playbook, field)
                  for field in fields] for playbook in playbooks])


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

    def take_action(self, parsed_args):
        playbook = models.Playbook.query.get(parsed_args.playbook_id)

        data = {
            'ID': playbook.id,
            'Path': playbook.path,
            'Time Start': playbook.time_start,
            'Time End': playbook.time_end
        }

        return zip(*sorted(six.iteritems(data)))
