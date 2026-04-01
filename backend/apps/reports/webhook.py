"""Webhook通知サービス

リスク・コンプライアンス・監査のイベントを外部システムに通知する。
Slack/Teams/メール等のWebhook URLに対してPOSTリクエストを送信。
"""

import logging
from datetime import UTC, datetime
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class WebhookNotifier:
    """Webhook通知送信クラス"""

    @staticmethod
    def send_notification(
        event_type: str,
        payload: dict[str, Any],
        webhook_url: str | None = None,
    ) -> bool:
        """Webhook通知を送信する。"""
        url = webhook_url or getattr(settings, "GRC_WEBHOOK_URL", None)
        if not url:
            logger.warning("Webhook URL not configured")
            return False

        data = {
            "event_type": event_type,
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "system": "Construction-GRC-System",
            "payload": payload,
        }
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info("Webhook sent: %s -> %s", event_type, url)
            return True
        except requests.RequestException as e:
            logger.error("Webhook failed: %s -> %s: %s", event_type, url, e)
            return False

    @classmethod
    def notify_risk_created(cls, risk_data: dict) -> bool:
        return cls.send_notification("risk.created", risk_data)

    @classmethod
    def notify_risk_level_changed(cls, risk_id: str, old_level: str, new_level: str) -> bool:
        return cls.send_notification(
            "risk.level_changed",
            {"risk_id": risk_id, "old_level": old_level, "new_level": new_level},
        )

    @classmethod
    def notify_compliance_status_changed(cls, req_id: str, old_status: str, new_status: str) -> bool:
        return cls.send_notification(
            "compliance.status_changed",
            {"req_id": req_id, "old": old_status, "new": new_status},
        )

    @classmethod
    def notify_audit_finding_created(cls, finding_data: dict) -> bool:
        return cls.send_notification("audit.finding_created", finding_data)

    @classmethod
    def notify_stable_achieved(cls, pr_number: int, run_count: int) -> bool:
        return cls.send_notification(
            "ci.stable_achieved",
            {"pr": pr_number, "consecutive_runs": run_count},
        )
