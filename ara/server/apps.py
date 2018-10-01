from django.contrib.admin.apps import AdminConfig


class AraAdminConfig(AdminConfig):
    default_site = "ara.server.admin.AraAdminSite"
