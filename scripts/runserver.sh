#!/usr/bin/env bash

RED='\033[0;31m'
NOCOLOR='\033[0m'

if [ ! -f requirements.txt ]; then
    echo -e "${RED}You seems to be in the wrong directory"
    echo -e "Execute this script from the root of ara with ./scripts/${0##*/}${NOCOLOR}"
    exit 1
fi

source venv/bin/activate

python manage.py migrate
python manage.py collectstatic --clear --no-input
DJANGO_DEBUG=1 python manage.py runserver

deactivate
