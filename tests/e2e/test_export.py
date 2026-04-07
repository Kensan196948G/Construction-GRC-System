"""CSV/PDFエクスポート E2Eテスト. SKIP_E2E=1 でスキップ。"""
import os
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:3000")
pytestmark = pytest.mark.skipif(os.getenv("SKIP_E2E") == "1", reason="E2Eテストスキップ")


def login(page: Page) -> None:
    page.goto(f"{BASE_URL}/login")
    page.fill('input[type="text"]', os.getenv("E2E_ADMIN_USER", "admin"))
    page.fill('input[type="password"]', os.getenv("E2E_ADMIN_PASSWORD", "adminpass"))
    page.click('button[type="submit"]')
    page.wait_for_url("**/dashboard", timeout=10000)


def test_reports_page_loads(page: Page):
    login(page)
    page.goto(f"{BASE_URL}/reports")
    expect(page.locator("h1, h2, .v-card-title")).to_be_visible(timeout=5000)


def test_compliance_page_loads(page: Page):
    login(page)
    page.goto(f"{BASE_URL}/compliance")
    expect(page.locator("h1, h2, .v-card-title")).to_be_visible(timeout=5000)
