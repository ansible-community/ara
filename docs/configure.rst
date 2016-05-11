Configuring ARA
===============
Set up Ansible to use ARA
-------------------------
To use ARA, you'll first need to set up Ansible to use the ARA callback_.

The callback comes provided when installing ARA but you need to let Ansible
know where it is located.

Set up your `ansible.cfg`_ file to seek that callback in the appropriate
directory, for example::

    [defaults]
    callback_plugins = /usr/lib/python2.7/site-packages/ara/callback:$VIRTUAL_ENV/lib/python2.7/site-packages/ara/callback

.. _callback: https://github.com/dmsimard/ara/blob/master/callback.py
.. _ansible.cfg: http://docs.ansible.com/ansible/intro_configuration.html#configuration-file

*That's it!*

ARA specific settings
---------------------
ARA uses the same mechanism and configuration files as Ansible to retrieve it's
configuration.

The order of priority is the following:

1. Environment variables
2. ``./ansible.cfg`` (*In the current working directory*)
3. ``~/.ansible.cfg`` (*In the home directory*)
4. ``/etc/ansible/ansible.cfg``

Database location
~~~~~~~~~~~~~~~~~
ARA records Ansible data in a sqlite database.
Both the callback and the web application needs to know where that database
is located.

By default, the path to the database is set to ``~/.ara/ansible.sqlite``.
You can change this path in the same way that you define your Ansible settings.

You can use an environment variable::

    export ARA_DATABASE=/tmp/ara.sqlite

You can also use the ``ansible.cfg`` file::

    [ara]
    database = /tmp/ara.sqlite

The next time you run Ansible, ARA will ensure the directory and the database
exists and then start using it.

The web application
-------------------
The ARA frontend does not necessarily need to run on the same machine that
Ansible is executed from but it does need a database and know it's location.

You could, for example, transfer databases from remote locations (and
aggregate them) so that you could browse playbook runs from a single interface.

The frontend that ARA provides is a simple Flask application.
As such, you can configure it to run like `any other Flask application`_.

To run the development webserver, you can run::

    $ ara-dev-server
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger pin code: 605-724-687

.. _any other Flask application: http://flask.pocoo.org/docs/0.10/deploying/uwsgi/
