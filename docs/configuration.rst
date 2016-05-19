Configuration
=============
Ansible
-------
To use ARA, you'll first need to set up Ansible to use the ARA callback_.

The callback comes provided when installing ARA but you need to let Ansible
know where it is located.

Set up your `ansible.cfg`_ file to seek that callback in the appropriate
directory. Here's an example that covers most common locations::

    [defaults]
    callback_plugins = /usr/lib/python2.7/site-packages/ara/callback:$VIRTUAL_ENV/lib/python2.7/site-packages/ara/callback:/usr/local/lib/python2.7/dist-packages/ara/callback

.. _callback: https://github.com/dmsimard/ara/blob/master/ara/callback/log_ara.py
.. _ansible.cfg: http://docs.ansible.com/ansible/intro_configuration.html#configuration-file

*That's it!*

ARA
---
ARA uses the same mechanism and configuration files as Ansible to retrieve it's
configuration. It comes with sane defaults that can be customized if need be.

The order of priority is the following:

1. Environment variables
2. ``./ansible.cfg`` (*In the current working directory*)
3. ``~/.ansible.cfg`` (*In the home directory*)
4. ``/etc/ansible/ansible.cfg``

When using the ansible.cfg file, the configuration options must be set under
the ara namespace, as follows::

    [ara]
    variable = value

.. note:: The callback, CLI client and web application all share the same
          settings. For example, if you configure the database location, all
          three will use that location.

Parameters and their defaults
-----------------------------
+----------------------+----------------------+-------------------------------------------+
| Environment variable | ansible.cfg variable | Default value                             |
+======================+======================+===========================================+
| ARA_DIR_             | dir                  | ~/.ara                                    |
+----------------------+----------------------+-------------------------------------------+
| ARA_DATABASE_        | database             | sqlite:///~/.ara/ansible.sqlite           |
+----------------------+----------------------+-------------------------------------------+
| ARA_LOG_             | logfile              | ~/.ara/ara.log                            |
+----------------------+----------------------+-------------------------------------------+
| ARA_LOG_LEVEL_       | loglevel             | INFO                                      |
+----------------------+----------------------+-------------------------------------------+
| ARA_LOG_FORMAT_      | logformat            | %(asctime)s - %(levelname)s - %(message)s |
+----------------------+----------------------+-------------------------------------------+
| ARA_SQL_DEBUG_       | sqldebug             | False                                     |
+----------------------+----------------------+-------------------------------------------+

ARA_DIR
~~~~~~~
Base directory where ARA will store it's log file and sqlite database, unless
specified otherwise.

ARA_DATABASE
~~~~~~~~~~~~
ARA records Ansible data in a database.
The callback, the CLI client and the web application all need to know where
that database is located.

ARA ensures the database exists and it's schema is created when it is run.

ARA comes out of the box with sqlite enabled and no additional setup required.
If, for example, you'd like to use MySQL instead, you will need to create a
database and it's credentials::

    CREATE DATABASE ara;
    CREATE USER ara@localhost IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON ara.* TO ara@localhost;
    FLUSH PRIVILEGES;

And then setup the database connection::

    export ARA_DATABASE="mysql+pymysql://ara:password@localhost/ara"
    # or
    [ara]
    database = mysql+pymysql://ara:password@localhost/ara

ARA_LOG
~~~~~~~
Path to the logfile to store ARA logs in.

ARA_LOG_LEVEL
~~~~~~~~~~~~~
The loglevel to adjust debug or verbosity.

ARA_LOG_FORMAT
~~~~~~~~~~~~~~
The log format of the logs.

ARA_SQL_DEBUG
~~~~~~~~~~~~~
Enables the SQLAlchemy echo verbose mode.

The CLI client and the web application
--------------------------------------
The CLI client and the web application do not need to be run on the same
machine that Ansible is executed from but they do need a database and know it's
location.

Both could query a local sqlite database or a remote MySQL database, for
example.
