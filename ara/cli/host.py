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

import json
import logging
import six

from cliff.lister import Lister
from cliff.show import ShowOne
from ara import models
from ara.fields import Field

LIST_FIELDS = (
    Field('ID'),
    Field('Name'),
    Field('Playbook ID', 'playbook.id'),
    Field('Latest facts', 'facts.timestamp')
)

SHOW_FIELDS = (
    Field('ID'),
    Field('Name'),
    Field('Playbook ID', 'playbook.id'),
    Field('Playbook Path', 'playbook.path'),
    Field('Latest facts', 'facts.timestamp')
)


class HostList(Lister):
    """Returns a list of hosts"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(HostList, self).get_parser(prog_name)
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Show hosts associated with a specified playbook',
        )
        g.add_argument(
            '--all', '-a',
            action='store_true',
            help='List all hosts in the database',)
        return parser

    def take_action(self, args):
        hosts = (models.Host.query
                 .order_by(models.Host.name))

        if args.playbook:
            hosts = (hosts
                     .filter_by(playbook_id=args.playbook))

        return [[field.name for field in LIST_FIELDS],
                [[field(host) for field in LIST_FIELDS]
                 for host in hosts]]


class HostShow(ShowOne):
    """Show details of a host"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(HostShow, self).get_parser(prog_name)
        parser.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Show host associated with the given playbook',
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Host id (or name when using --playbook) to show',
        )
        return parser

    def take_action(self, args):
        try:
            if args.playbook:
                host = (models.Host.query
                        .filter_by(playbook_id=args.playbook)
                        .filter((models.Host.id == args.host) |
                                (models.Host.name == args.host)).one())
            else:
                host = (models.Host.query
                        .filter_by(id=args.host).one())
        except (models.NoResultFound, models.MultipleResultsFound):
            raise RuntimeError('Host %s could not be found' % args.host)

        return [[field.name for field in SHOW_FIELDS],
                [field(host) for field in SHOW_FIELDS]]


class HostFacts(ShowOne):
    """Show facts for a host"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(HostFacts, self).get_parser(prog_name)
        parser.add_argument(
            '--playbook', '-b',
            metavar='<playbook-id>',
            help='Find host associated with the given playbook',
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Host id (or name when using --playbook) to show facts for',
        )
        parser.add_argument(
            'fact',
            nargs='*',
            metavar='<fact>',
            help='Show only named fact(s)',
        )
        return parser

    def take_action(self, args):
        try:
            if args.playbook:
                host = (models.Host.query
                        .filter_by(playbook_id=args.playbook)
                        .filter((models.Host.id == args.host) |
                                (models.Host.name == args.host)).one())
            else:
                host = (models.Host.query
                        .filter_by(id=args.host).one())
        except (models.NoResultFound, models.MultipleResultsFound):
            raise RuntimeError('Host %s could not be found' % args.host)

        if not host.facts:
            raise RuntimeError('No facts available for host %s' % args.host)

        facts = ((k, v) for k, v in
                 six.iteritems(json.loads(host.facts.values))
                 if not args.fact or k in args.fact
                 )
        return zip(*sorted(facts))
