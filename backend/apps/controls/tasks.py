"""ISO27001管理策 定期タスク"""

from celery import shared_task


@shared_task(name="controls.check_control_reviews")
def check_control_reviews():
    """管理策レビュー期限チェック（毎日実行）

    review_date が今日から14日以内の管理策を検出。
    ISO27001要求: 管理策の定期的な有効性レビュー。
    """
    from datetime import UTC, datetime, timedelta

    from apps.controls.models import ISO27001Control

    today = datetime.now(tz=UTC).date()
    cutoff = today + timedelta(days=14)
    upcoming = ISO27001Control.objects.filter(
        review_date__lte=cutoff,
        review_date__gte=today,
        is_applicable=True,
    )

    return {
        "upcoming_reviews": upcoming.count(),
        "controls": list(upcoming.values("control_id", "title", "review_date", "domain")),
    }


@shared_task(name="controls.calculate_soa_status")
def calculate_soa_status():
    """適用宣言書（SoA）ステータス集計（週次実行）"""
    from apps.controls.models import ISO27001Control

    applicable = ISO27001Control.objects.filter(is_applicable=True)
    total = applicable.count()
    implemented = applicable.filter(implementation_status="implemented").count()
    in_progress = applicable.filter(implementation_status="in_progress").count()
    not_started = applicable.filter(implementation_status="not_started").count()

    return {
        "total_applicable": total,
        "implemented": implemented,
        "in_progress": in_progress,
        "not_started": not_started,
        "compliance_rate": round(implemented / total * 100, 1) if total > 0 else 0,
    }
