#!/bin/bash -x
# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
DEV_DEPENDENCIES="gcc python3-devel postgresql-devel mariadb-connector-c-devel"

# Builds an ARA API server container image using the latest PyPi packages on CentOS Stream 8.
# TODO: update to stream9 once 1.6.0 is released https://github.com/ansible-community/ara/issues/401
build=$(buildah from quay.io/centos/centos:stream8)

# Ensure everything is up to date and install requirements
buildah run "${build}" -- /bin/bash -c "dnf update -y && dnf install -y which python3-pip python3-pip-wheel postgresql libpq mariadb-connector-c"

# Install development dependencies required for installing packages from PyPI
buildah run "${build}" -- dnf install -y ${DEV_DEPENDENCIES}

# Install ara from PyPI with API server extras for dependencies (django & django-rest-framework)
# including database backend libraries and gunicorn
buildah run "${build}" -- python3 -m pip install "ara[server]" "psycopg2<2.9" mysqlclient gunicorn

# Remove development dependencies and clean up
buildah run "${build}" -- /bin/bash -c "dnf remove -y ${DEV_DEPENDENCIES} && dnf autoremove -y && dnf clean all"

# Set up the container to execute SQL migrations and run the API server with gunicorn
# Temporarily set $TZ env variable pending release of 1.6.0 with timezone fixes
buildah config --env TZ=UTC "${build}"
buildah config --env ARA_BASE_DIR=/opt/ara "${build}"
buildah config --cmd "bash -c '/usr/local/bin/ara-manage migrate && /usr/local/bin/gunicorn --workers=4 --access-logfile - --bind 0.0.0.0:8000 ara.server.wsgi'" "${build}"
buildah config --port 8000 "${build}"

# Commit this container to an image name
buildah commit "${build}" "${1:-$USER/ara-api}"
