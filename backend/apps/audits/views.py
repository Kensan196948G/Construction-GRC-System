from rest_framework import viewsets

from .models import Audit, AuditFinding
from .serializers import AuditFindingSerializer, AuditSerializer


class AuditViewSet(viewsets.ModelViewSet):
    """内部監査 API ViewSet"""

    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    filterset_fields = ["status", "target_department"]
    search_fields = ["audit_id", "title"]


class AuditFindingViewSet(viewsets.ModelViewSet):
    """監査所見 API ViewSet"""

    queryset = AuditFinding.objects.all()
    serializer_class = AuditFindingSerializer
    filterset_fields = ["finding_type", "cap_status", "audit"]
    search_fields = ["finding_id", "title"]
