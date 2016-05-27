Usage
=====
Once ARA is installed_ and configured_, you're ready to use it!

.. _installed: installation.html
.. _configured: configuration.html

Using the callback
------------------
The callback is executed by Ansible automatically once the path is set properly
in the ``callback_plugins`` Ansible configuration.

After running an Ansible playbook, the database will be created if it doesn't
exist and will be used automatically.

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

Querying the database with the CLI
----------------------------------
ARA provides a CLI client to query the database.

Example commands::

    # ara help
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
      help           print detailed help for another command
      host list      Returns a list of hosts
      host show      Show details of a host
      play list      Returns a list of plays
      play show      Show details of a play
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
The frontend is a visualization of the data recorded in the database.

The interface provided by ARA provides is a simple Flask application.
As such, you can configure it to run like `any other Flask application`_.

To run the development webserver, you can use the ``ara-manage`` script
bundled with ARA::

    $ ara-manage runserver --help
    usage: ara-manage runserver [-?] [-h HOST] [-p PORT] [--threaded]
                                [--processes PROCESSES] [--passthrough-errors]
                                [-d] [-D] [-r] [-R]

    Runs the Flask development server i.e. app.run()

    optional arguments:
      -?, --help            show this help message and exit
      -h HOST, --host HOST
      -p PORT, --port PORT
      --threaded
      --processes PROCESSES
      --passthrough-errors
      -d, --debug           enable the Werkzeug debugger (DO NOT use in production
                            code)
      -D, --no-debug        disable the Werkzeug debugger
      -r, --reload          monitor Python files for changes (not 100{'const':
                            True, 'help': 'monitor Python files for changes (not
                            100% safe for production use)', 'option_strings':
                            ['-r', '--reload'], 'dest': 'use_reloader',
                            'required': False, 'nargs': 0, 'choices': None,
                            'default': None, 'prog': 'ara-manage runserver',
                            'container': <argparse._ArgumentGroup object at
                            0x7f6825596310>, 'type': None, 'metavar': None}afe for
                            production use)
      -R, --no-reload       do not monitor Python files for changes

    $ ara-manage runserver -h 0.0.0.0 -p 8080
     * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)

.. _any other Flask application: http://flask.pocoo.org/docs/0.10/deploying/uwsgi/

Generating a static version of the web application
--------------------------------------------------
ARA is able to generate a static html version of it's dynamic, database-driven
web application.

This can be useful if you need to browse the results of playbook runs without
having to rely on the database backend configured.

For example, in the context of continuous integration, you could run an Ansible
job with ARA, generate a static version and then recover the resulting build as
artifacts of the jobs, allowing you to browse the results in-place.

The ARA CLI client provides a command to generate a static version::

    $ ara help generate
    usage: ara generate [-h] --path <path>

    Generates a static tree of the web application

    optional arguments:
      -h, --help            show this help message and exit
      --path <path>, -p <path>
                            Path where the static files will be built in

    $ ara generate --path /tmp/build/
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
