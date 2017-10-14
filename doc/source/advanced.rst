.. _advanced_configuration:

Serving ARA sqlite databases over http
======================================

Hosting statically generated reports is not very efficient at a large scale.
The reports are relatively small in size but can contain thousands of files if
you are generating a report that contains thousands of tasks.

However, using a centralized database (such as MySQL) might not be optimal
either. Perhaps due to the latency or maybe because of the concurrency of the
runs.
It is also possible you are not interested in aggregating data in the first
place and would rather keep individual reports.

ARA ships a bundled WSGI middleware, ``wsgi_sqlite.py``.

This middleware allows you to store your ``ansible.sqlite`` databases on a
web server (for example, a logserver for your CI jobs) and load these databases
on the fly without needing to generate static reports.

It works by matching a requested URL
(ex: ``http://logserver/some/path/ara-report``) against the filesystem location
(ex: ``/srv/static/logs/some/path/ara-report/ansible.sqlite``) and loading
ARA's web application so that it reads from the database directly.

To put this use case into perspective, it was "benchmarked" against a single
job from the OpenStack-Ansible_ project:

- 4 playbooks
- 4647 tasks
- 4760 results
- 53 hosts, of which 39 had gathered host facts
- 416 saved files

Generating a static report from that database takes ~1min30s on an average
machine. It weighs 63MB (27MB recursively gzipped), contains 5321 files and
5243 directories.

This middleware allows you to host the exact same report on your web server
just by storing the sqlite database which is just one file and weighs 5.6MB.

.. _OpenStack-Ansible: https://github.com/openstack/openstack-ansible

wsgi_sqlite configuration
-------------------------

Configuration for the ``wsgi_sqlite.py`` script can be done through environment
variables, for example with Apache's ``SetEnv`` directive.

ARA_WSGI_USE_VIRTUALENV
~~~~~~~~~~~~~~~~~~~~~~~

Enable virtual environment usage if ARA is installed in a virtual
environment. You will need to set ``ARA_WSGI_VIRTUALENV_PATH`` if enabling
this.

Defaults to ``0``, set to ``1`` to enable.

ARA_WSGI_VIRTUALENV_PATH
~~~~~~~~~~~~~~~~~~~~~~~~

When using a virtual environment, where the virtualenv is located.
Defaults to ``None``, set to the absolute path of your virtualenv.

ARA_WSGI_TMPDIR_MAX_AGE
~~~~~~~~~~~~~~~~~~~~~~~

This WSGI middleware creates temporary directories which should be
discarded on a regular basis to avoid them accumulating.
This is a duration, in seconds, before cleaning directories up.

Defaults to ``3600``.

ARA_WSGI_LOG_ROOT
~~~~~~~~~~~~~~~~~

Absolute path on the filesystem that matches the ``DocumentRoot`` of your
webserver vhost.

For a ``DocumentRoot`` of ``/srv/static/logs``, this value should be
``/srv/static/logs``.

Defaults to ``/srv/static/logs``.

ARA_WSGI_DATABASE_DIRECTORY
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Subdirectory in which ARA sqlite databases are expected to reside in.
For example, ``ara-report`` would expect:
``http://logserver/some/path/ara-report/ansible.sqlite``.

This variable should match the ``WSGIScriptAliasMatch`` pattern of your
webserver vhost.

Defaults to ``ara-report``.

Using wsgi_sqlite with Apache's mod_wsgi
----------------------------------------

The vhost requires you to redirect requests to ``*/ara-report/*`` to the WSGI
middleware. In order to do so, the vhost must look like the following::

    <VirtualHost *:80>
      # Remember that DocumentRoot and ARA_WSGI_LOG_ROOT must match
      DocumentRoot /srv/static/logs
      ServerName logs.domain.tld

      ErrorLog /var/log/httpd/logs.domain.tld-error.log
      LogLevel warn
      CustomLog /var/log/httpd/logs.domain.tld-access.log combined

      SetEnv ARA_WSGI_TMPDIR_MAX_AGE 3600
      SetEnv ARA_WSGI_LOG_ROOT /srv/static/logs
      SetEnv ARA_WSGI_DATABASE_DIRECTORY ara-report
      WSGIDaemonProcess ara user=apache group=apache processes=4 threads=1
      WSGIScriptAliasMatch ^.*/ara-report /var/www/cgi-bin/ara-wsgi-sqlite
    </VirtualHost>

You'll notice the ``WSGIScriptAliasMatch`` directive pointing to the WSGI
script. This is bundled when installing ARA and can be copied to the location
of your choice by doing::

    cp -p $(which ara-wsgi-sqlite) /var/www/cgi-bin/
