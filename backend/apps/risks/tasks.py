"""リスク管理 定期タスク"""
from celery import shared_task


@shared_task(name="risks.check_review_deadlines")
def check_review_deadlines():
    """リスクレビュー期限の到来チェック（毎日実行）

    review_date が今日から7日以内のリスクを検出し、通知を生成する。
    ISO27001 A.8.8 技術的脆弱性の管理に対応。
    """
    from datetime import UTC, datetime, timedelta

    from apps.risks.models import Risk

    today = datetime.now(tz=UTC).date()
    cutoff = today + timedelta(days=7)
    upcoming = Risk.objects.filter(
        review_date__lte=cutoff,
        review_date__gte=today,
        status__in=["open", "in_progress"],
    )

    results = []
    for risk in upcoming:
        days_until = (risk.review_date - today).days
        results.append(
            {
                "risk_id": risk.risk_id,
                "title": risk.title,
                "review_date": str(risk.review_date),
                "days_until": days_until,
                "owner": str(risk.risk_owner) if risk.risk_owner else None,
            }
        )

    return {"upcoming_reviews": len(results), "risks": results}


@shared_task(name="risks.generate_risk_summary")
def generate_risk_summary():
    """リスクサマリレポート生成（週次実行）

    経営層GRCダッシュボード用のリスクサマリを生成する。
    """
    from apps.risks.models import Risk

    qs = Risk.objects.all()
    return {
        "total": qs.count(),
        "open": qs.filter(status="open").count(),
        "in_progress": qs.filter(status="in_progress").count(),
        "closed": qs.filter(status="closed").count(),
        "critical": sum(1 for r in qs if r.risk_level == "CRITICAL"),
        "high": sum(1 for r in qs if r.risk_level == "HIGH"),
    }
