"""共有テストフィクスチャ"""
import pytest


@pytest.fixture
def risk_data():
    """サンプルリスクデータ"""
    return {
        "risk_id": "RISK-TEST-001",
        "title": "テスト用リスク",
        "description": "テスト用のリスクデータ",
        "category": "IT",
        "likelihood_inherent": 3,
        "impact_inherent": 4,
        "treatment_strategy": "mitigate",
        "status": "open",
    }


@pytest.fixture
def control_data():
    """サンプルISO27001管理策データ"""
    return {
        "control_id": "A.5.1",
        "domain": "organizational",
        "title": "情報セキュリティのための方針群",
        "description": "テスト用管理策",
        "is_applicable": True,
        "implementation_status": "not_started",
        "evidence_required": ["方針文書", "承認記録"],
        "nist_csf_mapping": ["GV.PO-01"],
    }


@pytest.fixture
def compliance_data():
    """サンプルコンプライアンス要件データ"""
    return {
        "req_id": "KEN-TEST-001",
        "framework": "construction_law",
        "category": "許可要件",
        "title": "テスト用建設業法要件",
        "article_ref": "建設業法第3条",
        "is_mandatory": True,
        "frequency": "annual",
        "compliance_status": "unknown",
    }


@pytest.fixture
def audit_data():
    """サンプル監査データ"""
    return {
        "audit_id": "AUD-TEST-001",
        "title": "テスト用内部監査",
        "audit_type": "ISO27001定期監査",
        "target_department": "IT部門",
        "planned_start": "2026-04-01",
        "planned_end": "2026-04-15",
        "status": "planned",
    }
