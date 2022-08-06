#!/bin/bash -x
# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Builds an ARA API server container image from checked out source on CentOS Stream 9.
# Figure out source directory relative to the contrib/container-images directory
SCRIPT_DIR=$(cd `dirname $0` && pwd -P)
SOURCE_DIR=$(cd "${SCRIPT_DIR}/../.." && pwd -P)

# Clone the source to a temporary directory and generate an sdist tarball we can install from
pushd ${SOURCE_DIR}
python3 setup.py sdist
sdist=$(ls dist/ara-*.tar.gz)
popd

build=$(buildah from quay.io/centos/centos:stream9)

# Ensure everything is up to date and install requirements
buildah run "${build}" -- /bin/bash -c "dnf update -y && dnf install -y which python3-pip python3-pip-wheel"

# Install development dependencies in a single standalone transaction so we can fully undo it later
# without leaving dangling uninstalled dependencies
buildah run "${build}" -- dnf install -y python3-devel gcc postgresql postgresql-devel mariadb-connector-c-devel

# Install ara from source with API server extras for dependencies (django & django-rest-framework)
# including database backend libraries and gunicorn
buildah run --volume ${SOURCE_DIR}:/usr/local/src/ara:z "${build}" -- python3 -m pip install "/usr/local/src/ara/${sdist}[server]" "psycopg2-binary<2.9" mysqlclient gunicorn

# Remove development dependencies and clean up
transaction=$(buildah run "${build}" -- /bin/bash -c "dnf history | grep python3-devel | awk '{print \$1}'")
buildah run "${build}" -- /bin/bash -c "dnf history undo -y ${transaction} && dnf clean all"

# Set up the container to execute SQL migrations and run the API server with gunicorn
buildah config --env ARA_BASE_DIR=/opt/ara "${build}"
buildah config --cmd "bash -c '/usr/local/bin/ara-manage migrate && /usr/local/bin/gunicorn --workers=4 --access-logfile - --bind 0.0.0.0:8000 ara.server.wsgi'" "${build}"
buildah config --port 8000 "${build}"

# Commit this container to an image name
buildah commit "${build}" "${1:-$USER/ara-api}"
