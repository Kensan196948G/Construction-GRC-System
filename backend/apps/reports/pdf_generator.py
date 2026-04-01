"""PDFレポート生成ユーティリティ

WeasyPrint を使用したPDFレポート生成基盤。
各レポートタイプに応じたHTML→PDF変換を提供。
"""

from __future__ import annotations

import io
from datetime import UTC, datetime
from typing import Any


class PDFReportGenerator:
    """PDFレポート生成基盤クラス"""

    @staticmethod
    def generate_grc_dashboard_pdf(data: dict[str, Any]) -> bytes:
        """GRCダッシュボードPDFを生成する。

        Args:
            data: GRCDashboardView.get() の返却データ

        Returns:
            PDFバイナリデータ
        """
        html_content = PDFReportGenerator._render_dashboard_html(data)
        return PDFReportGenerator._html_to_pdf(html_content)

    @staticmethod
    def generate_compliance_report_pdf(data: dict[str, Any]) -> bytes:
        """コンプライアンス準拠率レポートPDFを生成する。"""
        html_content = PDFReportGenerator._render_compliance_html(data)
        return PDFReportGenerator._html_to_pdf(html_content)

    @staticmethod
    def generate_risk_report_pdf(data: dict[str, Any]) -> bytes:
        """リスク評価レポートPDFを生成する。"""
        html_content = PDFReportGenerator._render_risk_html(data)
        return PDFReportGenerator._html_to_pdf(html_content)

    @staticmethod
    def _html_to_pdf(html_content: str) -> bytes:
        """HTMLをPDFに変換する。

        WeasyPrintが利用可能な場合はそれを使用し、
        なければHTMLバイトを返す（フォールバック）。
        """
        try:
            from weasyprint import HTML

            pdf_buffer = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            return pdf_buffer.getvalue()
        except ImportError:
            return html_content.encode("utf-8")

    @staticmethod
    def _render_dashboard_html(data: dict[str, Any]) -> str:
        """ダッシュボードHTML生成"""
        now = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
        risks = data.get("risks", {})
        compliance = data.get("compliance", {})
        controls = data.get("controls", {})
        audits = data.get("audits", {})

        return f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="utf-8"><title>GRC ダッシュボードレポート</title>
<style>
body {{ font-family: 'Noto Sans JP', sans-serif; margin: 40px; color: #333; }}
h1 {{ color: #1565C0; border-bottom: 3px solid #1565C0; padding-bottom: 10px; }}
h2 {{ color: #424242; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background-color: #1565C0; color: white; }}
.metric {{ font-size: 2em; font-weight: bold; color: #1565C0; }}
.card {{ display: inline-block; padding: 20px; margin: 10px; border: 1px solid #ddd; border-radius: 8px; }}
.footer {{ margin-top: 40px; font-size: 0.9em; color: #888; border-top: 1px solid #ddd; padding-top: 10px; }}
</style></head>
<body>
<h1>🏗 建設業GRC 統合ダッシュボードレポート</h1>
<p>生成日時: {now}</p>

<h2>📊 リスク管理</h2>
<div class="card"><div class="metric">{risks.get("total", 0)}</div>リスク総数</div>
<table><tr><th>レベル</th><th>件数</th></tr>
{"".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in risks.get("by_level", {}).items())}
</table>

<h2>✅ コンプライアンス</h2>
<div class="card"><div class="metric">{compliance.get("rate", 0)}%</div>準拠率</div>
<table><tr><th>項目</th><th>件数</th></tr>
<tr><td>準拠</td><td>{compliance.get("compliant", 0)}</td></tr>
<tr><td>非準拠</td><td>{compliance.get("non_compliant", 0)}</td></tr>
<tr><td>部分準拠</td><td>{compliance.get("partial", 0)}</td></tr>
</table>

<h2>🛡 ISO27001 管理策</h2>
<div class="card"><div class="metric">{controls.get("rate", 0)}%</div>実施率</div>
<table><tr><th>ステータス</th><th>件数</th></tr>
<tr><td>実施済み</td><td>{controls.get("implemented", 0)}</td></tr>
<tr><td>実施中</td><td>{controls.get("in_progress", 0)}</td></tr>
<tr><td>未着手</td><td>{controls.get("not_started", 0)}</td></tr>
</table>

<h2>🔍 内部監査</h2>
<table><tr><th>項目</th><th>件数</th></tr>
<tr><td>監査総数</td><td>{audits.get("total_audits", 0)}</td></tr>
<tr><td>完了</td><td>{audits.get("completed", 0)}</td></tr>
<tr><td>所見総数</td><td>{audits.get("total_findings", 0)}</td></tr>
<tr><td>未解決所見</td><td>{audits.get("open_findings", 0)}</td></tr>
</table>

<div class="footer">
<p>Construction-GRC-System | ISO27001:2022 / NIST CSF 2.0 / 建設業法準拠</p>
</div>
</body></html>"""

    @staticmethod
    def _render_compliance_html(data: dict[str, Any]) -> str:
        """コンプライアンスHTML生成"""
        now = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
        return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><title>コンプライアンスレポート</title>
<style>body {{ font-family: sans-serif; margin: 40px; }}
h1 {{ color: #1565C0; }} table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; }} th {{ background: #1565C0; color: white; }}
</style></head><body>
<h1>コンプライアンス準拠率レポート</h1><p>生成日時: {now}</p>
<p>詳細データ: {len(data)} 件</p>
</body></html>"""

    @staticmethod
    def _render_risk_html(data: dict[str, Any]) -> str:
        """リスクHTML生成"""
        now = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
        return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><title>リスク評価レポート</title>
<style>body {{ font-family: sans-serif; margin: 40px; }}
h1 {{ color: #D32F2F; }} table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; }} th {{ background: #D32F2F; color: white; }}
</style></head><body>
<h1>リスク評価レポート</h1><p>生成日時: {now}</p>
<p>詳細データ: {len(data)} 件</p>
</body></html>"""
