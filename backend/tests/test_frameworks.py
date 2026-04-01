"""Framework API テスト."""

import django.db
from django.test import TestCase
import pytest

from apps.frameworks.models import Framework


class TestFrameworkModelDefinition:
    """Framework モデル定義テスト（DB不要）."""

    def test_framework_category_choices(self):
        choices = [c[0] for c in Framework.Category.choices]
        assert set(choices) == {"security", "compliance", "legal", "quality"}

    def test_framework_str(self):
        fw = Framework(code="nist_csf_2", name_ja="NIST CSF 2.0")
        assert str(fw) == "nist_csf_2: NIST CSF 2.0"

    def test_framework_str_iso(self):
        fw = Framework(code="iso27001", name_ja="ISO27001情報セキュリティ")
        assert str(fw) == "iso27001: ISO27001情報セキュリティ"

    def test_framework_default_is_active(self):
        fw = Framework()
        assert fw.is_active is True

    def test_framework_meta_ordering(self):
        assert Framework._meta.ordering == ["code"]

    def test_framework_meta_verbose_name(self):
        assert Framework._meta.verbose_name == "フレームワーク定義"

    def test_framework_code_max_length(self):
        field = Framework._meta.get_field("code")
        assert field.max_length == 30

    def test_framework_code_unique(self):
        field = Framework._meta.get_field("code")
        assert field.unique is True

    def test_framework_uuid_primary_key(self):
        field = Framework._meta.get_field("id")
        assert field.primary_key is True

    def test_framework_description_blank(self):
        field = Framework._meta.get_field("description")
        assert field.blank is True

    def test_framework_official_url_blank(self):
        field = Framework._meta.get_field("official_url")
        assert field.blank is True


@pytest.mark.django_db
@pytest.mark.integration
class TestFrameworkModel(TestCase):
    """Framework モデルCRUDテスト（DB必要 — PostgreSQL環境で実行）."""

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
