"""コンプライアンス管理 定期タスク"""
from celery import shared_task


@shared_task(name="compliance.check_assessment_deadlines")
def check_assessment_deadlines():
    """コンプライアンス評価期限の到来チェック（毎日実行）

    next_assessment が今日から30日以内の要件を検出し、通知を生成する。
    """
    from datetime import UTC, datetime, timedelta

    from apps.compliance.models import ComplianceRequirement

    today = datetime.now(tz=UTC).date()
    cutoff = today + timedelta(days=30)
    upcoming = ComplianceRequirement.objects.filter(
        next_assessment__lte=cutoff,
        next_assessment__gte=today,
    ).exclude(compliance_status="compliant")

    results = []
    for req in upcoming:
        days_until = (req.next_assessment - today).days
        results.append(
            {
                "req_id": req.req_id,
                "framework": req.framework,
                "title": req.title,
                "next_assessment": str(req.next_assessment),
                "days_until": days_until,
                "compliance_status": req.compliance_status,
            }
        )

    return {"upcoming_assessments": len(results), "requirements": results}


@shared_task(name="compliance.generate_compliance_report")
def generate_compliance_report():
    """法令別準拠率レポート生成（月次実行）"""
    from apps.compliance.models import ComplianceRequirement

    frameworks = ComplianceRequirement.Framework.choices
    report = {}
    for value, label in frameworks:
        qs = ComplianceRequirement.objects.filter(framework=value)
        total = qs.count()
        if total == 0:
            continue
        compliant = qs.filter(compliance_status="compliant").count()
        report[value] = {
            "label": label,
            "total": total,
            "compliant": compliant,
            "rate": round(compliant / total * 100, 1),
        }

    return report
