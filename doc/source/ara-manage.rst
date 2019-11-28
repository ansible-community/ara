ara-manage commandline interface
================================

``ara-manage`` is a command provided by ARA when the API server dependencies
are installed.

It is an alias to the ``python manage.py`` command interface provided by Django
and they can be used interchangeably if you are running ARA from source.

.. note::
    Django comes with a lot of built-in commands and they are not all used or
    relevant in the context of ARA so they might not be exposed, tested or
    documented.

    This documentation provides information about commands which we think are relevant.

    If you do not find a command documented here, you can find more information about
    it in the `Django documentation <https://docs.djangoproject.com/en/2.2/ref/django-admin/>`_.

    Please feel free to send a patch if we're missing anything !

ara-manage
----------

.. command-output:: ara-manage --help

ara-manage prune
----------------

Used to delete playbooks that are older than a specified amount of days.

.. command-output:: ara-manage prune --help

ara-manage changepassword
-------------------------

Change the password for a user.

Relevant when working with :ref:`authentication <api-security:user management>`.

.. command-output:: ara-manage changepassword --help

ara-manage createsuperuser
--------------------------

Superusers are relevant when setting up :ref:`authentication <api-security:user management>`.

.. command-output:: ara-manage createsuperuser --help

ara-manage makemigrations
-------------------------

Generally used to generate new SQL migrations after modifying the database model files.

.. command-output:: ara-manage makemigrations --help

ara-manage migrate
------------------

Runs SQL migrations.

They need to be run at least once before the API server can start.

.. command-output:: ara-manage migrate --help

ara-manage runserver
--------------------

Runs the embedded development server.

.. note::
    Good for small scale usage.

    Consider deploying with a WSGI application server and a web server for production use.

.. command-output:: ara-manage runserver --help

ara-manage generate
-------------------

Generates a static version of the built-in reporting web interface.

.. note::
    Good for small scale usage but inefficient and contains a lot of small files at a large scale.

.. command-output:: ara-manage generate --help
