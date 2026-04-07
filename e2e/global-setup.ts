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

  // Wait for redirect to dashboard — fail explicitly if login doesn't succeed
  try {
    await page.waitForURL(/dashboard|^\/$/, { timeout: 15000 })
  } catch {
    const errorText = await page.locator('.v-alert').textContent().catch(() => '(no error element)')
    const currentURL = page.url()
    throw new Error(
      `Global setup: login redirect failed. URL=${currentURL}, pageError=${errorText}`,
    )
  }

  // Verify tokens were captured in localStorage
  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'))
  if (!accessToken) {
    throw new Error(
      'Global setup: login appeared to succeed but no access_token found in localStorage',
    )
  }
  console.log(`Global setup: authenticated successfully (token length=${accessToken.length})`)

  await page.context().storageState({ path: '.auth-state.json' })
  await browser.close()
}

export default globalSetup
