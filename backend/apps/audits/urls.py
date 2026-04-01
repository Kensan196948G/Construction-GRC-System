from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ActivityLogViewSet, AuditFindingViewSet, AuditViewSet

router = DefaultRouter()
router.register(r"activity-logs", ActivityLogViewSet, basename="activity-log")
router.register(r"findings", AuditFindingViewSet, basename="finding")
router.register(r"", AuditViewSet, basename="audit")

urlpatterns = [
    path("", include(router.urls)),
]
