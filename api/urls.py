from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as NestedRouter

from api import views

router = DefaultRouter()
router.register(r'playbooks', views.PlaybookViewSet, base_name='playbooks')
router.register(r'records', views.RecordViewSet, base_name='records')
router.register(r'files', views.FileViewSet, base_name='files')

nested_router = NestedRouter.NestedSimpleRouter(router, r'playbooks', lookup='playbooks')
nested_router.register(r'records', views.RecordViewSet, base_name='playbook-records')
nested_router.register(r'files', views.FileViewSet, base_name='playbook-files')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(nested_router.urls)),
]
