"""アクティビティログ記録サービス"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ActivityLogger:
    """アクティビティログを記録するユーティリティクラス"""

    @staticmethod
    def log(
        user,
        action: str,
        model_name: str,
        object_id: str = "",
        object_repr: str = "",
        changes: dict | None = None,
        ip_address: str | None = None,
    ):
        from apps.audits.models import ActivityLog

        try:
            ActivityLog.objects.create(
                user=user if user and hasattr(user, "pk") else None,
                action=action,
                model_name=model_name,
                object_id=str(object_id),
                object_repr=str(object_repr)[:300],
                changes=changes or {},
                ip_address=ip_address,
            )
        except Exception:
            logger.exception("Failed to create activity log")

    @classmethod
    def log_create(cls, user, obj, ip=None):
        cls.log(
            user,
            "create",
            obj.__class__.__name__,
            str(obj.pk),
            str(obj),
            ip_address=ip,
        )

    @classmethod
    def log_update(cls, user, obj, changes=None, ip=None):
        cls.log(
            user,
            "update",
            obj.__class__.__name__,
            str(obj.pk),
            str(obj),
            changes=changes,
            ip_address=ip,
        )

    @classmethod
    def log_delete(cls, user, obj, ip=None):
        cls.log(
            user,
            "delete",
            obj.__class__.__name__,
            str(obj.pk),
            str(obj),
            ip_address=ip,
        )

    @classmethod
    def log_status_change(cls, user, obj, old_status, new_status, ip=None):
        cls.log(
            user,
            "status_change",
            obj.__class__.__name__,
            str(obj.pk),
            str(obj),
            changes={"old": old_status, "new": new_status},
            ip_address=ip,
        )
