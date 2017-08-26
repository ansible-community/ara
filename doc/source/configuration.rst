.. _configuration:

Configuration
=============

.. _configuration_ansible:

Ansible
-------

To begin using ARA, you'll first need to set up Ansible so it knows about the
the ARA :ref:`callback <faq_callback>` and, if necessary, the :ref:`ara_record <ara_record>` and :ref:`ara_read <ara_read>` modules.

The callback and modules are bundled when installing ARA but you need to know
where they have been installed in order to let Ansible know where they are located.

.. tip::

   The location where ARA will be depends on your operating system and how it
   is installed.
   Here's some examples of where ARA can be found:

   - ``/usr/lib/python2.7/site-packages/ara``
   - ``/usr/lib/python3.5/site-packages/ara``
   - ``$VIRTUAL_ENV/lib/python2.7/site-packages/ara``

   If you're not sure where ARA will end up being installed, you can use this
   snippet to print its location. It works in both Python 2 and Python 3::

      python -c "import os,ara; print(os.path.dirname(ara.__file__))"

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

.. _ansible.cfg: https://docs.ansible.com/ansible/intro_configuration.html#configuration-file

Using environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on the context and your use case, configuring Ansible using
`environment variables`_ instead of an ``ansible.cfg`` file might be more convenient.
Here's how you can set up Ansible to seek out ARA's callback and modules::

    $ export ara_location=$(python -c "import os,ara; print(os.path.dirname(ara.__file__))")
    $ export ANSIBLE_CALLBACK_PLUGINS=$ara_location/plugins/callbacks
    $ export ANSIBLE_ACTION_PLUGINS=$ara_location/plugins/actions
    $ export ANSIBLE_LIBRARY=$ara_location/plugins/modules

.. _environment variables: https://docs.ansible.com/ansible/intro_configuration.html#environmental-configuration

.. _configuration_ara:

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

.. _configuration_parameter_ara:

Parameters and their defaults
-----------------------------

+-------------------------------+----------------------------+-------------------------------------------+
| Environment variable          | [ara] ansible.cfg variable | Default value                             |
+===============================+============================+===========================================+
| ARA_DIR_                      | dir                        | ~/.ara                                    |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_DATABASE_                 | database                   | sqlite:///~/.ara/ansible.sqlite           |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_HOST_                     | host                       | 127.0.0.1                                 |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_PORT_                     | port                       | 9191                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_CONFIG_               | logconfig                  | None                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_FILE_                 | logfile                    | ~/.ara/ara.log                            |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_LEVEL_                | loglevel                   | INFO                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_FORMAT_               | logformat                  | %(asctime)s - %(levelname)s - %(message)s |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_SQL_DEBUG_                | sqldebug                   | False                                     |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_IGNORE_PARAMETERS_        | ignore_parameters          | extra_vars                                |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_IGNORE_EMPTY_GENERATION_  | ignore_empty_generation    | True                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_IGNORE_MIMETYPE_WARNINGS_ | ignore_mimetype_warnings   | True                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_PLAYBOOK_OVERRIDE_        | playbook_override          | None                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_PLAYBOOK_PER_PAGE_        | playbook_per_page          | 10                                        |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_RESULT_PER_PAGE_          | result_per_page            | 25                                        |
+-------------------------------+----------------------------+-------------------------------------------+

ARA_DIR
~~~~~~~

Base directory where ARA will store it's log file and sqlite database, unless
specified otherwise.

.. _ara_database:

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

Alternatively, if you prefer PostgreSQL, you can do the following in psql::

    CREATE ROLE ara WITH LOGIN PASSWORD 'password';
    CREATE DATABASE ara OWNER ara;
    GRANT ALL ON DATABASE ara TO ara;

Be sure you update your pg_hba.conf afterwards if needed.

Then, setup the database connection::

    export ARA_DATABASE="postgresql+psycopg2://ara:password@localhost:5432/ara"
    # or
    [ara]
    database = postgresql+psycopg2://ara:password@localhost:5432/ara

You will need to install the database driver by::

    # From pypi
    pip install psycopg2
    # For RHEL derivatives
    yum install python-psycopg2
    # For Debian or Ubuntu
    apt-get install python-psycopg2

ARA_HOST
~~~~~~~~

The host on which the development server will bind to by default when using the
``ara-manage runserver`` command.

It is equivalent to the ``-h`` or ``--host`` argument of the
``ara-manage runserver`` command.

ARA_PORT
~~~~~~~~

The port on which the development server will listen on by default when using
the ``ara-manage runserver`` command.

It is equivalent to the ``-p`` or ``--port`` argument of the
``ara-manage runserver`` command.

ARA_LOG_CONFIG
~~~~~~~~~~~~~~

Path to a python logging config file.

If the filename ends in ``.yaml`` or ``.yml`` the file will be loaded as yaml.
If the filename ends in ``.json`` the file will be loaded as json. The
resulting dict for either will be treated as a `logging config dict`_
and passed to `logging.config.dictConfig`.

Otherwise it will be assumed to a `logging config file`_ and the path will be
passed to `logging.config.fileConfig`.

If this option is given it superseeds the other individual log options.

.. _logging config dict: https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
.. _logging config file: https://docs.python.org/3/library/logging.config.html#logging-config-fileformat

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

ARA_IGNORE_PARAMETERS
~~~~~~~~~~~~~~~~~~~~~

ARA will, by default, save every parameter and option passed to
ansible-playbook (except ``extra-vars``) and make them available as part of
your reports.

If, for example, you use `extra_vars`_ to send a password or secret variable
to your playbooks, it is likely you don't want this saved in ARA's database.

This configuration allows you to customize what ARA will and will not save.
It is a list, provided by a comma-separated values.

.. _extra_vars: https://docs.ansible.com/ansible/playbooks_variables.html#passing-variables-on-the-command-line

ARA_IGNORE_EMPTY_GENERATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using ``ara generate html``, whether or not to ignore warnings provided
by flask-frozen about endpoints for which the application found no available
data.

For example, if you do not use the ``ara_record`` module as part of your
playbooks, this avoids printing a *MissingURLGeneratorWarning* because there
is no recorded data to render.

ARA_IGNORE_MIMETYPE_WARNINGS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using ``ara generate html``, whether or not to ignore file mimetype
warnings provided by flask-frozen.

ARA_PLAYBOOK_OVERRIDE
~~~~~~~~~~~~~~~~~~~~~

This configuration is exposed mostly for the purposes of the
``ara generate html`` and ``ara generate junit`` commands but you can use it
as well.

ARA_PLAYBOOK_OVERRIDE will limit the playbooks displayed in the web application
to the list of playbook IDs specified.
This is expected to be playbook IDs (ex: retrieved through
``ara playbook list``) in a comma-separated list.

ARA_PLAYBOOK_PER_PAGE
~~~~~~~~~~~~~~~~~~~~~

This is the amount of playbooks runs shown in a single page in the ARA web
interface. The default is ``10`` but you might want to tweak this number up
or down depending on the amount of hosts, tasks and task results contained in
your playbooks.
This directly influences the weight of the pages that will end up being
displayed. Setting this value too high might yield very heavy pages.

Set this parameter to ``0`` to disable playbook listing pagination entirely.

ARA_RESULT_PER_PAGE
~~~~~~~~~~~~~~~~~~~

This is the amount of results shown in a single page in the different data
tables such as hosts, plays and tasks of the ARA web interface.
The default is ``25`` but you might want to tweak this number up or down
depending on your preference.
This has no direct impact on the weight of the page being sent for the reports
as these data tables are rendered on the client side.

Set this parameter to ``0`` to disable pagination for results entirely.

The CLI client and the web application
--------------------------------------

The CLI client and the web application do not need to be run on the same
machine that Ansible is executed from but they do need a database and know it's
location.

Both could query a local sqlite database or a remote MySQL database, for
example.
