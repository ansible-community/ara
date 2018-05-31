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

import datetime
import logging
import os
import six
import sys

from ara import models
from ara import utils
from cliff.command import Command
from flask_frozen import Freezer, walk_directory
from flask_frozen import MissingURLGeneratorWarning
from flask_frozen import NotFoundWarning
from junit_xml import TestCase
from junit_xml import TestSuite
from oslo_utils import encodeutils
from oslo_serialization import jsonutils
from subunit import iso8601
from subunit.v2 import StreamResultToBytes
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
        filterwarnings('ignore', '.*', NotFoundWarning)
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
    """ Generate junit stream from ara data

    Tasks show up in the report as follows:
        'ok': pass
        'failed' with 'EXPECTED FAILURE' in the task name: pass
        'failed' with 'TOGGLE RESULT' in the task name: pass
        'ok' with 'TOGGLE RESULT' in the task name: failure
        'failed' due to an exception: error
        'failed' for other reasons: failure
        'skipped': skipped"
    """
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
            result_str = jsonutils.dumps(additional_results)
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
            elif ((result.status in ('failed', 'unreachable') and
                    result.ignore_errors is False and
                    'EXPECTED FAILURE' not in task_name and
                    'TOGGLE RESULT' not in task_name) or
                    (result.status == 'ok' and 'TOGGLE RESULT' in task_name)):
                test_case.add_failure_info(message=result.result)
            test_cases.append(test_case)
        test_suite = TestSuite('Ansible Tasks', test_cases)

        # TODO: junit_xml doesn't order the TestCase parameters.
        # This makes it so the order of the parameters for the same exact
        # TestCase is not guaranteed to be the same and thus results in a
        # different stdout (or file). This is easily reproducible on Py3.
        xml_string = six.text_type(test_suite.to_xml_string([test_suite]))
        if args.output_file == '-':
            if six.PY2:
                sys.stdout.write(encodeutils.safe_encode(xml_string))
            else:
                sys.stdout.buffer.write(encodeutils.safe_encode(xml_string))
        else:
            with open(args.output_file, 'wb') as f:
                f.write(encodeutils.safe_encode(xml_string))


class GenerateSubunit(Command):
    """ Generate subunit binary stream from ARA data """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GenerateSubunit, self).get_parser(prog_name)
        parser.add_argument(
            'output_file',
            metavar='<output file>',
            help='The file to write the subunit binary stream to. '
                 'Use "-" for stdout.',
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
        # Setup where the output stream must go
        if args.output_file == '-':
            output_stream = sys.stdout
        else:
            output_stream = open(args.output_file, 'wb')

        # Create the output stream
        output = StreamResultToBytes(output_stream)

        # Create the test run
        output.startTestRun()

        if args.playbook is not None:
            playbooks = args.playbook
            results = (models.TaskResult().query
                       .join(models.Task)
                       .filter(models.TaskResult.task_id == models.Task.id)
                       .filter(models.Task.playbook_id.in_(playbooks)))
        else:
            results = models.TaskResult().query.all()

        for result in results:
            # Generate a fixed length identifier for the task
            test_id = utils.generate_identifier(result)

            # Assign the test_status value
            if result.status in ('failed', 'unreachable'):
                if result.ignore_errors is False:
                    test_status = 'xfail'
                else:
                    test_status = 'fail'
            elif result.status == 'skipped':
                test_status = 'skip'
            else:
                test_status = 'success'

            # Determine the play file path
            if result.task.playbook and result.task.playbook.path:
                playbook_path = result.task.playbook.path
            else:
                playbook_path = ''

            # Determine the task file path
            if result.task.file and result.task.file.path:
                task_path = result.task.file.path
            else:
                task_path = ''

            # Assign the file_bytes value
            test_data = {
                'host': result.host.name,
                'playbook_id': result.task.playbook.id,
                'playbook_path': playbook_path,
                'play_name': result.task.play.name,
                'task_action': result.task.action,
                'task_action_lineno': result.task.lineno,
                'task_id': result.task.id,
                'task_name': result.task.name,
                'task_path': task_path
            }
            file_bytes = encodeutils.safe_encode(jsonutils.dumps(test_data))

            # Assign the start_time and stop_time value
            # The timestamp needs to be an epoch, so we need
            # to convert it.
            start_time = datetime.datetime.fromtimestamp(
                float(result.time_start.strftime('%s'))
            ).replace(tzinfo=iso8601.UTC)
            end_time = datetime.datetime.fromtimestamp(
                float(result.time_end.strftime('%s'))
            ).replace(tzinfo=iso8601.UTC)

            # Output the start of the event
            output.status(
                test_id=test_id,
                timestamp=start_time
            )

            # Output the end of the event
            output.status(
                test_id=test_id,
                test_status=test_status,
                test_tags=None,
                runnable=False,
                file_name=test_id,
                file_bytes=file_bytes,
                timestamp=end_time,
                eof=True,
                mime_type='text/plain; charset=UTF8'
            )

        output.stopTestRun()
