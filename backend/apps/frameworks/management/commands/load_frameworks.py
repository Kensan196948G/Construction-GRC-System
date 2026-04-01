"""全フレームワーク・法令フィクスチャデータの一括ロード"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "ISO27001管理策・NIST CSF・建設業法令の全フィクスチャデータを一括ロード"

    FIXTURES = [
        ("apps/frameworks/fixtures/iso27001_controls.json", "ISO27001管理策 (93件)"),
        ("apps/frameworks/fixtures/nist_csf_2.json", "NIST CSF 2.0 (21カテゴリ)"),
        ("apps/frameworks/fixtures/construction_regs.json", "建設業法令要件 (17件)"),
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("フレームワークデータの一括ロードを開始..."))

        for fixture_path, description in self.FIXTURES:
            try:
                call_command("loaddata", fixture_path)
                self.stdout.write(self.style.SUCCESS(f"  ✅ {description}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ {description}: {e}"))

        self.stdout.write(self.style.SUCCESS("フレームワークデータのロードが完了しました。"))
