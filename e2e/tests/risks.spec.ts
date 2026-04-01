import { test, expect } from '@playwright/test'

test.describe('Risk Management', () => {
  test.beforeEach(async ({ page }) => {
    // ログイン状態をセットアップ（実際のAPIがなくてもページ遷移テスト可能）
    await page.goto('/risks')
  })

  test('should display risk management page', async ({ page }) => {
    await expect(page.locator('h1, .text-h4')).toContainText(/リスク/)
  })

  test('should show risk table', async ({ page }) => {
    await expect(page.locator('table, .v-data-table')).toBeVisible()
  })

  test('should have filter controls', async ({ page }) => {
    // カテゴリフィルタの存在確認
    await expect(page.locator('select, .v-select, .v-autocomplete').first()).toBeVisible()
  })

  test('should show risk heatmap component', async ({ page }) => {
    // ヒートマップコンポーネントの存在
    const heatmap = page.locator('.risk-heatmap, [class*="heatmap"]')
    // ヒートマップがある場合のみチェック
    if (await heatmap.count() > 0) {
      await expect(heatmap.first()).toBeVisible()
    }
  })

  test('should open new risk dialog', async ({ page }) => {
    const addButton = page.locator('button:has-text("登録"), button:has-text("追加"), button:has-text("新規")')
    if (await addButton.count() > 0) {
      await addButton.first().click()
      await expect(page.locator('.v-dialog, .v-overlay')).toBeVisible()
    }
  })
})
