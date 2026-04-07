import { FullConfig } from '@playwright/test'
import * as fs from 'fs'

async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0].use.baseURL || 'http://localhost:3000'

  // Obtain JWT token directly via HTTP (bypasses browser-based login for reliability)
  const tokenURL = `${baseURL}/api/v1/auth/token/`
  console.log(`Global setup: fetching token from ${tokenURL}`)

  const res = await fetch(tokenURL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'admin', password: 'admin123' }),
  })

  if (!res.ok) {
    const body = await res.text()
    throw new Error(
      `Global setup: token request failed — HTTP ${res.status}: ${body}`,
    )
  }

  const data = (await res.json()) as { access: string; refresh: string }
  if (!data.access) {
    throw new Error(`Global setup: response has no 'access' field: ${JSON.stringify(data)}`)
  }
  console.log(`Global setup: token obtained (length=${data.access.length})`)

  // Write storageState JSON directly — no browser needed
  const storageState = {
    cookies: [],
    origins: [
      {
        origin: baseURL,
        localStorage: [
          { name: 'access_token', value: data.access },
          { name: 'refresh_token', value: data.refresh },
        ],
      },
    ],
  }
  fs.writeFileSync('.auth-state.json', JSON.stringify(storageState, null, 2))
  console.log('Global setup: storageState written to .auth-state.json')
}

export default globalSetup
