#!/bin/bash
# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Quick and dirty translation of release notes from git tags to rst format
# $ ./changelog-release-notes.sh > source/changelog-release-notes.rst

function header() {
    echo "${1}"
    characters=$(expr length "${1}")
    printf '%0.s*' $(seq 1 $characters)
    echo
    echo
}

function smallheader() {
    echo "${1}"
    characters=$(expr length "${1}")
    printf '%0.s#' $(seq 1 $characters)
    echo
    echo
}

echo ".."
echo "  note: generated through doc/changelog-release-notes.sh"
echo

header "Changelog and release notes"

# Order the git repository tags by date, exclude alpha, beta and rc releases,
# then reverse it so the most recent one is at the top instead.
for tag in $(git tag -l --sort=creatordate | egrep -v "a|b|rc" | tac); do
    tag_date=$(git log -1 --pretty='%cd' --date=format:'%Y-%m-%d' $tag)
    smallheader "${tag} (${tag_date})"
    echo "https://github.com/ansible-community/ara/releases/tag/${tag}"
    echo
    # Don't include a code-block if there's no message
    length=$(git tag -n9001 $tag | tail -n +3 | wc -l)
    if [ $length -gt 0 ]; then
        echo ".. code-block:: text"
        echo
        # Remove the header from the output and strip one whitespace from the left
        git tag -n9001 $tag | tail -n +3 | cut -c 1-
    fi
    echo
done
