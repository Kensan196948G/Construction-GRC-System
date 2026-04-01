from django.http import FileResponse, HttpResponse
from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.reports.export_service import CONTROL_FIELDS, ExportService
from grc.cache import CACHE_TTL, cache_key, get_or_set

from .models import Evidence, ISO27001Control, NistCSFCategory
from .serializers import (
    EvidenceSerializer,
    ISO27001ControlSerializer,
    NistCSFCategorySerializer,
    SoASerializer,
)


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

    @action(detail=False, methods=["get"], url_path="export/csv")
    def export_csv(self, request):
        """管理策一覧CSV"""
        qs = self.filter_queryset(self.get_queryset())
        content = ExportService.queryset_to_csv(qs, CONTROL_FIELDS)
        response = HttpResponse(content, content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="controls.csv"'
        return response

    @action(detail=False, methods=["get"], url_path="export/excel")
    def export_excel(self, request):
        """管理策一覧Excel"""
        qs = self.filter_queryset(self.get_queryset())
        content = ExportService.queryset_to_excel(qs, CONTROL_FIELDS, sheet_name="管理策一覧")
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="controls.xlsx"'
        return response


class EvidenceViewSet(viewsets.ModelViewSet):
    """証跡（エビデンス）ファイル API ViewSet"""

    queryset = Evidence.objects.select_related("control", "uploaded_by").all()
    serializer_class = EvidenceSerializer
    filterset_fields = ["control"]
    search_fields = ["title", "description", "file_name"]

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[parsers.MultiPartParser],
        url_path="upload",
    )
    def upload(self, request):
        """ファイルアップロードによる証跡登録"""
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"detail": "ファイルが必要です。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            data={
                "control": request.data.get("control"),
                "title": request.data.get("title", file_obj.name),
                "description": request.data.get("description", ""),
                "file": file_obj,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            uploaded_by=request.user if request.user.is_authenticated else None,
            file_name=file_obj.name,
            file_size=file_obj.size,
            file_type=file_obj.content_type or "",
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """証跡ファイルのダウンロード"""
        evidence = self.get_object()
        return FileResponse(
            evidence.file.open("rb"),
            as_attachment=True,
            filename=evidence.file_name,
        )


class NistCSFCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """NIST CSF 2.0 カテゴリ API ViewSet"""

    queryset = NistCSFCategory.objects.all()
    serializer_class = NistCSFCategorySerializer
    filterset_fields = ["function_id", "function_name"]
    search_fields = ["category_id", "category_name", "category_name_ja"]
