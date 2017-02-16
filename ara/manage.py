#!/usr/bin/env python
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


from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand

from ara.webapp import create_app
from ara.models import db

app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db, directory=app.config['DB_MIGRATIONS'])


@manager.command
def createall():
    db.create_all()


@manager.command
def dropall():
    """ Drops all database tables """

    if prompt_bool("Are you sure ? You will lose all your data !"):
        db.drop_all()


def main():
    manager.run()


if __name__ == '__main__':
    main()
