.. _configuration:

Configuration
=============

.. _configuration_ansible:

Ansible
-------

To begin using ARA, you'll first need to set up Ansible so it knows about the
the ARA :ref:`callback <faq_callback>` and, if necessary, the :ref:`ara_record <ara_record>` and :ref:`ara_read <ara_read>` modules.

The callback and modules are bundled when installing ARA but you need to know
where they have been installed in order to let Ansible know where they are
located.

This location will be different depending on your operating system, how you are
installing ARA and whether you are using Python 2 or Python 3.

ARA ships a set of convenience Python modules to help you configure Ansible to
use it.

They can be used like so::

    $ python -m ara.setup.path
    /usr/lib/python2.7/site-packages/ara

    $ python -m ara.setup.action_plugins
    /usr/lib/python2.7/site-packages/ara/plugins/actions

    $ python -m ara.setup.callback_plugins
    /usr/lib/python2.7/site-packages/ara/plugins/callbacks

    $ python -m ara.setup.library
    /usr/lib/python2.7/site-packages/ara/plugins/modules

Using ansible.cfg
~~~~~~~~~~~~~~~~~

This sets up a new `ansible.cfg`_ file to load the callbacks and modules from
the appropriate locations::

    $ python -m ara.setup.ansible | tee ansible.cfg
    [defaults]
    callback_plugins=/usr/lib/python2.7/site-packages/ara/plugins/callbacks
    action_plugins=/usr/lib/python2.7/site-packages/ara/plugins/actions
    library=/usr/lib/python2.7/site-packages/ara/plugins/modules

Or alternatively, if you have a customized `ansible.cfg`_ file, you can retrieve
only what you need using the other helpers such as the following:

- ``python -m ara.setup.callback_plugins``
- ``python -m ara.setup.action_plugins``
- ``python -m ara.setup.library``

.. _ansible.cfg: https://docs.ansible.com/ansible/intro_configuration.html#configuration-file

Using environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on the context and your use case, configuring Ansible using
`environment variables`_ instead of an ``ansible.cfg`` file might be more convenient.

ARA provides a helper module that prints out the necessary export commands::

    $ python -m ara.setup.env
    export ANSIBLE_CALLBACK_PLUGINS=/usr/lib/python2.7/site-packages/ara/plugins/callbacks
    export ANSIBLE_ACTION_PLUGINS=/usr/lib/python2.7/site-packages/ara/plugins/actions
    export ANSIBLE_LIBRARY=/usr/lib/python2.7/site-packages/ara/plugins/modules

Note that the module doesn't actually run those exports, you'll want to run them
yourself, add them in a bash script or a bashrc, etc.

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
| ARA_APPLICATION_ROOT_         | application_root           | /                                         |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_CONFIG_               | logconfig                  | None                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_FILE_                 | logfile                    | ~/.ara/ara.log                            |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_LEVEL_                | loglevel                   | INFO                                      |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_LOG_FORMAT_               | logformat                  | %(asctime)s - %(levelname)s - %(message)s |
+-------------------------------+----------------------------+-------------------------------------------+
| ARA_IGNORE_FACTS_             | ignore_facts               | ansible_env                               |
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
| SQLALCHEMY_ECHO_              | sqlalchemy_echo            | False                                     |
+-------------------------------+----------------------------+-------------------------------------------+
| SQLALCHEMY_POOL_SIZE_         | sqlalchemy_pool_size       | None (default managed by flask-sqlalchemy)|
+-------------------------------+----------------------------+-------------------------------------------+
| SQLALCHEMY_POOL_TIMEOUT_      | sqlalchemy_pool_timeout    | None (default managed by flask-sqlalchemy)|
+-------------------------------+----------------------------+-------------------------------------------+
| SQLALCHEMY_POOL_RECYCLE_      | sqlalchemy_pool_recycle    | None (default managed by flask-sqlalchemy)|
+-------------------------------+----------------------------+-------------------------------------------+

.. _SQLALCHEMY_ECHO: http://flask-sqlalchemy.pocoo.org/2.3/config/#configuration-keys
.. _SQLALCHEMY_POOL_SIZE: http://flask-sqlalchemy.pocoo.org/2.3/config/#configuration-keys
.. _SQLALCHEMY_POOL_TIMEOUT: http://flask-sqlalchemy.pocoo.org/2.3/config/#configuration-keys
.. _SQLALCHEMY_POOL_RECYCLE: http://flask-sqlalchemy.pocoo.org/2.3/config/#configuration-keys


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

ARA_APPLICATION_ROOT
~~~~~~~~~~~~~~~~~~~~

The path at which the web application should be loaded.

The default behavior is to load the application at the root (``/``) of your
host.
Change this parameter if you'd like to host your application elsewhere.

For example, ``/ara`` would make the application available under
``http://host/ara`` instead of ``http://host/``.

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

ARA_IGNORE_FACTS
~~~~~~~~~~~~~~~~

When Ansible gathers host facts or uses the setup module, your host facts are
recorded by ARA and are also available as part of your reports.

By default, only the host fact ``ansible_env`` is not saved due to the
sensitivity of the information it could contain such as tokens, passwords or
otherwise privileged information.

This configuration allows you to customize what ARA will and will not save.
It is a list, provided by comma-separated values.

ARA_IGNORE_PARAMETERS
~~~~~~~~~~~~~~~~~~~~~

ARA will, by default, save every parameter and option passed to
ansible-playbook (except ``extra-vars``) and make them available as part of
your reports.

If, for example, you use `extra_vars`_ to send a password or secret variable
to your playbooks, it is likely you don't want this saved in ARA's database.

This configuration allows you to customize what ARA will and will not save.
It is a list, provided by comma-separated values.

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
