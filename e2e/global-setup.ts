import { chromium, FullConfig } from '@playwright/test'

async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0].use.baseURL || 'http://localhost:3000'
  const browser = await chromium.launch()
  const page = await browser.newPage()

  // Perform login and save storage state for reuse in tests
  await page.goto(`${baseURL}/login`)
  await page.fill('input[type="text"]', 'admin')
  await page.fill('input[type="password"]', 'admin123')
  await page.click('button[type="submit"]')

  // Wait for redirect to dashboard
  await page.waitForURL(/dashboard|^\/$/, { timeout: 10000 }).catch(() => {
    // If redirect doesn't happen, continue — login test itself will verify this
  })

  await page.context().storageState({ path: 'e2e/.auth-state.json' })
  await browser.close()
}

export default globalSetup
