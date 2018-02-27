from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'playbooks', views.PlaybookViewSet, base_name='playbooks')
router.register(r'records', views.RecordViewSet, base_name='records')
router.register(r'files', views.FileViewSet, base_name='files')

urlpatterns = [
    url(r'^', include(router.urls)),
]
