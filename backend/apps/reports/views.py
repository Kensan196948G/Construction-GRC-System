from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.reports.views_dashboard import GRCDashboardView

from .models import Report
from .pdf_generator import PDFReportGenerator
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """レポート API ViewSet"""

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_fields = ["report_type"]
    search_fields = ["title"]

    @action(detail=False, methods=["get"], url_path="generate/dashboard-pdf")
    def generate_dashboard_pdf(self, request):
        """GRCダッシュボードPDFを生成してダウンロードする。"""
        dashboard_view = GRCDashboardView()
        dashboard_view.request = request
        data = {
            "risks": dashboard_view._risk_summary(),
            "compliance": dashboard_view._compliance_summary(),
            "controls": dashboard_view._controls_summary(),
            "audits": dashboard_view._audit_summary(),
        }
        pdf_bytes = PDFReportGenerator.generate_grc_dashboard_pdf(data)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="grc-dashboard-report.pdf"'
        return response

    @action(detail=False, methods=["get"], url_path="generate/compliance-pdf")
    def generate_compliance_pdf(self, request):
        """コンプライアンスレポートPDFを生成する。"""
        from apps.compliance.models import ComplianceRequirement

        data = list(ComplianceRequirement.objects.values("req_id", "framework", "title", "compliance_status"))
        pdf_bytes = PDFReportGenerator.generate_compliance_report_pdf(data)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="compliance-report.pdf"'
        return response

    @action(detail=False, methods=["get"], url_path="generate/risk-pdf")
    def generate_risk_pdf(self, request):
        """リスク評価レポートPDFを生成する。"""
        from apps.risks.models import Risk

        data = list(Risk.objects.values("risk_id", "title", "category", "status"))
        pdf_bytes = PDFReportGenerator.generate_risk_report_pdf(data)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="risk-report.pdf"'
        return response
