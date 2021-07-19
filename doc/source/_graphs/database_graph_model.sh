#!/bin/bash
# Copyright (c) 2021 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# To generate a database graph:
# - Install django_extensions (i.e, pip install django_extensions)
# - Uncomment `django_extensions` from INSTALLED_APPS in ara/server/settings.py (not settings.yaml!)
# - Install pygraphviz (on Fedora, dnf install graphviz-devel && pip install pygraphviz)

# More documentation about django_extensions and graph_models:
# - https://django-extensions.readthedocs.io/en/latest/installation_instructions.html
# - https://django-extensions.readthedocs.io/en/latest/graph_models.html

ara-manage graph_models api --pygraphviz \
    --group-models \
    --theme django2018 \
    --arrow-shape normal \
    --layout dot \
    --verbose-names \
    --no-inheritance \
    -o database-model.png
