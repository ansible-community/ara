Installing and using ARA
========================
Clone the source and install it
-------------------------------
::

    git clone https://github.com/dmsimard/ara
    cd ara
    pip install .

*ARA is on `PyPi`_ but is not currently kept up-to-date with the fast paced early development.*

.. _PyPi: https://pypi.python.org/pypi/ara

Set up the callback
-------------------
To use ARA, you'll first need to set up Ansible to use the ARA callback_.

The callback is provided when installing ARA but you need to let Ansible know
where to look for.
Set up your `ansible.cfg`_ file to seek that callback in the appropriate
directory, for example::

    [defaults]
    callback_plugins = /usr/lib/python2.7/site-packages/ara/callback:$VIRTUAL_ENV/lib/python2.7/site-packages/ara/callback

.. _callback: https://github.com/dmsimard/ara/blob/master/callback.py
.. _ansible.cfg: http://docs.ansible.com/ansible/intro_configuration.html#configuration-file

*That's it!*

The next time you run Ansible, ARA will generate a sqlite database at the
default path in ``~/.ara/ansible.sqlite``.

This is the database that the web application will use.

To modify the path at which the database is stored and read, modify the
configuration in ``site-packages/ara/__init__.py``.

**Note**: *The configuration of the database path will be made less awkward eventually.*

Set up the web application
--------------------------
Set this up like `any other Flask application`_, it's nothing special (yet).
To run the development webserver, you can run::

    python ara/run.py
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

.. _any other Flask application: http://flask.pocoo.org/docs/0.10/deploying/uwsgi/
