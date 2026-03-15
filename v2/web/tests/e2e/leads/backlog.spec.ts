import { test, expect } from '@playwright/test';

test.describe('Leads', () => {
  test('backlog page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/backlog');
    expect(response?.status()).toBe(200);
  });
});
