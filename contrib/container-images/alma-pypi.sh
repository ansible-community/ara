#!/bin/bash -x
# Copyright (c) 2026 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
DEV_DEPENDENCIES="gcc python3-devel postgresql-devel postgresql-server-devel mariadb-connector-c-devel"

# Builds an ARA API server container image using the latest PyPi packages on Alma 10.
# CentOS/RHEL 10 no longer supports older hardware
# Use Alma 10 for x86_64_v2 compatibility
# See: https://codeberg.org/ansible-community/ara-collection/issues/83
build=$(buildah from --platform=linux/amd64/v2 quay.io/almalinuxorg/almalinux:10)

# Ensure everything is up to date and install requirements
buildah run "${build}" -- /bin/bash -c "dnf update -y && dnf install -y which python3-pip python3-pip-wheel postgresql libpq mariadb-connector-c"

# Install development dependencies required for installing packages from PyPI
buildah run "${build}" -- dnf install -y ${DEV_DEPENDENCIES}

# Install ara from PyPI with API server extras for dependencies (django & django-rest-framework)
# including database backend libraries and gunicorn
# # django-health-check>=4.0.0 introduces backwards incompatible changes
# https://codeberg.org/ansible-community/ara/issues/644
buildah run "${build}" -- python3 -m pip install "ara[server,postgresql,mysql]" gunicorn "django-health-check<4.0.0"

# Remove development dependencies and clean up
buildah run "${build}" -- /bin/bash -c "dnf remove -y ${DEV_DEPENDENCIES} && dnf autoremove -y && dnf clean all && python3 -m pip cache purge"

# Set up the container to execute SQL migrations and run the API server with gunicorn
buildah config --env ARA_BASE_DIR=/opt/ara "${build}"
buildah config --cmd "bash -c '/usr/local/bin/ara-manage migrate && python3 -m gunicorn --workers=4 --access-logfile - --bind 0.0.0.0:8000 ara.server.wsgi'" "${build}"
buildah config --port 8000 "${build}"

# Commit this container to an image name
buildah commit "${build}" "${1:-$USER/ara-api}"
