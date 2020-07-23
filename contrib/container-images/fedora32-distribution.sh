#!/bin/bash -x
# Builds an ARA API server container image from Fedora 32 distribution packages.
build=$(buildah from fedora:32)

# Get all updates, install the ARA API server, database backends and gunicorn application server
# This lets users swap easily from the sqlite default to mysql or postgresql just by tweaking settings.yaml.
buildah run "${build}" -- /bin/bash -c "dnf update -y && dnf install -y ara ara-server python3-psycopg2 python3-mysql python3-gunicorn && dnf clean all"

# Set up the container to execute SQL migrations and run the API server with gunicorn
buildah config --env ARA_BASE_DIR=/opt/ara "${build}"
buildah config --cmd "bash -c '/usr/bin/ara-manage migrate && /usr/bin/gunicorn-3 --workers=4 --access-logfile - --bind 0.0.0.0:8000 ara.server.wsgi'" "${build}"
buildah config --port 8000 "${build}"

# Commit this container to an image name
buildah commit "${build}" "${1:-$USER/ara-api}"
