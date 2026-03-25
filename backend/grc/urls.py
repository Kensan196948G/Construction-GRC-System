from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/risks/", include("apps.risks.urls")),
    path("api/v1/compliance/", include("apps.compliance.urls")),
    path("api/v1/controls/", include("apps.controls.urls")),
    path("api/v1/audits/", include("apps.audits.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
]
