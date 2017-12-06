#!/usr/bin/env bash

RED='\033[0;31m'
NOCOLOR='\033[0m'

if [ ! -f requirements.txt ]; then
    echo -e "${RED}You seems to be in the wrong directory"
    echo -e "Execute this script from the root of ara with ./scripts/${0##*/}${NOCOLOR}"
    exit 1
fi

[ -d "venv" ] && rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r test-requirements.txt
deactivate
