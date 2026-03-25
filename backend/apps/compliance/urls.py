from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ComplianceRequirementViewSet

router = DefaultRouter()
router.register(r"", ComplianceRequirementViewSet, basename="compliance")

urlpatterns = [
    path("", include(router.urls)),
]
