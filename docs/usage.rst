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

To run the development webserver, you can run the ``ara-dev-server`` script
bundled with ARA::

    $ ara-dev-server
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger pin code: 605-724-687

You can see a recorded overview of the interface features on Youtube_.

.. _any other Flask application: http://flask.pocoo.org/docs/0.10/deploying/uwsgi/
.. _Youtube: https://www.youtube.com/watch?v=K3jTqgm2YuY
