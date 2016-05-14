Installing ARA
==============
Installing ARA is easy.

Packaged dependencies
---------------------
RHEL, CentOS, Fedora
~~~~~~~~~~~~~~~~~~~~
::

    yum -y install gcc python-devel libffi-devel openssl-devel

Ubuntu, Debian
~~~~~~~~~~~~~~
::

    apt-get -y install gcc python-dev libffi-dev libssl-dev

From source
-----------
::

    git clone https://github.com/dmsimard/ara
    cd ara
    pip install .

From pip
--------
::

    pip install ara
