import { test, expect } from '../fixtures';

/**
 * Settings & Configuration: US-033 to US-036
 * Priority: P1 - IMPORTANT
 */
test.describe('Settings & Configuration (US-033 to US-036)', () => {
  
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/settings');
  });

  /**
   * US-033: Configure Email Limits
   */
  test('US-033: should display email limit slider', async ({ settingsPage }) => {
    // Verify settings container
    await expect(settingsPage.locator('[data-testid="settings"]')).toBeVisible();
    
    // Verify email limit section
    await expect(settingsPage.locator('[data-testid="email-limit-section"]')).toBeVisible();
    
    // Verify slider
    await expect(settingsPage.locator('[data-testid="email-limit-slider"]')).toBeVisible();
  });

  test('US-033: should display current email limit', async ({ settingsPage }) => {
    const limitDisplay = await settingsPage.locator('[data-testid="email-limit-value"]').textContent();
    expect(limitDisplay).toContain('emails/day');
    
    // Should be numeric
    const limit = parseInt(limitDisplay?.match(/\d+/)?.[0] || '0');
    expect(limit).toBeGreaterThanOrEqual(5);
    expect(limit).toBeLessThanOrEqual(100);
  });

  test('US-033: should update email limit', async ({ settingsPage }) => {
    // Move slider
    await settingsPage.locator('[data-testid="email-limit-slider"]').fill('25');
    
    // Verify display updated
    await expect(settingsPage.locator('[data-testid="email-limit-value"]')).toContainText('25');
  });

  test('US-033: should save email limit', async ({ settingsPage }) => {
    // Set limit
    await settingsPage.locator('[data-testid="email-limit-slider"]').fill('30');
    
    // Click save
    await settingsPage.locator('[data-testid="save-settings-btn"]').click();
    
    // Verify success
    await expect(settingsPage.locator('[data-testid="success-toast"]')).toContainText('saved');
    
    // Verify persisted after reload
    await settingsPage.reload();
    await expect(settingsPage.locator('[data-testid="email-limit-value"]')).toContainText('30');
  });

  /**
   * US-034: Configure Auto-Approve
   */
  test('US-034: should display auto-approve section', async ({ settingsPage }) => {
    await expect(settingsPage.locator('[data-testid="auto-approve-section"]')).toBeVisible();
  });

  test('US-034: should display threshold slider', async ({ settingsPage }) => {
    await expect(settingsPage.locator('[data-testid="auto-approve-threshold"]')).toBeVisible();
  });

  test('US-034: should show current threshold', async ({ settingsPage }) => {
    const thresholdText = await settingsPage.locator('[data-testid="threshold-value"]').textContent();
    
    // Should show "Manual approval" if 0, or "Score >= X" if set
    expect(thresholdText).toMatch(/Manual approval|Score/);
  });

  test('US-034: should update auto-approve threshold', async ({ settingsPage }) => {
    // Set threshold to 80
    await settingsPage.locator('[data-testid="auto-approve-threshold"]').fill('80');
    
    // Verify display updated
    await expect(settingsPage.locator('[data-testid="threshold-value"]')).toContainText('Score ≥ 80');
  });

  test('US-034: should disable auto-approve with threshold 0', async ({ settingsPage }) => {
    // Set to 0
    await settingsPage.locator('[data-testid="auto-approve-threshold"]').fill('0');
    
    // Should show "Manual approval"
    await expect(settingsPage.locator('[data-testid="threshold-value"]')).toContainText('Manual');
  });

  test('US-034: should save auto-approve settings', async ({ settingsPage }) => {
    await settingsPage.locator('[data-testid="auto-approve-threshold"]').fill('75');
    await settingsPage.locator('[data-testid="save-settings-btn"]').click();
    
    await expect(settingsPage.locator('[data-testid="success-toast"]')).toContainText('saved');
  });

  /**
   * US-035: Configure Discovery Frequency
   */
  test('US-035: should display discovery schedule options', async ({ settingsPage }) => {
    await expect(settingsPage.locator('[data-testid="discovery-schedule-section"]')).toBeVisible();
    
    // Verify all options
    await expect(settingsPage.locator('[data-testid="schedule-hourly"]')).toBeVisible();
    await expect(settingsPage.locator('[data-testid="schedule-daily"]')).toBeVisible();
    await expect(settingsPage.locator('[data-testid="schedule-weekly"]')).toBeVisible();
    await expect(settingsPage.locator('[data-testid="schedule-manual"]')).toBeVisible();
  });

  test('US-035: should select discovery frequency', async ({ settingsPage }) => {
    // Click daily
    await settingsPage.locator('[data-testid="schedule-daily"]').click();
    
    // Verify selected
    await expect(settingsPage.locator('[data-testid="schedule-daily"]')).toHaveClass(/selected|active/);
  });

  test('US-035: should save discovery schedule', async ({ settingsPage }) => {
    await settingsPage.locator('[data-testid="schedule-daily"]').click();
    await settingsPage.locator('[data-testid="save-settings-btn"]').click();
    
    await expect(settingsPage.locator('[data-testid="success-toast"]')).toContainText('saved');
  });

  /**
   * US-036: Configure Notifications
   */
  test('US-036: should display notification preferences', async ({ settingsPage }) => {
    await expect(settingsPage.locator('[data-testid="notifications-section"]')).toBeVisible();
    
    // Verify checkboxes
    await expect(settingsPage.locator('[data-testid="notify-new-leads"]')).toBeVisible();
    await expect(settingsPage.locator('[data-testid="notify-email-replies"]')).toBeVisible();
    await expect(settingsPage.locator('[data-testid="notify-daily-summary"]')).toBeVisible();
  });

  test('US-036: should toggle notification preferences', async ({ settingsPage }) => {
    // Toggle new leads
    await settingsPage.locator('[data-testid="notify-new-leads"]').check();
    await expect(settingsPage.locator('[data-testid="notify-new-leads"]')).toBeChecked();
    
    // Toggle email replies
    await settingsPage.locator('[data-testid="notify-email-replies"]').check();
    await expect(settingsPage.locator('[data-testid="notify-email-replies"]')).toBeChecked();
    
    // Toggle daily summary
    await settingsPage.locator('[data-testid="notify-daily-summary"]').uncheck();
    await expect(settingsPage.locator('[data-testid="notify-daily-summary"]"')).not.toBeChecked();
  });

  test('US-036: should configure notification email', async ({ settingsPage }) => {
    const emailInput = settingsPage.locator('[data-testid="notification-email"]');
    await expect(emailInput).toBeVisible();
    
    // Clear and enter email
    await emailInput.fill('');
    await emailInput.fill('notifications@example.com');
    
    await expect(emailInput).toHaveValue('notifications@example.com');
  });

  test('US-036: should save notification settings', async ({ settingsPage }) => {
    await settingsPage.locator('[data-testid="notify-new-leads"]').check();
    await settingsPage.locator('[data-testid="notification-email"]').fill('test@example.com');
    await settingsPage.locator('[data-testid="save-settings-btn"]').click();
    
    await expect(settingsPage.locator('[data-testid="success-toast"]')).toContainText('saved');
  });
});
