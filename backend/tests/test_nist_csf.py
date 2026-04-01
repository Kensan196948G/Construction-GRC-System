"""NistCSFCategory モデルテスト."""

import pytest
from django.test import TestCase

from apps.controls.models import NistCSFCategory


class TestNistCSFCategoryDefinition:
    """NistCSFCategory モデル定義テスト（DB不要）."""

    def test_str_representation(self):
        cat = NistCSFCategory(category_id="GV.OC-01", category_name_ja="組織の状況")
        assert str(cat) == "GV.OC-01: 組織の状況"

    def test_str_with_different_category(self):
        cat = NistCSFCategory(category_id="ID.AM-01", category_name_ja="資産管理")
        assert str(cat) == "ID.AM-01: 資産管理"

    def test_meta_ordering(self):
        assert NistCSFCategory._meta.ordering == ["category_id"]

    def test_meta_verbose_name(self):
        assert NistCSFCategory._meta.verbose_name == "NIST CSFカテゴリ"

    def test_category_id_unique(self):
        field = NistCSFCategory._meta.get_field("category_id")
        assert field.unique is True

    def test_category_id_max_length(self):
        field = NistCSFCategory._meta.get_field("category_id")
        assert field.max_length == 20

    def test_function_id_max_length(self):
        field = NistCSFCategory._meta.get_field("function_id")
        assert field.max_length == 10

    def test_uuid_primary_key(self):
        field = NistCSFCategory._meta.get_field("id")
        assert field.primary_key is True

    def test_description_en_blank(self):
        field = NistCSFCategory._meta.get_field("description_en")
        assert field.blank is True

    def test_description_required(self):
        field = NistCSFCategory._meta.get_field("description")
        assert field.blank is False

    def test_function_name_max_length(self):
        field = NistCSFCategory._meta.get_field("function_name")
        assert field.max_length == 50

    def test_category_name_max_length(self):
        field = NistCSFCategory._meta.get_field("category_name")
        assert field.max_length == 200


@pytest.mark.django_db
class TestNistCSFCategoryModel(TestCase):
    """NistCSFCategory モデルCRUDテスト（DB必要）."""

    def _create_category(self, **kwargs):
        """テスト用NistCSFCategoryを作成するヘルパー."""
        defaults = {
            "function_id": "GV",
            "function_name": "GOVERN",
            "function_name_ja": "統治",
            "category_id": "GV.OC-01",
            "category_name": "Organizational Context",
            "category_name_ja": "組織の状況",
            "description": "組織の状況を理解する",
            "description_en": "Understand organizational context",
        }
        defaults.update(kwargs)
        return NistCSFCategory.objects.create(**defaults)

    def test_create_category(self):
        cat = self._create_category()
        assert cat.function_id == "GV"
        assert cat.function_name == "GOVERN"
        assert cat.category_id == "GV.OC-01"
        assert cat.id is not None

    def test_unique_category_id(self):
        self._create_category(category_id="GV.OC-01")
        with pytest.raises(Exception):
            self._create_category(category_id="GV.OC-01")

    def test_read_category(self):
        self._create_category(category_id="GV.RM-01")
        cat = NistCSFCategory.objects.get(category_id="GV.RM-01")
        assert cat.function_id == "GV"

    def test_update_category(self):
        cat = self._create_category(category_id="ID.AM-01")
        cat.category_name_ja = "資産管理（更新）"
        cat.save()
        cat.refresh_from_db()
        assert cat.category_name_ja == "資産管理（更新）"

    def test_delete_category(self):
        cat = self._create_category(category_id="PR.AC-01")
        cat_id = cat.id
        cat.delete()
        assert not NistCSFCategory.objects.filter(id=cat_id).exists()

    def test_ordering_by_category_id(self):
        self._create_category(category_id="PR.AC-01")
        self._create_category(category_id="DE.CM-01")
        self._create_category(category_id="GV.OC-01")
        ids = list(NistCSFCategory.objects.values_list("category_id", flat=True))
        assert ids == sorted(ids)
