"""フィクスチャデータのバリデーションテスト"""
import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "apps" / "frameworks" / "fixtures"


class TestISO27001Fixtures:
    """ISO27001管理策フィクスチャのテスト"""

    def test_fixture_file_exists(self):
        assert (FIXTURES_DIR / "iso27001_controls.json").exists()

    def test_total_controls_count(self):
        with open(FIXTURES_DIR / "iso27001_controls.json") as f:
            data = json.load(f)
        assert len(data) == 93, f"Expected 93 controls, got {len(data)}"

    def test_domain_distribution(self):
        with open(FIXTURES_DIR / "iso27001_controls.json") as f:
            data = json.load(f)
        domains = {}
        for item in data:
            d = item["fields"]["domain"]
            domains[d] = domains.get(d, 0) + 1
        assert domains.get("organizational") == 37
        assert domains.get("people") == 8
        assert domains.get("physical") == 14
        assert domains.get("technological") == 34

    def test_all_controls_have_required_fields(self):
        with open(FIXTURES_DIR / "iso27001_controls.json") as f:
            data = json.load(f)
        for item in data:
            fields = item["fields"]
            assert fields["control_id"], f"Missing control_id in {item['pk']}"
            assert fields["title"], f"Missing title for {fields['control_id']}"
            assert fields["domain"] in ("organizational", "people", "physical", "technological")


class TestNISTCSFFixtures:
    """NIST CSF 2.0フィクスチャのテスト"""

    def test_fixture_file_exists(self):
        assert (FIXTURES_DIR / "nist_csf_2.json").exists()

    def test_has_all_functions(self):
        with open(FIXTURES_DIR / "nist_csf_2.json") as f:
            data = json.load(f)
        assert len(data) >= 20, f"Expected at least 20 categories, got {len(data)}"


class TestConstructionRegsFixtures:
    """建設業法令フィクスチャのテスト"""

    def test_fixture_file_exists(self):
        assert (FIXTURES_DIR / "construction_regs.json").exists()

    def test_has_all_frameworks(self):
        with open(FIXTURES_DIR / "construction_regs.json") as f:
            data = json.load(f)
        frameworks = {item["fields"]["framework"] for item in data}
        assert "construction_law" in frameworks
        assert "quality_law" in frameworks
        assert "safety_law" in frameworks

    def test_minimum_requirements_count(self):
        with open(FIXTURES_DIR / "construction_regs.json") as f:
            data = json.load(f)
        assert len(data) >= 15, f"Expected at least 15 requirements, got {len(data)}"
