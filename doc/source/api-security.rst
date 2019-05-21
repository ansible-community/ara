.. _security:

ARA API Server authentication and security
==========================================

The API server ships with a default configuration that emphasizes simplicity to
let users get started quickly.

By default:

- A random SECRET_KEY will be generated once if none are supplied
- No users are created
- API authentication and permissions are not enabled
- ALLOWED_HOSTS and CORS_ORIGIN_WHITELIST are configured for use on localhost

These default settings can be configured according to the requirements of your
deployments.

Setting a custom secret key
---------------------------

By default, the API server randomly generates a token for the
:ref:`api-configuration:ARA_SECRET_KEY` setting if none have
been supplied by the user.

This value is persisted in the server configuration file in order to prevent
the key from changing on every instanciation of the server.

The default location for the server configuration file is
``~/.ara/server/settings.yaml``.

You can provide a custom secret key by supplying the ``ARA_SECRET_KEY``
environment variable or by specifying the ``SECRET_KEY`` setting in your server
configuration file.

User management
---------------

The API server leverages Django's `user management <https://docs.djangoproject.com/en/2.1/topics/auth/default/>`_
but doesn't create any user by default.

.. note::
    Creating users does not enable authentication on the API.
    In order to make authentication required for using the API, see `Enabling authentication for read or write access`_.

In order to create users, you'll need to create a superuser account before
running the API server::

    $ ara-manage createsuperuser --username=joe --email=joe@example.com
    Password:
    Password (again):
    Superuser created successfully.

.. tip::
    If you ever need to reset the password of a superuser account, this can be
    done with the "changepassword" command::

        $ ara-manage changepassword joe
        Changing password for user 'joe'
        Password:
        Password (again):
        Password changed successfully for user 'joe'

Once the superuser has been created, make sure the API server is started and
then login to the Django web administrative interface using the credentials
you just set up.

By default, you can start the API server with ``ara-manage runserver`` and
access the admin interface at ``http://127.0.0.1:8000/admin/``.

Log in to the admin interface:

.. image:: _static/admin_panel_login.png

Access the authentication and authorization configuration:

.. image:: _static/admin_panel_auth.png

And from here, you can manage existing users or create new ones:

.. image:: _static/admin_panel_users.png

Enabling authentication for read or write access
------------------------------------------------

Once you have created your users, you can enable authentication against the API
for read (ex: GET) and write (ex: DELETE, POST, PATCH) requests.

This is done with the two following configuration options:

- :ref:`api-configuration:ARA_READ_LOGIN_REQUIRED` for read access
- :ref:`api-configuration:ARA_WRITE_LOGIN_REQUIRED` for write access

These settings are global and are effective for all API endpoints.

Setting up authentication for the Ansible plugins
-------------------------------------------------

The callback plugin used to record playbooks as well as the ``ara_record``
action plugin will need to authenticate against the API if authentication is
enabled and required.

You can specify the necessary credentials through the ``ARA_API_USERNAME`` and
``ARA_API_PASSWORD`` environment variables or through your ``ansible.cfg`` file:

.. code-block:: ini

    [defaults]
    # ...

    [ara]
    api_client = http
    api_server = http://api.example.org
    api_username = ara
    api_password = password

Using authentication with the API clients
-----------------------------------------

To instanciate an authenticated client with the built-in basic HTTP
authentication provided by Django:

.. code-block:: python

    from ara.clients.utils import get_client
    client = get_client(
        client="http",
        endpoint="http://api.example.org",
        username="ara",
        password="password"
    )

If you have a custom authentication that is supported by the
`python requests <https://2.python-requests.org/en/master/user/authentication/>`_
library, you can also pass the relevant ``auth`` object directly to the client:

.. code-block:: python

    from ara.clients.http import AraHttpClient
    from requests_oauthlib import OAuth1
    auth = OAuth1(
        "YOUR_APP_KEY",
        "YOUR_APP_SECRET",
        "USER_OAUTH_TOKEN",
        "USER_OAUTH_TOKEN_SECRET"
    )
    client = AraHttpClient(endpoint="http://api.example.org", auth=auth)

Managing hosts allowed to serve the API
---------------------------------------

By default, :ref:`api-configuration:ARA_ALLOWED_HOSTS` authorizes
``localhost``, ``::1`` and ``127.0.0.1`` to serve requests for the API server.

In order to host an instance of the API server on another domain, the domain must
be part of this list or the application server will deny any requests sent to
it.

Managing CORS (cross-origin resource sharing)
---------------------------------------------

The :ref:`api-configuration:ARA_CORS_ORIGIN_WHITELIST` default is designed to
allow a local development instance of an `ara-web <https://github.com/ansible-community/ara-web>`_
dashboard to communicate with a local development instance of the API server.

The whitelist must contain the domain names where you plan on hosting instances
of ara-web.
