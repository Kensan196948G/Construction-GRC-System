"""サンプルリスクデータのシードコマンド

開発・デモ用に10件のサンプルリスクデータを投入する。

Usage:
    python manage.py seed_sample_data
    python manage.py seed_sample_data --clear  # 既存データ削除後に投入
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from apps.risks.models import Risk

SAMPLE_RISKS: list[dict[str, Any]] = [
    # --- IT系リスク (RISK-IT-001〜003) ---
    {
        "risk_id": "RISK-IT-001",
        "title": "ランサムウェアによる業務システム停止",
        "description": "マルウェア感染により基幹システムが暗号化され、業務が長期停止するリスク。",
        "category": Risk.Category.IT,
        "likelihood_inherent": 3,
        "impact_inherent": 5,
        "likelihood_residual": 2,
        "impact_residual": 4,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "EDR導入、バックアップの3-2-1ルール適用、従業員セキュリティ教育の実施",
        "status": Risk.Status.IN_PROGRESS,
    },
    {
        "risk_id": "RISK-IT-002",
        "title": "クラウドサービス障害によるデータ損失",
        "description": "利用中のクラウドサービスの障害・停止により、プロジェクトデータが損失するリスク。",
        "category": Risk.Category.IT,
        "likelihood_inherent": 2,
        "impact_inherent": 4,
        "likelihood_residual": 1,
        "impact_residual": 3,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "マルチリージョンバックアップ、オフラインバックアップの定期取得",
        "status": Risk.Status.IN_PROGRESS,
    },
    {
        "risk_id": "RISK-IT-003",
        "title": "内部不正による機密情報漏洩",
        "description": "従業員による意図的または過失による設計図面・入札情報等の機密情報漏洩リスク。",
        "category": Risk.Category.IT,
        "likelihood_inherent": 2,
        "impact_inherent": 5,
        "likelihood_residual": 1,
        "impact_residual": 4,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "DLP導入、アクセス権限の最小化、操作ログ監視、情報セキュリティ誓約書の取得",
        "status": Risk.Status.OPEN,
    },
    # --- 建設現場リスク (RISK-CONST-001〜003) ---
    {
        "risk_id": "RISK-CONST-001",
        "title": "高所作業中の墜落・転落事故",
        "description": "足場や高所作業車での作業中に墜落・転落が発生し、重傷・死亡事故に至るリスク。",
        "category": Risk.Category.CONSTRUCTION,
        "likelihood_inherent": 3,
        "impact_inherent": 5,
        "likelihood_residual": 1,
        "impact_residual": 5,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "フルハーネス型安全帯の義務化、足場点検の強化、KY活動の徹底",
        "status": Risk.Status.IN_PROGRESS,
    },
    {
        "risk_id": "RISK-CONST-002",
        "title": "施工品質不良による手戻り工事",
        "description": "施工管理体制の不備により品質基準を満たさず、手戻り工事が発生するリスク。",
        "category": Risk.Category.CONSTRUCTION,
        "likelihood_inherent": 3,
        "impact_inherent": 4,
        "likelihood_residual": 2,
        "impact_residual": 3,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "品質チェックリストの整備、第三者検査の導入、施工写真の自動記録",
        "status": Risk.Status.OPEN,
    },
    {
        "risk_id": "RISK-CONST-003",
        "title": "建設資材の供給遅延",
        "description": "サプライチェーン途絶により主要建設資材の調達が遅延し、工期に影響するリスク。",
        "category": Risk.Category.CONSTRUCTION,
        "likelihood_inherent": 4,
        "impact_inherent": 3,
        "likelihood_residual": 3,
        "impact_residual": 2,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "複数サプライヤーの確保、在庫バッファの設定、代替資材リストの作成",
        "status": Risk.Status.IN_PROGRESS,
    },
    # --- 法令コンプライアンスリスク (RISK-LEGAL-001〜002) ---
    {
        "risk_id": "RISK-LEGAL-001",
        "title": "建設業法違反による行政処分",
        "description": "技術者配置義務や下請契約の法令違反により、営業停止等の行政処分を受けるリスク。",
        "category": Risk.Category.LEGAL,
        "likelihood_inherent": 2,
        "impact_inherent": 5,
        "likelihood_residual": 1,
        "impact_residual": 5,
        "treatment_strategy": Risk.TreatmentStrategy.AVOID,
        "treatment_plan": "法令遵守チェックリストの運用、専任技術者の台帳管理、定期内部監査の実施",
        "status": Risk.Status.IN_PROGRESS,
    },
    {
        "risk_id": "RISK-LEGAL-002",
        "title": "個人情報保護法違反",
        "description": "従業員・協力会社の個人情報取扱い不備により、個人情報保護法に違反するリスク。",
        "category": Risk.Category.LEGAL,
        "likelihood_inherent": 2,
        "impact_inherent": 4,
        "likelihood_residual": 1,
        "impact_residual": 3,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "プライバシーポリシーの整備、個人情報取扱研修の実施、委託先の監督強化",
        "status": Risk.Status.OPEN,
    },
    # --- 財務リスク (RISK-FIN-001〜002) ---
    {
        "risk_id": "RISK-FIN-001",
        "title": "大型プロジェクトの採算悪化",
        "description": "資材高騰・工期延長等により大型プロジェクトの原価が予算を大幅に超過するリスク。",
        "category": Risk.Category.FINANCIAL,
        "likelihood_inherent": 3,
        "impact_inherent": 4,
        "likelihood_residual": 2,
        "impact_residual": 3,
        "treatment_strategy": Risk.TreatmentStrategy.MITIGATE,
        "treatment_plan": "月次原価管理の徹底、エスカレーション条項の契約盛り込み、予備費の確保",
        "status": Risk.Status.IN_PROGRESS,
    },
    {
        "risk_id": "RISK-FIN-002",
        "title": "取引先の倒産による債権回収不能",
        "description": "主要取引先の経営悪化・倒産により、売掛金等の債権が回収不能となるリスク。",
        "category": Risk.Category.FINANCIAL,
        "likelihood_inherent": 2,
        "impact_inherent": 3,
        "likelihood_residual": 1,
        "impact_residual": 2,
        "treatment_strategy": Risk.TreatmentStrategy.TRANSFER,
        "treatment_plan": "与信管理の強化、取引信用保険の付保、前受金条件の交渉",
        "status": Risk.Status.ACCEPTED,
    },
]


class Command(BaseCommand):
    help = "開発用サンプルリスクデータ（10件）をシードする"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="既存のサンプルデータを削除してから投入する",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        sample_risk_ids = [r["risk_id"] for r in SAMPLE_RISKS]

        if options["clear"]:
            deleted_count, _ = Risk.objects.filter(risk_id__in=sample_risk_ids).delete()
            self.stdout.write(self.style.WARNING(f"既存サンプルデータ {deleted_count} 件を削除しました"))

        created_count = 0
        skipped_count = 0
        today = datetime.now(tz=UTC).date()

        for risk_data in SAMPLE_RISKS:
            risk_id = risk_data["risk_id"]
            if Risk.objects.filter(risk_id=risk_id).exists():
                self.stdout.write(f"  スキップ: {risk_id}（既存）")
                skipped_count += 1
                continue

            Risk.objects.create(
                **risk_data,
                target_date=today + timedelta(days=90),
                review_date=today + timedelta(days=30),
            )
            self.stdout.write(self.style.SUCCESS(f"  作成: {risk_id} - {risk_data['title']}"))
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n完了: {created_count} 件作成, {skipped_count} 件スキップ"))
