CLI: ara API client
===================

Installing ara provides an ``ara`` command line interface client in order to
query API servers from shell scripts or from the terminal.

ara
---

.. command-output:: ara --help

ara expire
----------

.. note::

    This command requires write privileges.
    You can read more about read and write permissions :ref:`here <api-security:user management>`.

.. command-output:: ara expire --help

Examples:

.. code-block:: bash

    # Return which objects would be expired by ommitting --confirm
    ara expire

    # Expire running objects without updates faster than the default
    ara expire --hours 4 --confirm

ara playbook list
-----------------

.. command-output:: ara playbook list --help

Query a running API server for the 10 latest failed playbooks:

.. code-block:: bash

    ara playbook list --client http \
      --server https://api.demo.recordsansible.org \
      --status failed \
      --limit 10

Get a list of playbooks matching a partial path and order the results by
duration using the default offline API client:

.. code-block:: bash

    ara playbook list --path="playbooks/site.yaml" --order=duration

Get a list of playbooks and format the results as json or yaml instead of pretty tables:

.. code-block:: bash

    ara playbook list -f json
    ara playbook list -f yaml

ara playbook show
-----------------

.. command-output:: ara playbook show --help

Show details about a playbook from a running API server and format the result in json:

.. code-block:: bash

    ara playbook show --client http --server https://api.demo.recordsansible.org 1 -f json

Show details about a playbook from a local installation using the default offline
API client and format the result in yaml:

.. code-block:: bash

    ara playbook show 1 -f yaml

ara playbook delete
-------------------

.. note::

    This command requires write privileges.
    You can read more about read and write permissions :ref:`here <api-security:user management>`.

.. command-output:: ara playbook delete --help

ara playbook prune
------------------

Pruning keeps the database size in check and the performance optimal by deleting older playbooks.
It is recommended to run this command inside a task scheduler (such as cron) since the server does not run this command
automatically.

.. note::

    This command requires write privileges.
    You can read more about read and write permissions :ref:`here <api-security:user management>`.

.. command-output:: ara playbook prune --help

Examples:

.. code-block:: bash

    # Return which playbooks would be deleted by ommitting --confirm
    ara playbook prune

    # Different retention for successful, unsuccessful and expired playbooks
    ara playbook prune --status ok --days 30 --confirm
    ara playbook prune --status failed --days 90 --confirm
    ara playbook prune --status expired --days 3 --confirm

    # Different retention based on labels
    ara playbook prune --label dev --days 7 --confirm
    ara playbook prune --label prod --days 90 --confirm

    # Different retention based on name or path
    ara playbook prune --name demo --days 7
    ara playbook prune --path /home/jenkins --days 14

    # Delete more than 200 playbooks per command execution
    ara playbook prune --limit 9000 --confirm

ara play list
-------------

.. command-output:: ara play list --help

Examples:

.. code-block:: bash

    # List the top 25 longest plays
    ara play list --order=-duration --limit 25

    # List plays matching a name (full or partial)
    ara play list --name apache

    # List the plays for a specific playbook and format the result in json
    ara play list --playbook 1 -f json

ara play show
-------------

.. command-output:: ara play show --help

Examples:

.. code-block:: bash

    # Show a specific play and format the results as json
    ara play show 9001 -f json

ara play delete
---------------

.. note::

    This command requires write privileges.
    You can read more about read and write permissions :ref:`here <api-security:user management>`.

.. command-output:: ara play delete --help

ara host list
-------------

.. command-output:: ara host list --help

.. note::

    From the perspective of ARA, each host is unique to a playbook run.
    Their records contain the Ansible host facts as well as their stats for a
    particular playbook run.

Examples:

.. code-block:: bash

    # List the latest 25 host results
    ara host list --limit 25

    # List host records for a specific host name
    ara host list --name localhost

    # List all the host results for a specific playbook and format the result in json
    ara host list --playbook 1 -f json

    # Only return hosts with or without unreachable task results
    ara host list --with-unreachable
    ara host list --without-unreachable

    # Only return hosts with or without changed task results
    ara host list --with-changed
    ara host list --without-changed

    # Only return hosts with or without failed task results
    ara host list --with-failed
    ara host list --without-failed

ara host show
-------------

.. command-output:: ara host show --help

.. note::

    From the perspective of ARA, each host is unique to a playbook run.
    Their records contain the Ansible host facts as well as their stats for a
    particular playbook run.

Return stats for a specified host as well as a link to the playbook report it is
involved in:

.. code-block:: bash

    ara host show 1

Include host facts as well formatted in json:

.. code-block:: bash

    # Facts do not render well in the default pretty table format
    ara host show 1 --with-facts -f json

ara host delete
---------------

.. note::

    This command requires write privileges.
    You can read more about read and write permissions :ref:`here <api-security:user management>`.

.. command-output:: ara host delete --help

ara record list
---------------

.. command-output:: ara record list --help

Examples:

.. code-block:: bash

    # List records for a specific key
    ara record list --key log_url

    # List records for a specific playbook
    ara record list --playbook 9001

ara record show
---------------

.. command-output:: ara record show --help

Examples:

.. code-block:: bash

    # Show a specific record and format the results as json
    ara record show 9001 -f json

ara record delete
-----------------

.. command-output:: ara record delete --help

ara result list
---------------

.. command-output:: ara result list --help

Return the 10 most recent failed results:

.. code-block:: bash

    ara result list --status failed --limit 10

Return the 15 results with the highest duration for a specific playbook:

.. code-block:: bash

    ara result list --playbook 389 --order=-duration --limit 15

ara result show
---------------

.. command-output:: ara result show --help

Return detailed information about a specific result:

.. code-block:: bash

    ara result show 9001

Return detailed information about a specific result, including formatted content:

.. code-block:: bash

    ara result show 9001 --with-content -f json

ara result delete
-----------------

.. note::

    This command requires write privileges.
    You can read more about read and write permissions :ref:`here <api-security:user management>`.

.. command-output:: ara result delete --help

ara task list
-------------

.. command-output:: ara task list --help

.. note::

    ara doesn't have the concept of roles but it is possible to search for
    them by path, for example: ``ara task list --path "roles/install_apache"``

    Role names are included in the task names and it is possible to search for
    role-specific tasks there as well: ``ara task list --name install_apache``.

Examples:

.. code-block:: bash

    # Return the top 25 longest running tasks
    ara task list --order=-duration --limit 25

    # Return tasks from a specific playbook
    ara task list --playbook 9001

    # Return tasks for the package action
    ara task list --action package

    # Return tasks matching a path (partial or full)
    ara task list --path="roles/install_apache"

    # Return tasks matching a name (partial or full)
    ara task list --name install_apache

ara task show
-------------

.. command-output:: ara task show --help

Return detailed information about a specific task:

.. code-block:: bash

    ara task show 9001

ara task delete
---------------

.. note::

    This command requires write privileges.
    You can read more about read and write permissions :ref:`here <api-security:user management>`.

.. command-output:: ara task delete --help

CLI: ara-manage (django API server)
===================================

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

.. warning::
    ara-manage prune has been replaced by `ara playbook prune`_ in ara 1.5.
    It will be removed in ara 1.6.

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
