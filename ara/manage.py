#!/usr/bin/env python
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


from flask_script import commands
from flask_script import Manager
from flask_script import prompt_bool
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from ara.webapp import create_app
from ara.models import db

app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db, directory=app.config['DB_MIGRATIONS'])

# Overwrite the default runserver command to be able to pass a custom host
# and port from the config as the defaults
manager.add_command(
    "runserver",
    commands.Server(host=app.config['ARA_HOST'],
                    port=app.config['ARA_PORT'],
                    processes=8,
                    threaded=False)
)


@manager.command
def createall():
    db.create_all()


@manager.command
def dropall():
    """ Drops all database tables """

    if prompt_bool('Are you sure ? You will lose all your data !'):
        db.drop_all()


def main():
    manager.run()


if __name__ == '__main__':
    main()
