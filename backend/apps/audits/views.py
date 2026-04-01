from django.http import HttpResponse
from django_filters import rest_framework as django_filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import GRCUser
from apps.accounts.permissions import RoleBasedPermission
from apps.reports.export_service import (
    AUDIT_FIELDS,
    AUDIT_FINDING_FIELDS,
    ExportService,
)

from .models import ActivityLog, Audit, AuditFinding
from .serializers import ActivityLogSerializer, AuditFindingSerializer, AuditSerializer
from .workflow import AuditWorkflowService


class AuditViewSet(viewsets.ModelViewSet):
    """内部監査 API ViewSet"""

    queryset = Audit.objects.select_related("lead_auditor").prefetch_related("findings").all()
    serializer_class = AuditSerializer
    filterset_fields = ["status", "target_department"]
    search_fields = ["audit_id", "title"]
    allowed_roles = [GRCUser.Role.GRC_ADMIN, GRCUser.Role.AUDITOR]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleBasedPermission()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        """監査ステータス遷移 POST /api/v1/audits/{id}/transition/"""
        audit = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "status is required"}, status=400)

        success, message = AuditWorkflowService.transition_status(audit, new_status)
        if success:
            return Response({"message": message, "status": audit.status})
        return Response({"error": message}, status=400)

    @action(detail=False, methods=["get"], url_path="overdue-caps")
    def overdue_caps(self, request):
        """期限超過CAP一覧 GET /api/v1/audits/overdue-caps/"""
        overdue = AuditWorkflowService.get_overdue_caps()
        return Response({"count": len(overdue), "results": overdue})

    @action(detail=False, methods=["get"], url_path="upcoming-caps")
    def upcoming_caps(self, request):
        """期限間近CAP一覧 GET /api/v1/audits/upcoming-caps/"""
        days = int(request.query_params.get("days", 7))
        upcoming = AuditWorkflowService.get_upcoming_caps(days=days)
        return Response({"count": len(upcoming), "results": upcoming})

    @action(detail=False, methods=["get"], url_path="export/csv")
    def export_csv(self, request):
        """監査一覧CSV"""
        qs = self.filter_queryset(self.get_queryset())
        content = ExportService.queryset_to_csv(qs, AUDIT_FIELDS)
        response = HttpResponse(content, content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="audits.csv"'
        return response

    @action(detail=False, methods=["get"], url_path="export/excel")
    def export_excel(self, request):
        """監査一覧Excel"""
        qs = self.filter_queryset(self.get_queryset())
        content = ExportService.queryset_to_excel(qs, AUDIT_FIELDS, sheet_name="監査一覧")
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="audits.xlsx"'
        return response


class ActivityLogFilter(django_filters.FilterSet):
    """アクティビティログ用フィルタ"""

    timestamp_from = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    timestamp_to = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = ActivityLog
        fields = ["model_name", "action", "user"]


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """アクティビティログ API ViewSet（読み取り専用）"""

    queryset = ActivityLog.objects.select_related("user").all()
    serializer_class = ActivityLogSerializer
    filterset_class = ActivityLogFilter
    search_fields = ["model_name", "object_repr"]
    ordering_fields = ["timestamp"]


class AuditFindingViewSet(viewsets.ModelViewSet):
    """監査所見 API ViewSet"""

    queryset = AuditFinding.objects.select_related("audit", "cap_owner").all()
    serializer_class = AuditFindingSerializer
    filterset_fields = ["finding_type", "cap_status", "audit"]
    search_fields = ["finding_id", "title"]
    allowed_roles = [GRCUser.Role.GRC_ADMIN, GRCUser.Role.AUDITOR]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleBasedPermission()]
        return super().get_permissions()

    @action(detail=False, methods=["get"], url_path="export/csv")
    def export_csv(self, request):
        """監査所見一覧CSV"""
        qs = self.filter_queryset(self.get_queryset())
        content = ExportService.queryset_to_csv(qs, AUDIT_FINDING_FIELDS)
        response = HttpResponse(content, content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="audit_findings.csv"'
        return response

    @action(detail=False, methods=["get"], url_path="export/excel")
    def export_excel(self, request):
        """監査所見一覧Excel"""
        qs = self.filter_queryset(self.get_queryset())
        content = ExportService.queryset_to_excel(qs, AUDIT_FINDING_FIELDS, sheet_name="監査所見一覧")
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="audit_findings.xlsx"'
        return response
