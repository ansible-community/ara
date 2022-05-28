# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from rest_framework.renderers import BrowsableAPIRenderer


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """
    Renders the browsable api, but excludes the forms.

    If you are running ara in production you will collect a lot of data over time.
    This will slow down the browsable API
    because of the population of related keys into the dropdowns of the html POST/PUT form.
    This is noticed most strongly in the results API view (/api/v1/results or /api/v1/results/X)
    because there we have a lot of related fields (delegated_to, host, task, play, playbook).

    Using this renderer fixes issue #323.

    To enable this renderer it has to be set in `server/settings.py`:

        REST_FRAMEWORK = {
            ...
            "DEFAULT_RENDERER_CLASSES": (
                ...
                "ara.api.renderers.BrowsableAPIRendererWithoutForms",
                ...
            ),
            ...
        }

    """

    def get_rendered_html_form(self, data, view, method, request):
        return None
