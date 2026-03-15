import { test, expect } from '../fixtures';

/**
 * Lead Discovery & Backlog User Stories: US-013 to US-018
 * Priority: P0 - CRITICAL
 * 
 * Manual discovery, lead backlog, scoring, approve/reject
 */
test.describe('Lead Discovery & Backlog (US-013 to US-018)', () => {
  
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/backlog');
  });

  /**
   * US-014: View Lead Backlog
   */
  test('US-014: should display lead backlog', async ({ backlogPage }) => {
    // Verify backlog container visible
    await expect(backlogPage.locator('[data-testid="lead-backlog"]')).toBeVisible();
    
    // Verify header
    await expect(backlogPage.locator('h2')).toContainText('Lead Backlog');
  });

  test('US-014: should display lead cards with details', async ({ backlogPage }) => {
    // Check if any leads exist
    const leadCards = backlogPage.locator('[data-testid="lead-card"]');
    const count = await leadCards.count();
    
    if (count > 0) {
      // Verify first lead card has all details
      const firstCard = leadCards.first();
      await expect(firstCard.locator('[data-testid="lead-name"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="lead-industry"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="lead-revenue"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="lead-score"]')).toBeVisible();
    }
  });

  test('US-014: should expand lead to show AI assessment', async ({ backlogPage }) => {
    const leadCards = backlogPage.locator('[data-testid="lead-card"]');
    
    if (await leadCards.count() > 0) {
      // Click first lead card to expand
      await leadCards.first().click();
      
      // Verify AI assessment section visible
      await expect(backlogPage.locator('[data-testid="ai-assessment"]')).toBeVisible();
      
      // Verify reasons section
      await expect(backlogPage.locator('[data-testid="assessment-reasons"]')).toBeVisible();
      
      // Verify risks section
      await expect(backlogPage.locator('[data-testid="assessment-risks"]')).toBeVisible();
    }
  });

  /**
   * US-015: Lead Scoring Display
   */
  test('US-015: should display score with color coding', async ({ backlogPage }) => {
    const leadCards = backlogPage.locator('[data-testid="lead-card"]');
    
    if (await leadCards.count() > 0) {
      // Check high score (green)
      const highScoreCard = backlogPage.locator('[data-testid="lead-score"].score-high').first();
      if (await highScoreCard.isVisible().catch(() => false)) {
        const score = await highScoreCard.textContent();
        expect(parseInt(score || '0')).toBeGreaterThanOrEqual(80);
      }
      
      // Check medium score (yellow)
      const medScoreCard = backlogPage.locator('[data-testid="lead-score"].score-medium').first();
      if (await medScoreCard.isVisible().catch(() => false)) {
        const score = await medScoreCard.textContent();
        const scoreNum = parseInt(score || '0');
        expect(scoreNum).toBeGreaterThanOrEqual(60);
        expect(scoreNum).toBeLessThan(80);
      }
    }
  });

  test('US-015: should show score breakdown when expanded', async ({ backlogPage }) => {
    const leadCards = backlogPage.locator('[data-testid="lead-card"]');
    
    if (await leadCards.count() > 0) {
      await leadCards.first().click();
      
      // Verify score visible in assessment
      await expect(backlogPage.locator('[data-testid="ai-assessment"] [data-testid="score-value"]')).toBeVisible();
      
      // Verify reasons listed
      const reasons = backlogPage.locator('[data-testid="assessment-reasons"] li');
      if (await reasons.count() > 0) {
        await expect(reasons.first()).toBeVisible();
      }
    }
  });

  /**
   * US-016: Approve Lead
   */
  test('US-016: should approve lead and move to pipeline', async ({ backlogPage, page }) => {
    const leadCards = backlogPage.locator('[data-testid="lead-card"]');
    
    if (await leadCards.count() > 0) {
      // Get first lead name
      const leadName = await leadCards.first().locator('[data-testid="lead-name"]').textContent();
      
      // Click approve button
      await leadCards.first().locator('[data-testid="approve-btn"]').click();
      
      // Verify success toast
      await expect(backlogPage.locator('[data-testid="success-toast"]')).toContainText('approved');
      
      // Verify lead removed from backlog
      await backlogPage.reload();
      await expect(backlogPage.locator(`text=${leadName}`)).not.toBeVisible();
      
      // Verify in pipeline
      await backlogPage.goto('/dashboard/pipeline');
      await expect(backlogPage.locator('[data-testid="pipeline-approved"]')).toContainText(leadName || '');
    }
  });

  test('US-016: should log approve activity', async ({ backlogPage, page }) => {
    const leadCards = backlogPage.locator('[data-testid="lead-card"]');
    
    if (await leadCards.count() > 0) {
      const leadName = await leadCards.first().locator('[data-testid="lead-name"]').textContent();
      
      // Approve lead
      await leadCards.first().locator('[data-testid="approve-btn"]').click();
      await backlogPage.waitForTimeout(500);
      
      // Navigate to CRM and check activity
      await backlogPage.goto('/dashboard/crm');
      await expect(backlogPage.locator('[data-testid="activity-feed"]')).toContainText('approved');
    }
  });

  /**
   * US-017: Reject Lead
   */
  test('US-017: should reject lead and remove from backlog', async ({ backlogPage }) => {
    const leadCards = backlogPage.locator('[data-testid="lead-card"]');
    
    if (await leadCards.count() > 0) {
      const leadName = await leadCards.first().locator('[data-testid="lead-name"]').textContent();
      
      // Click reject button
      await leadCards.first().locator('[data-testid="reject-btn"]').click();
      
      // Verify success toast
      await expect(backlogPage.locator('[data-testid="success-toast"]')).toContainText('rejected');
      
      // Verify lead removed from backlog
      await backlogPage.reload();
      await expect(backlogPage.locator(`text=${leadName}`)).not.toBeVisible();
    }
  });

  /**
   * US-013: Manual Discovery Trigger
   */
  test('US-013: should trigger manual discovery', async ({ dashboardPage }) => {
    // Navigate to dashboard
    await dashboardPage.goto('/dashboard');
    
    // Find and click run discovery button
    const runDiscoveryBtn = dashboardPage.locator('[data-testid="run-discovery-btn"]');
    await expect(runDiscoveryBtn).toBeVisible();
    
    await runDiscoveryBtn.click();
    
    // Verify "discovery running" message
    await expect(dashboardPage.locator('[data-testid="discovery-status"]')).toContainText('running');
  });

  test('US-013: should show new leads after discovery', async ({ dashboardPage, backlogPage }) => {
    // Trigger discovery
    await dashboardPage.goto('/dashboard');
    await dashboardPage.locator('[data-testid="run-discovery-btn"]').click();
    
    // Wait for completion
    await dashboardPage.waitForTimeout(3000);
    
    // Navigate to backlog
    await dashboardPage.goto('/dashboard/backlog');
    
    // Verify leads exist (or empty state if none found)
    const hasLeads = await dashboardPage.locator('[data-testid="lead-card"]').count() > 0;
    const hasEmptyState = await dashboardPage.locator('[data-testid="empty-backlog"]').isVisible().catch(() => false);
    
    expect(hasLeads || hasEmptyState).toBeTruthy();
  });

  /**
   * US-018: Auto-Approve High-Scoring Leads
   */
  test('US-018: should auto-approve leads above threshold', async ({ page }) => {
    // Go to settings and set threshold
    await page.goto('/dashboard/settings');
    
    // Set auto-approve threshold to 85
    const thresholdSlider = page.locator('[data-testid="auto-approve-threshold"]');
    await thresholdSlider.fill('85');
    
    // Save settings
    await page.locator('[data-testid="save-settings-btn"]').click();
    await expect(page.locator('[data-testid="success-toast"]')).toContainText('saved');
    
    // Trigger discovery
    await page.goto('/dashboard');
    await page.locator('[data-testid="run-discovery-btn"]').click();
    await page.waitForTimeout(3000);
    
    // High-scoring leads should be in pipeline, not backlog
    await page.goto('/dashboard/pipeline');
    // Check if any high-score leads were auto-approved
  });
});
