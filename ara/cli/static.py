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

from debtcollector import moves
from ara.cli import generate

long_message = """[WARNING]
The "ara generate" command is deprecated and has been moved to
"ara generate html" command in ARA 0.10.6.

Please use the "ara generate html" command instead.
"ara generate" will be removed in a future version.
"""

message = '"ara generate" command has been moved to "ara generate html".'

print(long_message)

Generate = moves.moved_class(generate.GenerateHtml, 'GenerateHtml',
                             'ara',
                             version='0.10.6',
                             removal_version='?',
                             message=message)
