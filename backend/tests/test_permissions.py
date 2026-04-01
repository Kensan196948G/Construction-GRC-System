"""RBAC権限テスト."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from apps.accounts.models import GRCUser
from apps.accounts.permissions import (
    IsAuditor,
    IsComplianceOfficer,
    IsGRCAdmin,
    IsRiskOwner,
    ReadOnlyOrAdmin,
    RoleBasedPermission,
)


class MockRequest:
    """テスト用モックリクエスト."""

    def __init__(self, user=None, method="GET"):
        self.user = user
        self.method = method


class MockView:
    """テスト用モックビュー."""

    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []


class MockUser:
    """テスト用モックユーザー（DB不要）."""

    def __init__(self, role=None, is_authenticated=True):
        self.role = role
        self.is_authenticated = is_authenticated


@pytest.mark.django_db
class TestIsGRCAdmin:
    """IsGRCAdmin パーミッションテスト."""

    def test_allows_grc_admin(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN)
        request = MockRequest(user=user)
        assert IsGRCAdmin().has_permission(request, MockView()) is True

    def test_denies_auditor(self):
        user = MockUser(role=GRCUser.Role.AUDITOR)
        request = MockRequest(user=user)
        assert IsGRCAdmin().has_permission(request, MockView()) is False

    def test_denies_general(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user)
        assert IsGRCAdmin().has_permission(request, MockView()) is False

    def test_denies_unauthenticated(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN, is_authenticated=False)
        request = MockRequest(user=user)
        assert IsGRCAdmin().has_permission(request, MockView()) is False

    def test_denies_no_user(self):
        request = MockRequest(user=None)
        assert IsGRCAdmin().has_permission(request, MockView()) is False


@pytest.mark.django_db
class TestIsAuditor:
    """IsAuditor パーミッションテスト."""

    def test_allows_auditor(self):
        user = MockUser(role=GRCUser.Role.AUDITOR)
        request = MockRequest(user=user)
        assert IsAuditor().has_permission(request, MockView()) is True

    def test_allows_grc_admin(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN)
        request = MockRequest(user=user)
        assert IsAuditor().has_permission(request, MockView()) is True

    def test_denies_risk_owner(self):
        user = MockUser(role=GRCUser.Role.RISK_OWNER)
        request = MockRequest(user=user)
        assert IsAuditor().has_permission(request, MockView()) is False

    def test_denies_general(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user)
        assert IsAuditor().has_permission(request, MockView()) is False

    def test_denies_unauthenticated(self):
        user = MockUser(role=GRCUser.Role.AUDITOR, is_authenticated=False)
        request = MockRequest(user=user)
        assert IsAuditor().has_permission(request, MockView()) is False


@pytest.mark.django_db
class TestIsRiskOwner:
    """IsRiskOwner パーミッションテスト."""

    def test_allows_risk_owner(self):
        user = MockUser(role=GRCUser.Role.RISK_OWNER)
        request = MockRequest(user=user)
        assert IsRiskOwner().has_permission(request, MockView()) is True

    def test_allows_grc_admin(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN)
        request = MockRequest(user=user)
        assert IsRiskOwner().has_permission(request, MockView()) is True

    def test_denies_compliance_officer(self):
        user = MockUser(role=GRCUser.Role.COMPLIANCE_OFFICER)
        request = MockRequest(user=user)
        assert IsRiskOwner().has_permission(request, MockView()) is False

    def test_denies_general(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user)
        assert IsRiskOwner().has_permission(request, MockView()) is False


@pytest.mark.django_db
class TestIsComplianceOfficer:
    """IsComplianceOfficer パーミッションテスト."""

    def test_allows_compliance_officer(self):
        user = MockUser(role=GRCUser.Role.COMPLIANCE_OFFICER)
        request = MockRequest(user=user)
        assert IsComplianceOfficer().has_permission(request, MockView()) is True

    def test_allows_grc_admin(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN)
        request = MockRequest(user=user)
        assert IsComplianceOfficer().has_permission(request, MockView()) is True

    def test_denies_auditor(self):
        user = MockUser(role=GRCUser.Role.AUDITOR)
        request = MockRequest(user=user)
        assert IsComplianceOfficer().has_permission(request, MockView()) is False

    def test_denies_general(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user)
        assert IsComplianceOfficer().has_permission(request, MockView()) is False


@pytest.mark.django_db
class TestRoleBasedPermission:
    """RoleBasedPermission パーミッションテスト."""

    def test_allows_listed_role(self):
        user = MockUser(role=GRCUser.Role.AUDITOR)
        request = MockRequest(user=user)
        view = MockView(allowed_roles=[GRCUser.Role.AUDITOR, GRCUser.Role.GRC_ADMIN])
        assert RoleBasedPermission().has_permission(request, view) is True

    def test_denies_unlisted_role(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user)
        view = MockView(allowed_roles=[GRCUser.Role.AUDITOR, GRCUser.Role.GRC_ADMIN])
        assert RoleBasedPermission().has_permission(request, view) is False

    def test_allows_all_when_no_roles_defined(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user)
        view = MockView(allowed_roles=[])
        assert RoleBasedPermission().has_permission(request, view) is True

    def test_denies_unauthenticated(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN, is_authenticated=False)
        request = MockRequest(user=user)
        view = MockView(allowed_roles=[GRCUser.Role.GRC_ADMIN])
        assert RoleBasedPermission().has_permission(request, view) is False

    def test_allows_when_view_has_no_allowed_roles_attr(self):
        """allowed_roles属性がないビューは全認証ユーザー許可."""
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user)
        view = MagicMock(spec=[])  # no attributes
        assert RoleBasedPermission().has_permission(request, view) is True


@pytest.mark.django_db
class TestReadOnlyOrAdmin:
    """ReadOnlyOrAdmin パーミッションテスト."""

    def test_get_allowed_for_authenticated(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user, method="GET")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is True

    def test_head_allowed_for_authenticated(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user, method="HEAD")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is True

    def test_options_allowed_for_authenticated(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user, method="OPTIONS")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is True

    def test_post_denied_for_general(self):
        user = MockUser(role=GRCUser.Role.GENERAL)
        request = MockRequest(user=user, method="POST")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is False

    def test_post_allowed_for_admin(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN)
        request = MockRequest(user=user, method="POST")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is True

    def test_put_allowed_for_admin(self):
        user = MockUser(role=GRCUser.Role.GRC_ADMIN)
        request = MockRequest(user=user, method="PUT")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is True

    def test_delete_denied_for_non_admin(self):
        user = MockUser(role=GRCUser.Role.AUDITOR)
        request = MockRequest(user=user, method="DELETE")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is False

    def test_get_denied_for_unauthenticated(self):
        user = MockUser(role=GRCUser.Role.GENERAL, is_authenticated=False)
        request = MockRequest(user=user, method="GET")
        assert ReadOnlyOrAdmin().has_permission(request, MockView()) is False
