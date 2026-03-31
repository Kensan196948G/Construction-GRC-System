from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ISO27001ControlViewSet, NistCSFCategoryViewSet

router = DefaultRouter()
router.register(r"", ISO27001ControlViewSet, basename="control")
router.register(r"nist-csf", NistCSFCategoryViewSet, basename="nist-csf")

urlpatterns = [
    path("", include(router.urls)),
]
