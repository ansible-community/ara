Usage
=====

Once ARA is :ref:`installed <installation>` and
:ref:`configured <configuration_ansible>`, you're ready to use it!

Using the callback
------------------

The callback is executed by Ansible automatically once the path is set properly
in the ``callback_plugins`` Ansible configuration.

After running an Ansible playbook, the database will be created if it doesn't
exist and will be used automatically.

.. _ara_record:

Using the ara_record module
---------------------------

ARA comes with a built-in Ansible module called ``ara_record``.

This module can be used as an action for a task in your Ansible playbooks in
order to register whatever you'd like in a key/value format, for example::

    ---
    - name: Test playbook
      hosts: localhost
      tasks:
        - name: Get git version of playbooks
          command: git rev-parse HEAD
          register: git_version

        # Registering the result of an ara_record tasks is equivalent to
        # doing an ara_read on the key
        - name: Record git version
          ara_record:
            key: "git_version"
            value: "{{ git_version.stdout }}"
          register: version

        - name: Print recorded data
          debug:
            msg: "{{ version.playbook_id}} - {{ version.key }}: {{ version.value }}

It also supports data types which will have an impact on how the value will be
displayed in the web interface. The default type if not specified is "text".
Example usage::

    ---
    - ara_record:
        key: "{{ item.key }}"
        value: "{{ item.value }}"
        type: "{{ item.type }}"
      with_items:
        - { key: "log", value: "error", type: "text" }
        - { key: "website", value: "http://domain.tld", type: "url" }
        - { key: "data", value: '{ "key": "value" }', type: "json" }
        - { key: "somelist", value: ['one', 'two'], type: "list" }
        - { key: "somedict", value: {'key': 'value' }, type: "dict" }

It is also possible to run an ``ara_record`` task on a specific playbook that
might already be completed. This is particularly useful for recording data that
might only be available or computed after your playbook run has been completed::

    ---
    # Write data to a specific (previously run) playbook
    # (Retrieve playbook uuid's with 'ara playbook list')
    - ara_record:
        playbook: uuuu-iiii-dddd-0000
        key: logs
        value: "{{ lookup('file', '/var/log/ansible.log') }}"
        type: text

Or as an ad-hoc command::

    ansible localhost -m ara_record \
        -a "playbook=uuuu-iiii-dddd-0000 key=logs value={{ lookup('file', '/var/log/ansible.log') }}"

This data will be recorded inside ARA's database and associated with the
particular playbook run that was executed.

You can then query ARA, either through the CLI or the web interface to see the
recorded values.

.. _ara_read:

Using the ara_read module
-------------------------

ARA comes with a built-in Ansible module called ``ara_read`` that can read data
that was previously recorded with ``ara_record`` within the same playbook run.

This module can be used as an action for a task anywhere in your in your
Ansible playbooks as long as it is within the same playbook run. It can be
re-used across plays or roles if necessary, for example::

    ---
    - name: Test play on localhost
      hosts: localhost
      tasks:
        - name: Compute md5sum of file
          command: md5sum file
          register: local_mdfive

        - name: Record md5sum of dile
          ara_record:
            key: "md5sum"
            value: "{{ local_mdfive.stdout }}"

    - name: Test play on remote hosts
      hosts: webservers
      tasks:
          - name: Retrieve md5sum
            ara_read:
              key: "md5sum"
            register: mdfive

          - name: Compare md5sum of files
            shell: diff <(md5sum file) <(echo "{{ mdfive.value }}")

It is also possible to run an ``ara_read`` task on a specific playbook that
might already be completed. This is particularly useful for reading data that
might only be available or computed after your playbook run has been completed::

    ---
    # Read data from a specific (previously run) playbook
    # (Retrieve playbook uuid's with 'ara playbook list')
    - ara_read:
        playbook: uuuu-iiii-dddd-0000
        key: logs
      register: logs

Or as an ad-hoc command::

    ansible localhost -m ara_read -a "playbook=uuuu-iiii-dddd-0000 key=logs"


.. note::
    ``ara_read`` on a specific playbook id should only be used if you need to
    tie data back into Ansible for other tasks.
    If you just need to browse or view recorded data on the command line, you
    should probably be using the ARA CLI: ``ara data show``.

Looking at the data
-------------------

Once you've run ansible-playbook at least once, the database will be populated
with data::

    # Example with sqlite
    $ sqlite3 ~/.ara/ansible.sqlite
    SQLite version 3.11.0 2016-02-15 17:29:24
    Enter ".help" for usage hints.
    sqlite> select * from playbooks;
    15d05ac3-95b6-4767-ab1e-5365f76e5b09|playbooks/test.yml|2016-05-14 03:17:57.866103|2016-05-14 03:17:59.451822

    # Example with MySQL
    # mysql -e "select * from ara.playbooks;"
    +--------------------------------------+--------------+---------------------+---------------------+
    | id                                   | path         | time_start          | time_end            |
    +--------------------------------------+--------------+---------------------+---------------------+
    | 48912da8-4e83-4fdb-b73d-62b03f2a5ed9 | playbook.yml | 2016-05-14 03:27:39 | 2016-05-14 03:27:39 |
    +--------------------------------------+--------------+---------------------+---------------------+

.. _cli_client:

Querying the database with the CLI
----------------------------------

ARA provides a CLI client to query the database.

Example commands::

    $ ara help
    usage: ara [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug]

    A CLI client to query ARA databases

    optional arguments:
      --version            show program's version number and exit
      -v, --verbose        Increase verbosity of output. Can be repeated.
      -q, --quiet          Suppress output except warnings and errors.
      --log-file LOG_FILE  Specify a file to log output. Disabled by default.
      -h, --help           Show help message and exit.
      --debug              Show tracebacks on errors.

    Commands:
      complete       print bash completion command
      data list      Returns a list of recorded key/value pairs
      data show      Show details of a recorded key/value pair
      file list      Returns a list of files
      file show      Show details of a file
      generate html  Generates a static tree of the web application
      generate junit Generate junit stream from ara data
      help           print detailed help for another command
      host facts     Show facts for a host
      host list      Returns a list of hosts
      host show      Show details of a host
      play list      Returns a list of plays
      play show      Show details of a play
      playbook delete  Delete playbooks from the database.
      playbook list  Returns a list of playbooks
      playbook show  Show details of a playbook
      result list    Returns a list of results
      result show    Show details of a result
      stats list     Returns a list of statistics
      stats show     Show details of a statistic
      task list      Returns a list of tasks
      task show      Show details of a task

    # ara help result list
    usage: ara result list [-h] [-f {csv,json,table,value,yaml}] [-c COLUMN]
                           [--max-width <integer>] [--noindent]
                           [--quote {all,minimal,none,nonnumeric}]

    Returns a list of results

    optional arguments:
      -h, --help            show this help message and exit

    output formatters:
      output formatter options

      -f {csv,json,table,value,yaml}, --format {csv,json,table,value,yaml}
                            the output format, defaults to table
      -c COLUMN, --column COLUMN
                            specify the column(s) to include, can be repeated

    table formatter:
      --max-width <integer>
                            Maximum display width, 0 to disable

    json formatter:
      --noindent            whether to disable indenting the JSON

    CSV Formatter:
      --quote {all,minimal,none,nonnumeric}
                            when to include quotes, defaults to nonnumeric

    # ara result list
    +--------------------------------------+-----------+--------------------+---------+--------+---------+-------------+---------------+---------------------+---------------------+
    | ID                                   | Host      | Task               | Changed | Failed | Skipped | Unreachable | Ignore Errors | Time Start          | Time End            |
    +--------------------------------------+-----------+--------------------+---------+--------+---------+-------------+---------------+---------------------+---------------------+
    | 79ee4b5b-667d-43a1-b10d-b48ebf422141 | localhost | Ping               | False   | False  | False   | False       | False         | 2016-05-14 03:27:39 | 2016-05-14 03:27:39 |
    | b3a04d9e-c9df-4126-8481-5bdb9d9795f7 | localhost | Really debug thing | False   | False  | False   | False       | False         | 2016-05-14 03:27:39 | 2016-05-14 03:27:39 |
    +--------------------------------------+-----------+--------------------+---------+--------+---------+-------------+---------------+---------------------+---------------------+

    # ara result show b3a04d9e-c9df-4126-8481-5bdb9d9795f7 --long
    +---------------+-----------------------------------------------------------+
    | Field         | Value                                                     |
    +---------------+-----------------------------------------------------------+
    | ID            | b3a04d9e-c9df-4126-8481-5bdb9d9795f7                      |
    | Host          | localhost                                                 |
    | Task          | Really debug thing (1d24921e-bebc-4732-a362-32df24c8cb8b) |
    | Changed       | False                                                     |
    | Failed        | False                                                     |
    | Skipped       | False                                                     |
    | Unreachable   | False                                                     |
    | Ignore Errors | False                                                     |
    | Time Start    | 2016-05-14 03:27:39                                       |
    | Time End      | 2016-05-14 03:27:39                                       |
    | Result        | {                                                         |
    |               |     "_ansible_no_log": false,                             |
    |               |     "_ansible_verbose_always": true,                      |
    |               |     "changed": false,                                     |
    |               |     "failed": false,                                      |
    |               |     "msg": "Really debug thing",                          |
    |               |     "skipped": false,                                     |
    |               |     "unreachable": false                                  |
    |               | }                                                         |
    +---------------+-----------------------------------------------------------+

Browsing the web interface
--------------------------

The web UI frontend is a visualization of the data recorded in the database.
It provides insight on your playbooks, your hosts, your tasks and the results
of your playbook run.

The interface provided by ARA provides is a simple Flask application.
There are currently two documented options to host the web interface:

1. :ref:`Embedded development server <web_config_embedded>` (easiest but least performance)
3. :ref:`Apache with mod_wsgi <web_config_mod_wsgi>` (recommended)

These should be enough to get you started or help you choose your own path on
other `deployment options`_ you might be used to when hosting `Flask`_
applications.

.. _deployment options: http://flask.pocoo.org/docs/0.12/deploying/
.. _Flask: http://flask.pocoo.org/

.. _generating_html:

Generating a static HTML version of the web application
-------------------------------------------------------

ARA is able to generate a static html version of it's dynamic, database-driven
web application.

This can be useful if you need to browse the results of playbook runs without
having to rely on the database backend configured.

For example, in the context of continuous integration, you could run an Ansible
job with ARA, generate a static version and then recover the resulting build as
artifacts of the jobs, allowing you to browse the results in-place.

This is done with the ``ara generate html`` command.

By default, ARA will generate a static version for all the recorded playbook
runs in it's database.
It is also possible to generate a report for one or many specific playbooks.
This is done by retrieving the playbook IDs you are interested in with
``ara playbook list`` and then using the ``ara generate html`` command with the
``--playbook`` parameter::

    $ ara help generate html
    usage: ara generate html [-h] [--playbook <playbook> [<playbook> ...]] <path>

    Generates a static tree of the web application

    positional arguments:
      <path>                Path where the static files will be built in

    optional arguments:
      -h, --help            show this help message and exit
      --playbook <playbook> [<playbook> ...]
                            Only include the specified playbooks in the
                            generation.

    $ ara generate html /tmp/build/
    Generating static files at /tmp/build/...
    Done.
    $ tree /tmp/build/
    /tmp/build/
    ├── host
    │   ├── anotherhost
    │   ├── index.html
    │   └── localhost
    ├── index.html
    ├── play
    │   └── play
    │       └── 6ec9ef1d-dd73-4378-8347-1242f6be8f1e
    ├── playbook
    │   ├── bf81a7db-b549-49d9-b10e-19918225ec60
    │   │   ├── index.html
    │   │   └── results
    │   │       ├── anotherhost
    │   │       │   ├── index.html
    │   │       │   └── ok
    │   │       └── localhost
    │   │           ├── index.html
    │   │           └── ok
    │   └── index.html
    ├── result
    │   ├── 136100f7-fba7-44ba-83fc-1194509ad2dd
    │   ├── 37532523-b2ec-4931-bb73-3c7e5c6fa7bf
    │   ├── 3cef2a10-8f41-4f01-bc49-12bed179d7e9
    │   └── e3b7e172-c6e4-4ee4-b4bc-9a51ff84decb
    ├── static
    │   ├── css
    │   │   ├── ara.css
    │   │   ├── bootstrap.min.css
    │   │   └── bootstrap-theme.min.css
    │   └── js
    │       ├── bootstrap.min.js
    │       └── jquery-2.2.3.min.js
    └── task
        ├── 570fe763-69bb-4141-80d4-578189c5938b
        └── 946e1bc6-28b9-4f2f-ad4f-75b3c6c9032d

    13 directories, 22 files

Generating a static junit version of the task results
-----------------------------------------------------

ARA is able to generate a junit xml report that contains task results and their
status.

This is done with the ``ara generate junit`` command.

By default, ARA will generate a report on all task results across all the
recorded playbook runs in it's database.
It is also possible to generate a report for one or many specific playbooks.
This is done by retrieving the playbook IDs you are interested in with
``ara playbook list`` and then using the ``ara generate junit`` command with the
``--playbook`` parameter::

    $ ara help generate junit
    usage: ara generate junit [-h] [--playbook <playbook> [<playbook> ...]]
                              <output file>

    Generate junit stream from ara data

    positional arguments:
      <output file>         The file to write the junit xml to. Use "-" for
                            stdout.

    optional arguments:
      -h, --help            show this help message and exit
      --playbook <playbook> [<playbook> ...]
                            Only include the specified playbooks in the
                            generation.

    $ ara generate junit -
    <?xml version="1.0" ?>
    <testsuites errors="0" failures="3" tests="66" time="33.0">
        <testsuite errors="0" failures="3" name="Ansible Tasks" skipped="5" tests="66" time="33">
            <testcase classname="localhost._home_dev_ara_ara_tests_integration_smoke_yml.ARA_Tasks_test_play" name="Deferred setup" time="3.000000"/>
            <testcase classname="localhost._home_dev_ara_ara_tests_integration_smoke_yml.ARA_Tasks_test_play" name="include"/>
            <testcase classname="localhost._home_dev_ara_ara_tests_integration_smoke_yml.ARA_Tasks_test_play" name="Ensure temporary directory exists"/>
            <testcase classname="localhost._home_dev_ara_ara_tests_integration_smoke_yml.ARA_Tasks_test_play" name="Check if a file exists"/>
            <testcase classname="localhost._home_dev_ara_ara_tests_integration_smoke_yml.ARA_Tasks_test_play" name="Touch a file if it doesn't exist"/>
            <testcase classname="localhost._home_dev_ara_ara_tests_integration_smoke_yml.ARA_Tasks_test_play" name="Remove a file if it doesn't exist"/>
            <testcase classname="localhost._home_dev_ara_ara_tests_integration_smoke_yml.ARA_Tasks_test_play" name="Remove a file if it exists">
    [...]

Generating a static subunit version of the task results
-------------------------------------------------------

ARA is able to generate a subunit report that contains task results and their
status.

This is done with the ``ara generate subunit`` command.

By default, ARA will generate a report on all task results across all the
recorded playbook runs in it's database.
It is also possible to generate a report for one or many specific playbooks.
This is done by retrieving the playbook IDs you are interested in with
``ara playbook list`` and then using the ``ara generate subunit`` command with the
``--playbook`` parameter::

    $ ara help generate subunit
    usage: ara generate subunit [-h] [--playbook <playbook> [<playbook> ...]]
                                <output file>

    Generate subunit binary stream from ARA data

    positional arguments:
      <output file>         The file to write the subunit binary stream to. Use
                            "-" for stdout.

    optional arguments:
      -h, --help            show this help message and exit
      --playbook <playbook> [<playbook> ...]
                            Only include the specified playbooks in the
                            generation.

    $ ara generate subunit - | subunit2csv
    test,status,start_time,stop_time
    50d4e04fe034bea7479bc4a3fa3703254298baa8,success,2017-07-28 03:07:21+00:00,2017-07-28 03:07:21+00:00
    a62f7a36683972efe1ef6e51e389417521502153,success,2017-07-28 03:07:22+00:00,2017-07-28 03:07:22+00:00
    8902778f958439806aee2a22c26d8b79dc61c964,success,2017-07-28 03:07:22+00:00,2017-07-28 03:07:22+00:00
    fd2d199b22b635ed82b41d5edf8c1774f64484dc,success,2017-07-28 03:07:22+00:00,2017-07-28 03:07:22+00:00
    [...]
