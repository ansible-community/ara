#!/usr/bin/env python
import os
import sys


def main():
    from ara import server

    os.environ.setdefault("ARA_CFG", os.path.dirname(server.__file__) + "/configs/dev.cfg")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ara.server.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
