FAQ
===
What is ARA ?
-------------
ARA_ is an attempt to make Ansible_ runs easier to visualize, understand and
troubleshoot.

ARA is three things:

1. An `Ansible callback plugin`_ to record playbook runs into a local or remote database
2. A `CLI client`_ to query the database
3. A `web interface`_ to visualize the database

.. _ARA: https://github.com/dmsimard/ara
.. _Ansible: https://www.ansible.com/
.. _Ansible callback plugin: https://ara.readthedocs.io/en/latest/configuration.html#ansible
.. _CLI client: https://ara.readthedocs.io/en/latest/usage.html#querying-the-database-with-the-cli
.. _web interface: https://ara.readthedocs.io/en/latest/usage.html#browsing-the-web-interface

What does the web interface look like ?
---------------------------------------
A video is available on YouTube_ and the following are screenshots of the
web interface:

.. image:: images/preview1.png
.. image:: images/preview2.png

.. _YouTube: https://www.youtube.com/watch?v=k3qtgSFzAHI

Why is ARA being developed ?
----------------------------
Ansible is an awesome tool. It can be used for a lot of things.

Reading and interpreting the output of an ansible-playbook run, especially one
that is either long running, involves a lot of hosts or prints a lot of output
can be tedious.
This is especially true when you happen to be running Ansible hundreds of times
during the day, through automated means -- for example when doing continuous
integration or continuous delivery.

ARA aims to do one thing and do it well: Record Ansible runs and provide means
to visualize these records to help you be more efficient.

Why don't you use Ansible Tower, Rundeck or Semaphore ?
-------------------------------------------------------
`Ansible Tower`_ is currently a product from Ansible and has not been open
sourced (*yet*). We do not know when it will be made freely available and it's
source opened.

Ansible Tower, Semaphore_ and Rundeck_ all have something in common.
They are tools that controls (or wants to control) the whole workflow
from end-to-end and they do so in a fairly "centralized" fashion where
everything runs from the place where the software is hosted.
Inventory management, ACLs, playbook execution, editing features and so on.

Since they are the ones actually running Ansible, it makes sense that they can
record and display the data in an organized way.

ARA is decentralized and self-contained: ``pip install ara``, configure the
callback in ``ansible.cfg``, run a playbook and it'll be recorded, wherever it
is. ARA doesn't want to do things like inventory management, provide editing
features or control the workflow. It just wants to record data and provide an
intuitive interface for it.

When using ARA, you can store and browse your data locally and this is in fact
the default behavior. You are not required to use a central server or upload
your data elsewhere.

While the features provided by Tower and other products are definitely nice,
the scope of ARA is kept narrow on purpose.
By doing so, ARA remains a relatively simple application that is very easy to
install and configure. It does not require any changes to your setup or
workflow, it adds itself in transparently and seemlessly.

.. _Ansible Tower: https://www.ansible.com/tower
.. _Semaphore: https://github.com/ansible-semaphore/semaphore
.. _Rundeck: http://rundeck.org/plugins/ansible/2016/03/11/ansible-plugin.html

Can ARA be used outside the context of OpenStack or continuous integration ?
----------------------------------------------------------------------------
Of course, you can.

ARA has no dependencies or requirements with OpenStack or Jenkins for CI.
You can use ARA with Ansible for any playbook in any context.

ARA is completely generic but was developed out of necessity to make
troubleshooting OpenStack continuous integration jobs faster and easier.

What versions of Ansible are supported ?
----------------------------------------
ARA is currently being developed and tested against Ansible v2.0.1.0.

There were some regressions in the v2.0.2.0 release and we're currently staying
clear of that one.

What's an Ansible callback ?
----------------------------
`Ansible Callbacks`_ are essentially hooks provided by Ansible. Ansible will
send an event and you can react to it with a callback.
You could use a callback to do things like print additional details or, in the
case of ARA, record the playbook run data in a database.

.. _Ansible Callbacks: http://docs.ansible.com/ansible/developing_plugins.html