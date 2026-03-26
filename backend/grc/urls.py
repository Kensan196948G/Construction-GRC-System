from django.contrib import admin
from django.urls import include, path

from grc.health import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health-check"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/risks/", include("apps.risks.urls")),
    path("api/v1/compliance/", include("apps.compliance.urls")),
    path("api/v1/controls/", include("apps.controls.urls")),
    path("api/v1/audits/", include("apps.audits.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
]
