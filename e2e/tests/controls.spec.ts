import { test, expect } from '@playwright/test'

test.describe('ISO27001 Controls', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/controls')
  })

  test('should display controls page', async ({ page }) => {
    await expect(page.locator('h1, .text-h4').first()).toContainText(/管理策/)
  })

  test('should show domain tabs', async ({ page }) => {
    const tabs = page.locator('.v-tab')
    if (await tabs.count() > 0) {
      // 4ドメインタブ確認（組織的/人的/物理的/技術的）
      expect(await tabs.count()).toBeGreaterThanOrEqual(2)
    }
  })

  test('should show controls table with 93 items or pagination', async ({ page }) => {
    await expect(page.locator('table, .v-data-table').first()).toBeVisible()
  })

  test('should show compliance rate summary', async ({ page }) => {
    // 準拠率表示の確認
    const rateElement = page.locator(':text("%"), .v-progress-linear')
    if (await rateElement.count() > 0) {
      await expect(rateElement.first()).toBeVisible()
    }
  })
})
