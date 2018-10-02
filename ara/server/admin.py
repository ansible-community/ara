from django.contrib import admin


class AraAdminSite(admin.AdminSite):
    site_header = "Administration"
    index_title = "Administration Ara"
