import { test, expect } from '@playwright/test';

test.describe('Import', () => {
  test('dashboard loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard');
    expect(response?.status()).toBe(200);
  });
});
