// @ts-check
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: { timeout: 8_000 },
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],

  use: {
    baseURL: 'http://localhost:8765',
    headless: true,
    viewport: { width: 1440, height: 900 },
    actionTimeout: 8_000,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Serve the frontend/ directory with Python's built-in http.server
  webServer: {
    command: 'python -m http.server 8765 --directory frontend',
    port: 8765,
    reuseExistingServer: !process.env.CI,
    timeout: 10_000,
  },
});
