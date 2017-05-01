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

import json
import logging
import os
import sys

from ara import models
from cliff.command import Command
from flask_frozen import Freezer, walk_directory
from flask_frozen import MissingURLGeneratorWarning
from junit_xml import TestCase
from junit_xml import TestSuite
from warnings import filterwarnings


class GenerateHtml(Command):
    """ Generates a static tree of the web application """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GenerateHtml, self).get_parser(prog_name)
        parser.add_argument(
            'path',
            metavar='<path>',
            help='Path where the static files will be built in',
        )
        parser.add_argument(
            '--playbook',
            metavar='<playbook>',
            nargs='+',
            help='Only include the specified playbooks in the generation.',
            required=False,
            default=None,
        )
        return parser

    def take_action(self, args):
        self.app.ara.config['FREEZER_DESTINATION'] = os.path.abspath(args.path)

        if args.playbook is not None:
            self.app.ara.config['ARA_PLAYBOOK_OVERRIDE'] = args.playbook

        self.log.warn('Generating static files at %s...', args.path)
        if self.app.ara.config['ARA_IGNORE_EMPTY_GENERATION']:
            filterwarnings('ignore', '.*', MissingURLGeneratorWarning)
        freezer = Freezer(self.app.ara)

        # Patternfly fonts are called from inside the CSS and are therefore
        # not automatically found by flask-frozen. We need to generate URLs
        # for the fonts.
        patternfly = self.app.ara.config['XSTATIC']['patternfly']

        @freezer.register_generator
        def serve_static_packaged():
            for font in walk_directory(os.path.join(patternfly, 'fonts')):
                yield dict(
                    module='patternfly',
                    filename='fonts/%s' % font
                )
        freezer.freeze()

        print('Done.')


class GenerateJunit(Command):
    """ Generate junit stream from ara data """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GenerateJunit, self).get_parser(prog_name)
        parser.add_argument(
            'output_file',
            metavar='<output file>',
            help='The file to write the junit xml to. Use "-" for stdout.',
        )
        parser.add_argument(
            '--playbook',
            metavar='<playbook>',
            nargs='+',
            help='Only include the specified playbooks in the generation.',
            required=False,
            default=None,
        )

        return parser

    def take_action(self, args):
        test_cases = []
        if args.playbook is not None:
            playbooks = args.playbook
            results = (models.TaskResult().query
                       .join(models.Task)
                       .filter(models.TaskResult.task_id == models.Task.id)
                       .filter(models.Task.playbook_id.in_(playbooks)))
        else:
            results = models.TaskResult().query.all()

        for result in results:
            task_name = result.task.name
            if not task_name:
                task_name = result.task.action
            additional_results = {
                'host': result.host.name,
                'playbook_path': result.task.playbook.path
            }
            result_str = json.dumps(additional_results)
            test_path = \
                u'{playbook_file}.{play_name}'.format(
                    playbook_file=os.path.basename(result.task.playbook.path),
                    play_name=result.task.play.name)
            test_case = TestCase(
                name=task_name,
                classname=test_path,
                elapsed_sec=result.duration.seconds,
                stdout=result_str)
            if result.status == 'skipped':
                test_case.add_skipped_info(message=result.result)
            elif (result.status in ('failed', 'unreachable') and
                    result.ignore_errors is False):
                test_case.add_failure_info(message=result.result)
            test_cases.append(test_case)
        test_suite = TestSuite('Ansible Tasks', test_cases)

        xml_string = test_suite.to_xml_string([test_suite])
        if args.output_file == '-':
            sys.stdout.write(xml_string.encode(sys.stdout.encoding or 'utf-8'))
        else:
            with open(args.output_file, 'w') as f:
                f.write(xml_string.encode('utf-8'))
