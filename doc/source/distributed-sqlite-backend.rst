.. _distributed-sqlite-backend:

Distributed sqlite database backend
===================================

The ARA API server provides an optional backend that dynamically loads sqlite
databases based on the requested URL with the help of a WSGI application
middleware.

In summary, it maps an URL such as ``http://example.org/some/path/ara-report``
to a location on the file system like ``/var/www/logs/some/path/ara-report`` and
loads an ``ansible.sqlite`` database from that directory, if it exists.

.. note::
  This backend is not enabled by default and is designed with a specific range
  of use cases in mind. This documentation attempts to explain if this might
  be a good fit for you.

Use case
--------

Running at least one Ansible playbook with the ARA Ansible callback plugin
enabled will generate a database at ``~/.ara/server/ansible.sqlite`` by default.

sqlite, in the context of ARA, is good enough for most use cases:

- it is portable: everything the API server needs is in a single file that you can upload anywhere
- no network dependency or latency: sqlite is on your filesystem and doesn't rely on a remote database server
- relatively lightweight: Ansible's own integration tests used ~13MB for 415 playbooks, 1935 files, 12456 tasks, 12762 results, 586 hosts (and host facts)

However, since write concurrency does not scale very well with sqlite, it might
not be a good fit if you plan on having a single API server handle data for
multiple ``ansible-playbook`` commands running at the same time.

The distributed sqlite database backend and WSGI middleware provide an
alternative to work around this limitation.

This approach works best if it makes sense to logically split your playbooks
into different databases. One such example is in continuous integration (CI)
where you might have multiple jobs running Ansible playbooks concurrently.

If each CI job is recording to its own database, you probably no longer have
write concurrency issues and the database can be uploaded in your logs or as an
artifact after the job has been completed.

The file hierarchy on your log or artifact server might end up looking like
this::

    /var/www/logs/
    ├── 1
    │   ├── ara-report
    │   │   └── ansible.sqlite
    │   └── console.txt
    ├── 2
    │   ├── logs.tar.gz
    │   └── some
    │       └── path
    │           └── ara-report
    │               └── ansible.sqlite
    └── 3
        ├── builds.txt
        ├── dev
        │   └── ara-report
        │       └── ansible.sqlite
        └── prod
            └── ara-report
                └── ansible.sqlite

With the above example file tree, a single instance of the API server with the
distributed sqlite backend enabled would be able to respond to queries at the
following endpoints:

- http://example.org/1/ara-report
- http://example.org/2/some/path/ara-report
- http://example.org/3/dev/ara-report
- http://example.org/3/prod/ara-report

Configuration
-------------

For enabling and configuring the distributed sqlite backend, see:

- :ref:`ARA_DISTRIBUTED_SQLITE <api-configuration:ARA_DISTRIBUTED_SQLITE>`
- :ref:`ARA_DISTRIBUTED_SQLITE_PREFIX <api-configuration:ARA_DISTRIBUTED_SQLITE_PREFIX>`
- :ref:`ARA_DISTRIBUTED_SQLITE_ROOT <api-configuration:ARA_DISTRIBUTED_SQLITE_ROOT>`

When recording data to a sqlite database, the location of the database can be
defined with :ref:`ARA_DATABASE_NAME <api-configuration:ARA_DATABASE_NAME>`.
