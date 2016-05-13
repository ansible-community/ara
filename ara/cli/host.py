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
from ara import models, utils

FIELDS = (
    ('ID',),
    ('Name',),
)


class HostList(Lister):
    """Returns a list of hosts"""
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        hosts = models.Host.query.all()
        return utils.fields_from_iter(FIELDS, hosts)


class HostShow(ShowOne):
    """Show details of a host"""
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(HostShow, self).get_parser(prog_name)
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Host name or id to show',
        )
        return parser

    def take_action(self, parsed_args):
        host = (models.Host.query
                .filter((models.Host.id == parsed_args.host) |
                        (models.Host.name == parsed_args.host)).one())
        return utils.fields_from_object(FIELDS, host)
