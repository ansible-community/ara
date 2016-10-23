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

from debtcollector import moves
from ara.plugins.callbacks import log_ara

long_message = """[WARNING]
ara.callback has been moved to ara.plugins.callbacks in ARA 0.9.2.
Please update your Ansible Callback Plugins path to include
    <path>/ara/plugins/callbacks
instead of:
    <path>/ara/callback
<path>/ara/callback will be removed in a future version.
For more details, please refer to the latest available documentation."""

message = 'ara.callback has been moved to ara.plugins.callbacks'

print(long_message)

CommitAfter = moves.moved_class(log_ara.CommitAfter, 'CommitAfter',
                                'ara',
                                version='0.9.2',
                                removal_version='?',
                                message=message)

IncludeResult = moves.moved_class(log_ara.IncludeResult, 'IncludeResult',
                                  'ara',
                                  version='0.9.2',
                                  removal_version='?',
                                  message=message)

CallbackModule = moves.moved_class(log_ara.CallbackModule, 'CallbackModule',
                                   'ara',
                                   version='0.9.2',
                                   removal_version='?',
                                   message=message)
