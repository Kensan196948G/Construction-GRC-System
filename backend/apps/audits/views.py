from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import GRCUser
from apps.accounts.permissions import RoleBasedPermission

from .models import Audit, AuditFinding
from .serializers import AuditFindingSerializer, AuditSerializer
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
