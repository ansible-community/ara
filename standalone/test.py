import os
import sys

import django

parent_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_directory)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ara.settings")
django.setup()

from api import models

print(models.Playbook.objects.all())
