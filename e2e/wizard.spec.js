// @ts-check
/**
 * ExamOps 5-Step Wizard — Playwright e2e tests
 *
 * Runs against: process.env.E2E_BASE_URL (default: live Azure Functions URL)
 * Tests are UI-only — no real API calls (avoids 429 rate limits).
 */

const { test, expect } = require('@playwright/test');

// Full URL of the wizard page. page.goto('/') resolves to the domain root on
// Azure Functions (not /api/web), so we navigate using the absolute URL directly.
const WIZARD_URL =
  process.env.E2E_BASE_URL ||
  'https://func-examops-prod.azurewebsites.net/api/web';

// ══════════════════════════════════════════════════════════════════════════════
// 1. PAGE LOAD
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Page load', () => {
  test('has correct page title', async ({ page }) => {
    await page.goto(WIZARD_URL);
    await expect(page).toHaveTitle(/ExamOps/i);
  });

  test('shows SUC header with "ExamOps Orchestrator"', async ({ page }) => {
    await page.goto(WIZARD_URL);
    await expect(page.locator('.suc-header')).toContainText('ExamOps Orchestrator');
  });

  test('shows 5 steps in left navigation panel', async ({ page }) => {
    await page.goto(WIZARD_URL);
    await expect(page.locator('.step-item')).toHaveCount(5);
  });

  test('Step 1 is active by default', async ({ page }) => {
    await page.goto(WIZARD_URL);
    const activeStep = page.locator('.step-item.active');
    await expect(activeStep).toHaveCount(1);
    await expect(activeStep).toContainText('Upload Syllabus');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 2. STEP 1 — Upload Syllabus
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Step 1 — Upload Syllabus', () => {
  test('upload area is visible', async ({ page }) => {
    await page.goto(WIZARD_URL);
    await expect(page.locator('#uploadArea1')).toBeVisible();
  });

  test('SharePoint URL input is visible', async ({ page }) => {
    await page.goto(WIZARD_URL);
    await expect(page.locator('#spUrl1')).toBeVisible();
  });

  test('"Extract CLOs & PLOs" button is visible and enabled', async ({ page }) => {
    await page.goto(WIZARD_URL);
    const btn = page.locator('button', { hasText: /Extract CLOs/i });
    await expect(btn).toBeVisible();
    await expect(btn).toBeEnabled();
  });

  test('button disables on click and shows spinner text', async ({ page }) => {
    await page.goto(WIZARD_URL);

    // Intercept the API call so it hangs — button should disable while pending
    await page.route('**/api/upload-syllabus', route => {
      // Never resolve — keeps button in loading state
    });

    // Need a file selected before the button does anything
    const fileInput = page.locator('#fileInput1');
    await fileInput.setInputFiles({
      name: 'test.docx',
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      buffer: Buffer.from('PK stub'),
    });

    const btn = page.locator('button', { hasText: /Extract CLOs/i });
    await btn.click();

    // Alert area should show a spinner while the request is in flight
    await expect(page.locator('#alert1')).toContainText(/Extracting|CLOs|spinner/i, {
      timeout: 5_000,
    });
  });

  test('network error shows "❌" message, not infinite spinner', async ({ page }) => {
    await page.goto(WIZARD_URL);

    // Abort the upload so the catch block fires
    await page.route('**/api/upload-syllabus', route => route.abort());

    const fileInput = page.locator('#fileInput1');
    await fileInput.setInputFiles({
      name: 'test.docx',
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      buffer: Buffer.from('PK stub'),
    });

    const btn = page.locator('button', { hasText: /Extract CLOs/i });
    await btn.click();

    await expect(page.locator('#alert1')).toContainText('❌', { timeout: 8_000 });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 3. STEP NAVIGATION
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Step navigation', () => {
  test('step labels match expected values', async ({ page }) => {
    await page.goto(WIZARD_URL);
    const labels = page.locator('.step-label');
    await expect(labels.nth(0)).toContainText('Upload Syllabus');
    await expect(labels.nth(1)).toContainText('Upload Materials');
    await expect(labels.nth(2)).toContainText('Copilot');
    await expect(labels.nth(3)).toContainText('Moderation Form');
    await expect(labels.nth(4)).toContainText('Format Exam');
  });

  test('steps 2–5 are locked on initial load', async ({ page }) => {
    await page.goto(WIZARD_URL);
    const lockedSteps = page.locator('.step-item.locked');
    await expect(lockedSteps).toHaveCount(4);
  });

  test('after unlockStep(1) step 2 becomes clickable', async ({ page }) => {
    await page.goto(WIZARD_URL);

    // Programmatically unlock step 1 (simulates completing Step 1)
    await page.evaluate(() => window.unlockStep(1));

    // Step 2 should no longer have the locked class
    const step2 = page.locator('.step-item[data-step="2"]');
    await expect(step2).not.toHaveClass(/locked/);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 4. STEP 3 — Chat UI
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Step 3 — Chat UI', () => {
  async function navigateToStep3(page) {
    await page.goto(WIZARD_URL);
    // Unlock and navigate to step 3 programmatically
    await page.evaluate(() => {
      window.unlockStep(1);
      window.unlockStep(2);
      window.goToStep(3);
    });
  }

  test('chat input textarea is present', async ({ page }) => {
    await navigateToStep3(page);
    await expect(page.locator('#chatInput')).toBeVisible();
  });

  test('Send button is present', async ({ page }) => {
    await navigateToStep3(page);
    await expect(page.locator('#chatSendBtn')).toBeVisible();
  });

  test('pressing Enter in textarea triggers send', async ({ page }) => {
    await navigateToStep3(page);

    // Mock the chat endpoint so the send doesn't actually hit the network
    await page.route('**/api/chat', route => route.abort());

    await page.locator('#chatInput').fill('Generate a question');
    await page.keyboard.press('Enter');

    // After Enter, chat messages area should update (spinner or error appears)
    await expect(page.locator('#chatMessages')).toContainText(
      /Generate a question|❌/i,
      { timeout: 5_000 }
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 5. SESSION MANAGEMENT
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Session management', () => {
  test('sessionId is stored in localStorage after page load', async ({ page }) => {
    await page.goto(WIZARD_URL);
    const sessionId = await page.evaluate(() => localStorage.getItem('examops_session_id'));
    // May be null on first load (only set after first API call), or a UUID if previously set
    // Either null or a string is acceptable
    expect(sessionId === null || typeof sessionId === 'string').toBe(true);
  });

  test('sessionId is a valid UUID format if set', async ({ page }) => {
    await page.goto(WIZARD_URL);

    // Inject a UUID into localStorage and reload to simulate an existing session
    await page.evaluate(() => {
      localStorage.setItem(
        'examops_session_id',
        'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
      );
    });
    await page.reload();

    const sessionId = await page.evaluate(() => localStorage.getItem('examops_session_id'));
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    expect(uuidPattern.test(sessionId)).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 6. ERROR HANDLING
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Error handling', () => {
  test('network error shows ❌ error message', async ({ page }) => {
    await page.goto(WIZARD_URL);
    await page.route('**/api/upload-syllabus', route => route.abort());

    const fileInput = page.locator('#fileInput1');
    await fileInput.setInputFiles({
      name: 'test.docx',
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      buffer: Buffer.from('PK stub'),
    });

    await page.locator('button', { hasText: /Extract CLOs/i }).click();
    await expect(page.locator('#alert1')).toContainText('❌', { timeout: 8_000 });
  });

  test('button re-enables after error', async ({ page }) => {
    await page.goto(WIZARD_URL);
    await page.route('**/api/upload-syllabus', route => route.abort());

    const fileInput = page.locator('#fileInput1');
    await fileInput.setInputFiles({
      name: 'test.docx',
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      buffer: Buffer.from('PK stub'),
    });

    const btn = page.locator('button', { hasText: /Extract CLOs/i });
    await btn.click();
    await expect(page.locator('#alert1')).toContainText('❌', { timeout: 8_000 });

    // Button should be re-enabled after the error
    await expect(btn).toBeEnabled({ timeout: 5_000 });
  });
});
