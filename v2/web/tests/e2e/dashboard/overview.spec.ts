import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('dashboard page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard');
    expect(response?.status()).toBe(200);
  });

  test('backlog page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/backlog');
    expect(response?.status()).toBe(200);
  });

  test('pipeline page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/pipeline');
    expect(response?.status()).toBe(200);
  });

  test('crm page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/crm');
    expect(response?.status()).toBe(200);
  });

  test('settings page loads', async ({ page }) => {
    const response = await page.goto('http://localhost:3000/dashboard/settings');
    expect(response?.status()).toBe(200);
  });
});
