from rest_framework import viewsets

from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """レポート API ViewSet"""

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_fields = ["report_type"]
    search_fields = ["title"]
