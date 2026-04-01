"""PDFレポート生成テスト

PDFReportGenerator の各メソッドを検証。
WeasyPrint 未インストール環境ではHTMLバイトがフォールバック返却される。
"""

from __future__ import annotations

from django.test import TestCase

from apps.reports.pdf_generator import PDFReportGenerator


class TestPDFReportGeneratorDashboard(TestCase):
    """ダッシュボードPDF生成テスト"""

    def test_dashboard_returns_bytes(self) -> None:
        data = {
            "risks": {"total": 10, "by_level": {"HIGH": 3, "MEDIUM": 5, "LOW": 2}},
            "compliance": {"rate": 85, "compliant": 17, "non_compliant": 2, "partial": 1},
            "controls": {"rate": 70, "implemented": 7, "in_progress": 2, "not_started": 1},
            "audits": {"total_audits": 5, "completed": 3, "total_findings": 8, "open_findings": 2},
        }
        result = PDFReportGenerator.generate_grc_dashboard_pdf(data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_dashboard_contains_grc_content(self) -> None:
        data = {
            "risks": {"total": 0, "by_level": {}},
            "compliance": {"rate": 0},
            "controls": {"rate": 0},
            "audits": {"total_audits": 0},
        }
        result = PDFReportGenerator.generate_grc_dashboard_pdf(data)
        # WeasyPrint未インストール時はHTMLバイトが返る
        assert b"GRC" in result or b"html" in result.lower()

    def test_dashboard_empty_data(self) -> None:
        data = {
            "risks": {},
            "compliance": {},
            "controls": {},
            "audits": {},
        }
        result = PDFReportGenerator.generate_grc_dashboard_pdf(data)
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestPDFReportGeneratorCompliance(TestCase):
    """コンプライアンスPDF生成テスト"""

    def test_compliance_returns_bytes(self) -> None:
        data = [{"req_id": "KEN-001", "framework": "construction_law"}]
        result = PDFReportGenerator.generate_compliance_report_pdf(data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_compliance_empty_list(self) -> None:
        result = PDFReportGenerator.generate_compliance_report_pdf([])
        assert isinstance(result, bytes)

    def test_compliance_multiple_items(self) -> None:
        data = [
            {"req_id": "KEN-001", "framework": "construction_law"},
            {"req_id": "KEN-002", "framework": "quality_law"},
            {"req_id": "KEN-003", "framework": "safety_law"},
        ]
        result = PDFReportGenerator.generate_compliance_report_pdf(data)
        assert isinstance(result, bytes)
        # 3件分のデータが含まれるHTML
        assert b"3" in result


class TestPDFReportGeneratorRisk(TestCase):
    """リスクPDF生成テスト"""

    def test_risk_returns_bytes(self) -> None:
        data = [{"risk_id": "RISK-001", "title": "Test Risk"}]
        result = PDFReportGenerator.generate_risk_report_pdf(data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_risk_empty_list(self) -> None:
        result = PDFReportGenerator.generate_risk_report_pdf([])
        assert isinstance(result, bytes)

    def test_risk_multiple_items(self) -> None:
        data = [
            {"risk_id": "RISK-001", "title": "Risk A"},
            {"risk_id": "RISK-002", "title": "Risk B"},
        ]
        result = PDFReportGenerator.generate_risk_report_pdf(data)
        assert isinstance(result, bytes)
        assert b"2" in result


class TestPDFHtmlToFallback(TestCase):
    """_html_to_pdf フォールバック動作テスト"""

    def test_html_fallback_returns_utf8(self) -> None:
        html = "<html><body>Test</body></html>"
        result = PDFReportGenerator._html_to_pdf(html)
        assert isinstance(result, bytes)
        assert result == html.encode("utf-8") or b"%PDF" in result

    def test_html_fallback_preserves_japanese(self) -> None:
        html = "<html><body>日本語テスト</body></html>"
        result = PDFReportGenerator._html_to_pdf(html)
        assert isinstance(result, bytes)
        # フォールバック時はUTF-8エンコード
        if b"%PDF" not in result:
            assert "日本語テスト".encode() in result
