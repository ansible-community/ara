..
  note: generated through doc/changelog-release-notes.sh
.. _changelog-release-notes:

Changelog and release notes
***************************

1.7.2 (2024-08-29)
##################

https://github.com/ansible-community/ara/releases/tag/1.7.2

.. code-block:: text

    This is the 1.7.2 stable release of ara.
    
    1.7.2 is a maintenance and bugfix release that includes a few new features.
    
    Changes since 1.7.1:
    
    UI
    --
    
    - When recording diffs, properly format and display the "prepared" key
      for the modules that use it (apt, git, cli_config and others)
    - Sorting task results by duration when browsing playbook results works once again
    - Updated bootstrap css from 5.3.0 to 5.3.3
    
    Callback plugin
    ---------------
    
    - Catch SIGINT and SIGTERM signals resulting in the interruption of playbooks to
      set the status of the playbook to "expired" instead of keeping it running forever
      unless expired with `ara playbook expire` from the CLI.
    
    API Client
    ----------
    
    - Add support for UTF-8 encoded usernames and passwords
    
    Docs
    ----
    
    - Add .readthedocs.yaml to fix broken documentation builds
    - Formally include ara as a dependency in order to include --help commands in the docs
    - Added an introduction page
    
    Maintenance and packaging
    -------------------------
    
    - Made dependency on ruamel.yaml explicit rather than implicit
    - Update usage of logging.warn to logging.warning for
      python 3.13
    - Updated versions of Ansible tested in CI to Ansible 10 and ansible-core 2.17
    
    Upgrade notes
    -------------
    
    There are no API changes or SQL migrations in this release.

1.7.1 (2024-02-06)
##################

https://github.com/ansible-community/ara/releases/tag/1.7.1

.. code-block:: text

    This is the 1.7.1 stable release of ara.
    
    1.7.1 is a maintenance release that features minor bug fixes.
    
    Changes since 1.7.0:
    
    - Address deprecation of yaml.dump in ruamel.yaml when generating
      the default server settings.yaml file (#524)
    - Don't use setuptools/pkg_resources to retrieve the version of ara
      since it is not always installed by default.
    - Bumped the version of ansible, ansible-core and fedora used in Zuul
      CI jobs.

1.7.0 (2023-09-10)
##################

https://github.com/ansible-community/ara/releases/tag/1.7.0

.. code-block:: text

    This is the 1.7.0 stable release of ara.
    
    It features a refresh of the built-in web interface with the upgrade
    from bootstrap 4.6.0 to 5.3.0.
    
    It lifts the supported version of django up to the latest LTS, 4.2, and
    raises the minimum version of python to >=3.8 as a result.
    
    There's also bug fixes and new features.
    
    Changes since 1.6.1:
    
    UI
    --
    Boostrap and CSS:
    
    - Update bootstrap CSS from 4.6.0 to 5.3.0 and fix broken layout and
      components as a result of the update
    - Removed separate light/dark themes via bootstrap-darkly and
      bootstrap-flatly: bootstrap 5.3 features a new built-in dark theme
    - Re-worked the dark/light theme selection to match the new bootstrap
      built-in dark theme including pygments highlighting for pretty-printed
      output
    - Removed jquery, it is no longer required with bootstrap
    - Re-worked implementation of file line highlighting since it relied on
      jquery
    - Fixed tooltip implementation (i.e, for task tags) since the
      implementation in bootstrap had changed
    
    Site-wide minor cleanups and improvements:
    
    - Headers and font size made generally larger and more consistent
    - Improved the about and CLI argument modals
    - Improved display for the report and CLI argument buttons
    - Improved the playbook report header card
    - Adjusted search accordions to match new bootstrap theme
    - Improvements to responsiveness of layout at smaller (e.g, mobile)
      resolutions
    - Truncate excessively long controller hostnames such that they do not
      needlessly take up all the table's available width
    - Added support for colored diff when viewing task results
    - Fixed the API link when viewing tasks to properly direct to
      /api/v1/tasks
    
    Django templating:
    
    - Large chunks of templating were moved out to partials/tables and
      partials/search in order to improve readability.
    - Round of template cleanups and fixes as reported by djlint
    - Will continue to be a work in progress to simplify and standardize
      templates.
    
    API Server
    ----------
    
    - Raised the requirement on django from >=3.2,<3.3 to >=3.2,<4.3 to
      allow installation with the latest LTS release of django.
    - Raised the requirement on python from >=3.6 to >=3.8 to accomodate
      django 4.2.
    - Ignored Django warning about the lack of a STATIC_ROOT directory.
      ara uses whitenoise for serving static files which makes the warning
      superfluous. (#492)
    
    Ansible callback plugin
    -----------------------
    
    - Added ARA_RECORD_CONTROLLER_NAME and ARA_RECORD_USER_NAME settings to
      override the automatic detection of the controller hostname and user
      name for the specified values.
    - Added ARA_RECORD_TASK_CONTENT which defaults to true but can be set to
      false to prevent ara from recording the task content for use cases
      where it is not important or to avoid leaking sensitive information.
    
    Maintenance
    -----------
    
    Update versions, CI test jobs and container images:
    
    - containers: updated fedora base image from 36 to 38
    - containers: updated centos-pypi image from stream8 to stream9
    - zuul: Update fedora base image from 36 to 38
    - zuul: Update ansible version tested from 6.4.0 to 8.3.0
    - zuul: Update versions of ansible-core tested (2.14, 2.15)
    - Dropped testing for Ansible 2.9 which has been EOL for over a year.
    
    Upgrade notes
    -------------
    
    There are no API changes or SQL migrations in this release.

1.6.1 (2022-12-12)
##################

https://github.com/ansible-community/ara/releases/tag/1.6.1

.. code-block:: text

    This is the 1.6.1 stable release of ara.
    
    This is a minor release with two changes:
    
    - callback: Changed how ANSIBLE_TMP is found to work around a behavior
      change in ansible-core 2.14 that ended up creating a directory named
      {{ ANSIBLE_HOME ~ "
      For more information: https://github.com/ansible-community/ara/issues/469
    
    - Added a mysql extra to the python packaging for installing the
      mysqlclient library. This is in addition to the existing server and
      postgresql extra. They are used like this:
      pip install ara[server,mysql,postgresql]

1.6.0 (2022-12-01)
##################

https://github.com/ansible-community/ara/releases/tag/1.6.0

.. code-block:: text

    This is the 1.6.0 stable release of ara.
    
    It features a new "tasks" page to browse and search for tasks across playbook runs
    as well as many updates, fixes and improvements.
    
    Instructions for upgrading are included in the upgrade notes.
    
    Changes since 1.5.8:
    
    UI
    --
    
    - Added a new "Tasks" page similar to the existing pages for Playbooks and Hosts.
      It provides a browseable and searchable overview of tasks across playbook runs.
    - Refreshed the host index page:
      - Added a column as well as search arguments for playbook name (or path)
      - Replaced the playbook status by a concise summary of task status for the host
    
    - Updated the playbook summary card to include the playbook id, the version of ara as
      well as the version of python.
    - Re-ordered and resized columns in tables to optimize width and improve consistency
    - Resized and aligned fields in search forms to use the full width available
    - Improved how task tags are displayed
    - Updated HTML page titles to be consistent across pages
    - Replaced fields for searching by task ID and host ID by task name and host name
    - Truncate name fields to prevent exceedinly large names to distort entire tables
    - Corrected card header font sizes in the host report page
    
    callback plugin
    ---------------
    
    - Added support for recording the user who ran the playbook
    - Added support for recording the version of ara as well as the version of
      python used when running the playbook
    - Added options ARA_RECORD_USER and ARA_RECORD_CONTROLLER that can be
      set to false to avoid recording the user and controller hostname
    - Added support for specifying a SSL key, certificate and certificate
      authority for authenticating with a remote ara API server using
      ARA_API_KEY, ARA_API_CERT and ARA_API_CA respectively.
    - Fixed host fact recording to ensure it works when using FQCN-style tasks
      (ex: setup & ansible.builtin.setup)
    - Increased reliability and accuracy when recording results that can arrive
      out of order when using multi-threading or the free strategy by using the
      task uuid provided by Ansible
    - Truncate playbook, play, host and label names in circumstances where their
      length exceeds 255 characters
    - Ignore and don't record files in ~/.ansible/tmp by default
    
    API Server
    ----------
    
    - Bumped django requirement from 2.2 LTS to 3.2 LTS and removed the pin
      on the version of psycopg2 accordingly
    - Added a new configuration option, ARA_BASE_PATH, to let the server
      listen on an alternate path. It will continue to default to "/" but it
      could, for example, be set to "/ara/".
    - Lifted requirement on tzlocal, improve timezone detection and mitigate
      when the timezone can't be found by defaulting to UTC
    
    - Several new database model and API fields:
      - Added client_version and server_version fields to playbooks, meant to
        represent the version of the ara callback and server used in recording
        the playbook
      - Added python_version field to playbooks to save the version of python
        used by Ansible and the callback plugin when recording a playbook
      - Added a new "failed" status for tasks that is used by the callback plugin
        when there is at least one failed result for a given task
      - Added a new "uuid" field for tasks which is the uuid provided by Ansible
        for a task. It is used by the callback plugin to increase the reliability
        and accuracy when recording results even if they arrive out of order.
    
    - Several fixes and improvements for the distributed sqlite database backend:
      - Added a new index page for listing and linking to available databases.
        This is a work in progress that is intended to be improved in the future.
      - Return a HTTP 405 error when trying to write to read-only endpoints
      - Fixed the /healthcheck/ endpoint to make sure it is routed properly
      - Improved database engine settings and WSGI application configuration
        The WSGI application should now always be "ara.server.wsgi" instead of
        needing to specify "ara.server.wsgi.distributed_sqlite"
    
    API client
    ----------
    
    - Added support for specifying a SSL key, certificate and certificate
      authority for authenticating with a remote ara API server
    - Remove InsecureRequestWarning for insecure requests when SSL verification
      is not enabled.
    
    CLI
    ---
    
    - Fixed wrong parsing of durations longer than 24 hours
    - Added support for searching playbooks by user
    - Added support for specifying a SSL key, certificate and certificate
      authority for authenticating with a remote ara API server using
      ARA_API_KEY, ARA_API_CERT and ARA_API_CA respectively.
    
    Docs
    ----
    
    - Refreshed and improved the README, reformatted it from rst to markdown
    - Added a CONTRIBUTING.md file and refreshed contribution documentation
    - Explicitly call out and recommend setting up authentication for production
      use in order to prevent leaking sensitive information
    - Improved troubleshooting documentation and tips to improve playbook recording
      performance
    
    Tests and miscellaneous
    -----------------------
    
    - Bumped the black linter to the latest version and reformatted bits
      of code accordingly
    - Updated isort to version 5 and reformatted bits of code accordingly
    - Reformatted bits of code using pyupgrade in consideration of dropping
      support for python3.5
    - Updated versions of ansible(-core) we run integration tests with to include
      2.9, 2.11, 2.12, 2.13, 2.14 and 6.4.0.
      Although 2.9 is EOL, we will keep it for a while longer.
    
    container-images (contrib)
    --------------------------
    
    - The 'latest' tag of container images are now tagged from the latest
      PyPI release instead of the latest git source
    - Container images have been updated to the latest distribution images:
      CentOS 8 to CentOS 9 and Fedora 35 to Fedora 36
    - Add a centos-source.sh script so we can test from source in addition
      to PyPI
    - Install everything from PyPI (except ara when from source) in order
      to avoid mixing distribution packages with PyPI packages
    
    Upgrade notes
    -------------
    
    - ara 1.5.8 was the last version to support python3.5.
      Starting with ara 1.6.0, python3.6 or later is required.
    
    - ara 1.6.0 includes several database migrations and it is highly recommended
      to take a backup of the server database before updating.
      Database migrations are run automatically in many circumstances and can be run
      manually using "ara-manage migrate".
    
    - There are a few backwards incompatible changes introduced in ara 1.6.0 which
      makes it important to run the same version of ara everywhere to avoid running
      into problems if the version of the callback plugin and server do not match.
    
    - There is a database migration which grows the maximum length of the name fields
      for plays and labels which was later reverted due to potential issues when using
      the MySQL database backend.

1.5.8 (2022-03-24)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.8

.. code-block:: text

    This is the 1.5.8 stable release of ara.
    
    It features new callback and server settings as well as fixes and
    maintenance.
    
    Instructions for upgrading are included in the upgrade notes.
    
    Callback plugin
    ---------------
    
    - Improved debug logging to include some hooks that were missing (#374)
    - Added a localhost_to_hostname toggle in the callback (#336)
      This adds two configuration parameters to the callback:
      - ARA_LOCALHOST_AS_HOSTNAME
      - ARA_LOCALHOST_AS_HOSTNAME_FORMAT
    
      These are useful in use cases where playbooks are run against localhost,
      whether directly (with ansible-playbook) or indirectly (via
      ansible-pull).
    
      When enabled, ara will save results under the hostname (or fqdn) of
      'localhost' instead of associating every result to localhost.
      This is meant to make it easier to distinguish results between different
      hosts even though the playbooks may have all run against 'localhost'.
    
    Server
    ------
    
    - Added a setting for CSRF_TRUSTED_ORIGINS (#345)
    - Fixed logging configuration to avoid conflicting with ansible (#367)
      See upgrade notes for changes to the server's settings.yaml.
    
    UI
    --
    
    - API browser: disable forms to improve performance (#323)
    - Include the version of ara when generating static reports (#318)
    - Add a column in task results for displaying the task's tags (#281,#375)
    
    CLI
    ---
    
    - Added "--latest" to "ara host list" to show only the latest playbook (#327)
    
    Docs
    ----
    
    - Refreshed authentication docs and recommend using EXTERNAL_AUTH
      with nginx or apache in front (#319)
    - Add database and authentication tips to troubleshooting (#355)
    
    Packaging and dependencies
    --------------------------
    
    - API Server container images have been bumped to fedora35 and centos8-stream
    - Updated setup.cfg to fix a deprecation warning for python 3.10 (#371)
    - Fixed distutils.sysconfig deprecation warning on python 3.10 (#369)
    - Fixed dynaconf deprecation warning when loading settings (#369)
    - psycopg2 has been pinned to <2.9 due to incompatibility with django 2.2 (#321,#326)
    - dynaconf has been pinned to <3.0 when using python3.5 (#372)
      dynaconf>=3.0 supports python>=3.6.
    
    Misc
    ----
    
    - General CI maintenance
    - Updated Zuul to test the latest versions of ansible and ansible-core
    - Re-enabled container image updates on DockerHub and Quay.io
    - Added an example script with ansible-runner (#343)
    
    Upgrade notes
    -------------
    
    - There have been fixes to logging which requires changes to the
      server's settings.yaml or LOGGING configuration. (#367)
      A warning will be printed if the configuration file must be updated
      and it can be updated manually or by generating a new configuration file.
    
    - ara 1.5.8 is the last release that will support python3.5.
      Python 3.5 reached the end of its life on September 13th, 2020.
      An upcoming release will update the version of django to the next LTS (2.2 to 3.2)
      which will bump the requirement to python>=3.6.

1.5.7 (2021-07-31)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.7

.. code-block:: text

    This is the 1.5.7 stable release of ara.
    
    It features a new "hosts" page to browse and search playbook reports by host
    as well as fixes and improvements.
    
    Instructions for upgrading are included in the upgrade notes.
    
    Changes since 1.5.6:
    
    UI
    --
    
    - Added a new "hosts" page to browse and search reports by host name
    - Improved page HTML titles to be dynamic based on the context
    - Added a note highlighting if a task has been delegated to another host
      (https://github.com/ansible-community/ara/issues/282)
    - Improved how long file paths or playbook names are truncated and displayed
    
    API
    ---
    
    - Added a new read-only API endpoint: /api/v1/latesthosts
      It provides the latest playbook result for each host name.
      Under the hood, it implements the machinery for updating the latest host
      every time a host is created or deleted and includes a SQL migration to
      initially populate a new database table with the latest hosts.
    - Added a `delegated_to` field to results in order to record a host id to which
      a task has been delegated.
    - Added support for finding results delegated to a specific host:
      /api/v1/results?delegated_to=<host_id>
    
    Callback plugin
    ---------------
    
    - Fixed tasks and results being recorded out of order when using "strategy: free"
      (https://github.com/ansible-community/ara/issues/260)
    - Added support for recording 'delegate_to' on tasks
    
    Documentation
    -------------
    
    - Removed an unused sphinx lexer to allow recent versions of sphinx>=4
    - Created a new troubleshooting guide with common issues:
      https://ara.readthedocs.io/en/latest/troubleshooting.html
    - Added a database relationship graph to the endpoint documentation:
      https://ara.readthedocs.io/en/latest/api-documentation.html#relationship-between-objects
    
    Upgrade notes
    -------------
    
    It is always recommended to take a backup of your database before upgrading.
    
    This release includes two database migrations that must be run:
    - One for populating the data for the new /api/v1/latesthosts endpoint as well
      as the new 'hosts' page
    - One for adding a `delegated_to` field in the results.
      Note that delegated tasks will only be recorded as such from 1.5.7 on.
    
    After upgrading to 1.5.7, database migrations can be run manually with the
    `ara-manage migrate` command if they are not taken care of automatically by the
    callback plugin.
    
    Known issues
    ------------
    
    ara will not record task delegation for tasks that are skipped or for
    items in a loop that are skipped because Ansible doesn't provide the
    necessary information in those cases.

1.5.6 (2021-04-14)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.6

.. code-block:: text

    This is the 1.5.6 stable release of ara.
    
    It features a refresh of the playbook reporting interface included with the API server as well as fixes and improvements.
    
    Changes since 1.5.5:
    
    UI
    --
    
    - Refactored the built-in reporting UI with the bootstrap CSS framework using themes from bootswatch
    - Added a dark theme in addition to the default light theme (toggle at the top right)
    - Improved the mobile version of the reporting interface
    - Improved the playbook and task result tables
    - Revamped search forms for playbook and playbook results
    - Revamped hosts table in playbook reports
    - Added task results to the host details page that includes host facts
    - Moved ansible-playbook CLI arguments to a modal
    - Added an "about" modal with the version of ara and links to resources
    - Moved the link to the documentation to the "about" modal
    - Clicking on a host or task name in a playbook report will now filter results for that host or task
    - bugfix: Links to files including a lineno will now highlight that line (https://github.com/ansible-community/ara/issues/154)
    - bugfix: Fixed broken documentation link to ara_record (https://github.com/ansible-community/ara/issues/219)
    
    API
    ---
    
    - Playbook references will now always include CLI arguments, for example:
      /api/v1/tasks/1 ->
      {
        "id": 1,
        "playbook": {
          "id": 1,
          "arguments": {
            #...
          }
        }
      }
    
    Callback plugin
    ---------------
    
    - bugfix: Truncate play UUIDs given back by ansible-runner when running in serial (https://github.com/ansible-community/ara/issues/211)

1.5.5 (2021-01-29)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.5

.. code-block:: text

    This is the 1.5.5 stable release of ara.
    
    Changes since 1.5.4:
    
    API
    ---
    
    - Added support for searching playbooks by ansible_version, for example:
      /api/v1/playbooks?ansible_version=2.10
    
    UI
    --
    
    - Added syntax highlighting to task results
    - Added support for rendering nested results for tasks with loops
    - Added support for rendering diffs provided by "ansible-playbook --diff"
    - Added support for searching playbooks by ansible_version
    - The playbook links in the index no longer filter to changed results
    - Ordering by date or duration no longer discards existing search arguments
    - Clicking on the logo or the "playbooks" link now discards existing search arguments
    
    CLI
    ---
    
    - Added support for searching playbooks by ansible_version
    - Added missing argument for --controller to "ara playbook metrics"

1.5.4 (2020-12-18)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.4

.. code-block:: text

    This is the 1.5.4 stable release of ara.
    
    Changes since 1.5.3:
    
    CLI
    ---
    
    New commands were added to the 'ara' CLI:
    
    - ara playbook metrics: provides stats aggregated by name, path, ansible version or controller
    - ara host metrics: provides task result stats for hosts across playbooks
    - ara task metrics: provides duration stats aggregated by task name, action/module or path
    
    Refer to the documentation for examples and more information on these commands:
    https://ara.readthedocs.io/en/latest/cli.html
    
    Callback plugin
    ---------------
    
    - Threading is now disabled by default to avoid running into sqlite locking contention
      For details, see: https://github.com/ansible-community/ara/issues/195
    - The callback didn't provide a timezone for timestamps which could result in a wrong
      interpretation by the API server. Timestamps are now provided as UTC.
    
    Controller hostname
    -------------------
    
    The hostname of the controller that ran the playbook is now recorded by ara.
    
    Playbooks can be filtered by controller in the UI as well as the API:
    
        /api/v1/playbooks?controller=localhost
    
    As well as with the CLI, for example:
    
        ara playbook list --controller=localhost
        ara playbook metrics --controller=localhost
    
    Container images
    ----------------
    
    - ARA API server container images are now published to quay.io/recordsansible/ara-api
      in addition to hub.docker.com/r/recordsansible/ara-api.
    - Fedora 32 images were replaced by images based on Fedora 33
    - The 'which' package is now installed as a dependency
    - Removed a temporary workaround for dynaconf switching from PyYAML to ruamel.yaml
    
    UI
    --
    
    - Added missing information about the play when browsing details for a task result
    
    Upgrade notes
    -------------
    
    The new controller hostname feature introduces a SQL migration to update the database schema.
    After upgrading, database migrations will need to be run at least once using 'ara-manage migrate'.
    
    Because the hostname was not previously saved and can't be recovered retroactively,
    playbooks that were recorded before the upgrade will have the controller set to 'localhost'.

1.5.3 (2020-10-23)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.3

.. code-block:: text

    This is the 1.5.3 stable release of ARA.
    
    This release works around a bug introduced in 1.5.2 which could
    sometimes cause the Ansible playbook execution to lock up when using the
    default offline API client.
    
    For details, see https://github.com/ansible-community/ara/issues/183

1.5.2 (2020-10-16)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.2

.. code-block:: text

    This is the 1.5.2 stable release of ARA.
    
    Changes since 1.5.1:
    
    Ansible callback plugin
    -----------------------
    
    - Significant performance improvement by running non-blocking API calls in threads
      https://github.com/ansible-community/ara/issues/171
    - Handler tasks are now also recorded in addition to regular tasks
      https://github.com/ansible-community/ara/issues/178
    
    API
    ---
    
    - Add support for searching handler tasks (ex: /api/v1/tasks?handler=true)
    
    UI
    --
    
    - Hosts in the playbook report are now sorted alphabetically by hostname
    - Added a column to display the number of tasks in the playbook summary

1.5.1 (2020-09-23)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.1

.. code-block:: text

    This is a re-release of the 1.5.0 stable version of ara in order to fix
    a release issue to PyPi.

1.5.0.1 (2020-09-23)
####################

https://github.com/ansible-community/ara/releases/tag/1.5.0.1

.. code-block:: text

    This is a re-release of the 1.5.0 stable version of ara in order to fix
    a release issue to PyPi.

1.5.0 (2020-09-23)
##################

https://github.com/ansible-community/ara/releases/tag/1.5.0

.. code-block:: text

    This is the 1.5.0 stable release of ARA.
    
    Changes since 1.4.3:
    
    CLI
    ---
    
    A new 'ara' CLI API client is now available with the following commands:
    
    - expire           Expires objects that have been in the running state for too long
    - host delete      Deletes the specified host and associated resources
    - host list        Returns a list of hosts based on search queries
    - host show        Returns a detailed view of a specified host
    - play delete      Deletes the specified play and associated resources
    - play list        Returns a list of plays based on search queries
    - play show        Returns a detailed view of a specified play
    - playbook delete  Deletes the specified playbook and associated resources
    - playbook list    Returns a list of playbooks based on search queries
    - playbook prune   Deletes playbooks beyond a specified age in days
    - playbook show    Returns a detailed view of a specified playbook
    - record delete    Deletes the specified record and associated resources
    - record list      Returns a list of records based on search queries
    - record show      Returns a detailed view of a specified record
    - result delete    Deletes the specified result and associated resources
    - result list      Returns a list of results based on search queries
    - result show      Returns a detailed view of a specified result
    - task delete      Deletes the specified task and associated resources
    - task list        Returns a list of tasks based on search queries
    - task show        Returns a detailed view of a specified task
    
    More information on the CLI commands is available in the docs:
    https://ara.readthedocs.io/en/latest/cli.html
    
    API server
    ----------
    
    New settings have been added:
    
    - ARA_EXTERNAL_AUTH for enabling Django's external authentication
    - ARA_DATABASE_OPTIONS for passing options to the Django database backend such as SSL.
    
    More information on the API server settings are available in the docs:
    https://ara.readthedocs.io/en/latest/api-configuration.html
    
    API
    ---
    
    - Added created/updated fields to list views (ex: /api/v1/playbooks, /api/v1/results)
    - Added support for filtering hosts based on their results, for example:
      - return hosts with no changes: /api/v1/hosts?changed__lt=1
      - return hosts with failures: /api/v1/hosts?failed__gt=0
      - return hosts with unreachable tasks: /api/v1/hosts?unreachable__gt=0
    - Added support for searching results by changed (ex: /api/v1/results?changed=true)
    - Added support for searching results by play, task or host (ex: /api/v1/results?task=<id>)
    - Nested children resources are no longer returned, improving performance
      considerably for larger playbooks. For example, querying a single playbook's
      details no longer returns it's entire hierarchy of plays, tasks, results and hosts.
      These must now instead be queried individually, ex: /api/v1/results?playbook=<id>
      See https://github.com/ansible-community/ara/issues/158 for details.
    - The result statuses "changed" and "ignored" have been removed. These weren't
      actually used anywhere, it was instead inferred by a combination of the status
      as well as the "changed" and "ignore_error" fields.
      See https://github.com/ansible-community/ara/issues/150 for details.
    - A new status was added for playbooks, plays and tasks: "expired".
      This status is meant to be used to identify resources that have been in the
      "running" state for too long and will never complete.
      Use the new "ara expire" CLI command for expiring resources.
      See https://github.com/ansible-community/ara/issues/26 for details.
    
    UI
    --
    
    - URLs have been pluralized to match the endpoints provided by the API.
      For example:
        /playbook/1.html -> /playbooks/1.html
        /result/1.html -> /results/1.html
    - Links to playbooks from the index will now filter results by default based on
      their status. For example, a failed playbook will link to results that are failed
      or unreachable while a successful playbook will link to results that are changed.
    
    When browsing a playbook's details:
    - Links to files from task actions have been fixed to use the correct anchor
      when linking to a specific line
    - Task results are now paginated
    - A search form has been added to the task results pane, allowing search
      by host id, task id, status and changed
    - The hosts table has been updated to leverage the new search
      capabilities. Clicking on the host will search tasks for this host and
      clicking on the number in status column for a host (i.e, "20" changed)
      will search for that host and that status. As a result, host facts
      have been moved to it's own column.
    
    Ansible plugins
    ---------------
    
    - New feature: argument labels.
      Based on the configuration, the callback will now automatically label
      playbooks after specified CLI arguments. For example, when "--check" is used,
      it will label the playbook with "check:True" -- or "check:False" when it isn't used.
    - Starting with Ansible 2.8, the callback leverages a new hook in order to improve
      the accuracy of task result durations.
      See https://github.com/ansible-community/ara/issues/173 for details.
    
    Documentation
    -------------
    
    - Refreshed installation docs into a "getting started" guide
    - Added notes about installation on CentOS 7 / RHEL 7 as well as Mac OS
    - Refreshed and merged Ansible plugin configuration and use case docs
    - Changelogs and release notes have been incorporated in the docs
    
    Upgrade notes
    -------------
    
    - The introduction of the new CLI adds a requirement on the cliff python library.
    - ara 1.5.0 introduces significant API changes, some of which aren't backwards
      compatible such as no longer returning nested resources.
    - Two small SQL migrations have been added to remove result statuses and add the
      expired status for playbooks, plays and tasks. Run them with "ara-manage migrate".
    - "ara-manage prune" has been deprecated and is replaced by "ara playbook prune".
      The new prune command provides additional filters in order to only delete
      playbooks matching certain criteria such as label, name, path or status.

1.4.3 (2020-08-11)
##################

https://github.com/ansible-community/ara/releases/tag/1.4.3

.. code-block:: text

    This is the 1.4.3 stable release of ARA.
    
    The only change since 1.4.2 is an additional regression fix with the
    latest version of dynaconf. For more information, see the issue:
    https://github.com/ansible-community/ara/issues/149

1.4.2 (2020-07-02)
##################

https://github.com/ansible-community/ara/releases/tag/1.4.2

.. code-block:: text

    This is the 1.4.2 stable release of ARA.
    
    This release comes sooner than expected in order to fix a regression when
    installing ara with the latest version of dynaconf (3.0.0) due to a change in
    the preferred yaml package.
    
    For more information about this issue, see https://github.com/ansible-community/ara/issues/146
    
    Built-in reporting interface
    ----------------------------
    
    - Improvements to the interface scaling and rendering for mobile devices
    - The playbook index has been refactored from a list of cards to a table view
      and searching/filtering controls are no longer hidden in a submenu
    - Sorting by playbook date and duration is now built into the table headers
    - The Ansible CLI arguments are now available from the playbook index
    - The host stats summary now displays colors and icons for the different statuses
    - Task result columns were re-ordered and statuses now have colors and icons
    - Long task results or host facts should no longer render off-screen

1.4.1 (2020-05-26)
##################

https://github.com/ansible-community/ara/releases/tag/1.4.1

.. code-block:: text

    This is the 1.4.1 stable release of ARA.
    
    Changes since 1.4.0:
    
    Ansible Adhoc command recording
    -------------------------------
    
    It is now possible to record "ansible" commands in addition to the
    existing support for "ansible-playbook" commands starting with Ansible
    2.9.7 and above.
    
    To record Ansible adhoc commands, set 'bin_ansible_callbacks' to true in
    your ansible.cfg or run: export ANSIBLE_LOAD_CALLBACK_PLUGINS=true
    
    API
    ---
    
    - Added search for ignore_errors in results:
        /api/v1/results?status=failed # includes "ignore_errors: true"
        /api/v1/results?status=failed&ignore_errors=false
    
    - Added search for task by action:
        /api/v1/tasks?action=package
        /api/v1/tasks?action=command
    
    - Adjusted search for file paths to be partial:
        /api/v1/files?path=/home/user/ansible/roles/foo/tasks/main.yaml
        /api/v1/files?path=foo
    
    - Added search for task by path:
       /api/v1/tasks?path=/home/user/ansible/roles/foo/tasks/main.yaml
       /api/v1/tasks?path=foo
    
    - Fixed an error 500 when querying playbooks with labels
    
    Built-in UI
    -----------
    
    - The path to the playbooks that are displayed when no names are given
      by "ara_playbook_name" are now truncated from the left rather than
      from the right. For example, given:
      /home/user/git/source/organization/repo/playbooks/prod/restart-everything.yaml
    
      Before:
      /home/user/git/source/organization/repo/playbooks/...
      After:
      ...zation/repo/playbooks/prod/restart-everything.yaml
    
    Container images
    ----------------
    
    The project now publishes simple container images suitable for use with sqlite,
    mysql and postgresql database backends out of the box.
    
    The images are currently available on Docker Hub:
    https://hub.docker.com/r/recordsansible/ara-api
    
    You can learn about how the images are built, how you can build
    your own and how you can run them in the documentation:
    https://ara.readthedocs.io/en/latest/container-images.html

1.4.0 (2020-04-16)
##################

https://github.com/ansible-community/ara/releases/tag/1.4.0

.. code-block:: text

    This is the 1.4.0 stable release of ARA.
    
    Changes since 1.3.2:
    
    API
    ---
    
    - Added support for searching plays, tasks and hosts by name
    - Added support for searching playbooks by label
    - Fixed label representation to be consistent through different calls
    - Reversed the default sort order for playbooks, plays, tasks and results
    
    API server
    ----------
    
    - Validate that settings.yaml (or ARA_SETTINGS) exists before launching (thank you @zswanson!)
    - Template the default settings file without objects generated by python-box
    
    Bundled reporting interface
    ---------------------------
    
    - Added a default robots.txt to prevent crawling
    - Added support for searching by label
    - Improved the display of labels in the playbook list
    - Added pagination support when browsing the playbook report list
    - Use relative links for pagination (thank you @flowerysong !)
    - Bumped included patternfly CSS from 2.21.5 to 2.56.3
    
    ara_api Ansible role
    ------------
    
    - Provide sensible PATH defaults when virtualenvs are not used
    - Added support for installing from Fedora packages
    - Only run SQL migrations once when necessary
    - Allow retries when attempting to run SQL migrations
    - Ensure settings.yaml permissions are 0640
    - Added "ara_api_secure_logging" variable to control behavior of sensitive tasks with no_log
    - Properly default to IPv6 when no IPv4 is available
    - Default gunicorn worker count based on number of available CPU cores
    - Added support for deploying on EL8
    
    Ansible plugins
    ---------------
    
    - New Ansible plugins: ara_playbook and ara_api
    - Improved consistency of stored task results (thank you @flowerysong!)
    - Fix bad logic when determining if labels should be updated
    - Added support for not saving files based on patterns (thank you @LaurentDumont!)
    - Added support for specifying default playbook labels
    
    Integration tests
    -----------------
    
    - Refactored integration tests to simplify and improve coverage across different
      database backends, linux distributions and versions of Ansible
    
    Upgrade notes
    -------------
    
    - 1.4 introduces a new SQL migration to ensure labels are unique. If upgrading
      from a previous version, you will need to run SQL migrations with ``ara-manage migrate``.

0.16.7 (2020-04-14)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.7

.. code-block:: text

    0.16.7 is a maintenance release for ARA 0.x.
    
    Changes since 0.16.6:
    
    - Fix typo in ara.setup.env for ANSIBLE_ACTION_PLUGINS [1]
    - Pin pyfakefs to <4 in order to avoid breaking python2 usage [2]
    - Pin junit-xml to <=1.8 in order to avoid deprecation warnings in unit tests
    
    ARA 0.x end of life
    -------------------
    
    The code base for ARA 0.x has not been actively maintained and developed
    since 2018 and will officially reach end of life June 4th, 2019, one year
    after the release of ARA 1.0.
    
    Unless critical bugs are found between this release and June 4th, 0.16.7
    will be the last supported release of the 0.x branch.
    
    Please use the latest version of ARA to benefit from the
    new features and fixes.
    
    [1]: https://github.com/ansible-community/ara/pull/97
    [2]: https://github.com/ansible-community/ara/issues/118

1.3.2 (2019-12-12)
##################

https://github.com/ansible-community/ara/releases/tag/1.3.2

.. code-block:: text

    This is the 1.3.2 stable release of ARA.
    
    Changes since 1.3.1:
    
    - Fix compatibility with the new version of
      django-rest-framework, 3.11 [1]
    
    [1]: https://github.com/ansible-community/ara/issues/102

1.3.1 (2019-12-06)
##################

https://github.com/ansible-community/ara/releases/tag/1.3.1

.. code-block:: text

    This is the 1.3.1 stable release of ARA.
    
    Changes since 1.3.0:
    
    - bugfix: the callback plugin now properly retrieves host facts for
      both setup and gather_fact tasks
    - bugfix: fixed a typo in ara.setup.env which set the
      ANSIBLE_ACTION_PLUGINS to the callback directory instead of the
      action module directory.
    - unit tests: use assertLogs instead of patch_logger since
      patch_logger was removed from django 3.
    - misc: bumped versions of Ansible used in integration tests

1.3.0 (2019-12-03)
##################

https://github.com/ansible-community/ara/releases/tag/1.3.0

.. code-block:: text

    This is the 1.3.0 stable release of ARA.
    
    Changes since 1.2.0:
    
    General
    -------
    
    - Removed hard requirement on python 3.6 due to the usage of f-strings.
      ARA should also work on python 3.5 now.
    
    Web user interface
    ------------------
    
    - Added a tab at the top of the playbook list to search, sort and filter by date
      - Search can be based on the playbook's name, path, or status
      - Sort can be ascending or descending for start date, end date or duration
      - Filter can show playbooks in the last 60 minutes, 24 hours, 7 days or 30 days
    - Fixed a bad link to the task file in the detailed result view
    
    API
    ---
    
    - Added support for searching date fields for playbooks, plays, tasks and results [1]
      For example:
    
        /api/v1/playbooks?started_before=2019-10-01T09:57:36.489016
        /api/v1/results?created_after=2019-10-01T09:57:36.489016
    
    - The duration of items is now calculated and stored in the database model
      instead of being calculated on demand by the API. This provides the ability to
      easily sort objects based on their duration.
      A SQL migration has been added as a result of this change.
    
    - Added support for ordering objects by most fields [2]
      For example:
    
        /api/v1/playbooks?order=id (ascending, oldest first)
        /api/v1/playbooks?order=-id (descending, most recent first)
    
      The currently supported fields available for sorting are:
        - created
        - updated
        - started (for playbooks, plays, tasks, results)
        - ended (for playbooks plays, tasks, results)
        - duration (for playbooks, plays, tasks, results)
        - path (for files)
        - key (for records)
        - ok, skipped, changed, failed and unreachable (for hosts)
    
    - Added support for searching playbooks by their full path or only part of it.
      For example, a playbook with the path ``/home/user/ansible/playbook.yml``
      can be found by searching for either ``user`` or the full path.
    
    - Searching for playbook names now also supports partial search.
    
    - Improved handling of non-ascii/binary output to prevent UnicodeEncodeError
      exceptions [3]
    
    - Standardized the search by status for playbooks, plays, tasks and results
    
    - The built-in development server now checks if psycopg2 or mysqlclient are
      installed before launching when using the postgresql or mysql database backend. [4]
    
    API client
    ----------
    
    - Added support for ignoring SSL verification [5]
    
    Plugins
    -------
    
    - Added the ``ARA_API_INSECURE`` setting to the callback plugin to ignore SSL
      verification.
    
    CLI
    ---
    
    - Added an ``ara-manage prune`` command to delete playbooks older than a specified
      amount of days. [6]
    
    Documentation
    -------------
    
    - Refreshed docs on installation
    - First iteration of documentation for the ``ara-manage`` commands
    - Docs now require the API server dependencies to be installed so CLI snippets
      can be included automatically with sphinxcontrib-programoutput.
    
    Upgrade notes
    -------------
    
    - 1.3.0 introduces a new SQL migration to move durations from the API to the
      database model. If upgrading from a previous version, you will need to run
      SQL migrations with ``ara-manage migrate``.
    
    Referenced or fixed issues
    --------------------------
    
    [1]: https://github.com/ansible-community/ara/issues/30
    [2]: https://github.com/ansible-community/ara/issues/68
    [3]: https://github.com/ansible-community/ara/issues/48
    [4]: https://github.com/ansible-community/ara/issues/63
    [5]: https://github.com/ansible-community/ara/issues/90
    [6]: https://github.com/ansible-community/ara/issues/31

0.16.6 (2019-11-18)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.6

.. code-block:: text

    0.16.6 is a maintenance release for ARA 0.x.
    
    Changes since 0.16.5:
    
    - Fixed web application crash due to encoding/decoding of binary
      non-ascii content in task results
    - The sqlite middleware was adapted to support running under gunicorn.
    - ``python -m ara.setup.env`` now returns commands that use bash expansion to
      take into account existing environment variables
    
    Eventual end of life for ARA 0.x
    --------------------------------
    
    All new feature and development effort for more than a year has been spent on
    the master branch of ARA which is the basis of version 1.x releases.
    
    Users are encouraged to try the latest release of ARA and create an issue on
    GitHub if they encounter any issues or missing features.
    
    ARA 0.16.6 could be the last release of ARA 0.x if no major issues are found.

1.2.0 (2019-10-25)
##################

https://github.com/ansible-community/ara/releases/tag/1.2.0

.. code-block:: text

    This is the 1.2.0 stable release of ARA.
    
    Changes since 1.1.0:
    
    New bundled reporting interface
    -------------------------------
    
    - A new simple built-in web reporting interface is now bundled with the API server
    - The simple web reporting interface can be exported to static html with ``ara-manage generate <path>``
    
    API
    ---
    
    - An ``items`` field was added to playbook, plays and task objects to display the number of child references
    - The task file path is now available as task.path
    - Playbook labels as well as ansible_version are now always provided for playbook objects
    - The "created" and "updated" fields are now provided when querying a host list
    
    Settings
    --------
    
    - New setting to control the timezone used for storing and displaying data: ``ARA_TIME_ZONE``
    - New setting to provide a list of regex patterns for whitelisting CORS: ``ARA_CORS_ORIGIN_REGEX_WHITELIST``
    - The default for ``ARA_DISTRIBUTED_SQLITE_PREFIX`` was changed from /ara-api to /ara-report
    
    Other changes
    -------------
    
    - Significant performance improvements by reducing the amount of API calls to host and file endpoints by the callback plugin during playbook execution
    - A basic healthcheck has been implemented at ``/healthcheck/`` to allow simple monitoring of the interface and database connection
    - ``python -m ara.setup.env`` now returns commands that use bash expansion to take into account existing environment variables
    - The API clients will strip trailing slashes if they are provided in the endpoints
    - Removed a needless newline when generating the default settings.yaml file
    
    Upgrade notes
    -------------
    
    The new healthcheck feature adds a dependency on the django-health-check library
    and includes a SQL migration that needs to be run before it can be used.
    SQL migrations can be executed by running ``ara-manage migrate``.

1.1.0 (2019-07-02)
##################

https://github.com/ansible-community/ara/releases/tag/1.1.0

.. code-block:: text

    Changes since 1.0.1:
    - Added support for dynamically serving multiple sqlite databases
      dynamically from a single API server instance [1]
    - ara_record no longer instanciates it's own API client and will
      instead retrieve the client instance used by the callback.
    - Django's CONN_MAX_AGE database setting for configuring the
      duration of a database connection is now exposed [2]
    - The ARA API client timeout as configured by Ansible through the
      callback plugin is now always an integer.
    - The offline API client now has an argument to prevent SQL
      migrations from running automatically [3]
    
    For the ara_api Ansible role [4]:
    - The role no longer attempts to set up and manage a PID file when
      setting up a persistent service running with gunicorn.
    - The bundled selinux policy file for running out of a user's home
      directory has been updated and is now integration tested.
    - Added support and integration tests for deploying Django with the
      MySQL backend
    
    [1]: https://ara.readthedocs.io/en/latest/distributed-sqlite-backend.html
    [2]: https://ara.readthedocs.io/en/latest/api-configuration.html#ara-database-conn-max-age
    [3]: https://ara.readthedocs.io/en/latest/api-usage.html#ara-offline-api-client
    [4]: https://ara.readthedocs.io/en/latest/ansible-role-ara-api.html

0.16.5 (2019-06-04)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.5

.. code-block:: text

    Changes since 0.16.4:
    
    - Updated references to the master git branch or documentation
      now that 0.x development work has been moved to stable/0.x

1.0.1 (2019-06-05)
##################

https://github.com/ansible-community/ara/releases/tag/1.0.1

.. code-block:: text

    Changes since 1.0.0:
    
    - Updated references to the feature/1.0 git branch or documentation
      now that 1.0 development work has been moved to master
    - Fixed an issue preventing the HTTP API client from being used unless
      the server dependencies had been installed.
    - Added support for customizing the amount of results per page returned
      by the API with ARA_PAGE_SIZE [1]
    - The ara_api role now sets up a basic selinux policy when running
      gunicorn out of a home directory on Red Hat based systems.
    
    [1]: https://ara.readthedocs.io/en/latest/api-configuration.html#ara-page-size

1.0.0 (2019-06-03)
##################

https://github.com/ansible-community/ara/releases/tag/1.0.0

.. code-block:: text

    This is the first release of ARA on top of a new framework and API,
    dubbed version 1.0.
    
    This new release marks the deprecation of ARA 0.x and while full feature parity
    has not yet been achieved, we are moving forward and we will iterate to add
    missing features in future releases.
    
    Main changes from ARA 0.x:
    
    - The backend has been re-written from Flask to Django/Django-rest-framework
    - A new API as well as built-in API clients are available to record and query playbook results
    - The project's dependencies have been decoupled: the Ansible plugins, API backend and web interface can be installed independently from one another
    - The web interface has been re-written as a standalone project -- ara-web: https://github.com/ansible-community/ara-web
    
    In summary, all the different components before 1.0, including the web interface,
    would communicate directly with the database model.
    
    After 1.0, these components communicate with the new REST API which results in
    easier development, maintenance and integration.

0.16.4 (2019-05-22)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.4

.. code-block:: text

    This is a stable release of ARA, 0.16.4.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, is
             currently in beta and is not backwards compatible with ARA 0.x.
             In order to avoid upgrading unexpectedly when 1.0 is released,
             we recommend pinning ara to <1.0.0 in your scripts and requirements.
    ***
    
    Changelog since 0.16.3:
    - Fixed a regression when saving tasks with Ansible 2.8 [1]
    
    [1]: https://github.com/ansible-community/ara/issues/46

0.16.3 (2019-01-21)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.3

.. code-block:: text

    This is a stable release of ARA, 0.16.3.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL database schema.
    ***
    
    Changelog:
    - Update integration tests to target latest versions of Ansible (2.7.6,
    2.6.12 and 2.5.14)
    - Adjust how CLI options are saved to support the upcoming release of
      Ansible, 2.8.

0.16.2 (2019-01-02)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.2

.. code-block:: text

    This is the newest stable release of ARA, 0.16.2.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL database schema.
    ***
    
    This release comes thanks to bug fixes contributed by the community:
    
    - Jonathan Herlin fixed the deprecation notice "Call to deprecated
      function CreateFile. Use create_file instead." when generating HTML
      reports.
    - Sorin Sbarnea addressed testing warnings and made it so future
      warnings would be considered as errors
    - Sorin Sbarnea removed integration testing for the "static: no"
      argument from Ansible includes since this parameter has been removed
      from Ansible after being deprecated.

0.16.1 (2018-09-04)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.1

.. code-block:: text

    This is the newest stable release of ARA, 0.16.1.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL database schema.
    ***
    
    This is a hotfix release to address a bug in host facts sanitization
    with the introduction of the "ARA_IGNORE_FACTS" feature in 0.16.0.
    While task results were properly sanitized, host facts were not.
    
    0.16.1 addresses the issue by sanitizing both host facts and task
    results.

0.16.0 (2018-08-27)
###################

https://github.com/ansible-community/ara/releases/tag/0.16.0

.. code-block:: text

    This is the newest stable release of ARA, 0.16.0.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL database schema.
    ***
    
    This release of ARA is made possible thanks to the following contributions:
    
    - Tristan de Cacqueray from Red Hat resolved an issue where under certain
      circumstances, an empty ARA_LOG_FILE configuration could raise an exception.
    - Artem Goncharov from Open Telekom Cloud resolved an issue where configuration
      parameters through environment variables could not taken into account
      properly when using the ara-wsgi and ara-wsgi-sqlite scripts.
    - Joshua Harlow from GoDaddy submitted several improvements to performance and
      RAM usage when browsing large reports.
    - Sorin Sbarnea from Red Hat contributed documentation on serving static ARA
      reports with nginx and improved the junit export to allow for overrides
    - Haikel Guemar from Red Hat identified and fixed usage of reserved key words
      in Python 3.7
    - Robert de Bock for suggesting a security improvement around host facts
      and the ansible_env fact.
    
    Other improvements include:
    
    - Improve self-healing when running into a race condition where the playbook
      run is interrupted early enough for the playbook to be created in the
      database but before it's file was saved.
    - Prevent ARA's logging configuration from "leaking" into the configuration
      of other python modules at runtime.
    - Add a trailing slash to file links in the file tab, resolving an issue
      where reverse proxies might get confused when doing SSL termination.
    
    Security:
    
    Robert de Bock from ING Bank reported that sensitive information might
    be stored in environment variables from the Ansible control node and
    that as such, there should be a way to prevent the 'ansible_env' host
    fact from being recorded by ARA.
    
    As such, we have added a new configuration parameter: ARA_IGNORE_FACTS [1].
    ARA_IGNORE_FACTS is a comma-separated list of host facts that ARA will not
    record in it's database.
    ARA will also sanitize the output of gather_facts and setup tasks to prevent
    these facts from displaying in the task results.
    By default, only the "ansible_env" fact is ignored due to the high likelihood
    of it containing sensitive information.
    
    Maintenance:
    
    - Dropped backwards compatibility layer for supporting Ansible 2.3
    - Updated integration jobs to test against the latest versions of Ansible 2.4,
      2.5 and 2.6
    
    [1]: https://ara.readthedocs.io/en/latest/configuration.html#ara-ignore-facts

0.15.0 (2018-05-01)
###################

https://github.com/ansible-community/ara/releases/tag/0.15.0

.. code-block:: text

    This is the newest stable release of ARA, 0.15.0.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL database schema.
    ***
    
    Changelog:
    
    - ARA: Ansible Run Analysis has been "rebranded" to ARA Records Ansible
      (Another Recursive Acronym)
    - Significant improvements to memory usage and performance when running ARA as
      a WSGI application with 'ara-wsgi' or 'ara-wsgi-sqlite'.
    - Resolved an issue where the 'ara-wsgi-sqlite' middleware could serve a
      cached report instead of the requested one
    - Added support for configuring the 'SQLALCHEMY_POOL_SIZE',
      'SQLALCHEMY_POOL_TIMEOUT' and 'SQLALCHEMY_POOL_RECYCLE' parameters.
      See the configuration documentation [1] for more details.
    - Logging was fixed and improved to provide better insight when in DEBUG level.
    - Vastly improved the default logging configuration.
      ARA will create a default logging configuration file in '~/.ara/logging.yml'
      that you can customize, if need be. Deleting this file will make ARA create
      a new one with updated defaults.
    - Added python modules to help configure Ansible to use ARA, for example,
      'python -m ara.setup.callback_plugins' will print the path to ARA's callback
      plugins.
      You can find more examples in the configuration documentation. [1]
    - Implemented a workaround for fixing a race condition where an
      'ansible-playbook' command may be interrupted after the playbook was recorded
      in the database but before playbook file was saved.
    - Flask 0.12.3 was blacklisted from ARA's requirements [2], this was a broken
      release.
    - The ARA CLI can now be called with "python -m ara" if you need to specify a
      specific python interpreter, for example.
    - Updated and improved integration tests across different operating systems,
      python2 and python3 with different versions of Ansible. The full test matrix
      is available in the README. [3].
    
    [1]: https://ara.readthedocs.io/en/stable/configuration.html
    [2]: https://github.com/openstack/ara/commit/87272840bfc8b4c5db10593e47884e33a0f4af40
    [3]: https://github.com/openstack/ara#contributing-testing-issues-and-bugs

0.14.6 (2018-02-05)
###################

https://github.com/ansible-community/ara/releases/tag/0.14.6

.. code-block:: text

    This is a maintenance release for the stable version of ARA.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL schema.
             Please see this blog post [1] for details.
    ***
    
    Changelog:
    - Unit and integration changes improvements
    - Workaround an issue where Ansible could sometimes return a non-boolean
      value for the "ignore_errors" field.
    
    [1]: https://dmsimard.com/2017/11/22/status-update-ara-1.0/

0.14.5 (2017-10-26)
###################

https://github.com/ansible-community/ara/releases/tag/0.14.5

.. code-block:: text

    This is a release for the version 0.14.5 of ARA.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL schema.
             Please see this blog post [1] for details.
    ***
    
    This version notably fixes an issue when using ansible.cfg to
    configure ARA when using Ansible 2.4.0.
    0.14.5 is meant to be used with Ansible 2.4.1 and using it with Ansible
    2.4.0 is not recommended because it does not contain a necessary bugfix [2].
    
    Changelog:
    - ARA can be configured through an ansible.cfg file with Ansible 2.4.1.
    - Ansible 2.4.0 is blacklisted in requirements.txt
    - Added a WSGI middleware to load sqlite databases at variable locations
      for advanced large-scale usage. See documentation [1] for details.
    - Resolved an issue when clicking on permalink icons (blue chain links)
      on Firefox. (Thanks Mohammed Naser)
    
    [1]: http://ara.readthedocs.io/en/latest/advanced.html#serving-ara-sqlite-databases-over-http
    [2]: https://github.com/ansible/ansible/pull/31200

0.14.4 (2017-09-20)
###################

https://github.com/ansible-community/ara/releases/tag/0.14.4

.. code-block:: text

    0.14.4 adds Ansible 2.4 support for ARA.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL schema.
             Please see this blog post [1] for details.
    ***
    
    Changelog:
    - Add support for Ansible 2.4

0.14.3 (2017-09-17)
###################

https://github.com/ansible-community/ara/releases/tag/0.14.3

.. code-block:: text

    0.14.3 is a minor bugfix release for ARA.
    Note that ARA does not yet support Ansible 2.4.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL schema.
             Please see this blog post [1] for details.
    ***
    
    Changelog:
    - Bugfix: 'include_role' tasks with 'static: no' are now handled properly
      (See Ansible issue: https://github.com/ansible/ansible/issues/30385 )
    - Backport from 1.0: 404 not found errors when generating static reports will
      now be ignored as they are non-fatal.
    - Ansible was pinned to <2.4, ARA does not yet support Ansible 2.4.
    - Pygments was pinned to >=1.6, prior versions did not have the required
      JSONLexer methods.
    - Flask was pinned to >=0.11, prior versions did not provide the
      flask_logging.DEBUG_LOG_OUTPUT variable. The version prior to 0.11 was released
      in 2013.

0.14.2 (2017-08-29)
###################

https://github.com/ansible-community/ara/releases/tag/0.14.2

.. code-block:: text

    Bugfix: "logging.config" also needed to be imported for
            the new file configuration option to work properly.

0.14.1 (2017-08-27)
###################

https://github.com/ansible-community/ara/releases/tag/0.14.1

.. code-block:: text

    0.14.1 is a minor bugfix release for ARA.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL schema.
             Please see this blog post [1] for details.
    ***
    
    Changelog:
    - Bugfix: Implicit tasks with no specific file and task
      information provided by Ansible (such as "gather_facts")
      now resolve back to the playbook file by default. See upstream
      Ansible bug [2] for details.
    
    - Feature: Logging for ARA and it's components can now be done
      through a logging configuration file [3].
    
    - Integration tests on Fedora 26 with python3.6 were
      added to the existing tests under CentOS 7 and
      Ubuntu 16.04.
    
    [1]: https://dmsimard.com/2017/08/16/whats-coming-in-ara-1.0/
    [2]: https://github.com/ansible/ansible/issues/28451
    [3]: https://ara.readthedocs.io/en/latest/configuration.html#ara-log-config

0.14.0 (2017-07-31)
###################

https://github.com/ansible-community/ara/releases/tag/0.14.0

.. code-block:: text

    0.14.0 is a major release for ARA which brings significant changes
    and introduces full Python 3 support with Ansible 2.3.x.
    
    ***
    WARNING: Please note that the next major version of ARA, 1.0, will contain
             backwards incompatible changes due to significant refactor work
             involving core back end code as well as the SQL schema.
    ***
    
    Changelog for 0.14.0 (up from 0.13.3):
    
    New features:
    - Python 3 now works and is supported
      - All unit and integration tests are passing on python 3
      - New code contributions to ARA are simultaneously gated against py2
        and py3 tests to avoid regressions
    - Added the 'ara generate subunit' [1] command in order to export playbook
      run data to the subunit format
    
    Improvements:
    - Host facts, task results and records display has been improved with
      highlighting where appropriate
    - Addressed a backwards database schema relationship between files and
      tasks (no migration required)
    
    Updates and deprecations:
    - Flask has been unpinned from 0.11.1 (latest release is currently 0.12.2)
    - Ansible 2.1.x is no longer supported (end of life and out of support upstream as well)
    - A regression in unit tests was fixed in order to allow us to unpin Pytest
    
    Docs:
    - Improve FAQ on what versions of Ansible are supported [2]
    - Added a FAQ on the status of Python 3 support [3]
    
    Misc:
    - Preliminary work in order to support the upcoming release of Ansible (2.4)
    - ARA has been relicensed from Apache 2.0 to GPLv3 to simplify it's
      relationship with Ansible which is itself GPLv3. Rationale behind the
      change is available in the commit [4]
    
    Special thanks
    - Lars Kellogg-Stedman for help on python 3 and database schema troubleshooting
    - Jesse Pretorius for contributing support for Subunit generation
    
    [1]: https://ara.readthedocs.io/en/latest/usage.html#generating-a-static-subunit-version-of-the-task-results
    [2]: https://ara.readthedocs.io/en/latest/faq.html#what-versions-of-ansible-are-supported
    [3]: https://ara.readthedocs.io/en/latest/faq.html#does-ara-support-running-on-python-3
    [4]: https://review.openstack.org/#/c/486733/

0.13.3 (2017-06-30)
###################

https://github.com/ansible-community/ara/releases/tag/0.13.3

.. code-block:: text

    This release addresses a regression introduced in 0.13.2
    where files would no longer be displayed correctly and would
    instead show raw HTML.

0.13.2 (2017-06-22)
###################

https://github.com/ansible-community/ara/releases/tag/0.13.2

.. code-block:: text

    This is a minor feature/bugfix release for ARA.
    
    Changelog:
    - Security: Use the 'escape' jinja2 filter instead of the
      'safe' filter to escape potentially problematic HTML
      characters and prevent them from being interpreted.
    
    - ara_record can now be used as a standalone task outside
      the context of a playbook run to, for example, record data
      on a playbook run that has already been completed.
      An example use case is to attach the ansible-playbook run
      stdout as a record of the playbook [1][2].
      More details is available in the documentation [3].
    
    - ara_record now returns the equivalent of ara_read when
      registering the task where ara_record runs. This avoids
      needing to run ara_read if you don't need to.
    
    Misc:
    - Unit test fixes after the release of Ansible 2.3.1
    - Work and testing against Ansible Devel (unreleased 2.4) has started
    
    [1]: https://github.com/openstack/ara/blob/a72ece2e7ab69cd4e2882ba207152703b2bc0a90/run_tests.sh#L95-L96
    [2]: https://github.com/openstack/ara/blob/a72ece2e7ab69cd4e2882ba207152703b2bc0a90/run_tests.sh#L130
    [3]: http://ara.readthedocs.io/en/latest/usage.html#using-the-ara-record-module

0.13.1 (2017-05-21)
###################

https://github.com/ansible-community/ara/releases/tag/0.13.1

.. code-block:: text

    This is a minor release to fix the warning that Alembic
    0.9.2 started introducing during SQL migrations.
    
    The "About" page has also been improved.

0.13.0 (2017-05-04)
###################

https://github.com/ansible-community/ara/releases/tag/0.13.0

.. code-block:: text

    ARA 0.13.0 marks a new major release for ARA, dropping deprecations
    and modifying your database schema with automated migrations.
    
    Please read the release notes and back up your database just in
    case before upgrading.
    
    General / UI
    ============
    - The home page has been relocated to "about" and the default home
      page is now the report list.
    - Playbooks reports now have permanent links.
      Use the blue chain icon on the left hand side of the report list.
    - Host facts, files and task results now have permanent links.
      Use the blue chain icon on the top right of the popups.
    - Note: Permanent links have slightly grown the weight and amount
      of files generated in a static report but has no significant impact on
      generation time.
    - Browsing tips have been improved and folded into "?" tooltips
      inside each panel.
    - The file panel was improved to show a file browser interface
      instead of a file list.
    - There is a new panel, "Parameters", which contains all parameters
      used as part of your ansible-playbook commands.
    - Role names are now included when recording task results, this means
      you can now search for the role name in your task result list.
    - Task tags are now included when recording task results, this means
      you can now search for the tag name in your task result list.
    - Task results that are provided from a loop (ex: with_items) are now
      properly saved and displayed.
      Note that an upstream Ansible issue can make it so the last item in a
      loop is someetimes not saved (Ansible issue #24207)
    - There has been some level of performance improvements which may
      be more noticeable on larger deployments.
    - Fixed an issue where tooltips would sometime not display properly
      in the hosts table.
    - Fixed an issue that would cause "include" tasks to be recorded and
      displayed twice by ARA on Ansible >= 2.2.
    - External CSS and JS libraries are no longer bundled with ARA and
      we now used packaged versions with python-XStatic.
    - The UI has been resized a bit in general to be less of a problem on
      larger resolutions (>=1920px wide)
    
    Configuration
    =============
    - New parameter: ARA_HOST to select the host to bind on default
      with the embedded development web server. (Defaults to '127.0.0.1')
    - New parameter: ARA_PORT to select the port on which the
      embedded development web server will listen on. (Defaults to '9191')
    - The embedded development web server will now use threads by
      default, improving performance significantly.
    - New parameter: ARA_IGNORE_PARAMETERS to avoid saving
      potentially sensitive data when recording ansible-playbook command
      line parameters. (Defaults to 'extra_vars')
    
    Database
    ========
    - There is a new SQL migration to provide the necessary schema for
      ansible metadata (ansible-playbook parameters) as well as task tags.
    - Fixed a bad migration statement for a column in the table 'data'
    
    Deprecations and removals
    =========================
    - The command "ara generate" has been removed, it was deprecated
      and replaced by "ara generate html" in ARA 0.11.
    - The URLs under /playbook/ have been removed, they were deprecated
      and redirected to the new playbook reports page in ARA 0.12.
    
    Distribution packaging and unbundling
    =====================================
    ARA no longer carries in-tree external CSS and JS libraries (jquery,
    jquery-datatables, patternfly, patternfly-bootstrap-treeview, bootstrap).
    For that effort:
    - We've packaged and created new packages on PyPi for missing
      python-XStatic libraries: patternfly, patternfly-bootstrap-treeview
    - We've updated the python-XStatic package for jquery-datatables on
      PyPi
    
    ARA 0.13 will be the first version to be packaged for RHEL-derivative
    distributions. For that effort we've packaged new packages for Fedora
    and EPEL:
    - python-xstatic-patternfly
    - python-xstatic-patternfly-bootstrap-treeview
    - python-xstatic-datatables
    - python-pyfakefs

0.12.5 (2017-04-19)
###################

https://github.com/ansible-community/ara/releases/tag/0.12.5

.. code-block:: text

    0.12.5 is a small maintenance release.
    
    Changelog:
    - Fix encoding/decoding issues when using non-ascii characters
      in playbooks and improve integration testing for this kind of
      problem.
    - The full playbook path is no longer printed in the table.
      The playbook path turned out to be too long and truncated most of
      the time. Only the file name is shown now. The full path is still
      available in the tooltip when hovering over the playbook file name.
    - Improved performance for the reports page, especially when viewing
      playbook runs with a larger amount of data.
    - Considerably reduced package/module size on disk

0.12.4 (2017-04-01)
###################

https://github.com/ansible-community/ara/releases/tag/0.12.4

.. code-block:: text

    0.12.4 is primarily a maintenance/bugfix release.
    
    Callback changes:
    - Task results as recorded by ARA are now "filtered" by Ansible's
      _dump_results method [1]. This will only be effective on task recording
      moving forward, it will not edit previously recorded playbooks.
      The _dump_results method strips Ansible 'internal' keys (_ansible_*)
      from the task results and also respects the 'no_log: yes' task directive.
      Prior to this change, ARA did not respect the no_log directive and
      recorded the raw task results as well as all the Ansible internal keys.
      Task results should be cleaner now and be properly censored when using
      'no_log'.
      This ultimately results in what is hopefully less unnecessary things
      in the task results and the net effect should be positive.
    
    Internal changes:
    - Refactor of ARA's configuration module to fix issues in order to properly
      detect configuration parameters like booleans or lists. This refactor
      also brings cleaner backwards and forwards compatibility from Ansible 2.1
      through 2.3.
    - Fixed issue to prevent PBR from throwing exceptions when overriding the
      version
    - Different changes in both the CLI and the testing framework in order to
      bootstrap and teardown the application properly to prevent context from
      leaking where it shouldn't be
    
    UI changes:
    - Javascript datatables in the UI where most of the content is displayed
      will now throw warnings in the background (javascript console) rather
      than in the foreground (javascript alert). These warnings are fairly
      expected, especially in the case of incomplete or interrupted playbooks.
    - Adjust wording when notifying users about a playbook that is incomplete
      or was interrupted to make it more straightforward
    - Performance improvements on the home and reports page, more optimization
      will follow in the future.
    - Fixed an odd problem where certain webservers (ex: nginx) would not behave
      well for the statically generated version of the reports.
    
    CLI changes:
    - The "ara generate html" command will now suppress
      "MissingURLGeneratorWarning" warnings by default. A new configuration
      parameter 'ignore_empty_generation' was introduced to revert back to
      the previous behavior. For context on this change, see the commit [2].
    - Alembic messages that are not related to migrations are now sent to the
      background.
    
    Database:
    - Fix PosgreSQL support, add documentation for using it it and provide
      instructions for integration testing it
    
    Documentation:
    - The project now has a manifesto [3] to express in writing the project's core
      values and philosophy
    - Improved contributor documentation
    - Added a FAQ on running the ARA callback and the web application on
      different machines
    
    [1]: https://github.com/ansible/ansible/blob/b3251c9585b0b0180fcdf09748e9a0dc439bc1aa/lib/ansible/plugins/callback/__init__.py
    [2]: http://git.openstack.org/cgit/openstack/ara/commit/?id=440dac3789ca12c50f63a89850a7e65c1ac93789
    [3]: http://ara.readthedocs.io/en/latest/manifesto.html

0.12.3 (2017-03-09)
###################

https://github.com/ansible-community/ara/releases/tag/0.12.3

.. code-block:: text

    This is a bugfix release for the 0.12 series.
    It includes two fixes for the data and tooltips in the
    host panel to display properly.

0.12.2 (2017-03-07)
###################

https://github.com/ansible-community/ara/releases/tag/0.12.2

.. code-block:: text

    This is a minor release that aims to significantly improve
    web application performance on large scale deployments of
    ARA, tested against hundreds of playbooks composed of hundreds
    of thousands of tasks, task results and files.
    
    This is achieved by deferring the bulk of the data loading
    and processing to AJAX calls in the background.

0.12.1 (2017-03-03)
###################

https://github.com/ansible-community/ara/releases/tag/0.12.1

.. code-block:: text

    This is a small bugfix release to ensure pages from
    pagination can be detected as html mimetype.

0.12.0 (2017-03-01)
###################

https://github.com/ansible-community/ara/releases/tag/0.12.0

.. code-block:: text

    This is a major release which features a complete
    rewrite of the web application interface.
    
    The home page now highlights the data recorded by ARA
    and the core of the UI now revolves around the one and
    single playbook reports page.
    
    There were three main objectives with this UI work:
    - Improve UX (ex: being able to search, find & sort things easily
      * Everything is now searchable and sortable
      * Browsing tips have been added to help users get the most out
        of the interface features
    
    - Improve scalability and performance: the interface should be
      fast and easy to browse whether you have dozens or thousands
      of hosts and tasks
      * Every result list or table are now paginated
      * You can customize pagination preferences with the
        ARA_PLAYBOOK_PER_PAGE and ARA_RESULT_PER_PAGE
        configuration parameters.
    
    - Improve static generation time and weight
      Examples of the same data sets before and after:
      * ARA integration tests (5 playbooks, 59 tasks, 69 results):
        * Before: 5.4 seconds, 1.6MB (gzipped), 217 files
        * After: 2 seconds, 1.2MB (gzipped), 119 files
      * OpenStack-Ansible (1 playbook, 1547 tasks, 1667 results):
        * Before: 6m21 seconds, 31MB (gzipped), 3710 files
        * After: 20 seconds, 8.9MB (gzipped), 1916 files
    
    Other features and fixes include:
    - First party WSGI support [1]
    - Fixed syntax highlighting support when viewing files
    - Preparations for supporting the upcoming Ansible 2.3 release
    - Preparations for full python 3 support
    - Various performance improvements
    
    Misc:
    - Jinja HTML templates are now fully indented with no regards
      to line length or PEP8 to privilege readability over long and
      nested content.
    - Added some missing web application unit tests
    - Various javascript and css optimizations
    - The web application backend in itself was significantly
      simplified: less routes, less templates, less code
    - Added a configuration parameter ARA_PLAYBOOK_PER_PAGE which
      controls the amount of playbooks per page in the playbook
      report list.
    - Added a configuration parameter ARA_RESULT_PER_PAGE which
      controls the amount of results per page in the data results
      table (such as hosts, plays and tasks).
    
    Known issues:
    - The file list table in the file panel will eventually
      be replaced by a folder/file hierarchy tree
    
    [1]: http://ara.readthedocs.io/en/latest/webserver.html

0.11.0 (2017-02-13)
###################

https://github.com/ansible-community/ara/releases/tag/0.11.0

.. code-block:: text

    - New feature: ARA UI and Ansible version (ARA UI is running with)
      are now shown at the top right
    - New feature: The Ansible version a playbook was run is now stored
      and displayed in the playbook reports
    - New feature: New command: "ara generate junit": generates a junit
      xml stream of all task results
    - New feature: ara_record now supports two new types: "list" and "dict",
      each rendered appropriately in the UI
    - UI: Add ARA logo and favicon
    - UI: Left navigation bar was removed (top navigation bar will be
      further improved in future versions)
    - Bugfix: CLI commands could sometimes fail when trying to format
      as JSON or YAML
    - Bugfix: Database and logs now properly default to ARA_DIR if ARA_DIR
      is changed
    - Bugfix: When using non-ascii characters (ex: äëö) in playbook files,
      web application or static generation could fail
    - Bugfix: Trying to use ara_record to record non strings
      (ex: lists or dicts) could fail
    - Bugfix: Ansible config: 'tmppath' is now a 'type_value' instead of a
      boolean
    - Deprecation: The "ara generate" command was deprecated and moved to
      "ara generate html"
    - Deprecation: The deprecated callback location, ara/callback has been
      removed. Use ara/plugins/callbacks.
    - Misc: Various unit and integration testing coverage improvements and
      optimization
    - Misc: Slowly started working on full python 3 compatibility

0.10.5 (2017-01-16)
###################

https://github.com/ansible-community/ara/releases/tag/0.10.5

.. code-block:: text

    Ansible 2.2.1.0 shipped with a hard dependency on Jinja2 < 2.9 [1].
    Since Flask has a requirement on Jinja2 >= 2.4, it would pick up
    2.9.4 first and then disregard Ansible's requirement.
    
    [1]: https://github.com/ansible/ansible/commit/6c6570583f6e74521e3a4f95fe42ffddb69634fe

0.10.4 (2017-01-15)
###################

https://github.com/ansible-community/ara/releases/tag/0.10.4

.. code-block:: text

    New feature:
    
    - Playbook lists now have an icon to display their
      status, whether it has been completed or not
      and if it has been successful or not.
    
    Bug fixes/maintenance:
    
    - Fix SyntaxError when creating ARA directory
      under Python3
    - Update static patternfly assets to 3.17.0
    - Fixed some bad logic in integration tests in order
      to properly test different versions of Ansible

0.10.3 (2016-12-12)
###################

https://github.com/ansible-community/ara/releases/tag/0.10.3

.. code-block:: text

    This is a minor release that continues ongoing efforts
    to streamline some things in order to package ARA for
    linux distributions.
    
    Flask-Testing is no longer a dependency and tests have
    been rewritten accordingly.

0.10.2 (2016-12-10)
###################

https://github.com/ansible-community/ara/releases/tag/0.10.2

.. code-block:: text

    This is a minor release to streamline some things in
    order to package ARA for linux distributions.
    
    - pymysql is no longer installed by default
    - tests are now shipped inside the module
    - misc fixes (pep8, bandit)

0.10.1 (2016-12-05)
###################

https://github.com/ansible-community/ara/releases/tag/0.10.1

.. code-block:: text

    This is a bugfix release that resolves an issue that made
    it impossible to use MySQL (and potentially other RDBMS).
    
    For more details, see commit [1].
    
    [1]: https://git.openstack.org/cgit/openstack/ara/commit/?id=dd159df4f0c152d28455fedf6c6f1e0b56cd7350

0.10.0 (2016-12-01)
###################

https://github.com/ansible-community/ara/releases/tag/0.10.0

.. code-block:: text

    This is a major release.
    For the full list of changes between 0.9.3 and 0.10.0, please
    view the list of commits on GitHub [1].
    
    Summary:
    - Database schema is now stable and automatically migrated.
      Databases created on >= 0.9.0 are supported.
    - Significant web interface improvements
    - New built-in Ansible modules: ara_record and ara_read for
      recording arbitrary data with ARA
    - Improved unit and integration testing coverage
    
    [1]: https://github.com/openstack/ara/compare/0.9.3...0.10.0

0.9.3 (2016-11-14)
##################

https://github.com/ansible-community/ara/releases/tag/0.9.3


0.9.2 (2016-10-22)
##################

https://github.com/ansible-community/ara/releases/tag/0.9.2

.. code-block:: text

    This is a maintenance release.
    
    - Update static assets to their latest versions
      (Patternfly, Flask, etc.)
    - The location of the callback has been changed from
      ara/callback to ara/plugins/callbacks/. The previous
      location has been deprecated and will be removed in
      a future version.
    - Bugfix: The home link in the navigation now behaves
      more as expected and redirect to the root of the web
      application rather than the root of the domain or
      filesystem.
    - Misc: Integration test coverage improvements

0.9.1 (2016-09-15)
##################

https://github.com/ansible-community/ara/releases/tag/0.9.1

.. code-block:: text

    - Introduced a parameter (defaulting to true) to hide warnings
      introduced in 0.9.0 that are safe to ignore.

0.9.0 (2016-09-13)
##################

https://github.com/ansible-community/ara/releases/tag/0.9.0

.. code-block:: text

    - ARA is now hosted by the OpenStack project community infrastructure.
      - ARA's source code is now available at:
        https://git.openstack.org/cgit/openstack/ara
        or mirrored at
        https://github.com/openstack/ara
      - Submitting patches is now done through OpenStack's Gerrit
        system.
        Documentation on how to contribute is available at
        http://ara.readthedocs.io/en/latest/contributing.html
      - Unit and integration testing is no longer done through
        Travis but instead by OpenStack Zuul testing infrastructure.
    
    - UI Revamp: First implementation
      This is the first release in which lands a first implementation of
      a large UI revamp with the Patternfly [1] CSS framework. There are
      some small issues and quirks but we will iterate in order to fix
      them.
    
    - Playbook file storage
      ARA now stores a unique, zipped copy of playbook files allowing you
      to see the content of your task files as they ran in a particular
      ansible-playbook run. The UI leverages that feature and also provides
      a direct link with line highlight to show where a particular action
      took place.
    
    [1]: https://www.patternfly.org/

0.8.1 (2016-06-03)
##################

https://github.com/ansible-community/ara/releases/tag/0.8.1

.. code-block:: text

    This reverts commit 00673c1cf231dbd3058ca187295e67e39f6c9fff.
    2.1 has a regression [1] that breaks ARA and 2.0.2.0 had other
    regressions we are not interested in.
    
    [1]: https://github.com/ansible/ansible/issues/16125

0.8.0 (2016-06-02)
##################

https://github.com/ansible-community/ara/releases/tag/0.8.0

.. code-block:: text

    stop catching bare Exceptions

0.7.1 (2016-05-30)
##################

https://github.com/ansible-community/ara/releases/tag/0.7.1

.. code-block:: text

    Temporarily pin flask

0.7.0 (2016-05-27)
##################

https://github.com/ansible-community/ara/releases/tag/0.7.0

.. code-block:: text

    Try really hard to pretty print json-looking results

0.6.0 (2016-05-21)
##################

https://github.com/ansible-community/ara/releases/tag/0.6.0


0.5.2 (2016-05-18)
##################

https://github.com/ansible-community/ara/releases/tag/0.5.2


0.5.1 (2016-05-17)
##################

https://github.com/ansible-community/ara/releases/tag/0.5.1

.. code-block:: text

    iterate over results containing multiple items

0.5.0 (2016-05-14)
##################

https://github.com/ansible-community/ara/releases/tag/0.5.0

.. code-block:: text

    Merge development work

0.4.0 (2016-05-10)
##################

https://github.com/ansible-community/ara/releases/tag/0.4.0


0.3.1 (2016-05-09)
##################

https://github.com/ansible-community/ara/releases/tag/0.3.1

.. code-block:: text

    This isn't a proper configuration file yet but will allow to
    transition toward that goal while improving configurability with
    very low effort.

0.3 (2016-05-09)
################

https://github.com/ansible-community/ara/releases/tag/0.3

.. code-block:: text

    - Properly support browsing multiple playbook runs in /playbook
    - Add run info at the top
    - Minor tweaks to models, effectively just add foreign keys on
      playbook_uuid for sanity

0.2 (2016-05-09)
################

https://github.com/ansible-community/ara/releases/tag/0.2


0.1 (2016-05-08)
################

https://github.com/ansible-community/ara/releases/tag/0.1


