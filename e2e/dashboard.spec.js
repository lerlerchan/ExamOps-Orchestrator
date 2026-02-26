// @ts-check
/**
 * ExamOps Dashboard — Playwright e2e tests
 *
 * Server: python -m http.server 8765 --directory frontend (started by playwright.config.js)
 * URL:    http://localhost:8765/dashboard.html
 */

const { test, expect } = require('@playwright/test');

const URL = '/dashboard.html';

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Speed up the pipeline JS timers so tests don't wait 8 seconds. */
async function speedUpTimers(page) {
  await page.addInitScript(() => {
    // Replace sleep() with near-instant resolution
    window.__origSleep = window.sleep;
    window.sleep = (ms) => new Promise(r => setTimeout(r, Math.min(ms, 10)));
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// 1. PAGE LOAD
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Page load', () => {
  test('has correct title', async ({ page }) => {
    await page.goto(URL);
    await expect(page).toHaveTitle(/ExamOps/i);
  });

  test('shows logo mark and brand name', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.logo-mark')).toHaveText('EO');
    await expect(page.locator('.logo-text')).toContainText('ExamOps');
  });

  test('shows Azure online status indicator', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.header-status')).toContainText('Azure Online');
  });

  test('renders page title with italic "Examination"', async ({ page }) => {
    await page.goto(URL);
    const h1 = page.locator('.page-title');
    await expect(h1).toContainText('Format');
    await expect(h1).toContainText('Examination');
  });

  test('renders page subtitle', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.page-sub')).toContainText('.docx');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 2. THEME SWITCHER
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Theme switcher', () => {
  test('defaults to dark theme (saved in localStorage)', async ({ page }) => {
    await page.goto(URL);
    const theme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    // First visit defaults to dark; or whatever localStorage has
    expect(['dark', 'light']).toContain(theme);
  });

  test('shows both Light and Dark pill buttons', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('button.theme-pill[data-mode="light"]')).toBeVisible();
    await expect(page.locator('button.theme-pill[data-mode="dark"]')).toBeVisible();
  });

  test('clicking Light pill sets data-theme=light', async ({ page }) => {
    await page.goto(URL);
    await page.locator('button.theme-pill[data-mode="light"]').click();
    const theme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    expect(theme).toBe('light');
  });

  test('clicking Dark pill sets data-theme=dark', async ({ page }) => {
    await page.goto(URL);
    await page.locator('button.theme-pill[data-mode="light"]').click();
    await page.locator('button.theme-pill[data-mode="dark"]').click();
    const theme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    expect(theme).toBe('dark');
  });

  test('theme persists in localStorage after switch', async ({ page }) => {
    await page.goto(URL);
    await page.locator('button.theme-pill[data-mode="light"]').click();
    const stored = await page.evaluate(() => localStorage.getItem('examops-theme'));
    expect(stored).toBe('light');
  });

  test('slider element moves when theme changes', async ({ page }) => {
    await page.goto(URL);
    await page.locator('button.theme-pill[data-mode="dark"]').click();
    const darkLeft = await page.locator('#theme-slider').evaluate(el => el.style.left);

    await page.locator('button.theme-pill[data-mode="light"]').click();
    const lightLeft = await page.locator('#theme-slider').evaluate(el => el.style.left);

    // Slider position must differ between modes
    expect(darkLeft).not.toBe(lightLeft);
  });

  test('switcher has aria-label for accessibility', async ({ page }) => {
    await page.goto(URL);
    const label = await page.locator('#theme-switcher').getAttribute('aria-label');
    expect(label).toMatch(/theme/i);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 3. STAT CARDS
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Stat cards', () => {
  test('shows 4 stat cards', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.stat-card')).toHaveCount(4);
  });

  test('Jobs Today card shows 47', async ({ page }) => {
    await page.goto(URL);
    const cards = page.locator('.stat-card');
    await expect(cards.nth(0)).toContainText('47');
    await expect(cards.nth(0)).toContainText('Jobs Today');
  });

  test('Avg Compliance card shows 94%', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.stat-card').nth(1)).toContainText('94');
  });

  test('Avg Proc Time card shows 18s', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.stat-card').nth(2)).toContainText('18');
  });

  test('Failed Jobs card shows 3', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.stat-card').nth(3)).toContainText('3');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 4. SIDEBAR NAVIGATION
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Sidebar navigation', () => {
  test('Dashboard nav item is active by default', async ({ page }) => {
    await page.goto(URL);
    const active = page.locator('.nav-item.active');
    await expect(active).toBeVisible();
    await expect(active).toContainText('Dashboard');
  });

  test('My Documents badge shows 14', async ({ page }) => {
    await page.goto(URL);
    const badges = page.locator('.nav-badge');
    await expect(badges.first()).toContainText('14');
  });

  test('Batch Queue badge shows 3', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.nav-badge').nth(1)).toContainText('3');
  });

  test('user avatar shows initials AL', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.avatar')).toContainText('AL');
  });

  test('user name shows Aileen Lee', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.user-name')).toContainText('Aileen Lee');
  });

  test('user role shows Exam Coordinator', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.user-role')).toContainText('Coordinator');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 5. UPLOAD ZONE
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Upload zone', () => {
  test('upload zone is visible', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#drop-zone')).toBeVisible();
  });

  test('shows drop instruction text', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.upload-title')).toContainText('Drop your exam paper');
  });

  test('shows .docx constraint', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#drop-zone')).toContainText('.docx');
  });

  test('shows file size constraint', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#drop-zone')).toContainText('50 MB');
  });

  test('file input accepts only .docx', async ({ page }) => {
    await page.goto(URL);
    const accept = await page.locator('#file-input').getAttribute('accept');
    expect(accept).toBe('.docx');
  });

  test('Format Document button is hidden by default', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#format-btn')).toBeHidden();
  });

  test('simulating file selection shows Format button', async ({ page }) => {
    await page.goto(URL);
    // Directly call processFile() via JS to simulate a file being chosen
    await page.evaluate(() => {
      window.processFile({ name: 'TestExam.docx', size: 204800 });
    });
    await expect(page.locator('#format-btn')).toBeVisible();
  });

  test('upload title updates to filename after selection', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => {
      window.processFile({ name: 'MidtermPaper.docx', size: 102400 });
    });
    await expect(page.locator('.upload-title')).toContainText('MidtermPaper.docx');
  });

  test('drop zone shows "drag-over" class on dragover event', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => {
      const dz = document.getElementById('drop-zone');
      const ev = new DragEvent('dragover', { bubbles: true, cancelable: true });
      dz.dispatchEvent(ev);
    });
    const cls = await page.locator('#drop-zone').getAttribute('class');
    expect(cls).toContain('drag-over');
  });

  test('drag-over class removed on dragleave', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => {
      const dz = document.getElementById('drop-zone');
      dz.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true }));
      dz.dispatchEvent(new DragEvent('dragleave', { bubbles: true }));
    });
    const cls = await page.locator('#drop-zone').getAttribute('class');
    expect(cls).not.toContain('drag-over');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 6. TEMPLATE PICKER
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Template picker', () => {
  test('shows 4 template options', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.template-item')).toHaveCount(4);
  });

  test('SUC Standard 2025 is selected by default', async ({ page }) => {
    await page.goto(URL);
    const selected = page.locator('.template-item.selected');
    await expect(selected).toBeVisible();
    await expect(selected).toContainText('SUC Standard 2025');
  });

  test('SUC Standard has Default tag', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.template-item.selected .template-tag')).toContainText('Default');
  });

  test('clicking another template selects it', async ({ page }) => {
    await page.goto(URL);
    const engineering = page.locator('.template-item').filter({ hasText: 'Engineering Faculty' });
    await engineering.click();
    await expect(engineering).toHaveClass(/selected/);
  });

  test('clicking a template deselects the previous one', async ({ page }) => {
    await page.goto(URL);
    await page.locator('.template-item').filter({ hasText: 'Engineering Faculty' }).click();
    const suc = page.locator('.template-item').filter({ hasText: 'SUC Standard 2025' });
    await expect(suc).not.toHaveClass(/selected/);
  });

  test('only one template is selected at a time', async ({ page }) => {
    await page.goto(URL);
    await page.locator('.template-item').filter({ hasText: 'Science' }).click();
    await expect(page.locator('.template-item.selected')).toHaveCount(1);
  });

  test('all four template names are visible', async ({ page }) => {
    await page.goto(URL);
    const names = ['SUC Standard 2025', 'Engineering Faculty', 'Business', 'Science'];
    for (const name of names) {
      await expect(page.locator('.template-item').filter({ hasText: name })).toBeVisible();
    }
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 7. JOB HISTORY TABLE
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Job history table', () => {
  test('table renders 8 rows by default', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#job-tbody tr')).toHaveCount(8);
  });

  test('first row shows JOB-0091', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#job-tbody tr').first()).toContainText('JOB-0091');
  });

  test('shows Complete badges for done jobs', async ({ page }) => {
    await page.goto(URL);
    const done = page.locator('#job-tbody .badge.done');
    await expect(done.first()).toContainText('Complete');
  });

  test('shows Running badge for in-progress job', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#job-tbody .badge.running')).toContainText('Running');
  });

  test('shows Failed badge for failed job', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#job-tbody .badge.failed')).toContainText('Failed');
  });

  test('score pills show correct values', async ({ page }) => {
    await page.goto(URL);
    // JOB-0091 should show 97%
    const firstRow = page.locator('#job-tbody tr').first();
    await expect(firstRow).toContainText('97%');
  });

  test('search filters rows by filename', async ({ page }) => {
    await page.goto(URL);
    await page.locator('.search-input').fill('MATH');
    await page.waitForTimeout(100);
    const rows = page.locator('#job-tbody tr');
    await expect(rows).toHaveCount(1);
    await expect(rows.first()).toContainText('MATH2301');
  });

  test('search filters rows by job ID', async ({ page }) => {
    await page.goto(URL);
    await page.locator('.search-input').fill('JOB-0086');
    await page.waitForTimeout(100);
    await expect(page.locator('#job-tbody tr')).toHaveCount(1);
  });

  test('clearing search restores all 8 rows', async ({ page }) => {
    await page.goto(URL);
    await page.locator('.search-input').fill('MATH');
    await page.waitForTimeout(100);
    await page.locator('.search-input').fill('');
    await page.waitForTimeout(100);
    await expect(page.locator('#job-tbody tr')).toHaveCount(8);
  });

  test('search with no match shows 0 rows', async ({ page }) => {
    await page.goto(URL);
    await page.locator('.search-input').fill('ZZZNOMATCH999');
    await page.waitForTimeout(100);
    await expect(page.locator('#job-tbody tr')).toHaveCount(0);
  });

  test('table has correct column headers', async ({ page }) => {
    await page.goto(URL);
    const headers = page.locator('#job-table thead th');
    await expect(headers).toHaveCount(8);
    await expect(headers.filter({ hasText: 'Job ID' })).toBeVisible();
    await expect(headers.filter({ hasText: 'Status' })).toBeVisible();
    await expect(headers.filter({ hasText: 'Score' })).toBeVisible();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 8. TOAST NOTIFICATIONS
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Toast notifications', () => {
  test('toast appears when showToast() is called', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => window.showToast('Test Title', 'Test sub message'));
    await expect(page.locator('.toast.show')).toBeVisible();
  });

  test('toast shows correct title', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => window.showToast('Hello World', 'A subtitle'));
    await expect(page.locator('.toast-title')).toContainText('Hello World');
  });

  test('toast shows correct subtitle', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => window.showToast('Title', 'Sub message here'));
    await expect(page.locator('.toast-sub')).toContainText('Sub message here');
  });

  test('success toast has success class', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => window.showToast('OK', 'All good', 'success'));
    await expect(page.locator('.toast.success')).toBeVisible();
  });

  test('error toast has error class', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => window.showToast('Err', 'Something failed', 'error'));
    await expect(page.locator('.toast.error')).toBeVisible();
  });

  test('View History button triggers a toast', async ({ page }) => {
    await page.goto(URL);
    await page.getByRole('button', { name: /View History/i }).click();
    await expect(page.locator('.toast.show')).toBeVisible();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 9. FORMATTING PIPELINE (full flow with speedup)
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Formatting pipeline', () => {
  test.setTimeout(30_000);   // pipeline takes ~8s normally, ~2s with speedup

  test('pipeline card is hidden before formatting starts', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('#pipeline-card')).not.toHaveClass(/visible/);
  });

  test('results section is hidden before formatting starts', async ({ page }) => {
    await page.goto(URL);
    const style = await page.locator('#results-section').getAttribute('style');
    expect(style).toContain('display:none');
  });

  test('calling startFormatting() shows upload overlay', async ({ page }) => {
    await page.goto(URL);
    // Use a MutationObserver inside the page to detect the transient overlay.
    // We await startFormatting() inside evaluate so there's no floating promise.
    const wasVisible = await page.evaluate(async () => {
      const overlay = document.getElementById('upload-overlay');
      let seen = false;
      const observer = new MutationObserver(() => {
        if (overlay.classList.contains('visible')) seen = true;
      });
      observer.observe(overlay, { attributes: true, attributeFilter: ['class'] });
      await window.startFormatting();
      observer.disconnect();
      return seen;
    }, { timeout: 25000 });
    expect(wasVisible).toBe(true);
  });

  test('pipeline card becomes visible after upload completes', async ({ page }) => {
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#pipeline-card')).toHaveClass(/visible/, { timeout: 20000 });
  });

  test('pipeline filename shows in the card', async ({ page }) => {
    await page.goto(URL);
    // processFile() sets the script-scoped `let selectedFile` variable correctly.
    // Setting window.selectedFile would not affect the let binding.
    await page.evaluate(() => {
      window.processFile({ name: 'CS3101_Final.docx', size: 102400 });
      window.startFormatting();
    });
    await expect(page.locator('#pipeline-card')).toHaveClass(/visible/, { timeout: 20000 });
    await expect(page.locator('#pipeline-filename')).toContainText('CS3101_Final.docx', { timeout: 8000 });
  });

  test('pipeline percentage reaches 100%', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#pipeline-pct')).toHaveText('100%', { timeout: 15000 });
  });

  test('all 6 step nodes show done (✓) after completion', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    // Wait for pipeline to complete
    await expect(page.locator('#pipeline-pct')).toHaveText('100%', { timeout: 15000 });
    // All 6 step nodes should now have .done class and show ✓
    for (let i = 0; i < 6; i++) {
      await expect(page.locator(`#step-${i}`)).toHaveClass(/done/, { timeout: 3000 });
    }
  });

  test('pipeline log contains entries', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#pipeline-pct')).toHaveText('100%', { timeout: 15000 });
    const logLines = await page.locator('#pipeline-log .log-line').count();
    expect(logLines).toBeGreaterThan(0);
  });

  test('results section becomes visible after pipeline completes', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
  });

  test('compliance gauge shows 94% after completion', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#gauge-pct')).toHaveText('94%', { timeout: 20000 });
  });

  test('fix counters are populated after completion', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
    // Wait for counter animations to finish (fix-numbering should reach 8)
    await expect(page.locator('#fix-numbering')).toHaveText('8', { timeout: 5000 });
    await expect(page.locator('#fix-spacing')).toHaveText('4', { timeout: 5000 });
  });

  test('diff report is visible in results', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('.diff-body')).toBeVisible();
  });

  test('diff report contains deletion lines', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('.diff-line.del').first()).toBeVisible();
  });

  test('diff report contains addition lines', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('.diff-line.add').first()).toBeVisible();
  });

  test('Download .docx button is visible in results', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
    await expect(page.getByRole('button', { name: /Download .docx/i })).toBeVisible();
  });

  test('Post to Teams button is visible in results', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
    await expect(page.getByRole('button', { name: /Post to Teams/i })).toBeVisible();
  });

  test('completion toast fires after pipeline finishes', async ({ page }) => {
    await speedUpTimers(page);
    await page.goto(URL);
    await page.evaluate(() => window.startFormatting());
    await expect(page.locator('#results-section')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('.toast.show')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('.toast-title')).toContainText('Formatting complete');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 10. RESPONSIVE LAYOUT
// ══════════════════════════════════════════════════════════════════════════════

test.describe('Layout & accessibility', () => {
  test('shell grid is rendered', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('.shell')).toBeVisible();
  });

  test('aside sidebar is rendered', async ({ page }) => {
    await page.goto(URL);
    await expect(page.locator('aside')).toBeVisible();
  });

  test('header is sticky (z-index set)', async ({ page }) => {
    await page.goto(URL);
    const zIndex = await page.locator('header').evaluate(el => getComputedStyle(el).zIndex);
    expect(Number(zIndex)).toBeGreaterThanOrEqual(100);
  });

  test('page has no horizontal overflow at 1440px', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(URL);
    const overflow = await page.evaluate(() => document.body.scrollWidth <= window.innerWidth);
    expect(overflow).toBe(true);
  });

  test('theme switcher has role="group"', async ({ page }) => {
    await page.goto(URL);
    const role = await page.locator('#theme-switcher').getAttribute('role');
    expect(role).toBe('group');
  });
});
