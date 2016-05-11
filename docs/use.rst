Using ARA
=========
Once ARA is installed_ and configured_, you're ready to use it!

.. _installed: install.html
.. _configured: configure.html

Using the callback
------------------
The callback is executed by Ansible automatically once the path is set properly
in the ``callback_plugins`` Ansible configuration.

After running an Ansible playbook, the database will be created if it doesn't
exist and will be used::

    $ ansible-playbook -i hosts playbooks/test.yml

    PLAY [Test playbook] ***********************************************************

    TASK [Debug thing] *************************************************************
    ok: [localhost] => {
        "msg": "Debug thing"
    }
    ok: [anotherhost] => {
        "msg": "Debug thing"
    }

    TASK [Ping] ********************************************************************
    ok: [localhost]
    fatal: [anotherhost]: UNREACHABLE! => {"changed": false, "msg": "SSH encountered an unknown error during the connection. We recommend you re-run the command using -vvvv, which will enable SSH debugging output to help diagnose the issue", "unreachable": true}
        to retry, use: --limit @playbooks/test.retry

    PLAY RECAP *********************************************************************
    anotherhost                : ok=1    changed=0    unreachable=1    failed=0
    localhost                  : ok=2    changed=0    unreachable=0    failed=0

    $ ansible-playbook -i hosts playbooks/test.yml

    PLAY [Test playbook] ***********************************************************

    TASK [Really debug thing] ******************************************************
    ok: [localhost] => {
        "msg": "Really debug thing"
    }
    ok: [anotherhost] => {
        "msg": "Really debug thing"
    }

    TASK [Ping] ********************************************************************
    ok: [localhost]
    ok: [anotherhost]

    PLAY RECAP *********************************************************************
    anotherhost                : ok=2    changed=0    unreachable=0    failed=0
    localhost                  : ok=2    changed=0    unreachable=0    failed=0

Looking at the raw data
-----------------------
Once you've run ansible-playbook at least once, the database will be populated
with data::

    $ sqlite3 ~/.ara/ansible.sqlite
    SQLite version 3.11.0 2016-02-15 17:29:24
    Enter ".help" for usage hints.
    sqlite> .schema
    CREATE TABLE playbooks (
        id VARCHAR NOT NULL,
        playbook VARCHAR,
        start VARCHAR,
        "end" VARCHAR,
        duration VARCHAR,
        PRIMARY KEY (id)
    );
    CREATE TABLE tasks (
        id VARCHAR NOT NULL,
        playbook_uuid VARCHAR,
        host VARCHAR,
        play VARCHAR,
        task VARCHAR,
        module VARCHAR,
        start VARCHAR,
        "end" VARCHAR,
        duration VARCHAR,
        result TEXT,
        changed INTEGER,
        failed INTEGER,
        skipped INTEGER,
        unreachable INTEGER,
        ignore_errors INTEGER,
        PRIMARY KEY (id),
        FOREIGN KEY(playbook_uuid) REFERENCES playbooks (id)
    );
    CREATE TABLE stats (
        id VARCHAR NOT NULL,
        playbook_uuid VARCHAR,
        host VARCHAR,
        changed INTEGER,
        failures INTEGER,
        ok INTEGER,
        skipped INTEGER,
        unreachable INTEGER,
        PRIMARY KEY (id),
        FOREIGN KEY(playbook_uuid) REFERENCES playbooks (id)
    );
    sqlite> select * from playbooks;
    6ad2b2d9-cf29-4922-ab74-a6f57d9165d3|test.yml|2016-05-10 18:16:46.905262|2016-05-10 18:16:47.165491|0.260229
    6d105db1-84f3-4359-992d-ae2b937d14bd|test.yml|2016-05-10 18:17:12.061596|2016-05-10 18:17:14.082141|2.020545
    sqlite> select * from tasks limit 1;
    76a66eea-9e8f-46ec-b268-6029b1ab0dfd|6ad2b2d9-cf29-4922-ab74-a6f57d9165d3|localhost|Test playbook|Debug thing|debug|2016-05-10 18:16:46.918963|2016-05-10 18:16:46.934754|0.015791|{"skipped": false, "_ansible_no_log": false, "changed": false, "failed": false, "msg": "Debug thing", "unreachable": false, "_ansible_verbose_always": true}|0|0|0|0|0
    sqlite> select * from stats limit 1;
    c8b3db9c-defd-4370-9e8c-e3f6b9877271|6ad2b2d9-cf29-4922-ab74-a6f57d9165d3|anotherhost|0|0|1|0|1

Browsing the web interface
--------------------------
The frontend is a visualization of the data recorded in the database.

It can be started either from the bundled development server with
``ara-dev-server`` or configured as a proper WSGI application with a web server
in front.

You can see a recorded overview of the interface features on Youtube_.

.. _Youtube: https://www.youtube.com/watch?v=K3jTqgm2YuY
