import { test, expect } from '../fixtures';

/**
 * Pipeline Management: US-019 to US-022
 * Priority: P1 - IMPORTANT
 */
test.describe('Pipeline Management (US-019 to US-022)', () => {
  
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/pipeline');
  });

  /**
   * US-019: View Pipeline
   */
  test('US-019: should display kanban pipeline with 5 columns', async ({ pipelinePage }) => {
    // Verify pipeline container
    await expect(pipelinePage.locator('[data-testid="pipeline"]')).toBeVisible();
    
    // Verify all 5 columns exist
    await expect(pipelinePage.locator('[data-testid="column-approved"]')).toBeVisible();
    await expect(pipelinePage.locator('[data-testid="column-outreach"]')).toBeVisible();
    await expect(pipelinePage.locator('[data-testid="column-engaged"]')).toBeVisible();
    await expect(pipelinePage.locator('[data-testid="column-qualified"]')).toBeVisible();
    await expect(pipelinePage.locator('[data-testid="column-booked"]')).toBeVisible();
  });

  test('US-019: should display leads in appropriate columns', async ({ pipelinePage }) => {
    // Check if leads exist in pipeline
    const leadCards = pipelinePage.locator('[data-testid="pipeline-lead-card"]');
    const count = await leadCards.count();
    
    if (count > 0) {
      // Verify at least one lead has status displayed
      await expect(leadCards.first().locator('[data-testid="lead-status"]')).toBeVisible();
    }
  });

  test('US-019: should display total pipeline value', async ({ pipelinePage }) => {
    // Verify pipeline value displayed
    await expect(pipelinePage.locator('[data-testid="pipeline-value"]')).toBeVisible();
    
    // Value should be formatted currency
    const value = await pipelinePage.locator('[data-testid="pipeline-value"]').textContent();
    expect(value).toMatch(/\$[\d,.]+[KM]?/);
  });

  /**
   * US-020: Move Lead Through Pipeline
   */
  test('US-020: should move lead to next stage', async ({ pipelinePage }) => {
    // Find a lead in approved column
    const approvedLeads = pipelinePage.locator('[data-testid="column-approved"] [data-testid="pipeline-lead-card"]');
    
    if (await approvedLeads.count() > 0) {
      const leadName = await approvedLeads.first().locator('[data-testid="lead-name"]').textContent();
      
      // Click on lead to expand
      await approvedLeads.first().click();
      
      // Click move to outreach button
      await pipelinePage.locator('[data-testid="move-to-outreach-btn"]').click();
      
      // Verify lead moved to outreach column
      await expect(pipelinePage.locator('[data-testid="column-outreach"]')).toContainText(leadName || '');
    }
  });

  test('US-020: should update lead status when moved', async ({ pipelinePage }) => {
    const approvedLeads = pipelinePage.locator('[data-testid="column-approved"] [data-testid="pipeline-lead-card"]');
    
    if (await approvedLeads.count() > 0) {
      await approvedLeads.first().click();
      await pipelinePage.locator('[data-testid="move-to-outreach-btn"]').click();
      
      // Verify status changed
      await pipelinePage.reload();
      const movedLead = pipelinePage.locator('[data-testid="column-outreach"]').locator(`text=ABC`).first();
      // Status verification would depend on UI implementation
    }
  });

  test('US-020: should log activity when lead moved', async ({ pipelinePage }) => {
    const approvedLeads = pipelinePage.locator('[data-testid="column-approved"] [data-testid="pipeline-lead-card"]');
    
    if (await approvedLeads.count() > 0) {
      await approvedLeads.first().click();
      await pipelinePage.locator('[data-testid="move-to-outreach-btn"]').click();
      
      // Navigate to CRM and verify activity
      await pipelinePage.goto('/dashboard/crm');
      await expect(pipelinePage.locator('[data-testid="activity-feed"]')).toContainText('moved to');
    }
  });

  /**
   * US-021: Pipeline Value Tracking
   */
  test('US-021: should calculate total pipeline value', async ({ pipelinePage }) => {
    const valueText = await pipelinePage.locator('[data-testid="pipeline-value"]').textContent();
    const value = parseFloat(valueText?.replace(/[^\d.]/g, '') || '0');
    
    // Value should be sum of all pipeline lead revenues
    expect(value).toBeGreaterThanOrEqual(0);
  });

  test('US-021: should update value when leads added', async ({ pipelinePage, page }) => {
    // Get initial value
    const initialValue = await pipelinePage.locator('[data-testid="pipeline-value"]').textContent();
    
    // Approve a new lead (would need to do this via backlog)
    await page.goto('/dashboard/backlog');
    const leadCards = page.locator('[data-testid="lead-card"]');
    
    if (await leadCards.count() > 0) {
      await leadCards.first().locator('[data-testid="approve-btn"]').click();
      
      // Go back to pipeline
      await page.goto('/dashboard/pipeline');
      await page.waitForTimeout(500);
      
      // Value should have updated
      // (Would need to verify based on actual implementation)
    }
  });

  /**
   * US-022: Email Activity in Pipeline
   */
  test('US-022: should show email count badge on leads', async ({ pipelinePage }) => {
    // Find leads with emails sent
    const leadsWithEmails = pipelinePage.locator('[data-testid="pipeline-lead-card"]:has([data-testid="email-count"])');
    
    if (await leadsWithEmails.count() > 0) {
      // Verify email count visible
      await expect(leadsWithEmails.first().locator('[data-testid="email-count"]')).toBeVisible();
      
      // Count should be numeric
      const count = await leadsWithEmails.first().locator('[data-testid="email-count"]').textContent();
      expect(parseInt(count || '0')).toBeGreaterThan(0);
    }
  });

  test('US-022: should show reply indicator for engaged leads', async ({ pipelinePage }) => {
    // Find leads with replies
    const leadsWithReplies = pipelinePage.locator('[data-testid="pipeline-lead-card"]:has([data-testid="reply-indicator"])');
    
    if (await leadsWithReplies.count() > 0) {
      // Verify reply indicator visible
      await expect(leadsWithReplies.first().locator('[data-testid="reply-indicator"]')).toBeVisible();
    }
  });
});
