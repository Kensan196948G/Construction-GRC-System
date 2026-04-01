from django.db.models import Count, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import GRCUser
from apps.accounts.permissions import RoleBasedPermission
from grc.cache import CACHE_TTL, cache_key, get_or_set

from .models import Risk
from .serializers import RiskSerializer


class RiskViewSet(viewsets.ModelViewSet):
    """リスク管理 API ViewSet"""

    queryset = Risk.objects.select_related("risk_owner").all()
    serializer_class = RiskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "status", "treatment_strategy"]
    search_fields = ["risk_id", "title", "description"]
    ordering_fields = ["created_at", "risk_id", "status"]
    allowed_roles = [GRCUser.Role.GRC_ADMIN, GRCUser.Role.RISK_OWNER]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleBasedPermission()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def heatmap(self, request):
        """5x5 リスクヒートマップデータ"""

        def _build():
            risks = self.get_queryset().filter(status__in=["open", "in_progress"])
            matrix = {}
            for risk in risks:
                key = f"{risk.likelihood_inherent},{risk.impact_inherent}"
                if key not in matrix:
                    matrix[key] = {
                        "likelihood": risk.likelihood_inherent,
                        "impact": risk.impact_inherent,
                        "count": 0,
                        "risks": [],
                    }
                matrix[key]["count"] += 1
                matrix[key]["risks"].append(RiskSerializer(risk).data)
            return {"matrix": list(matrix.values())}

        data = get_or_set(cache_key("risk_heatmap"), _build, CACHE_TTL["risk_heatmap"])
        return Response(data)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """リスクダッシュボードサマリ"""

        def _build():
            qs = self.get_queryset()

            # ステータス別をDB一括集計
            by_status = dict(qs.values("status").annotate(count=Count("id")).values_list("status", "count"))

            # リスクレベル別をDB側で集計 (N+1クエリ回避)
            scored = qs.annotate(
                risk_score=F("likelihood_inherent") * F("impact_inherent"),
            )
            return {
                "total": qs.count(),
                "open": by_status.get("open", 0),
                "in_progress": by_status.get("in_progress", 0),
                "closed": by_status.get("closed", 0),
                "critical": scored.filter(risk_score__gte=15).count(),
                "high": scored.filter(risk_score__gte=10, risk_score__lt=15).count(),
                "medium": scored.filter(risk_score__gte=5, risk_score__lt=10).count(),
                "low": scored.filter(risk_score__lt=5).count(),
            }

        data = get_or_set(cache_key("risk_dashboard"), _build, CACHE_TTL["risk_dashboard"])
        return Response(data)
