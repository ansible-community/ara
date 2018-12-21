.. _configuring:

ara-server configuration
========================

ara-server ships with sane defaults, supports the notion of different
environments (*such as dev, staging, prod*) and allows you to customize the
configuration with files, environment variables or a combination of both.

ara-server is a Django application that leverages django-rest-framework.
Both `Django <https://docs.djangoproject.com/en/2.1/ref/settings/>`_ and
`django-rest-framework <https://www.django-rest-framework.org/api-guide/settings/>`_
have extensive configuration options which are not necessarily exposed or made
customizable by ARA for the sake of simplicity.

Overview
--------

This is a brief overview of the different configuration options for ara-server.
For more details, click on the configuration parameters.

+--------------------------------+------------------------------------------------------+------------------------------------------+
| Environment Variable           | Usage                                                | default                                  |
+================================+======================================================+==========================================+
| ARA_BASE_DIR_                  | Default directory for storing data and configuration | ``~/.ara``                               |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_SETTINGS_                  | Path to an ara-server configuration file             | ``None``                                 |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_ENV_                       | Environment to load configuration for                | ``default``                              |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_LOG_LEVEL_                 | Log level of the different components                | ``INFO``                                 |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_LOGGING_                   | Logging configuration                                | See ARA_LOGGING_                         |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_CORS_ORIGIN_WHITELIST_     | django-cors-headers's CORS_ORIGIN_WHITELIST_ setting | ``["127.0.0.1:8000", "localhost:3000"]`` |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_ALLOWED_HOSTS_             | Django's ALLOWED_HOSTS_ setting                      | ``["127.0.0.1", "localhost", "::1"]``    |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_STATIC_ROOT_               | Django's STATIC_ROOT_ setting                        | ``~/.ara/server/www/static``             |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_DEBUG_                     | Django's DEBUG_ setting                              | ``false``                                |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_SECRET_KEY_ (**Required**) | Django's SECRET_KEY_ setting                         | ``None``                                 |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_DATABASE_ENGINE_           | Django's ENGINE_ database setting                    | ``django.db.backends.sqlite3``           |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_DATABASE_NAME_             | Django's NAME_ database setting                      | ``~/.ara/server/ansible.sqlite``         |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_DATABASE_USER_             | Django's USER_ database setting                      | ``None``                                 |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_DATABASE_PASSWORD_         | Django's PASSWORD_ database setting                  | ``None``                                 |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_DATABASE_HOST_             | Django's HOST_ database setting                      | ``None``                                 |
+--------------------------------+------------------------------------------------------+------------------------------------------+
| ARA_DATABASE_PORT_             | Django's PORT_ database setting                      | ``None``                                 |
+--------------------------------+------------------------------------------------------+------------------------------------------+

.. _CORS_ORIGIN_WHITELIST: https://github.com/ottoyiu/django-cors-headers
.. _STATIC_ROOT: https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-STATIC_ROOT
.. _ALLOWED_HOSTS: https://docs.djangoproject.com/en/2.1/ref/settings/#allowed-hosts
.. _DEBUG: https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-DEBUG
.. _SECRET_KEY: https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY
.. _ENGINE: https://docs.djangoproject.com/en/2.1/ref/settings/#engine
.. _NAME: https://docs.djangoproject.com/en/2.1/ref/settings/#name
.. _USER: https://docs.djangoproject.com/en/2.1/ref/settings/#user
.. _PASSWORD: https://docs.djangoproject.com/en/2.1/ref/settings/#password
.. _HOST: https://docs.djangoproject.com/en/2.1/ref/settings/#host
.. _PORT: https://docs.djangoproject.com/en/2.1/ref/settings/#port

Configuration variables
-----------------------

ARA_BASE_DIR
~~~~~~~~~~~~

- **Environment variable**: ``ARA_BASE_DIR``
- **Configuration file variable**: ``BASE_DIR``
- **Type**: ``string``
- **Default**: ``~/.ara``

The directory where data will be stored by default.

Changing this location influences the default root directory for the
``ARA_STATIC_ROOT`` and ``ARA_DATABASE_NAME`` parameters.

This is also the default location where the configuration template
(``default_config.yaml``) is generated by ARA.

ARA_SETTINGS
~~~~~~~~~~~~

- **Environment variable**: ``ARA_SETTINGS``
- **Configuration file variable**: None, this variable defines the configuration file itself.
- **Type**: ``string``
- **Default**: ``None``
- **Provided by**: dynaconf_

Location of an ara-server configuration file to load settings from.
``ara-server`` generates a default configuration template at ``~/.ara/server/default_config.yaml``
that you can use to get started.

Note that while the configuration template is in YAML by default, it is possible
to have configuration files written in ``ini``, ``json`` and ``toml`` as well.

Settings and configuration parsing in ara-server is provided by the dynaconf_
python module.

.. _dynaconf: https://github.com/rochacbruno/dynaconf

ARA_ENV
~~~~~~~

- **Environment variable**: ``ARA_ENV``
- **Configuration file variable**: None, this variable defines which section of a configuration file is loaded.
- **Type**: ``string``
- **Default**: ``default``
- **Provided by**: dynaconf_

If you are using ara-server in different environments and would like keep your
configuration in a single file, you can use this variable to select a specific
environment's settings.

For example::

    # Increase verbosity and debugging for the "dev" environment
    dev:
        LOG_LEVEL: DEBUG
        DEBUG: TRUE
        SECRET_KEY: dev
    # Make sure we're not running DEBUG in production and use standard verbosity.
    production:
        LOG_LEVEL: INFO
        DEBUG: FALSE
        SECRET_KEY: prod

In order to use the settings from the "dev" environment, you would set
``ARA_ENV`` to ``dev``.

Another approach to environment-specific configuration is to use
``ARA_SETTINGS`` and keep your settings in different files instead.

ARA_LOG_LEVEL
~~~~~~~~~~~~~

- **Environment variable**: ``ARA_LOG_LEVEL``
- **Configuration file variable**: ``LOG_LEVEL``
- **Type**: ``string``
- **Default**: ``INFO``

Log level of the different components from ``ara-server``.

``ARA_LOG_LEVEL`` changes the log level of the default logging configuration
provided by ARA_LOGGING_.

ARA_LOGGING
~~~~~~~~~~~

- **Environment variable**: *Not recommended, use configuration file*
- **Configuration file variable**: ``LOGGING``
- **Type**: ``dictionary``
- **Default**::

    LOGGING:
        disable_existing_loggers: false
        formatters:
        normal:
            format: '%(asctime)s %(levelname)s %(name)s: %(message)s'
        handlers:
        console:
            class: logging.StreamHandler
            formatter: normal
            level: INFO
            stream: ext://sys.stdout
        loggers:
        ara:
            handlers:
            - console
            level: INFO
            propagate: 0
        root:
        handlers:
        - console
        level: INFO
        version: 1

The python logging configuration for ``ara-server``.

ARA_CORS_ORIGIN_WHITELIST
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_CORS_ORIGIN_WHITELIST``
- **Configuration file variable**: ``CORS_ORIGIN_WHITELIST``
- **Provided by**: `django-cors-headers <https://github.com/ottoyiu/django-cors-headers>`_
- **Type**: ``list``
- **Default**: ``["127.0.0.1:8000", "localhost:3000"]``
- **Examples**:

  - ``export ARA_CORS_ORIGIN_WHITELIST="['api.ara.example.org', 'web.ara.example.org']"``
  - In a YAML configuration file::

      dev:
        CORS_ORIGIN_WHITELIST:
          - 127.0.0.1:8000
          - localhost:3000
      production:
        CORS_ORIGIN_WHITELIST:
          - api.ara.example.org
          - web.ara.example.org

Hosts in the whitelist for `Cross-Origin Resource Sharing <https://en.wikipedia.org/wiki/Cross-origin_resource_sharing>`_.

This setting is typically used in order to allow the API and a web interface
(*such as ara-web_*) to talk to each other.

.. _ara-web: https://github.com/openstack/ara-web

ARA_ALLOWED_HOSTS
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_ALLOWED_HOSTS``
- **Configuration file variable**: ``ALLOWED_HOSTS``
- **Type**: ``list``
- **Provided by**: Django's ALLOWED_HOSTS_
- **Default**: ``["127.0.0.1", "localhost", "::1"]``

A list of strings representing the host/domain names that this Django site can
serve.

If you are planning on hosting an instance of ``ara-server`` somewhere, you'll
need to add your domain name to this list.

ARA_DEBUG
~~~~~~~~~

- **Environment variable**: ``ARA_DEBUG``
- **Configuration file variable**: ``DEBUG``
- **Provided by**: Django's DEBUG_
- **Type**: ``string``
- **Default**: ``false``

Whether or not Django's debug mode should be enabled.

The Django project recommends turning this off for production use.

ARA_SECRET_KEY
~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_SECRET_KEY``
- **Configuration file variable**: ``SECRET_KEY``
- **Provided by**: Django's SECRET_KEY_
- **Type**: ``string``
- **Default**: ``None`` (**Must be set**)

A secret key for a particular Django installation. This is used to provide
cryptographic signing, and should be set to a unique, unpredictable value.

ARA_STATIC_ROOT
~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_STATIC_ROOT``
- **Configuration file variable**: ``STATIC_ROOT``
- **Provided by**: Django's STATIC_ROOT_
- **Type**: ``string``
- **Default**: ``~/.ara/server/www/static``

The absolute path to the directory where Django's collectstatic command will
collect static files for deployment.

The static files are required for the built-in API browser by
django-rest-framework.

ARA_DATABASE_ENGINE
~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_ENGINE``
- **Configuration file variable**: ``DATABASES["default"]["ENGINE"]``
- **Provided by**: Django's ENGINE_ database setting
- **Type**: ``string``
- **Default**: ``django.db.backends.sqlite3``
- **Examples**:
  - ``django.db.backends.postgresql``
  - ``django.db.backends.mysql``

The Django database driver to use.

When using anything other than sqlite3 default driver, make sure to set the
other database settings to allow ara-server to connect to the database.

ARA_DATABASE_NAME
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_NAME``
- **Configuration file variable**: ``DATABASES["default"]["NAME"]``
- **Provided by**: Django's NAME_ database setting
- **Type**: ``string``
- **Default**: ``~/.ara/server/ansible.sqlite``

The name of the database.

When using sqlite, this is the absolute path to the sqlite database file.
When using drivers such as MySQL or Postgresql, it's the name of the database.

ARA_DATABASE_USER
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_USER``
- **Configuration file variable**: ``DATABASES["default"]["USER"]``
- **Provided by**: Django's USER_ database setting
- **Type**: ``string``
- **Default**: ``None``

The username to connect to the database.

Required when using something other than sqlite.

ARA_DATABASE_PASSWORD
~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_PASSWORD``
- **Configuration file variable**: ``DATABASES["default"]["PASSWORD"]``
- **Provided by**: Django's PASSWORD_ database setting
- **Type**: ``string``
- **Default**: ``None``

The password to connect to the database.

Required when using something other than sqlite.

ARA_DATABASE_HOST
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_HOST``
- **Configuration file variable**: ``DATABASES["default"]["HOST"]``
- **Provided by**: Django's HOST_ database setting
- **Type**: ``string``
- **Default**: ``None``

The host for the database server.

Required when using something other than sqlite.

ARA_DATABASE_PORT
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_PORT``
- **Configuration file variable**: ``DATABASES["default"]["PORT"]``
- **Provided by**: Django's PORT_ database setting
- **Type**: ``string``
- **Default**: ``None``

The port to use when connecting to the database server.

It is not required to set the port if you're using default ports for MySQL or
PostgreSQL.