"""キャッシュ無効化シグナル

モデル保存/削除時に関連キャッシュを自動無効化する。
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from grc.cache import cache_key, invalidate

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender="risks.Risk")
def invalidate_risk_cache(sender, **kwargs):
    """Risk変更時にリスク関連キャッシュを無効化。"""
    invalidate(
        cache_key("risk_heatmap"),
        cache_key("risk_dashboard"),
        cache_key("dashboard"),
    )
    logger.debug("Risk cache invalidated")


@receiver([post_save, post_delete], sender="controls.ISO27001Control")
def invalidate_control_cache(sender, **kwargs):
    """ISO27001Control変更時に管理策関連キャッシュを無効化。"""
    invalidate(
        cache_key("control_rate"),
        cache_key("soa"),
        cache_key("dashboard"),
    )
    logger.debug("Control cache invalidated")


@receiver([post_save, post_delete], sender="compliance.ComplianceRequirement")
def invalidate_compliance_cache(sender, **kwargs):
    """ComplianceRequirement変更時にダッシュボードキャッシュを無効化。"""
    invalidate(cache_key("dashboard"))
    logger.debug("Compliance cache invalidated")
