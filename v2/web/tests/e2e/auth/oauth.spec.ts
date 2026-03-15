import { test, expect } from '@playwright/test';

/**
 * US-001: User Registration via Google OAuth
 * Priority: P0 - CRITICAL
 */
test.describe('US-001: User Registration via Google OAuth', () => {
  
  test('landing page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/');
    expect(response?.status()).toBe(200);
  });

  test('onboarding page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/onboarding');
    expect(response?.status()).toBe(200);
  });

  test('dashboard page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard');
    expect(response?.status()).toBe(200);
  });
});
