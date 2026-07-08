#!/bin/bash
# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# The parent directory of this script
tests=$(dirname $0)
export PROJECT_ROOT=$(cd `dirname $tests` && pwd -P)
export PROJECT_LIB="${PROJECT_ROOT}/ara"
export LINTING_TARGETS=("${PROJECT_LIB}" "${PROJECT_ROOT}/tests" "${PROJECT_ROOT}/doc" "${PROJECT_ROOT}/manage.py")
ret=0

function banner() {
    echo
    printf '#%.0s' {1..50}
    echo
    echo "# ${1}"
    printf '#%.0s' {1..50}
    echo
}

# Let this script work even though it might not be run by tox
if [ -z "${VIRTUAL_ENV}" ]; then
    pushd "${PROJECT_ROOT}"
    tox -e linters --notest
    source .tox/linters/bin/activate
    popd
fi

banner black
time black --diff --check "${LINTING_TARGETS[@]}"
ret+=$?

banner isort
time isort --check-only --diff "${LINTING_TARGETS[@]}"
ret+=$?

banner flake8
time flake8 "${LINTING_TARGETS[@]}"
ret+=$?

# B303 - Use of insecure MD2, MD4, or MD5 hash function.
# B324 - Use of weak MD4, MD5, or SHA1 hash for security. Consider usedforsecurity=False
# We're using sha1 to generate a hash of file contents.
banner bandit
time bandit -r "${LINTING_TARGETS[@]}" --skip B303,B324
ret+=$?

# The Grafana dashboard is generated from _generate_dashboard.py, which is the
# source of truth; contrib/grafana/ara-dashboard.json is its committed output.
# Regenerate it and fail if it drifted (someone changed the generator without
# committing the regenerated json), then validate every PromQL expression and
# metric name in the dashboard. Both scripts write/read paths relative to the
# project root, so run them from there. The staleness check restores the
# committed json afterwards so the linter never leaves the tree dirty.
banner "grafana dashboard"
pushd "${PROJECT_ROOT}" >/dev/null
committed=$(mktemp)
cp contrib/grafana/ara-dashboard.json "${committed}"
python3 contrib/grafana/_generate_dashboard.py
if ! diff -u "${committed}" contrib/grafana/ara-dashboard.json; then
    echo "contrib/grafana/ara-dashboard.json is out of date;"
    echo "run 'python3 contrib/grafana/_generate_dashboard.py' and commit the result."
    ret+=1
fi
cp "${committed}" contrib/grafana/ara-dashboard.json
rm -f "${committed}"
time python3 contrib/grafana/_validate_dashboard.py
ret+=$?
popd >/dev/null

if [ $ret -gt 0 ]
then
  echo
  echo "At least one linter detected errors!"
  exit 1
fi
