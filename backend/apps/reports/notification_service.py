"""統合通知サービス

Slack Webhook、メール、ログの3チャネルで通知を送信する。
設定に応じてチャネルを切り替え可能。
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
import requests

logger = logging.getLogger(__name__)


class NotificationService:
    """統合通知サービス"""

    @classmethod
    def notify(
        cls,
        event_type: str,
        title: str,
        message: str,
        severity: str = "info",
        extra: dict | None = None,
    ) -> dict[str, bool]:
        """全有効チャネルに通知を送信する。"""
        results: dict[str, bool] = {}

        # Slack通知
        if getattr(settings, "GRC_SLACK_WEBHOOK_URL", None):
            results["slack"] = cls._send_slack(title, message, severity, event_type)

        # メール通知
        if getattr(settings, "GRC_NOTIFICATION_EMAILS", None):
            results["email"] = cls._send_email(title, message, severity)

        # 常にログ出力
        log_method = logger.warning if severity in ("critical", "high") else logger.info
        log_method("GRC Notification [%s] %s: %s", event_type, title, message)
        results["log"] = True

        return results

    @classmethod
    def _send_slack(cls, title: str, message: str, severity: str, event_type: str) -> bool:
        """Slack Incoming Webhook に通知を送信する。"""
        url = settings.GRC_SLACK_WEBHOOK_URL
        color_map = {
            "critical": "#D32F2F",
            "high": "#FF6F00",
            "warning": "#FFA000",
            "info": "#1565C0",
            "success": "#388E3C",
        }
        color = color_map.get(severity, "#1565C0")

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"\U0001f3d7 GRC: {title}",
                    "text": message,
                    "fields": [
                        {"title": "イベント", "value": event_type, "short": True},
                        {
                            "title": "重要度",
                            "value": severity.upper(),
                            "short": True,
                        },
                    ],
                    "footer": "Construction-GRC-System",
                }
            ]
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error("Slack notification failed: %s", e)
            return False

    @classmethod
    def _send_email(cls, title: str, message: str, severity: str) -> bool:
        """メール通知を送信する。"""
        recipients = settings.GRC_NOTIFICATION_EMAILS
        if isinstance(recipients, str):
            recipients = [r.strip() for r in recipients.split(",")]

        subject = f"[GRC-{severity.upper()}] {title}"
        body = f"{message}\n\n--\nConstruction-GRC-System 自動通知"

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error("Email notification failed: %s", e)
            return False

    # -- 便利メソッド --

    @classmethod
    def notify_risk_critical(cls, risk_id: str, title: str) -> dict[str, bool]:
        """CRITICALリスク発生通知"""
        return cls.notify(
            "risk.critical",
            f"\U0001f6a8 リスクCRITICAL: {title}",
            f"リスク {risk_id} がCRITICALレベルに到達しました。即座に対応が必要です。",
            severity="critical",
        )

    @classmethod
    def notify_cap_overdue(cls, finding_id: str, days_overdue: int) -> dict[str, bool]:
        """CAP期限超過通知"""
        return cls.notify(
            "audit.cap_overdue",
            f"\u26a0\ufe0f CAP期限超過: {finding_id}",
            f"是正処置が {days_overdue} 日超過しています。",
            severity="high",
        )

    @classmethod
    def notify_compliance_degraded(cls, framework: str, old_rate: float, new_rate: float) -> dict[str, bool]:
        """準拠率低下通知"""
        return cls.notify(
            "compliance.degraded",
            f"\U0001f4c9 準拠率低下: {framework}",
            f"準拠率が {old_rate}% → {new_rate}% に低下しました。",
            severity="warning",
        )

    @classmethod
    def notify_audit_completed(cls, audit_id: str, findings_count: int) -> dict[str, bool]:
        """監査完了通知"""
        return cls.notify(
            "audit.completed",
            f"\u2705 監査完了: {audit_id}",
            f"監査が完了しました。所見数: {findings_count} 件",
            severity="info",
        )

    @classmethod
    def notify_daily_digest(cls, summary: dict) -> dict[str, bool]:
        """日次GRCダイジェスト通知"""
        msg = (
            f"リスク: {summary.get('risks', 0)} 件"
            f" (CRITICAL: {summary.get('critical_risks', 0)})\n"
            f"準拠率: {summary.get('compliance_rate', 0)}%\n"
            f"未対応所見: {summary.get('open_findings', 0)} 件"
        )
        return cls.notify(
            "system.daily_digest",
            "\U0001f4ca 日次GRCダイジェスト",
            msg,
            severity="info",
        )
