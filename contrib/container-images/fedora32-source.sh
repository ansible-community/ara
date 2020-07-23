#!/bin/bash -x
# Builds an ARA API server container image from checked out source on Fedora 32.
# Figure out source directory relative to the contrib/container-images directory
SCRIPT_DIR=$(cd `dirname $0` && pwd -P)
SOURCE_DIR=$(cd "${SCRIPT_DIR}/../.." && pwd -P)

# Clone the source to a temporary directory and generate an sdist tarball we can install from
pushd ${SOURCE_DIR}
python3 setup.py sdist
sdist=$(ls dist/ara-*.tar.gz)
popd

build=$(buildah from fedora:32)

# Get all updates, install pip, database backends and gunicorn application server
# This lets users swap easily from the sqlite default to mysql or postgresql just by tweaking settings.yaml.
# Note: We use the packaged versions of psycopg2 and mysql python libraries so
#       we don't need to install development libraries before installing them from PyPi.
buildah run "${build}" -- /bin/bash -c "dnf update -y && dnf install -y python3-pip python3-psycopg2 python3-mysql python3-gunicorn && dnf clean all"

# Install ara from source with API server extras for dependencies (django & django-rest-framework)
buildah run --volume ${SOURCE_DIR}:/usr/local/src/ara:z "${build}" -- /bin/bash -c "pip3 install /usr/local/src/ara/${sdist}[server]"

# Set up the container to execute SQL migrations and run the API server with gunicorn
buildah config --env ARA_BASE_DIR=/opt/ara "${build}"
buildah config --cmd "bash -c '/usr/local/bin/ara-manage migrate && /usr/bin/gunicorn-3 --workers=4 --access-logfile - --bind 0.0.0.0:8000 ara.server.wsgi'" "${build}"
buildah config --port 8000 "${build}"

# Commit this container to an image name
buildah commit "${build}" "${1:-$USER/ara-api}"
