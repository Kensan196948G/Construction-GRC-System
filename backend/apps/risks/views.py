from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Risk
from .serializers import RiskSerializer


class RiskViewSet(viewsets.ModelViewSet):
    """リスク管理 API ViewSet"""

    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "status", "treatment_strategy"]
    search_fields = ["risk_id", "title", "description"]
    ordering_fields = ["created_at", "risk_id", "status"]

    @action(detail=False, methods=["get"])
    def heatmap(self, request):
        """5x5 リスクヒートマップデータ"""
        risks = self.get_queryset().filter(status__in=["open", "in_progress"])
        matrix = {}
        for risk in risks:
            key = f"{risk.likelihood_inherent},{risk.impact_inherent}"
            if key not in matrix:
                matrix[key] = {"likelihood": risk.likelihood_inherent, "impact": risk.impact_inherent, "count": 0, "risks": []}
            matrix[key]["count"] += 1
            matrix[key]["risks"].append(RiskSerializer(risk).data)
        return Response({"matrix": list(matrix.values())})

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """リスクダッシュボードサマリ"""
        qs = self.get_queryset()
        return Response(
            {
                "total": qs.count(),
                "open": qs.filter(status="open").count(),
                "in_progress": qs.filter(status="in_progress").count(),
                "closed": qs.filter(status="closed").count(),
                "critical": sum(1 for r in qs if r.risk_level == "CRITICAL"),
                "high": sum(1 for r in qs if r.risk_level == "HIGH"),
                "medium": sum(1 for r in qs if r.risk_level == "MEDIUM"),
                "low": sum(1 for r in qs if r.risk_level == "LOW"),
            }
        )
