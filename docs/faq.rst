FAQ
===
What is ARA ?
-------------
ARA_ is an attempt to make Ansible_ runs easier to visualize, understand and
troubleshoot.

ARA is two things:

1. An Ansible callback plugin to record playbook runs into an sqlite database
2. A Flask_ web interface to visualize that sqlite database

.. _ARA: https://github.com/dmsimard/ara
.. _Ansible: https://www.ansible.com/
.. _Flask: http://flask.pocoo.org/

What does it look like ?
------------------------
A video is available on YouTube_ and the following is a screenshot of the
web interface:

.. image:: images/preview.png

.. _YouTube: https://www.youtube.com/watch?v=K3jTqgm2YuY

Why is ARA being developed ?
----------------------------
Ansible is an awesome tool. It can be used for a lot of things.

Reading and interpreting the output of an ansible-playbook run, especially one
that is either long running, involves a lot of hosts or prints a lot of output
can be tedious.
This is especially true when you happen to be running ansible hundreds of times
during the day, through automated means -- for example when doing continuous
integration.

ARA aims to do one thing and do it well: Record Ansible runs and provide an
intuitive interface to browse the results of those runs.

Why don't you use Ansible Tower ?
---------------------------------
`Ansible Tower`_ is currently a product from Ansible and has not been Open
Sourced (yet). We do not know when it will be made freely available and it's
source opened.

Ansible Tower works in a fairly centralized way where you can trigger runs from
the web interface and it will record that run in it's database so you can see
the results in it's web interface.

ARA does not aim to be able to do things like control host inventory, actually
control the execution of playbooks and other (nice) features of Tower.

By using a callback and storing the database locally, the user is free to
browse the results locally.
Another use case would be to upload databases (ex: from CI jobs) to a central
server running the ARA web interface, this would provide a mean to browse
aggregated results.

.. _Ansible Tower: https://www.ansible.com/tower

What versions of Ansible are supported ?
----------------------------------------
ARA is currently being developed and tested against Ansible v2.0.1.0.

There were some regressions in the v2.0.2.0 release and we're currently staying
clear of that one.
