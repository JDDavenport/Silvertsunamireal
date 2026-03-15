import { test, expect } from '@playwright/test';

test.describe('Onboarding', () => {
  test('onboarding page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/onboarding');
    expect(response?.status()).toBe(200);
  });
});
