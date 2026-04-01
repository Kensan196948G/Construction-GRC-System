"""認証基盤テスト."""

from __future__ import annotations

from unittest.mock import MagicMock

from django.test import RequestFactory
import pytest

from apps.accounts.models import GRCUser
from apps.accounts.permissions import (
    IsAuditor,
    IsExecutiveOrAbove,
    IsGRCAdmin,
    RoleBasedPermission,
)


@pytest.mark.django_db
class TestRoleChoices:
    """ロール定義のテスト."""

    def test_role_choices(self) -> None:
        """6ロールが定義されていることを確認."""
        choices: list[tuple[str, str]] = GRCUser.Role.choices
        assert len(choices) == 6
        role_values: set[str] = {value for value, _label in choices}
        expected: set[str] = {
            "grc_admin",
            "risk_owner",
            "compliance_officer",
            "auditor",
            "executive",
            "general",
        }
        assert role_values == expected


@pytest.mark.django_db
class TestUserCreation:
    """GRCUserインスタンス生成テスト."""

    def test_user_creation(self) -> None:
        """GRCUserが正しく作成されることを確認."""
        user: GRCUser = GRCUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="securepassword123",
            role=GRCUser.Role.RISK_OWNER,
            department="IT部門",
            display_name="テストユーザー",
            phone="03-1234-5678",
        )
        assert user.pk is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == GRCUser.Role.RISK_OWNER
        assert user.department == "IT部門"
        assert user.display_name == "テストユーザー"
        assert user.phone == "03-1234-5678"
        assert user.check_password("securepassword123")

    def test_user_str(self) -> None:
        """__str__がdisplay_nameを返すことを確認."""
        user: GRCUser = GRCUser(username="testuser", display_name="表示名テスト")
        assert str(user) == "表示名テスト"

    def test_user_str_fallback(self) -> None:
        """display_name未設定時にusernameへフォールバックすることを確認."""
        user: GRCUser = GRCUser(username="testuser")
        assert str(user) == "testuser"

    def test_default_role(self) -> None:
        """デフォルトロールがgeneralであることを確認."""
        user: GRCUser = GRCUser.objects.create_user(
            username="defaultuser",
            password="securepassword123",
        )
        assert user.role == GRCUser.Role.GENERAL


@pytest.mark.django_db
class TestPermissions:
    """パーミッションクラスの動作テスト."""

    @pytest.fixture()
    def factory(self) -> RequestFactory:
        return RequestFactory()

    @pytest.fixture()
    def admin_user(self) -> GRCUser:
        return GRCUser.objects.create_user(
            username="admin",
            password="pass123",
            role=GRCUser.Role.GRC_ADMIN,
        )

    @pytest.fixture()
    def auditor_user(self) -> GRCUser:
        return GRCUser.objects.create_user(
            username="auditor",
            password="pass123",
            role=GRCUser.Role.AUDITOR,
        )

    @pytest.fixture()
    def executive_user(self) -> GRCUser:
        return GRCUser.objects.create_user(
            username="executive",
            password="pass123",
            role=GRCUser.Role.EXECUTIVE,
        )

    @pytest.fixture()
    def general_user(self) -> GRCUser:
        return GRCUser.objects.create_user(
            username="general",
            password="pass123",
            role=GRCUser.Role.GENERAL,
        )

    def _make_request(self, factory: RequestFactory, user: GRCUser) -> MagicMock:
        request = factory.get("/")
        request.user = user
        return request

    def test_is_grc_admin_allows_admin(self, factory: RequestFactory, admin_user: GRCUser) -> None:
        request = self._make_request(factory, admin_user)
        assert IsGRCAdmin().has_permission(request, MagicMock()) is True

    def test_is_grc_admin_denies_general(self, factory: RequestFactory, general_user: GRCUser) -> None:
        request = self._make_request(factory, general_user)
        assert IsGRCAdmin().has_permission(request, MagicMock()) is False

    def test_is_auditor_allows_auditor(self, factory: RequestFactory, auditor_user: GRCUser) -> None:
        request = self._make_request(factory, auditor_user)
        assert IsAuditor().has_permission(request, MagicMock()) is True

    def test_is_auditor_allows_admin(self, factory: RequestFactory, admin_user: GRCUser) -> None:
        request = self._make_request(factory, admin_user)
        assert IsAuditor().has_permission(request, MagicMock()) is True

    def test_is_auditor_denies_general(self, factory: RequestFactory, general_user: GRCUser) -> None:
        request = self._make_request(factory, general_user)
        assert IsAuditor().has_permission(request, MagicMock()) is False

    def test_is_executive_allows_executive(self, factory: RequestFactory, executive_user: GRCUser) -> None:
        request = self._make_request(factory, executive_user)
        assert IsExecutiveOrAbove().has_permission(request, MagicMock()) is True

    def test_is_executive_allows_admin(self, factory: RequestFactory, admin_user: GRCUser) -> None:
        request = self._make_request(factory, admin_user)
        assert IsExecutiveOrAbove().has_permission(request, MagicMock()) is True

    def test_is_executive_denies_general(self, factory: RequestFactory, general_user: GRCUser) -> None:
        request = self._make_request(factory, general_user)
        assert IsExecutiveOrAbove().has_permission(request, MagicMock()) is False

    def test_role_based_permission_with_allowed_roles(self, factory: RequestFactory, auditor_user: GRCUser) -> None:
        request = self._make_request(factory, auditor_user)
        view = MagicMock()
        view.allowed_roles = [GRCUser.Role.AUDITOR, GRCUser.Role.GRC_ADMIN]
        assert RoleBasedPermission().has_permission(request, view) is True

    def test_role_based_permission_denies_unlisted_role(self, factory: RequestFactory, general_user: GRCUser) -> None:
        request = self._make_request(factory, general_user)
        view = MagicMock()
        view.allowed_roles = [GRCUser.Role.AUDITOR, GRCUser.Role.GRC_ADMIN]
        assert RoleBasedPermission().has_permission(request, view) is False

    def test_role_based_permission_allows_all_when_no_roles(
        self, factory: RequestFactory, general_user: GRCUser
    ) -> None:
        """allowed_roles未設定時は全認証ユーザーを許可."""
        request = self._make_request(factory, general_user)
        view = MagicMock()
        view.allowed_roles = []
        assert RoleBasedPermission().has_permission(request, view) is True
