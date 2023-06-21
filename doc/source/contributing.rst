.. _contributing:

Contributing to ARA
===================

`ARA Records Ansible <https://ara.recordsansible.org>`_ is a free and open
source community project that welcomes and appreciates contributions.

While this page focuses around development of the project itself, contributions
aren't only about pull requests, code or code reviews.

They can be in the form of documentation, feedback and comments, suggestions and
ideas, issues and bug reports, or just helping out other users in the
`chat rooms <https://ara.recordsansible.org/community/>`_.

Code contributions
------------------

Pull requests welcome
~~~~~~~~~~~~~~~~~~~~~

The ara repository is hosted on GitHub and every pull request is automatically
tested with linters, unit tests as well as a variety of integration test
scenarios.

This results in higher standards, better code, improved testing coverage,
less regressions and increased stability.

There are many tutorials on how to create a pull request on GitHub but the process
generally looks like the following:

- Fork the `ara repository on GitHub <https://github.com/ansible-community/ara>`_
- Run ``git clone`` on your fork
- Create a new branch: ``git checkout -b cool_feature``
- Do your changes and test or preview them locally, as appropriate
- Commit your changes with ``git commit``
- Push your commit to your fork with ``git push origin cool_feature``
- Open a pull request using the proposed link returned by the ``git push`` command

.. image:: ../source/_static/github-pull-request.gif

Testing changes locally
~~~~~~~~~~~~~~~~~~~~~~~

You are encouraged to test your changes in a local environment before sending
them for review.

Most of the tests that are run against a pull request are fast and can be run
from your development environment without any changes to the system.

`Tox <https://pypi.org/project/tox/>`_ handles the creation of a python virtual
environment in which the tests are run from and must be installed:

- ``tox -e py3`` for unit tests
- ``tox -e linters`` for pep8/flake8/bandit/bashate/black/isort/etc
- ``tox -e docs`` for testing and building documentation to ``docs/build/html``
- ``tox -e ansible-integration`` installs ansible and runs integration tests

Changes to the server, API, Ansible plugins or web interface can generally be
manually tested and previewed from within a tox virtual environment like this:

.. code-block:: bash

    tox -e ansible-integration --notest
    source .tox/ansible-integration/bin/activate
    export ANSIBLE_CALLBACK_PLUGINS=$(python3 -m ara.setup.callback_plugins)
    export ANSIBLE_ACTION_PLUGINS=$(python3 -m ara.setup.action_plugins)
    export ANSIBLE_LOOKUP_PLUGINS=$(python3 -m ara.setup.lookup_plugins)
    ansible-playbook tests/integration/smoke.yaml
    ara-manage runserver
    # Browse to http://127.0.0.1:8000
