Configuration
=============

Ansible
-------

To begin using ARA, you'll first need to set up Ansible so it knows about the
the ARA callback_ and, if necessary, the ara_record_ and ara_read_ modules.

The callback and modules are bundled when installing ARA but you need to know
where they have been installed in order to let Ansible know where they are located.

.. tip::

   The location where ARA will be depends on your operating system and how it
   is installed.
   Here's an example of some common locations:

   - ``/usr/lib/python2.7/site-packages/ara``
   - ``/usr/local/lib/python2.7/dist-packages/ara``
   - ``$VIRTUAL_ENV/lib/python2.7/site-packages/ara``

   If you're not sure where ARA has ended up being installed, you can use this
   snippet to print it's location::

      python -c "import os,ara; print(os.path.dirname(ara.__file__))"

.. _callback: https://ara.readthedocs.io/en/latest/faq.html#what-s-an-ansible-callback
.. _ara_record: https://ara.readthedocs.io/en/latest/usage.html#using-the-ara-record-module
.. _ara_read: https://ara.readthedocs.io/en/latest/usage.html#using-the-ara-read-module

Using ansible.cfg
~~~~~~~~~~~~~~~~~

Set up your `ansible.cfg`_ file to seek the callback and modules in the appropriate
directories::

    $ export ara_location=$(python -c "import os,ara; print(os.path.dirname(ara.__file__))")
    $ cat > ansible.cfg <<EOF
    [defaults]
    # callback_plugins configuration is required for the ARA callback
    callback_plugins = $ara_location/plugins/callbacks

    # action_plugins and library configuration is required for the ara_record and ara_read modules
    action_plugins = $ara_location/plugins/actions
    library = $ara_location/plugins/modules
    EOF

.. _ansible.cfg: http://docs.ansible.com/ansible/intro_configuration.html#configuration-file

Using environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on the context and your use case, configuring Ansible using
`environment variables`_ instead of an ``ansible.cfg`` file might be more convenient.
Here's how you can set up Ansible to seek out ARA's callback and modules::

    $ export ara_location=$(python -c "import os,ara; print(os.path.dirname(ara.__file__))")
    $ export ANSIBLE_CALLBACK_PLUGINS=$ara_location/plugins/callbacks
    $ export ANSIBLE_ACTION_PLUGINS=$ara_location/plugins/actions
    $ export ANSIBLE_LIBRARY=$ara_location/plugins/modules

.. _environment variables: http://docs.ansible.com/ansible/intro_configuration.html#environmental-configuration

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

.. note::

   The callback, CLI client and web application all share the same
   settings. For example, if you configure the database location, all
   three will use that location.

Parameters and their defaults
-----------------------------

+-------------------------------+--------------------------+-------------------------------------------+
| Environment variable          | ansible.cfg variable     | Default value                             |
+===============================+==========================+===========================================+
| ARA_DIR_                      | dir                      | ~/.ara                                    |
+-------------------------------+--------------------------+-------------------------------------------+
| ARA_DATABASE_                 | database                 | sqlite:///~/.ara/ansible.sqlite           |
+-------------------------------+--------------------------+-------------------------------------------+
| ARA_LOG_FILE_                 | logfile                  | ~/.ara/ara.log                            |
+-------------------------------+--------------------------+-------------------------------------------+
| ARA_LOG_LEVEL_                | loglevel                 | INFO                                      |
+-------------------------------+--------------------------+-------------------------------------------+
| ARA_LOG_FORMAT_               | logformat                | %(asctime)s - %(levelname)s - %(message)s |
+-------------------------------+--------------------------+-------------------------------------------+
| ARA_SQL_DEBUG_                | sqldebug                 | False                                     |
+-------------------------------+--------------------------+-------------------------------------------+
| ARA_IGNORE_MIMETYPE_WARNINGS_ | ignore_mimetype_warnings | True                                      |
+-------------------------------+--------------------------+-------------------------------------------+

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

When using a different database driver such as MySQL (pymysql), you also need
to make sure you install the driver::

    # From pypi
    pip install pymysql
    # For RHEL derivatives
    yum install python-PyMySQL
    # For Debian or Ubuntu
    apt-get install python-pymysql

ARA_LOG_FILE
~~~~~~~~~~~~

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

ARA_IGNORE_MIMETYPE_WARNINGS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whether or not to ignore mimetype warnings when generating the static version
of the ARA web application.

The CLI client and the web application
--------------------------------------

The CLI client and the web application do not need to be run on the same
machine that Ansible is executed from but they do need a database and know it's
location.

Both could query a local sqlite database or a remote MySQL database, for
example.
