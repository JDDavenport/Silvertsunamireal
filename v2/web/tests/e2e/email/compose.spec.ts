import { test, expect } from '@playwright/test';

test.describe('Email', () => {
  test('settings page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/settings');
    expect(response?.status()).toBe(200);
  });
});
