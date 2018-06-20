from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Administration'
admin.site.index_title = 'Administration Ara'

routes = [
    url(r'^api/v1/', include('ara.api.urls')),
    url(r'^admin/', admin.site.urls),
]
urlpatterns = routes + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
