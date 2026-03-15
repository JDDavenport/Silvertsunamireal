import { test, expect } from '@playwright/test';

test.describe('CRM', () => {
  test('crm page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/crm');
    expect(response?.status()).toBe(200);
  });
});
