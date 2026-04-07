"""リスク管理 CRUD E2Eテスト. SKIP_E2E=1 でスキップ。"""
import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
pytestmark = pytest.mark.skipif(os.getenv("SKIP_E2E") == "1", reason="E2Eテストスキップ")


def login(page: Page) -> None:
    page.goto(f"{BASE_URL}/login")
    page.fill('input[type="text"], [data-testid="username"]', os.getenv("E2E_ADMIN_USER", "admin"))
    page.fill('input[type="password"], [data-testid="password"]', os.getenv("E2E_ADMIN_PASSWORD", "adminpass"))
    page.click('button[type="submit"], [data-testid="login-button"]')
    page.wait_for_url(f"**/dashboard", timeout=10000)


def test_risk_list_page_loads(page: Page):
    login(page)
    page.goto(f"{BASE_URL}/risks")
    expect(page.locator("h1, h2, .v-card-title")).to_contain_text("リスク", timeout=5000)


def test_risk_page_has_content(page: Page):
    login(page)
    page.goto(f"{BASE_URL}/risks")
    expect(page.locator(".v-data-table, .v-list, table, [data-testid='risk-list']")).to_be_visible(timeout=8000)


def test_dashboard_page_loads(page: Page):
    login(page)
    page.goto(f"{BASE_URL}/dashboard")
    expect(page.locator("h1, h2, .v-card-title")).to_be_visible(timeout=5000)
