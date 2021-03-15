# Copyright (c) 2021 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.conf import settings


def ui_theme(request):
    return {
        "UI_THEME": settings.UI_THEME,
        "UI_THEME_VARIANT": settings.UI_THEME_VARIANT
    }
