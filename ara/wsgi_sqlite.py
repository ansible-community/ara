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

# A WSGI script to load the ARA web application against a variable database
# location requested over HTTP.
# Can be configured using environment variables (i.e, Apache SetEnv) with the
# following variables:
#
# ARA_WSGI_USE_VIRTUALENV
#   Enable virtual environment usage if ARA is installed in a virtual
#   environment.
#   Defaults to '0', set to '1' to enable.
# ARA_WSGI_VIRTUALENV_PATH
#   When using a virtual environment, where the virtualenv is located.
#   Defaults to None, set to the absolute path of your virtualenv.
# ARA_WSGI_TMPDIR_MAX_AGE
#   This WSGI middleware creates temporary directories which should be
#   discarded on a regular basis to avoid them accumulating.
#   This is a duration, in seconds, before cleaning directories up.
#   Defaults to 3600.
# ARA_WSGI_LOG_ROOT
#   Absolute path on the filesystem that matches the DocumentRoot of your
#   webserver vhost.
#   Defaults to '/srv/static/logs'.
# ARA_WSGI_DATABASE_DIRECTORY
#   Subdirectory in which ARA sqlite databases are expected to reside in.
#   For example, 'ara-report' would expect:
#     http://logserver/some/path/ara-report/ansible.sqlite
#   This variable should match the 'WSGIScriptAliasMatch' pattern of your
#   webserver vhost.
#   Defaults to 'ara-report'

import logging
import os
import re
import shutil
import six
import time

logger = logging.getLogger('ara.wsgi_sqlite')
if not logger.handlers:
    logging.basicConfig(format='%(name)s:%(levelname)s:%(message)s')


def bad_request(environ, start_response, message):
    logger.error('HTTP 400: %s' % message)
    message = """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
        <title>400 Bad Request</title>
        <h1>Bad Request</h1>
        <p>%s</p>""" % message
    status = '400 Bad Request'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    return [message]


def application(environ, start_response):
    # Apache SetEnv variables are passed only in environ variable
    if (int(environ.get('ARA_WSGI_USE_VIRTUALENV', 0)) == 1 and
       environ.get('ARA_WSGI_VIRTUALENV_PATH')):
        # Backwards compatibility, we did not always suffix activate_this.py
        activate_this = environ.get('ARA_WSGI_VIRTUALENV_PATH')
        if 'activate_this.py' not in activate_this:
            activate_this = os.path.join(activate_this, 'bin/activate_this.py')

        if six.PY2:
            execfile(activate_this, dict(__file__=activate_this))  # nosec
        else:
            exec(open(activate_this).read())  # nosec

    TMPDIR_MAX_AGE = int(environ.get('ARA_WSGI_TMPDIR_MAX_AGE', 3600))
    LOG_ROOT = environ.get('ARA_WSGI_LOG_ROOT', '/srv/static/logs')
    DATABASE_DIRECTORY = environ.get(
        'ARA_WSGI_DATABASE_DIRECTORY',
        'ara-report'
    )

    request = environ['REQUEST_URI']
    match = re.search('/(?P<path>.*/{}/)'.format(DATABASE_DIRECTORY), request)
    if not match:
        return bad_request(environ, start_response,
                           'No "/{}/" in URL.'.format(DATABASE_DIRECTORY))

    path = os.path.abspath(os.path.join(LOG_ROOT, match.group('path')))

    # Ensure we don't escape outside LOG_ROOT and we are looking at a
    # valid directory
    if not path.startswith(LOG_ROOT) or not os.path.isdir(path):
        logger.error('Directory access violation: %s' % path)
        return bad_request(environ, start_response, 'No directory found.')

    database = os.path.join(path, 'ansible.sqlite')
    if not os.path.isfile(database):
        return bad_request(environ, start_response, 'No ARA database found.')

    # ARA and Ansible (when loading configuration) both expect a directory
    # they are able to write to, this can be safely discarded.
    # Nothing is read from here and there is therefore no security risks.
    # It needs to be at a known location in order to be able to clean it up
    # so it doesn't accumulate needless directories and files.
    # TODO: ARA 1.0 no longer requires temporary directories, clean this up.
    tmpdir = '/tmp/ara_wsgi_sqlite'  # nosec
    if os.path.exists(tmpdir):
        # Periodically delete this directory to avoid accumulating directories
        # and files endlessly
        now = time.time()
        if now - TMPDIR_MAX_AGE > os.path.getmtime(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)
    os.environ['ANSIBLE_LOCAL_TEMP'] = os.path.join(tmpdir, '.ansible')
    os.environ['ARA_DIR'] = os.path.join(tmpdir, '.ara')

    # Path to the ARA database
    os.environ['ARA_DATABASE'] = 'sqlite:///{}'.format(database)
    # The intent is that we are dealing with databases that already exist.
    # Therefore, we're not really interested in creating the database and
    # making sure that the SQL migrations are done. Toggle that off.
    # This needs to be a string, we're setting an environment variable
    os.environ['ARA_AUTOCREATE_DATABASE'] = 'false'

    msg = 'Request {request} mapped to {database} with root {root}'.format(
        request=request,
        database='sqlite:///{}'.format(database),
        root=match.group('path')
    )
    logger.debug(msg)

    from ara.webapp import create_app
    try:
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(database)
        app.config['APPLICATION_ROOT'] = match.group('path')
        return app(environ, start_response)
    except Exception as e:
        # We're staying relatively vague on purpose to avoid disclosure
        logger.error('ARA bootstrap failure for %s: %s' % (database, str(e)))
        return bad_request(environ, start_response, 'ARA bootstrap failure.')


def main():
    return application
