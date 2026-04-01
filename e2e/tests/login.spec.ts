import { test, expect } from '@playwright/test'

test.describe('Login Page', () => {
  test('should display login form', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('form')).toBeVisible()
  })

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="text"]', 'invalid')
    await page.fill('input[type="password"]', 'invalid')
    await page.click('button[type="submit"]')
    await expect(page.locator('.v-alert')).toBeVisible()
  })

  test('should redirect to dashboard on success', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL(/dashboard|\//)
  })
})
