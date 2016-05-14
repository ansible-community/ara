#   Copyright 2016 Red Hat, Inc. All Rights Reserved.
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

import logging
import os
import pbr.version

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ara.config import *  # NOQA

# Setup version
version_info = pbr.version.VersionInfo('ara')
try:
    __version__ = version_info.version_string()
except AttributeError:
    __version__ = None

# We always create ARA_DIR.  If people want to put a sqlite database
# somewhere else, it's their job to create the necessary directory.
if not os.path.isdir(ARA_DIR):
    os.makedirs(ARA_DIR, mode=0700)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ARA_DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = ARA_SQL_DEBUG
db = SQLAlchemy(app)

LOG = logging.getLogger(__name__)
if ARA_LOG is not None:
    _fmt = logging.Formatter(ARA_LOG_FORMAT)
    _fh = logging.FileHandler(ARA_LOG)
    _fh.setFormatter(_fmt)

    LOG.setLevel(ARA_LOG_LEVEL)
    LOG.addHandler(_fh)

from ara import views, models

LOG.debug('Making sure database tables are created...')
db.create_all()
