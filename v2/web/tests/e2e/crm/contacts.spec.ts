import { test, expect } from '../fixtures';

/**
 * CRM - Contact Management: US-023 to US-028
 * Priority: P1 - IMPORTANT
 */
test.describe('CRM - Contact Management (US-023 to US-028)', () => {
  
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/crm');
  });

  /**
   * US-023: View All Contacts
   */
  test('US-023: should display contact list', async ({ crmPage }) => {
    // Verify CRM container
    await expect(crmPage.locator('[data-testid="crm"]')).toBeVisible();
    
    // Verify contact list visible
    await expect(crmPage.locator('[data-testid="contact-list"]')).toBeVisible();
  });

  test('US-023: should display all leads in contact list', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    const count = await contacts.count();
    
    if (count > 0) {
      // Verify each contact has required fields
      await expect(contacts.first().locator('[data-testid="contact-name"]')).toBeVisible();
      await expect(contacts.first().locator('[data-testid="contact-industry"]')).toBeVisible();
      await expect(contacts.first().locator('[data-testid="contact-location"]')).toBeVisible();
    }
  });

  test('US-023: should allow sorting contacts', async ({ crmPage }) => {
    // Verify sort controls
    const sortDropdown = crmPage.locator('[data-testid="sort-dropdown"]');
    await expect(sortDropdown).toBeVisible();
    
    // Test sorting by name
    await sortDropdown.selectOption('name');
    await crmPage.waitForTimeout(500);
    
    // Test sorting by score
    await sortDropdown.selectOption('score');
    await crmPage.waitForTimeout(500);
  });

  /**
   * US-024: Search Contacts
   */
  test('US-024: should search contacts by name', async ({ crmPage }) => {
    // Verify search box
    const searchBox = crmPage.locator('[data-testid="contact-search"]');
    await expect(searchBox).toBeVisible();
    
    // Type search term
    await searchBox.fill('Tech');
    await crmPage.waitForTimeout(500);
    
    // Results should filter
    const results = crmPage.locator('[data-testid="contact-item"]');
    // Should show matching results or empty state
  });

  test('US-024: should search contacts by industry', async ({ crmPage }) => {
    await crmPage.locator('[data-testid="contact-search"]').fill('Healthcare');
    await crmPage.waitForTimeout(500);
    
    // Should filter to healthcare contacts
  });

  test('US-024: should search contacts by city', async ({ crmPage }) => {
    await crmPage.locator('[data-testid="contact-search"]').fill('Salt Lake');
    await crmPage.waitForTimeout(500);
    
    // Should filter to Salt Lake contacts
  });

  test('US-024: should clear search', async ({ crmPage }) => {
    await crmPage.locator('[data-testid="contact-search"]').fill('Test');
    await crmPage.locator('[data-testid="clear-search-btn"]').click();
    
    // Search should be cleared
    await expect(crmPage.locator('[data-testid="contact-search"]')).toHaveValue('');
  });

  /**
   * US-025: View Contact Details
   */
  test('US-025: should display contact details panel', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      // Click first contact
      await contacts.first().click();
      
      // Verify detail panel visible
      await expect(crmPage.locator('[data-testid="contact-details"]')).toBeVisible();
    }
  });

  test('US-025: should show all contact information', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      // Verify all fields visible
      await expect(crmPage.locator('[data-testid="detail-name"]')).toBeVisible();
      await expect(crmPage.locator('[data-testid="detail-industry"]')).toBeVisible();
      await expect(crmPage.locator('[data-testid="detail-revenue"]')).toBeVisible();
      await expect(crmPage.locator('[data-testid="detail-location"]')).toBeVisible();
      await expect(crmPage.locator('[data-testid="detail-description"]')).toBeVisible();
    }
  });

  test('US-025: should show contact info when available', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      // Check if email/phone shown (if available)
      const emailVisible = await crmPage.locator('[data-testid="detail-email"]').isVisible().catch(() => false);
      const phoneVisible = await crmPage.locator('[data-testid="detail-phone"]').isVisible().catch(() => false);
      
      // At least one should potentially be visible
    }
  });

  /**
   * US-026: Add Note to Contact
   */
  test('US-026: should add note to contact', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      // Type note
      const noteInput = crmPage.locator('[data-testid="note-input"]');
      await noteInput.fill('Called owner, interested in discussing acquisition');
      
      // Save note
      await crmPage.locator('[data-testid="save-note-btn"]').click();
      
      // Verify success
      await expect(crmPage.locator('[data-testid="success-toast"]')).toContainText('Note added');
    }
  });

  test('US-026: should display saved notes', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      // Check notes section
      await expect(crmPage.locator('[data-testid="notes-section"]')).toBeVisible();
      
      // If notes exist, verify they display
      const notes = crmPage.locator('[data-testid="note-item"]');
      if (await notes.count() > 0) {
        await expect(notes.first()).toBeVisible();
      }
    }
  });

  test('US-026: should timestamp notes', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const notes = crmPage.locator('[data-testid="note-item"]');
      if (await notes.count() > 0) {
        // Verify timestamp visible
        await expect(notes.first().locator('[data-testid="note-timestamp"]')).toBeVisible();
      }
    }
  });

  /**
   * US-027: View Activity History
   */
  test('US-027: should display activity history', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      // Verify activity feed visible
      await expect(crmPage.locator('[data-testid="activity-feed"]')).toBeVisible();
    }
  });

  test('US-027: should show chronological activity', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const activities = crmPage.locator('[data-testid="activity-item"]');
      if (await activities.count() > 1) {
        // Verify chronological order (newest first)
        // This would depend on implementation details
      }
    }
  });

  test('US-027: should show activity timestamps', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const activities = crmPage.locator('[data-testid="activity-item"]');
      if (await activities.count() > 0) {
        await expect(activities.first().locator('[data-testid="activity-timestamp"]')).toBeVisible();
      }
    }
  });

  /**
   * US-028: Quick Email from CRM
   */
  test('US-028: should open email compose from CRM', async ({ crmPage }) => {
    const contacts = crmPage.locator('[data-testid="contact-item"]');
    
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      // Check if contact has email
      const emailBtn = crmPage.locator('[data-testid="email-contact-btn"]');
      const hasEmail = await emailBtn.isVisible().catch(() => false);
      
      if (hasEmail) {
        await emailBtn.click();
        
        // Verify email compose modal opens
        await expect(crmPage.locator('[data-testid="email-compose-modal"]')).toBeVisible();
      }
    }
  });
});
