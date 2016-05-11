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

import os

ARA_DIR = os.environ.get('ARA_DIR', os.path.expanduser('~/.ara'))

DEFAULT_ARA_LOG_LEVEL = os.environ.get('ARA_LOG_LEVEL', 'DEBUG')
DEFAULT_ARA_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATABASE_PATH = os.path.join(ARA_DIR, 'ansible.sqlite')
DEFAULT_DATABASE = 'sqlite:///{}'.format(DEFAULT_DATABASE_PATH)
DEFAULT_PORT = 5000
