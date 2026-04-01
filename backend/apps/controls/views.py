from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from grc.cache import CACHE_TTL, cache_key, get_or_set

from .models import ISO27001Control, NistCSFCategory
from .serializers import ISO27001ControlSerializer, NistCSFCategorySerializer, SoASerializer


class ISO27001ControlViewSet(viewsets.ModelViewSet):
    """ISO27001 管理策 API ViewSet"""

    queryset = ISO27001Control.objects.select_related("owner").all()
    serializer_class = ISO27001ControlSerializer
    filterset_fields = ["domain", "implementation_status", "is_applicable"]
    search_fields = ["control_id", "title", "description"]

    @action(detail=False, methods=["get"])
    def soa(self, request):
        """適用宣言書（SoA）データ"""

        def _build():
            controls = self.get_queryset()
            serializer = SoASerializer(controls, many=True)
            return serializer.data

        data = get_or_set(cache_key("soa"), _build, CACHE_TTL["control_rate"])
        return Response(data)

    @action(detail=False, methods=["get"], url_path="compliance-rate")
    def compliance_rate(self, request):
        """準拠率サマリ"""

        def _build():
            qs = self.get_queryset()
            applicable = qs.filter(is_applicable=True)
            total = applicable.count()
            implemented = applicable.filter(implementation_status="implemented").count()
            in_progress = applicable.filter(implementation_status="in_progress").count()
            rate = (implemented / total * 100) if total > 0 else 0
            return {
                "total_applicable": total,
                "implemented": implemented,
                "in_progress": in_progress,
                "not_started": applicable.filter(implementation_status="not_started").count(),
                "compliance_rate": round(rate, 1),
            }

        data = get_or_set(cache_key("control_rate"), _build, CACHE_TTL["control_rate"])
        return Response(data)


class NistCSFCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """NIST CSF 2.0 カテゴリ API ViewSet"""

    queryset = NistCSFCategory.objects.all()
    serializer_class = NistCSFCategorySerializer
    filterset_fields = ["function_id", "function_name"]
    search_fields = ["category_id", "category_name", "category_name_ja"]
