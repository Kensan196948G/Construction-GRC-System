from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ComplianceRequirement
from .serializers import ComplianceRequirementSerializer


class ComplianceRequirementViewSet(viewsets.ModelViewSet):
    """コンプライアンス要件 API ViewSet"""

    queryset = ComplianceRequirement.objects.all()
    serializer_class = ComplianceRequirementSerializer
    filterset_fields = ["framework", "compliance_status", "is_mandatory"]
    search_fields = ["req_id", "title", "description"]

    @action(detail=False, methods=["get"], url_path="compliance-rate")
    def compliance_rate(self, request):
        """法令別準拠率"""
        frameworks = ComplianceRequirement.Framework.choices
        rates = {}
        for value, label in frameworks:
            qs = self.get_queryset().filter(framework=value)
            total = qs.count()
            compliant = qs.filter(compliance_status="compliant").count()
            rates[value] = {
                "label": label,
                "total": total,
                "compliant": compliant,
                "rate": round(compliant / total * 100, 1) if total > 0 else 0,
            }
        return Response(rates)
