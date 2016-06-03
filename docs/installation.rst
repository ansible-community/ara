Installing ARA
==============
Installing ARA is easy.

RHEL, CentOS, Fedora packages
-----------------------------
Required dependencies
~~~~~~~~~~~~~~~~~~~~~
::

    yum -y install gcc python-devel libffi-devel openssl-devel

Development or integration testing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    yum -y install python-virtualenv git hg svn rubygems python-setuptools tree
    easy_install pip

Ubuntu, Debian packages
-----------------------
Required dependencies
~~~~~~~~~~~~~~~~~~~~~
::

    apt-get -y install gcc python-dev libffi-dev libssl-dev

Development or integration testing dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    apt-get -y install python-pip python-virtualenv ruby git mercurial subversion tree

Installing ARA from source
--------------------------
::

    git clone https://github.com/dmsimard/ara
    cd ara
    pip install .

Installing ARA from pip
-----------------------
::

    pip install ara
