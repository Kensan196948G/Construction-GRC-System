"""Framework API テスト."""

import django.db
import pytest
from django.test import TestCase

from apps.frameworks.models import Framework


class TestFrameworkModel(TestCase):
    """Framework モデルテスト."""

    def test_create_framework(self):
        fw = Framework.objects.create(
            code="iso27001",
            name="ISO/IEC 27001:2022",
            name_ja="ISO27001情報セキュリティ",
            version="2022",
            category="security",
        )
        assert fw.code == "iso27001"
        assert fw.is_active is True
        assert str(fw) is not None

    def test_framework_unique_code(self):
        Framework.objects.create(code="test_fw", name="Test", name_ja="テスト", version="1.0", category="security")
        with pytest.raises(django.db.IntegrityError):
            Framework.objects.create(code="test_fw", name="Test2", name_ja="テスト2", version="2.0", category="legal")

    def test_framework_str(self):
        fw = Framework(code="nist_csf_2", name_ja="NIST CSF 2.0")
        assert str(fw) == "nist_csf_2: NIST CSF 2.0"

    def test_framework_category_choices(self):
        choices = [c[0] for c in Framework.Category.choices]
        assert set(choices) == {"security", "compliance", "legal", "quality"}

    def test_framework_default_is_active(self):
        fw = Framework.objects.create(
            code="test_active",
            name="Active Test",
            name_ja="アクティブテスト",
            version="1.0",
            category="quality",
        )
        assert fw.is_active is True

    def test_framework_ordering(self):
        Framework.objects.create(code="z_framework", name="Z", name_ja="Z", version="1.0", category="security")
        Framework.objects.create(code="a_framework", name="A", name_ja="A", version="1.0", category="security")
        frameworks = list(Framework.objects.values_list("code", flat=True))
        assert frameworks == sorted(frameworks)

    def test_framework_optional_fields(self):
        fw = Framework.objects.create(
            code="minimal",
            name="Minimal",
            name_ja="最小",
            version="1.0",
            category="legal",
            description="",
            official_url="",
        )
        assert fw.description == ""
        assert fw.official_url == ""

    def test_framework_uuid_primary_key(self):
        fw = Framework.objects.create(
            code="uuid_test",
            name="UUID Test",
            name_ja="UUIDテスト",
            version="1.0",
            category="compliance",
        )
        assert fw.id is not None
        assert len(str(fw.id)) == 36  # UUID format
