.. _installation:

Installing ARA
==============

Installing ARA is easy.

RHEL, CentOS, Fedora packages
-----------------------------

Required dependencies
~~~~~~~~~~~~~~~~~~~~~

::

    yum install gcc python-devel libffi-devel openssl-devel redhat-rpm-config

Development or integration testing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    yum install python-setuptools libselinux-python libxml2-devel libxslt-devel
    easy_install pip
    pip install tox

Ubuntu, Debian packages
-----------------------

Required dependencies
~~~~~~~~~~~~~~~~~~~~~

::

    apt-get install gcc python-dev libffi-dev libssl-dev

Development or integration testing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    apt-get install python-pip libxml2-dev libxslt1-dev
    pip install tox

Installing ARA from trunk source
--------------------------------

::

    pip install git+https://git.openstack.org/openstack/ara

Installing ARA from latest release on PyPi
------------------------------------------

::

    pip install [--user] ara

When installing ARA using ``--user``, command line scripts will be installed
inside ``~/.local/bin`` folder which may not be in ``PATH``. You may want to
assure that this folder is in PATH or to use the alternative calling method
``pyhton -m ara`` which calls Ansible module directly.

The alternative calling method has the advantage that allows user to control
which python interpreter would be used. For example you could install ARA in
both python2 and python3 and call the one you want.
