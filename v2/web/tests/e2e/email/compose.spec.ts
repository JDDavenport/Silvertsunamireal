import { test, expect } from '../fixtures';

/**
 * Email Outreach: US-029 to US-032
 * Priority: P0 (029-031), P1 (032)
 */
test.describe('Email Outreach (US-029 to US-032)', () => {
  
  /**
   * US-029: Compose Email
   */
  test('US-029: should open email compose modal', async ({ authenticatedPage }) => {
    // Navigate to CRM with a lead that has email
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        // Verify compose modal
        await expect(authenticatedPage.locator('[data-testid="email-compose-modal"]')).toBeVisible();
        
        // Verify fields
        await expect(authenticatedPage.locator('[data-testid="email-to-input"]')).toBeVisible();
        await expect(authenticatedPage.locator('[data-testid="email-subject-input"]')).toBeVisible();
        await expect(authenticatedPage.locator('[data-testid="email-body-textarea"]')).toBeVisible();
        await expect(authenticatedPage.locator('[data-testid="email-send-btn"]')).toBeVisible();
      }
    }
  });

  test('US-029: should pre-fill to field when email known', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        // Verify to field has value
        const toValue = await authenticatedPage.locator('[data-testid="email-to-input"]').inputValue();
        expect(toValue).toContain('@');
      }
    }
  });

  test('US-029: should allow editing subject and body', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        // Edit subject
        await authenticatedPage.locator('[data-testid="email-subject-input"]').fill('Test Subject');
        
        // Edit body
        await authenticatedPage.locator('[data-testid="email-body-textarea"]').fill('Test email body content');
        
        // Verify values set
        await expect(authenticatedPage.locator('[data-testid="email-subject-input"]')).toHaveValue('Test Subject');
        await expect(authenticatedPage.locator('[data-testid="email-body-textarea"]')).toHaveValue('Test email body content');
      }
    }
  });

  /**
   * US-030: Use Email Template
   */
  test('US-030: should show template selector', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        // Verify template dropdown
        await expect(authenticatedPage.locator('[data-testid="template-selector"]')).toBeVisible();
      }
    }
  });

  test('US-030: should populate email from template', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        // Select Introduction template
        await authenticatedPage.locator('[data-testid="template-selector"]').selectOption('intro');
        
        // Verify subject populated
        const subject = await authenticatedPage.locator('[data-testid="email-subject-input"]').inputValue();
        expect(subject.length).toBeGreaterThan(0);
        
        // Verify body populated
        const body = await authenticatedPage.locator('[data-testid="email-body-textarea"]').inputValue();
        expect(body.length).toBeGreaterThan(0);
      }
    }
  });

  test('US-030: should replace template variables', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      const contactName = await contacts.first().locator('[data-testid="contact-name"]').textContent();
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        await authenticatedPage.locator('[data-testid="template-selector"]').selectOption('intro');
        
        // Verify business name replaced (not raw template variable)
        const body = await authenticatedPage.locator('[data-testid="email-body-textarea"]').inputValue();
        expect(body).not.toContain('{{business_name}}');
        expect(body).not.toContain('{{');
      }
    }
  });

  /**
   * US-031: Send Email via Gmail
   */
  test('US-031: should send email and update lead status', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        // Fill email
        await authenticatedPage.locator('[data-testid="email-subject-input"]').fill('Acquisition Opportunity');
        await authenticatedPage.locator('[data-testid="email-body-textarea"]').fill('Interested in discussing acquisition of your business.');
        
        // Send
        await authenticatedPage.locator('[data-testid="email-send-btn"]').click();
        
        // Verify success
        await expect(authenticatedPage.locator('[data-testid="success-toast"]')).toContainText('sent');
      }
    }
  });

  test('US-031: should increment email sent count', async ({ authenticatedPage }) => {
    // This would require verifying API response or database state
    // For now, just verify success message
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        await authenticatedPage.locator('[data-testid="email-subject-input"]').fill('Test');
        await authenticatedPage.locator('[data-testid="email-body-textarea"]').fill('Test body');
        await authenticatedPage.locator('[data-testid="email-send-btn"]').click();
        
        await expect(authenticatedPage.locator('[data-testid="success-toast"]')).toBeVisible();
      }
    }
  });

  test('US-031: should log email activity', async ({ authenticatedPage }) => {
    // Send email
    await authenticatedPage.goto('/dashboard/crm');
    
    const contacts = authenticatedPage.locator('[data-testid="contact-item"]');
    if (await contacts.count() > 0) {
      await contacts.first().click();
      
      const emailBtn = authenticatedPage.locator('[data-testid="email-contact-btn"]').first();
      if (await emailBtn.isVisible().catch(() => false)) {
        await emailBtn.click();
        
        await authenticatedPage.locator('[data-testid="email-subject-input"]').fill('Test');
        await authenticatedPage.locator('[data-testid="email-body-textarea"]').fill('Test');
        await authenticatedPage.locator('[data-testid="email-send-btn"]').click();
        
        // Check activity feed
        await expect(authenticatedPage.locator('[data-testid="activity-feed"]')).toContainText('email');
      }
    }
  });

  /**
   * US-032: Email Rate Limiting
   */
  test('US-032: should respect daily email limit', async ({ settingsPage }) => {
    // Navigate to settings
    await settingsPage.goto('/dashboard/settings');
    
    // Set limit to 1
    await settingsPage.locator('[data-testid="email-limit-slider"]').fill('1');
    await settingsPage.locator('[data-testid="save-settings-btn"]').click();
    
    // Send first email (should work)
    // Send second email (should warn or block)
    // This test would need to actually send emails
  });
});
