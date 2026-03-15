import { test, expect } from '@playwright/test';

test.describe('Pipeline', () => {
  test('pipeline page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/pipeline');
    expect(response?.status()).toBe(200);
  });
});
