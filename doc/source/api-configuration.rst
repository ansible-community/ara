.. _configuring:

ARA API server configuration
============================

The API server ships with sane defaults, supports the notion of different
environments (*such as dev, staging, prod*) and allows you to customize the
configuration with files, environment variables or a combination of both.

The API is a Django application that leverages django-rest-framework.
Both `Django <https://docs.djangoproject.com/en/4.2/ref/settings/>`_ and
`django-rest-framework <https://www.django-rest-framework.org/api-guide/settings/>`_
have extensive configuration options which are not necessarily exposed or made
customizable by ARA for the sake of simplicity.

Overview
--------

This is a brief overview of the different configuration options for the API server.
For more details, click on the configuration parameters.

+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| Environment Variable             | Default                                                | Usage                                                      |
+==================================+========================================================+============================================================+
| ARA_ALLOWED_HOSTS_               | ``["127.0.0.1", "localhost", "::1"]``                  | Django's ALLOWED_HOSTS_ setting                            |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_BASE_DIR_                    | ``~/.ara/server``                                      | Default directory for storing data and configuration       |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_BASE_PATH_                   | ``/``                                                  | Default URL-path under which ARA resides                   |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_CORS_ORIGIN_WHITELIST_       | ``["http://127.0.0.1:8000", "http://localhost:3000"]`` | django-cors-headers's CORS_ORIGIN_WHITELIST_ setting       |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_CORS_ORIGIN_REGEX_WHITELIST_ | ``[]``                                                 | django-cors-headers's CORS_ORIGIN_REGEX_WHITELIST_ setting |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_CSRF_TRUSTED_ORIGINS_        | ``[]``                                                 | Django's CSRF_TRUSTED_ORIGINS_ setting                     |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_CONN_MAX_AGE_       | ``0``                                                  | Django's CONN_MAX_AGE_ database setting                    |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_ENGINE_             | ``django.db.backends.sqlite3``                         | Django's ENGINE_ database setting                          |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_HOST_               | ``None``                                               | Django's HOST_ database setting                            |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_NAME_               | ``~/.ara/server/ansible.sqlite``                       | Django's NAME_ database setting                            |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_PASSWORD_           | ``None``                                               | Django's PASSWORD_ database setting                        |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_PORT_               | ``None``                                               | Django's PORT_ database setting                            |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_USER_               | ``None``                                               | Django's USER_ database setting                            |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DATABASE_OPTIONS_            | ``{}``                                                 | Django's OPTIONS_ database setting                         |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DEBUG_                       | ``False``                                              | Django's DEBUG_ setting                                    |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DISTRIBUTED_SQLITE_          | ``False``                                              | Whether to enable distributed sqlite backend               |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DISTRIBUTED_SQLITE_PREFIX_   | ``ara-report``                                         | Prefix to delegate to the distributed sqlite backend       |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_DISTRIBUTED_SQLITE_ROOT_     | ``/var/www/logs``                                      | Root under which sqlite databases are expected             |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_ENV_                         | ``default``                                            | Environment to load configuration for                      |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_EXTERNAL_AUTH_               | ``False``                                              | Whether or not to enable external authentication           |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_LOGGING_                     | See ARA_LOGGING_                                       | Logging configuration                                      |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_LOG_LEVEL_                   | ``INFO``                                               | Log level of the different components                      |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_PAGE_SIZE_                   | ``100``                                                | Amount of results returned per page by the API             |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_READ_LOGIN_REQUIRED_         | ``False``                                              | Whether authentication is required for reading data        |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_SECRET_KEY_                  | Randomized token, see ARA_SECRET_KEY_                  | Django's SECRET_KEY_ setting                               |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_SETTINGS_                    | ``~/.ara/server/settings.yaml``                        | Path to an API server configuration file                   |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_TIME_ZONE_                   | Local system timezone                                  | Time zone used when storing and returning results          |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+
| ARA_WRITE_LOGIN_REQUIRED_        | ``False``                                              | Whether authentication is required for writing data        |
+----------------------------------+--------------------------------------------------------+------------------------------------------------------------+

.. _CORS_ORIGIN_WHITELIST: https://github.com/adamchainz/django-cors-headers#cors_origin_whitelist
.. _CORS_ORIGIN_REGEX_WHITELIST: https://github.com/adamchainz/django-cors-headers#cors_origin_regex_whitelist
.. _CSRF_TRUSTED_ORIGINS: https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
.. _ALLOWED_HOSTS: https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts
.. _DEBUG: https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-DEBUG
.. _SECRET_KEY: https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-SECRET_KEY
.. _TIME_ZONE: https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-TIME_ZONE
.. _ENGINE: https://docs.djangoproject.com/en/4.2/ref/settings/#engine
.. _NAME: https://docs.djangoproject.com/en/4.2/ref/settings/#name
.. _USER: https://docs.djangoproject.com/en/4.2/ref/settings/#user
.. _PASSWORD: https://docs.djangoproject.com/en/4.2/ref/settings/#password
.. _HOST: https://docs.djangoproject.com/en/4.2/ref/settings/#host
.. _PORT: https://docs.djangoproject.com/en/4.2/ref/settings/#port
.. _CONN_MAX_AGE: https://docs.djangoproject.com/en/4.2/ref/settings/#conn-max-age
.. _OPTIONS: https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-OPTIONS

Configuration variables
-----------------------

ARA_ALLOWED_HOSTS
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_ALLOWED_HOSTS``
- **Configuration file variable**: ``ALLOWED_HOSTS``
- **Type**: ``list``
- **Provided by**: Django's ALLOWED_HOSTS_
- **Default**: ``["127.0.0.1", "localhost", "::1"]``
- **Examples**:

  - ``export ARA_ALLOWED_HOSTS="['api.ara.example.org', 'web.ara.example.org']"``
  - In a YAML configuration file::

      dev:
        ALLOWED_HOSTS:
          - 127.0.0.1
          - localhost
      production:
        ALLOWED_HOSTS:
          - api.ara.example.org
          - web.ara.example.org

A list of strings representing the host/domain names that this Django site can
serve.

If you are planning on hosting an instance of the API server somewhere, you'll
need to add your domain name to this list.

ARA_BASE_DIR
~~~~~~~~~~~~

- **Environment variable**: ``ARA_BASE_DIR``
- **Configuration file variable**: ``BASE_DIR``
- **Type**: ``string``
- **Default**: ``~/.ara/server``

The directory where data will be stored by default.

Changing this location influences the default root directory for the
``ARA_DATABASE_NAME`` and ``ARA_SETTINGS`` parameters.

This is also used to determine the location where the default configuration
file, ``settings.yaml``, will be generated by the API server.

ARA_BASE_PATH
~~~~~~~~~~~~~

- **Environment variable**: ``ARA_BASE_PATH``
- **Configuration file variable**: ``BASE_PATH``
- **Type**: ``string``
- **Default**: ``/``

The URL path under which ARA should get deployed.

By default this is empty, meaning that ARA will listen directly on ``/``.
This setting can be used in conjunction with a reverse proxy to deploy ARA
on sub paths without having the reverse proxy to rewrite all URLs in the
generated HTML.

ARA_CORS_ORIGIN_WHITELIST
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_CORS_ORIGIN_WHITELIST``
- **Configuration file variable**: ``CORS_ORIGIN_WHITELIST``
- **Provided by**: `django-cors-headers <https://github.com/adamchainz/django-cors-headers>`_
- **Type**: ``list``
- **Default**: ``["127.0.0.1:8000", "localhost:3000"]``
- **Examples**:

  - ``export ARA_CORS_ORIGIN_WHITELIST="['https://api.ara.example.org', 'https://web.ara.example.org']"``
  - In a YAML configuration file::

      dev:
        CORS_ORIGIN_WHITELIST:
          - http://127.0.0.1:8000
          - http://localhost:3000
      production:
        CORS_ORIGIN_WHITELIST:
          - https://api.ara.example.org
          - https://web.ara.example.org

Hosts in the whitelist for `Cross-Origin Resource Sharing <https://en.wikipedia.org/wiki/Cross-origin_resource_sharing>`_.

This setting is typically used in order to allow the API and a web client
(such as `ara-web <https://github.com/ansible-community/ara-web>`_) to talk to
each other.

ARA_CORS_ORIGIN_REGEX_WHITELIST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_CORS_ORIGIN_REGEX_WHITELIST``
- **Configuration file variable**: ``CORS_ORIGIN_REGEX_WHITELIST``
- **Provided by**: `django-cors-headers <https://github.com/adamchainz/django-cors-headers>`_
- **Type**: ``list``
- **Default**: ``[]``
- **Examples**:

  - ``export ARA_CORS_ORIGIN_REGEX_WHITELIST="['^https://pr-\d+.ara-web.example.org$']"``
  - In a YAML configuration file::

      dev:
        CORS_ORIGIN_REGEX_WHITELIST:
          - '^https://pr-\d+.ara-web.example.org$'
      production:
        CORS_ORIGIN_REGEX_WHITELIST:
          - '^https://web.ara.example.(org|net)$'

Hosts in the whitelist for `Cross-Origin Resource Sharing <https://en.wikipedia.org/wiki/Cross-origin_resource_sharing>`_.

This setting is typically used in order to allow the API and a web client
(such as `ara-web <https://github.com/ansible-community/ara-web>`_) to talk to
each other.

Especially useful for situations like CI where the deployment domain may not be
known in advance, this setting is applied in addition to the individual domains
in the CORS_ORIGIN_WHITELIST.

ARA_CSRF_TRUSTED_ORIGINS
~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_CSRF_TRUSTED_ORIGINS``
- **Configuration file variable**: ``CSRF_TRUSTED_ORIGINS``
- **Provided by**: `Django's CSRF_TRUSTED_ORIGINS_ setting <https://docs.djangoproject.com/en/2.2/ref/settings/#csrf-trusted-origins>`_
- **Type**: ``list``
- **Default**: ``[]``
- **Examples**:

  - ``export CSRF_TRUSTED_ORIGINS="['api.ara.example.org', 'web.ara.example.org']"``
  - In a YAML configuration file::

      dev:
        CSRF_TRUSTED_ORIGINS:
          - 127.0.0.1:8000
          - localhost:3000
      production:
        CSRF_TRUSTED_ORIGINS:
          - api.ara.example.org
          - web.ara.example.org

A list of hosts which are trusted origins for unsafe requests (e.g. POST).
For a secure unsafe request, Django’s CSRF protection requires that the
request have a Referer header that matches the origin present in the Host
header. This prevents, for example, a POST request from
subdomain.example.com from succeeding against api.example.com. If you need
cross-origin unsafe requests over HTTPS, continuing the example, add
"subdomain.example.com" to this list. The setting also supports subdomains,
so you could add ".example.com", for example, to allow access from all
subdomains of example.com.

ARA_DATABASE_CONN_MAX_AGE
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_CONN_MAX_AGE``
- **Configuration file variable**: ``DATABASE_CONN_MAX_AGE``
- **Provided by**: Django's CONN_MAX_AGE_ database setting
- **Type**: ``integer``
- **Default**: ``0``

The lifetime of a database connection, in seconds, before it is recycled by
Django.

The default of ``0`` results in connections being closed automatically
after each request and is appropriate if the API server is not running as a
persistent service.

When running the API server as a persistent service, this setting can be
increased to values such as ``300`` in order to enable persistent connections
and avoid the performance overhead of re-establishing connections for each
request.

When using the ``django.db.backends.mysql`` database engine, this value should
be lower than the MySQL server's ``wait_timeout`` configuration to prevent the
database server from closing the connection before Django can complete queries.

ARA_DATABASE_ENGINE
~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_ENGINE``
- **Configuration file variable**: ``DATABASE_ENGINE``
- **Provided by**: Django's ENGINE_ database setting
- **Type**: ``string``
- **Default**: ``django.db.backends.sqlite3``
- **Examples**:

  - ``django.db.backends.sqlite3``
  - ``django.db.backends.postgresql``
  - ``django.db.backends.mysql``
  - ``ara.server.db.backends.distributed_sqlite``

The Django database driver to use.

When using anything other than sqlite3 default driver, make sure to set the
other database settings to allow the API server to connect to the database.

ARA_DATABASE_NAME
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_NAME``
- **Configuration file variable**: ``DATABASE_NAME``
- **Provided by**: Django's NAME_ database setting
- **Type**: ``string``
- **Default**: ``~/.ara/server/ansible.sqlite``

The name of the database.

When using sqlite, this is the absolute path to the sqlite database file.
When using drivers such as MySQL or PostgreSQL, it's the name of the database.

ARA_DATABASE_USER
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_USER``
- **Configuration file variable**: ``DATABASE_USER``
- **Provided by**: Django's USER_ database setting
- **Type**: ``string``
- **Default**: ``None``

The username to connect to the database.

Required when using something other than sqlite.

ARA_DATABASE_PASSWORD
~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_PASSWORD``
- **Configuration file variable**: ``DATABASE_PASSWORD``
- **Provided by**: Django's PASSWORD_ database setting
- **Type**: ``string``
- **Default**: ``None``

The password to connect to the database.

Required when using something other than sqlite.

ARA_DATABASE_HOST
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_HOST``
- **Configuration file variable**: ``DATABASE_HOST``
- **Provided by**: Django's HOST_ database setting
- **Type**: ``string``
- **Default**: ``None``

The host for the database server.

Required when using something other than sqlite.

ARA_DATABASE_PORT
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_PORT``
- **Configuration file variable**: ``DATABASE_PORT``
- **Provided by**: Django's PORT_ database setting
- **Type**: ``string``
- **Default**: ``None``

The port to use when connecting to the database server.

It is not required to set the port if you're using default ports for MySQL or
PostgreSQL.

ARA_DATABASE_OPTIONS
~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DATABASE_OPTIONS``
- **Configuration file variable**: ``DATABASE_OPTIONS``
- **Provided by**: Django's OPTIONS_ database setting
- **Type**: ``dictionary``
- **Default**: ``{}``
- **Example**::

    export ARA_DATABASE_OPTIONS='@json {"ssl": {"ca": "/etc/ssl/certificate.pem"}}'
    # or in settings.yaml:
    DATABASE_OPTIONS:
      ssl:
        ca: "/etc/ssl/certificate.pem"

Database options to pass to the Django database backend.

ARA_DEBUG
~~~~~~~~~

- **Environment variable**: ``ARA_DEBUG``
- **Configuration file variable**: ``DEBUG``
- **Provided by**: Django's DEBUG_
- **Type**: ``string``
- **Default**: ``false``

Whether or not Django's debug mode should be enabled.

The Django project recommends turning this off for production use.

ARA_DISTRIBUTED_SQLITE
~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DISTRIBUTED_SQLITE``
- **Configuration file variable**: ``DISTRIBUTED_SQLITE``
- **Provided by**: ``ara.server.db.backends.distributed_sqlite`` and ``ara.server.wsgi.distributed_sqlite``
- **Type**: ``bool``
- **Default**: ``False``

Whether or not to enable the distributed sqlite database backend and WSGI application.

This feature is useful for loading different ARA sqlite databases dynamically
based on request URLs.

For more information, see: :ref:`distributed sqlite backend <distributed-sqlite-backend>`.

ARA_DISTRIBUTED_SQLITE_PREFIX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DISTRIBUTED_SQLITE_PREFIX``
- **Configuration file variable**: ``DISTRIBUTED_SQLITE_PREFIX``
- **Provided by**: ``ara.server.db.backends.distributed_sqlite`` and ``ara.server.wsgi.distributed_sqlite``
- **Type**: ``string``
- **Default**: ``ara-report``

Under which URL should requests be delegated to the distributed sqlite wsgi application.
``ara-report`` would delegate everything under ``.*/ara-report/.*``

The path leading to this prefix must contain the ``ansible.sqlite`` database file, for example:
``/var/www/logs/some/path/ara-report/ansible.sqlite``.

For more information, see: :ref:`distributed sqlite backend <distributed-sqlite-backend>`.

ARA_DISTRIBUTED_SQLITE_ROOT
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_DISTRIBUTED_SQLITE_ROOT``
- **Configuration file variable**: ``DISTRIBUTED_SQLITE_ROOT``
- **Provided by**: ``ara.server.db.backends.distributed_sqlite`` and ``ara.server.wsgi.distributed_sqlite``
- **Type**: ``string``
- **Default**: ``/var/www/logs``

Root directory under which databases will be found relative to the requested URLs.

This will restrict where the WSGI application will go to seek out databases.

For example, the URL ``example.org/some/path/ara-report`` would translate to
``/var/www/logs/some/path/ara-report``.

For more information, see: :ref:`distributed sqlite backend <distributed-sqlite-backend>`.

ARA_ENV
~~~~~~~

- **Environment variable**: ``ARA_ENV``
- **Configuration file variable**: None, this variable defines which section of a configuration file is loaded.
- **Type**: ``string``
- **Default**: ``development``
- **Provided by**: dynaconf_

If you are using the API server in different environments and would like keep
your configuration in a single file, you can use this variable to select a
specific environment's settings.

For example::

    # Default settings are used only when not provided in the environments
    default:
        READ_LOGIN_REQUIRED: false
        WRITE_LOGIN_REQUIRED: false
        LOG_LEVEL: INFO
        DEBUG: false
    # Increase verbosity and debugging for the default development environment
    development:
        LOG_LEVEL: DEBUG
        DEBUG: true
        SECRET_KEY: dev
    # Enable write authentication when using the production environment
    production:
        WRITE_LOGIN_REQUIRED: true
        SECRET_KEY: prod

With the example above, loading the development environment would yield the
following settings:

- READ_LOGIN_REQUIRED: ``false``
- WRITE_LOGIN_REQUIRED: ``false``
- LOG_LEVEL: ``DEBUG``
- DEBUG: ``true``
- SECRET_KEY: ``dev``

Another approach to environment-specific configuration is to use
``ARA_SETTINGS`` and keep your settings in different files such as ``dev.yaml``
or ``prod.yaml`` instead.

.. tip::
   If it does not exist, the API server will generate a default configuration
   file at ``~/.ara/server/settings.yaml``.
   This generated file sets up all the configuration keys in the **default**
   environment.
   This lets users override only the parameters they are interested in for
   specific environments.

ARA_EXTERNAL_AUTH
~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_EXTERNAL_AUTH``
- **Configuration file variable**: ``EXTERNAL_AUTH``
- **Type**: ``bool``
- **Default**: ``False``
- **Provided by**: django-rest-framework `authentication <https://www.django-rest-framework.org/api-guide/authentication/>`_

Whether or not to enable external authentication.

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
        level: INFO
        version: 1

The python logging configuration for the API server.

ARA_LOG_LEVEL
~~~~~~~~~~~~~

- **Environment variable**: ``ARA_LOG_LEVEL``
- **Configuration file variable**: ``LOG_LEVEL``
- **Type**: ``string``
- **Default**: ``INFO``

Log level of the different components from the API server.

``ARA_LOG_LEVEL`` changes the log level of the default logging configuration
provided by ARA_LOGGING_.

ARA_SETTINGS
~~~~~~~~~~~~

- **Environment variable**: ``ARA_SETTINGS``
- **Configuration file variable**: None, this variable defines the configuration file itself.
- **Type**: ``string``
- **Default**: ``None``
- **Provided by**: dynaconf_

Location of an API server configuration file to load settings from.
The API server will generate a default configuration file at
``~/.ara/server/settings.yaml`` that you can use to get started.

Note that while the configuration file is in YAML by default, it is possible
to have configuration files written in ``ini``, ``json`` and ``toml`` as well.

Settings and configuration parsing by the API server is provided by the dynaconf_
python library.

.. _dynaconf: https://github.com/rochacbruno/dynaconf

ARA_PAGE_SIZE
~~~~~~~~~~~~~

- **Environment variable**: ``ARA_PAGE_SIZE``
- **Configuration file variable**: ``PAGE_SIZE``
- **Type**: ``integer``
- **Default**: ``100``
- **Provided by**: django-rest-framework `pagination <https://www.django-rest-framework.org/api-guide/pagination/>`_

When querying the API server or the built-in reporting interface, the amount
of items per page returned by default.

ARA_READ_LOGIN_REQUIRED
~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_READ_LOGIN_REQUIRED``
- **Configuration file variable**: ``READ_LOGIN_REQUIRED``
- **Type**: ``bool``
- **Default**: ``False``
- **Provided by**: `django-rest-framework permissions <https://www.django-rest-framework.org/api-guide/permissions>`_

Determines if authentication is required before being authorized to query all
API endpoints exposed by the server.

There is no concept of granularity: users either have access to query
everything or they don't.

Enabling this feature first requires setting up :ref:`users <api-security:Authentication and user management>`.

ARA_SECRET_KEY
~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_SECRET_KEY``
- **Configuration file variable**: ``SECRET_KEY``
- **Provided by**: Django's SECRET_KEY_
- **Type**: ``string``
- **Default**: Randomized with ``django.utils.crypto.get_random_string()``

A secret key for a particular Django installation. This is used to provide
cryptographic signing, and should be set to a unique, unpredictable value.

If it is not set, a random token will be generated and persisted in the
default configuration file.

ARA_TIME_ZONE
~~~~~~~~~~~~~

- **Environment variable**: ``ARA_TIME_ZONE``
- **Configuration file variable**: ``TIME_ZONE``
- **Provided by**: Django's TIME_ZONE_
- **Type**: ``string``
- **Default**: Local system timezone
- **Examples**:

  - ``UTC``
  - ``US/Eastern``
  - ``America/Montreal``
  - ``Europe/Paris``

The time zone to store and return results in.

ARA_WRITE_LOGIN_REQUIRED
~~~~~~~~~~~~~~~~~~~~~~~~

- **Environment variable**: ``ARA_WRITE_LOGIN_REQUIRED``
- **Configuration file variable**: ``WRITE_LOGIN_REQUIRED``
- **Type**: ``bool``
- **Default**: ``False``
- **Provided by**: `django-rest-framework permissions <https://www.django-rest-framework.org/api-guide/permissions>`_

Determines if authentication is required before being authorized to post data to
all API endpoints exposed by the server.

There is no concept of granularity: users either have access to query
everything or they don't.

Enabling this feature first requires setting up :ref:`users <api-security:Authentication and user management>`.
