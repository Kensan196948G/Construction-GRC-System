from django.contrib import admin
from django.urls import include, path

import grc.signals  # noqa: F401 -- register cache invalidation signals
from apps.reports.views_dashboard import GRCDashboardView
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
    path("api/v1/frameworks/", include("apps.frameworks.urls")),
    path("api/v1/dashboard/", GRCDashboardView.as_view(), name="grc-dashboard"),
]

try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
except ImportError:
    pass
