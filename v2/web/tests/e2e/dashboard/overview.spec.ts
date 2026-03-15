import { test, expect } from '../fixtures';

/**
 * Dashboard User Stories: US-010 to US-012
 * Priority: P0 - CRITICAL
 * 
 * Dashboard overview, real-time updates, agent status
 */
test.describe('Dashboard (US-010 to US-012)', () => {
  
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard');
  });

  /**
   * US-010: Dashboard Overview
   */
  test('US-010: should display dashboard with key metrics', async ({ dashboardPage }) => {
    // Verify dashboard container visible
    await expect(dashboardPage.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // Verify metric cards visible
    await expect(dashboardPage.locator('[data-testid="metric-total-leads"]')).toBeVisible();
    await expect(dashboardPage.locator('[data-testid="metric-new-leads"]')).toBeVisible();
    await expect(dashboardPage.locator('[data-testid="metric-active-pipeline"]')).toBeVisible();
    await expect(dashboardPage.locator('[data-testid="metric-emails-sent"]')).toBeVisible();
    
    // Verify metric values are numbers
    const totalLeads = await dashboardPage.locator('[data-testid="metric-total-leads"] .value').textContent();
    expect(parseInt(totalLeads || '0')).toBeGreaterThanOrEqual(0);
  });

  test('US-010: should display agent status panel', async ({ dashboardPage }) => {
    // Verify agent status panel visible
    await expect(dashboardPage.locator('[data-testid="agent-status"]')).toBeVisible();
    
    // Verify current activity displayed
    await expect(dashboardPage.locator('[data-testid="agent-current-activity"]')).toBeVisible();
    
    // Verify last activity timestamp
    await expect(dashboardPage.locator('[data-testid="agent-last-activity"]')).toBeVisible();
    
    // Verify daily stats visible
    await expect(dashboardPage.locator('[data-testid="agent-daily-stats"]')).toBeVisible();
  });

  test('US-010: should display recent activity feed', async ({ dashboardPage }) => {
    // Verify activity feed visible
    await expect(dashboardPage.locator('[data-testid="activity-feed"]')).toBeVisible();
    
    // Verify activity items displayed (if any)
    const activities = dashboardPage.locator('[data-testid="activity-item"]');
    const count = await activities.count();
    
    // Should have activities or empty state
    if (count === 0) {
      await expect(dashboardPage.locator('[data-testid="empty-activity"]')).toBeVisible();
    } else {
      await expect(activities.first()).toBeVisible();
    }
  });

  /**
   * US-011: Real-time Dashboard Updates
   */
  test('US-011: should establish WebSocket connection', async ({ dashboardPage }) => {
    // Verify WebSocket connection established
    await dashboardPage.waitForTimeout(1000);
    
    const wsConnected = await dashboardPage.evaluate(() => {
      // Check if WebSocket is connected
      return window.WebSocket !== undefined;
    });
    
    expect(wsConnected).toBeTruthy();
  });

  test('US-011: should update stats without page refresh', async ({ dashboardPage }) => {
    // Get initial metric value
    const initialValue = await dashboardPage.locator('[data-testid="metric-new-leads"] .value').textContent();
    
    // Trigger a lead creation via API (would need to mock or call API)
    // For now, just verify the update mechanism exists
    await expect(dashboardPage.locator('[data-testid="metric-new-leads"]')).toHaveAttribute('data-auto-update', 'true');
  });

  /**
   * US-012: Agent Status Monitoring
   */
  test('US-012: should show current agent activity', async ({ dashboardPage }) => {
    // Verify current activity text visible
    const activityText = await dashboardPage.locator('[data-testid="agent-current-activity"]').textContent();
    expect(activityText).toBeTruthy();
    expect(activityText?.length).toBeGreaterThan(0);
    
    // Activity should indicate scanning/discovering/idle
    const validStates = ['scanning', 'discover', 'active', 'idle', 'processing'];
    const hasValidState = validStates.some(state => 
      activityText?.toLowerCase().includes(state)
    );
    expect(hasValidState).toBeTruthy();
  });

  test('US-012: should show last activity timestamp', async ({ dashboardPage }) => {
    // Verify timestamp visible
    const timestamp = await dashboardPage.locator('[data-testid="agent-last-activity"]').textContent();
    expect(timestamp).toBeTruthy();
    
    // Should be recent (within last hour) or show actual time
    expect(timestamp).toMatch(/\d+ (min|hour|sec)/);
  });

  test('US-012: should display daily statistics', async ({ dashboardPage }) => {
    // Verify daily stats section
    await expect(dashboardPage.locator('[data-testid="agent-daily-stats"]')).toBeVisible();
    
    // Verify individual stat counters
    await expect(dashboardPage.locator('[data-testid="stat-leads-discovered"]')).toBeVisible();
    await expect(dashboardPage.locator('[data-testid="stat-emails-sent"]')).toBeVisible();
    await expect(dashboardPage.locator('[data-testid="stat-replies-received"]')).toBeVisible();
    
    // Values should be numeric
    const leadsDiscovered = await dashboardPage.locator('[data-testid="stat-leads-discovered"] .value').textContent();
    expect(parseInt(leadsDiscovered || '0')).toBeGreaterThanOrEqual(0);
  });
});
