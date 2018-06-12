.. _webserver_configuration:

Web Server Configuration
========================

The web interface provided by ARA is a simple Flask application.
There are many ways to `deploy and host`_ a Flask application, here we cover
two different ways which should help you get started.

In any case, ARA will need to be installed before you proceed. Refer to the
:ref:`documentation <installation>` if you need to know how to install ARA.

.. _deploy and host: http://flask.pocoo.org/docs/0.12/deploying/

.. _web_config_embedded:

Embedded server
---------------

ARA comes bundled with an embedded server meant for development or
debugging purposes.

Note that any serious deployment should probably not be running off of this as
it is not meant to be serving clients directly at any kind of scale.

To start the development server, use the provided ``ara-manage runserver``
command::

    $ ara-manage runserver --help
    usage: ara-manage runserver [-?] [-h HOST] [-p PORT] [--threaded]
                                [--processes PROCESSES] [--passthrough-errors]
                                [-d] [-D] [-r] [-R]

    Runs the Flask development server i.e. app.run()

    optional arguments:
      -?, --help            show this help message and exit
      -h HOST, --host HOST
      -p PORT, --port PORT
      --threaded
      --processes PROCESSES
      --passthrough-errors
      -d, --debug           enable the Werkzeug debugger (DO NOT use in production
                            code)
      -D, --no-debug        disable the Werkzeug debugger
      -r, --reload          monitor Python files for changes (not 100% safe for
                            production use)
      -R, --no-reload       do not monitor Python files for changes

To expose any non-default configurations to the development server (such as the
database location), the same principles as usual apply -- you need to have an
:ref:`ansible.cfg file or declare environment variables <configuration_ara>`.

For example, to fire the server to listen on all IPv4 addresses on port 8080
while using a database at ``/tmp/ara.sqlite``::

    $ export ARA_DATABASE="sqlite:////tmp/ara.sqlite"
    $ ara-manage runserver -h 0.0.0.0 -p 8080
     * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)

.. _web_config_mod_wsgi:

Apache+mod_wsgi
---------------

.. note::

    ARA needs to be installed on the server where Apache will be running.
    Refer to the :ref:`documentation <installation>` if you need to know how
    to install ARA.

Fedora/CentOS/RHEL
~~~~~~~~~~~~~~~~~~

Install Apache+mod_wsgi
+++++++++++++++++++++++

::

    yum install httpd mod_wsgi
    systemctl enable httpd
    systemctl start httpd

Create a directory for Ansible and ARA
++++++++++++++++++++++++++++++++++++++

This directory is where we will store the files that Apache will need to read
and write to.

::

    mkdir -p /var/www/ara

Copy ARA's WSGI script to the web directory
+++++++++++++++++++++++++++++++++++++++++++

ARA provides a WSGI script when it is installed: ``ara-wsgi``.
We need to copy it to the directory we just created, ``/var/www/ara``.

The location where ``ara-wsgi`` is installed depends on how you installed ARA
and the distribution you are running. You can use ``which`` to find where it
is located::

    cp -p $(which ara-wsgi) /var/www/ara/

Create the Ansible and ARA configuration
++++++++++++++++++++++++++++++++++++++++

The defaults provided by ARA and Ansible are not suitable for a use case where
we are deploying with Apache. We need to provide different settings::

    cat <<EOF >/var/www/ara/ansible.cfg
    [defaults]
    # This directory is required to store temporary files for Ansible and ARA
    local_tmp = /var/www/ara/.ansible/tmp

    [ara]
    # This will default the database and logs location to be inside that directory.
    dir = /var/www/ara/.ara
    EOF

For additional parameters, such as the database location or backend, look at
the :ref:`configuration documentation <configuration_parameter_ara>`.

File permissions and SElinux
++++++++++++++++++++++++++++

Make sure everything is owned by Apache so it can read and write to the
directory::

    chown -R apache:apache /var/www/ara

Additionally, if you are running with selinux enforcing, you need to allow
Apache to manage the files in ``/var/www/ara``. You can toggle the
``httpd_unified`` boolean for that::

    setsebool -P httpd_unified 1

Apache configuration
++++++++++++++++++++

Set up the Apache virtual host at ``/etc/httpd/conf.d/ara.conf``::

    <VirtualHost *:80>
        # Replace ServerName by your hostname
        ServerName ara.domain.tld

        ErrorLog /var/log/httpd/ara-error.log
        LogLevel warn
        CustomLog /var/log/httpd/ara-access.log combined

        WSGIDaemonProcess ara user=apache group=apache processes=4 threads=1
        WSGIScriptAlias / /var/www/ara/ara-wsgi

        SetEnv ANSIBLE_CONFIG /var/www/ara/ansible.cfg

        <Directory /var/www/ara>
            WSGIProcessGroup ara
            WSGIApplicationGroup %{GLOBAL}
            Require all granted
        </Directory>
    </VirtualHost>

Restart Apache and you're done::

    systemctl restart httpd

You should now be able to access the web interface at the domain you set up !

Debian/Ubuntu
~~~~~~~~~~~~~

Install Apache+mod_wsgi
+++++++++++++++++++++++

::

    apt-get install apache2 libapache2-mod-wsgi
    systemctl enable apache2
    systemctl start apache2

Create the directory for Ansible and ARA
++++++++++++++++++++++++++++++++++++++++

This directory is where we will store the files that Apache will need to read
and write to.

::

    mkdir -p /var/www/ara

Copy ARA's WSGI script to the web directory
+++++++++++++++++++++++++++++++++++++++++++

ARA provides a WSGI script when it is installed: ``ara-wsgi``.
We need to copy it to the directory we just created, ``/var/www/ara``.

The location where ``ara-wsgi`` is installed depends on how you installed ARA
and the distribution you are running. You can use ``which`` to find where it
is located::

    cp -p $(which ara-wsgi) /var/www/ara/

Create the Ansible and ARA configuration
++++++++++++++++++++++++++++++++++++++++

The defaults provided by ARA and Ansible are not suitable for a use case where
we are deploying with Apache. We need to provide different settings::

    cat <<EOF >/var/www/ara/ansible.cfg
    [defaults]
    # This directory is required to store temporary files for Ansible and ARA
    local_tmp = /var/www/ara/.ansible/tmp

    [ara]
    # This will default the database and logs location to be inside that directory.
    dir = /var/www/ara/.ara
    EOF

For additional parameters, such as the database location or backend, look at
the :ref:`configuration documentation <configuration_parameter_ara>`.

File permissions
++++++++++++++++

Make sure everything is owned by Apache so it can read and write to the
directory::

    chown -R www-data:www-data /var/www/ara

Apache configuration
++++++++++++++++++++

Set up the Apache virtual host at ``/etc/apache2/sites-available/ara.conf``::

    <VirtualHost *:80>
        # Replace ServerName by your hostname
        ServerName ara.domain.tld

        ErrorLog /var/log/apache2/ara-error.log
        LogLevel warn
        CustomLog /var/log/apache2/ara-access.log combined

        WSGIDaemonProcess ara user=www-data group=www-data processes=4 threads=1
        WSGIScriptAlias / /var/www/ara/ara-wsgi

        SetEnv ANSIBLE_CONFIG /var/www/ara/ansible.cfg

        <Directory /var/www/ara>
            WSGIProcessGroup ara
            WSGIApplicationGroup %{GLOBAL}
            Require all granted
        </Directory>
    </VirtualHost>

Ensure the configuration is enabled::

    a2ensite ara

Restart Apache and you're done::

    systemctl restart apache2

You should now be able to access the web interface at the domain you set up !

Serving static HTML reports
---------------------------

Nginx Configuration
~~~~~~~~~~~~~~~~~~~

Assuming that you are storing ARA reports as static html using a Nginx server
you may find this configuration useful as it assures that prezipped files
(like ``index.html.gz``) are served transparently by the server. ::

    location /artifacts {
        gzip_static on;
        root /var/www/html;
        autoindex on;
        index index.html index.htm;
        rewrite ^(.*)/$ $1/index.html;
    }

You may need a different nginx build that has the ngx_http_gzip_static_module_
compiled. For example nginx from EPEL_ (CentOS/RHEL)
yum repositories includes this module.

.. _ngx_http_gzip_static_module: https://nginx.org/en/docs/http/ngx_http_gzip_static_module.html
.. _EPEL: https://fedoraproject.org/wiki/EPEL
