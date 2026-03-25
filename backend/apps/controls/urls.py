from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ISO27001ControlViewSet

router = DefaultRouter()
router.register(r"", ISO27001ControlViewSet, basename="control")

urlpatterns = [
    path("", include(router.urls)),
]
