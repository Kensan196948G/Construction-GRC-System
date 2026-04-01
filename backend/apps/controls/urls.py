from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EvidenceViewSet, ISO27001ControlViewSet, NistCSFCategoryViewSet

router = DefaultRouter()
router.register(r"evidences", EvidenceViewSet, basename="evidence")
router.register(r"nist-csf", NistCSFCategoryViewSet, basename="nist-csf")
router.register(r"", ISO27001ControlViewSet, basename="control")

urlpatterns = [
    path("", include(router.urls)),
]
