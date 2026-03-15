import { test, expect } from '../fixtures';

/**
 * US-001: User Registration via Google OAuth
 * Priority: P0 - CRITICAL
 * 
 * As a prospective buyer
 * I want to sign up using my Google account
 * So that I can quickly access the platform
 */
test.describe('US-001: User Registration via Google OAuth', () => {
  
  test('should display Google OAuth button on landing page', async ({ page }) => {
    await page.goto('/');
    
    // Verify landing page loads
    await expect(page).toHaveURL('/');
    
    // Verify Google OAuth button visible
    const googleButton = page.locator('button:has-text("Get Started with Google"), button:has-text("Sign in with Google")');
    await expect(googleButton).toBeVisible();
    await expect(googleButton).toBeEnabled();
  });

  test('should initiate OAuth flow when button clicked', async ({ page, context }) => {
    await page.goto('/');
    
    // Mock the OAuth popup
    const [popup] = await Promise.all([
      context.waitForEvent('page'),
      page.click('button:has-text("Get Started with Google")')
    ]);
    
    // Verify popup opened to Google OAuth
    await expect(popup).toHaveURL(/accounts\.google\.com/);
  });

  test('should complete OAuth and create user session', async ({ page }) => {
    // Mock successful OAuth callback
    await page.goto('/auth/callback?code=mock_auth_code&state=mock_state');
    
    // Should redirect to onboarding or dashboard
    await page.waitForURL(/\/(onboarding|dashboard)/);
    
    // Verify token stored
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
    
    // Verify user data stored
    const user = await page.evaluate(() => localStorage.getItem('user'));
    expect(user).toBeTruthy();
    const userData = JSON.parse(user!);
    expect(userData.email).toBeTruthy();
    expect(userData.name).toBeTruthy();
  });

  test('should redirect new users to onboarding', async ({ page }) => {
    // Mock new user OAuth completion
    await page.goto('/auth/callback?code=new_user_code');
    
    // Should redirect to onboarding for first-time users
    await page.waitForURL(/\/onboarding/);
    
    // Verify onboarding chat visible
    await expect(page.locator('[data-testid="onboarding-chat"]')).toBeVisible();
  });

  test('should redirect returning users to dashboard', async ({ page }) => {
    // Mock returning user OAuth completion
    await page.goto('/auth/callback?code=returning_user_code');
    
    // Should redirect to dashboard for returning users
    await page.waitForURL(/\/dashboard/);
    
    // Verify dashboard visible
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
  });
});
