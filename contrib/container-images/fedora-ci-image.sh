#!/bin/bash -x
# Copyright (c) 2025 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# This image is meant to be used for exercising CI tests on Codeberg/Forgejo
build=$(buildah from quay.io/fedora/fedora:43)

# Ensure everything is up to date and install requirements
buildah run "${build}" -- /bin/bash -c "dnf update -y && dnf install -y git awk hostname nodejs nodejs20 tox which python3 python3-packaging python3-devel python3-pip python3-wheel"

# Commit this container to an image name
buildah commit "${build}" "${1:-$USER/fedora-ci-image}"
