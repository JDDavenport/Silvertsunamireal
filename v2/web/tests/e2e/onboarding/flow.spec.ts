import { test, expect } from '../fixtures';

/**
 * Onboarding User Stories: US-002 through US-009
 * Priority: P0 - CRITICAL
 * 
 * Complete 7-question onboarding flow
 */
test.describe('Onboarding Flow (US-002 to US-009)', () => {
  
  test.beforeEach(async ({ page }) => {
    // Mock authenticated new user
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user', JSON.stringify({
        id: 'test-user-id',
        email: 'test@example.com',
        name: 'Test User'
      }));
    });
    await page.goto('/onboarding');
    await expect(page.locator('[data-testid="onboarding-chat"]')).toBeVisible();
  });

  /**
   * US-002: Professional Background
   */
  test('US-002: should capture professional background', async ({ page }) => {
    // Verify first question about background
    await expect(page.locator('[data-testid="chat-message"]')).toContainText('professional background');
    
    // Type response
    const input = page.locator('[data-testid="chat-input"]');
    await input.fill('10 years in software engineering, last 3 as CTO at a SaaS startup');
    await input.press('Enter');
    
    // Verify response sent and acknowledged
    await expect(page.locator('[data-testid="user-message"]')).toContainText('software engineering');
    await expect(page.locator('[data-testid="assistant-message"]').nth(1)).toBeVisible();
  });

  /**
   * US-003: Business Experience
   */
  test('US-003: should capture business ownership experience', async ({ page }) => {
    // Complete background first
    await page.locator('[data-testid="chat-input"]').fill('Software background');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    await page.waitForTimeout(500);
    
    // Verify question about business experience
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText(/business before|first acquisition/i);
    
    // Select first acquisition
    await page.locator('[data-testid="chat-input"]').fill('This would be my first acquisition');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    
    // Verify acknowledged
    await expect(page.locator('[data-testid="user-message"]').last()).toContainText('first acquisition');
  });

  /**
   * US-004: Budget Range
   */
  test('US-004: should capture budget range', async ({ page }) => {
    // Navigate through first two questions
    await page.locator('[data-testid="chat-input"]').fill('Software background');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    await page.waitForTimeout(500);
    
    await page.locator('[data-testid="chat-input"]').fill('First acquisition');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    await page.waitForTimeout(500);
    
    // Verify budget question
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText(/budget|range|\$/i);
    
    // Enter budget
    await page.locator('[data-testid="chat-input"]').fill('$1M to $5M');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    
    // Verify parsed
    await expect(page.locator('[data-testid="user-message"]').last()).toContainText('$1M');
  });

  /**
   * US-005: Industry Preferences
   */
  test('US-005: should capture industry preferences', async ({ page }) => {
    // Navigate through first 3 questions
    for (let i = 0; i < 3; i++) {
      await page.locator('[data-testid="chat-input"]').fill('Test response');
      await page.locator('[data-testid="chat-input"]').press('Enter');
      await page.waitForTimeout(500);
    }
    
    // Verify industry question
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText(/industr|sector/i);
    
    // Enter industries
    await page.locator('[data-testid="chat-input"]').fill('Technology, Healthcare, and Business Services');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    
    // Verify response
    await expect(page.locator('[data-testid="user-message"]').last()).toContainText('Technology');
  });

  /**
   * US-006: Location Preferences
   */
  test('US-006: should capture location preferences', async ({ page }) => {
    // Navigate through first 4 questions
    for (let i = 0; i < 4; i++) {
      await page.locator('[data-testid="chat-input"]').fill('Test response');
      await page.locator('[data-testid="chat-input"]').press('Enter');
      await page.waitForTimeout(500);
    }
    
    // Verify location question
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText(/location|geographic|area/i);
    
    // Enter locations
    await page.locator('[data-testid="chat-input"]').fill('Utah, Colorado, and Arizona');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    
    // Verify response
    await expect(page.locator('[data-testid="user-message"]').last()).toContainText('Utah');
  });

  /**
   * US-007: Business Values
   */
  test('US-007: should capture business values/priorities', async ({ page }) => {
    // Navigate through first 5 questions
    for (let i = 0; i < 5; i++) {
      await page.locator('[data-testid="chat-input"]').fill('Test response');
      await page.locator('[data-testid="chat-input"]').press('Enter');
      await page.waitForTimeout(500);
    }
    
    // Verify values question
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText(/important|value|priorit|looking for/i);
    
    // Enter values
    await page.locator('[data-testid="chat-input"]').fill('Steady cash flow, established team, growth potential');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    
    // Verify response
    await expect(page.locator('[data-testid="user-message"]').last()).toContainText('cash flow');
  });

  /**
   * US-008: Timeline
   */
  test('US-008: should capture acquisition timeline', async ({ page }) => {
    // Navigate through first 6 questions
    for (let i = 0; i < 6; i++) {
      await page.locator('[data-testid="chat-input"]').fill('Test response');
      await page.locator('[data-testid="chat-input"]').press('Enter');
      await page.waitForTimeout(500);
    }
    
    // Verify timeline question
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText(/timeline|when|6 months|year/i);
    
    // Enter timeline
    await page.locator('[data-testid="chat-input"]').fill('Within 6 months');
    await page.locator('[data-testid="chat-input"]').press('Enter');
    
    // Verify response
    await expect(page.locator('[data-testid="user-message"]').last()).toContainText('6 months');
  });

  /**
   * US-009: Profile Generation and Completion
   */
  test('US-009: should generate profile and complete onboarding', async ({ page }) => {
    // Complete all 7 questions
    const responses = [
      '10 years in software engineering',
      'First acquisition',
      '$1M to $5M',
      'Technology, Healthcare',
      'Utah, Colorado',
      'Cash flow and team',
      'Within 6 months'
    ];
    
    for (const response of responses) {
      await page.locator('[data-testid="chat-input"]').fill(response);
      await page.locator('[data-testid="chat-input"]').press('Enter');
      await page.waitForTimeout(600);
    }
    
    // Verify completion summary
    await expect(page.locator('[data-testid="completion-summary"]')).toBeVisible();
    await expect(page.locator('[data-testid="completion-summary"]')).toContainText('Technology');
    await expect(page.locator('[data-testid="completion-summary"]')).toContainText('$1M - $5M');
    await expect(page.locator('[data-testid="completion-summary"]')).toContainText('Utah');
    
    // Verify "Go to Dashboard" button
    const dashboardBtn = page.locator('button:has-text("Go to Dashboard")');
    await expect(dashboardBtn).toBeVisible();
    await expect(dashboardBtn).toBeEnabled();
    
    // Click dashboard button
    await dashboardBtn.click();
    
    // Verify redirect to dashboard
    await page.waitForURL(/\/dashboard/);
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
  });
});
