import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  // Authenticated page fixture
  authenticatedPage: async ({ page }, use) => {
    // Mock authentication for testing
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user', JSON.stringify({
        id: 'test-user-id',
        email: 'test@example.com',
        name: 'Test User'
      }));
    });
    await use(page);
  },
  
  // Dashboard page with pre-loaded state
  dashboardPage: async ({ authenticatedPage }, use) => {
    await authenticatedPage.goto('/dashboard');
    await expect(authenticatedPage.locator('[data-testid="dashboard"]')).toBeVisible();
    await use(authenticatedPage);
  },
  
  // Backlog page
  backlogPage: async ({ authenticatedPage }, use) => {
    await authenticatedPage.goto('/dashboard/backlog');
    await expect(authenticatedPage.locator('[data-testid="lead-backlog"]')).toBeVisible();
    await use(authenticatedPage);
  },
  
  // Pipeline page
  pipelinePage: async ({ authenticatedPage }, use) => {
    await authenticatedPage.goto('/dashboard/pipeline');
    await expect(authenticatedPage.locator('[data-testid="pipeline"]')).toBeVisible();
    await use(authenticatedPage);
  },
  
  // CRM page
  crmPage: async ({ authenticatedPage }, use) => {
    await authenticatedPage.goto('/dashboard/crm');
    await expect(authenticatedPage.locator('[data-testid="crm"]')).toBeVisible();
    await use(authenticatedPage);
  },
  
  // Settings page
  settingsPage: async ({ authenticatedPage }, use) => {
    await authenticatedPage.goto('/dashboard/settings');
    await expect(authenticatedPage.locator('[data-testid="settings"]')).toBeVisible();
    await use(authenticatedPage);
  }
});

export { expect };
