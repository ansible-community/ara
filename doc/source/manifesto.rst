.. _manifesto:

Manifesto: Project core values
==============================

ARA is an open source project that was created by Ansible users for Ansible
users.

Its purpose is to provide a way to simply and easily understand what happens
throughout playbook runs at any scale.

ARA itself is composed of several components to achieve that purpose. The
project as well as those components adhere to some important core values.

This manifesto exists to explain the different core values incorporated in the
project's development and roadmap for users, contributors and developers alike.

1) Simplicity is fundamental
----------------------------

In the `Zen of Python`_, you'll find the following:

    **Simple is better than complex**

This is paramount to the project.
ARA should always be simple to install, simple to use and simple to understand.

Simplicity is also expressed in terms of configurability: ARA should come with
sane and working defaults out of the box.

It should be simple (but not required) to customize the behavior of ARA.
This is why ARA can be configured using the exact same means as Ansible.

.. _Zen of Python: https://www.python.org/dev/peps/pep-0020/

2) Do one thing and do it well
------------------------------

The scope of the ARA project is narrow on purpose and is strongly aligned with
one of the values from the `UNIX philosophy`_:

    **Write programs that do one thing and do it well**

ARA records Ansible playbook runs and makes the recorded data available and
intuitive for users and systems.

A narrow project scope for ARA allows developers and users to focus on a
limited feature set in order to ensure each component is built and usable both
simply and optimally.

.. _UNIX philosophy: https://en.wikipedia.org/wiki/Unix_philosophy

3) Empower users to get their work done
---------------------------------------

This core value of the project is about being receptive to user feedback and
understanding what they need.

ARA should provide generic implementations to allow them to get their work
done while keeping in mind the two previous core values.

This warrants examples in order to have a common understanding of what this
means:

* ARA does not provide additional data beyond what is sent and made available
  by Ansible directly. Ansible upstream modules can be improved to send more
  information that would then be made available to ARA.

* ARA does not "connect" directly to systems such as Logstash_ but provides
  machine-readable output through its command line interface (CLI), allowing
  users to feed data easily to the system of their choosing.

* ARA does not tell you which host Ansible ran from or automatically discover
  the git versions of your playbooks but allows you to save arbitrary data in
  its database for future reference.

.. _Logstash: https://www.elastic.co/products/logstash

4) Don't require users to change their workflows
------------------------------------------------

ARA should never require users to change how they already use Ansible beyond
installing and configuring Ansible to use ARA.

ARA should be a drop-in, seamless and transparent addition to their workflows.

5) De-centralized, offline and standalone by default
----------------------------------------------------

It should never be required to run Ansible with ARA from one single, unique and
central location.

Users should be able to record data no matter where Ansible runs, whether it is
on their laptops, workstations, servers, virtual machines, etc.

ARA should provide the means to easily aggregate collected data in the form of
a centralized relational database but it should default to a standalone,
offline and self-contained mode of operation.
