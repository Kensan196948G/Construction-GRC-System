"""NistCSFCategory モデルテスト."""

import pytest
from django.db import IntegrityError
from django.test import TestCase

from apps.controls.models import NistCSFCategory


class TestNistCSFCategoryModel(TestCase):
    """NistCSFCategory モデルCRUDテスト."""

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
        assert cat.function_name_ja == "統治"
        assert cat.category_id == "GV.OC-01"
        assert cat.category_name == "Organizational Context"
        assert cat.category_name_ja == "組織の状況"
        assert cat.id is not None

    def test_str_representation(self):
        cat = self._create_category()
        assert str(cat) == "GV.OC-01: 組織の状況"

    def test_unique_category_id(self):
        self._create_category(category_id="GV.OC-01")
        with pytest.raises(IntegrityError):
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

    def test_description_en_optional(self):
        cat = self._create_category(category_id="RS.RP-01", description_en="")
        assert cat.description_en == ""

    def test_uuid_primary_key(self):
        cat = self._create_category(category_id="RC.RP-01")
        assert cat.id is not None
        assert len(str(cat.id)) == 36
