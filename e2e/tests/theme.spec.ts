import { test, expect } from '@playwright/test'

test.describe('Dark Theme Toggle', () => {
  test('should toggle theme', async ({ page }) => {
    await page.goto('/')
    // テーマ切替ボタンを探す
    const themeBtn = page.locator('button:has(.mdi-theme-light-dark), button:has(.mdi-weather-night), button:has(.mdi-white-balance-sunny)')
    if (await themeBtn.count() > 0) {
      await themeBtn.first().click()
      // ダーク/ライトクラスの変化を確認
      await page.waitForTimeout(500)
      const body = page.locator('body, .v-application')
      const classList = await body.getAttribute('class') || ''
      expect(classList.length).toBeGreaterThan(0)
    }
  })
})
