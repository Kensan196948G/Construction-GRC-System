import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('should navigate to all main pages', async ({ page }) => {
    await page.goto('/')
    const pages = ['/risks', '/compliance', '/controls', '/audits', '/reports']
    for (const path of pages) {
      await page.goto(path)
      await expect(page).toHaveURL(new RegExp(path))
    }
  })
})
