Installing ARA
==============
Installing ARA is easy.

RHEL, CentOS, Fedora packages
-----------------------------
Required dependencies
~~~~~~~~~~~~~~~~~~~~~
::

    yum -y install gcc python-devel libffi-devel openssl-devel redhat-rpm-config

Development or integration testing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    yum -y install python-setuptools tree libselinux-python
    easy_install pip
    pip install tox

Ubuntu, Debian packages
-----------------------
Required dependencies
~~~~~~~~~~~~~~~~~~~~~
::

    apt-get -y install gcc python-dev libffi-dev libssl-dev

Development or integration testing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    apt-get -y install python-pip tree
    pip install tox

Installing ARA from trunk source
--------------------------------
::

    pip install git+https://git.openstack.org/openstack/ara

Installing ARA from latest release on PyPi
------------------------------------------
::

    pip install ara
