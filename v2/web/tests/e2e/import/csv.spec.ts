import { test, expect } from '../fixtures';

/**
 * CSV Import: US-037 to US-040
 * Priority: P1 - IMPORTANT
 */
test.describe('CSV Import (US-037 to US-040)', () => {
  
  test.beforeEach(async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/dashboard/import');
  });

  /**
   * US-037: Upload CSV Preview
   */
  test('US-037: should display CSV upload interface', async ({ authenticatedPage }) => {
    // Verify import page
    await expect(authenticatedPage.locator('[data-testid="csv-import-page"]')).toBeVisible();
    
    // Verify upload area
    await expect(authenticatedPage.locator('[data-testid="csv-upload-area"]')).toBeVisible();
    
    // Verify file input
    await expect(authenticatedPage.locator('[data-testid="csv-file-input"]')).toBeVisible();
  });

  test('US-037: should accept CSV file upload', async ({ authenticatedPage }) => {
    // Create test CSV
    const csvContent = `Business Name,Industry,Revenue,Employees,City,State
ABC Technology LLC,Technology,2500000,25,Salt Lake City,UT
Summit Services Inc,Services,1800000,12,Provo,UT
Peak Manufacturing,Manufacturing,5200000,48,Ogden,UT`;
    
    // Upload file
    const fileInput = authenticatedPage.locator('[data-testid="csv-file-input"]');
    await fileInput.setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    // Verify preview appears
    await expect(authenticatedPage.locator('[data-testid="csv-preview"]')).toBeVisible();
  });

  test('US-037: should auto-detect column mapping', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Industry,Revenue,Employees,City,State
ABC Technology LLC,Technology,2500000,25,Salt Lake City,UT`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    // Verify column mapping detected
    await expect(authenticatedPage.locator('[data-testid="column-mapping"]')).toBeVisible();
    
    // Verify mappings show
    await expect(authenticatedPage.locator('[data-testid="mapping-name"]')).toContainText('Business Name');
    await expect(authenticatedPage.locator('[data-testid="mapping-industry"]')).toContainText('Industry');
  });

  test('US-037: should show preview of first 5 rows', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Industry,Revenue
Lead1,Technology,1000000
Lead2,Services,2000000
Lead3,Manufacturing,3000000
Lead4,Healthcare,4000000
Lead5,Retail,5000000
Lead6,Construction,6000000`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    // Verify preview shows 5 rows
    const previewRows = authenticatedPage.locator('[data-testid="preview-row"]');
    await expect(previewRows).toHaveCount(5);
  });

  test('US-037: should show validation errors', async ({ authenticatedPage }) => {
    const csvContent = `Company,Industry,Revenue
,Technology,1000000
Lead2,,2000000`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    // Verify errors section
    await expect(authenticatedPage.locator('[data-testid="import-errors"]')).toBeVisible();
  });

  /**
   * US-038: Import CSV Data
   */
  test('US-038: should import leads from CSV', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Industry,Revenue,Employees,City,State
ABC Technology LLC,Technology,2500000,25,Salt Lake City,UT
Summit Services Inc,Services,1800000,12,Provo,UT`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    // Click import
    await authenticatedPage.locator('[data-testid="import-btn"]').click();
    
    // Verify success
    await expect(authenticatedPage.locator('[data-testid="import-success"]')).toContainText('2 leads imported');
  });

  test('US-038: should show import summary', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Industry,Revenue
Lead1,Technology,1000000
Lead2,Services,2000000`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    await authenticatedPage.locator('[data-testid="import-btn"]').click();
    
    // Verify summary shows imported count
    await expect(authenticatedPage.locator('[data-testid="import-summary"]')).toContainText('imported');
  });

  test('US-038: should log import activity', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Industry
Test Lead,Technology`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    await authenticatedPage.locator('[data-testid="import-btn"]').click();
    
    // Navigate to dashboard and check activity
    await authenticatedPage.goto('/dashboard');
    await expect(authenticatedPage.locator('[data-testid="activity-feed"]')).toContainText('import');
  });

  /**
   * US-039: CSV Format Flexibility
   */
  test('US-039: should accept Company column name', async ({ authenticatedPage }) => {
    const csvContent = `Company,Industry,Revenue
ABC Tech,Technology,1000000`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    // Should map Company to name
    await expect(authenticatedPage.locator('[data-testid="mapping-name"]')).toContainText('Company');
  });

  test('US-039: should accept Annual Revenue column name', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Annual Revenue
Test Company,$1,000,000`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    await expect(authenticatedPage.locator('[data-testid="mapping-revenue"]')).toContainText('Annual Revenue');
  });

  test('US-039: should accept Email Address column name', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Email Address
Test Company,test@example.com`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    await expect(authenticatedPage.locator('[data-testid="mapping-email"]')).toContainText('Email Address');
  });

  test('US-039: should parse various revenue formats', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,Revenue
Lead1,$1.2M
Lead2,$500K
Lead3,2500000
Lead4,$1,500,000`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    // All should be parseable
    await expect(authenticatedPage.locator('[data-testid="preview-row"]')).toHaveCount(4);
  });

  /**
   * US-040: Duplicate Detection
   */
  test('US-040: should detect duplicates by name and city', async ({ authenticatedPage }) => {
    // Import first time
    const csvContent = `Business Name,City,State
ABC Tech,Salt Lake City,UT`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    await authenticatedPage.locator('[data-testid="import-btn"]').click();
    await authenticatedPage.waitForTimeout(500);
    
    // Import same again
    await authenticatedPage.goto('/dashboard/import');
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    await authenticatedPage.locator('[data-testid="import-btn"]').click();
    
    // Should show 0 imported, 1 duplicate
    await expect(authenticatedPage.locator('[data-testid="import-success"]')).toContainText('0 imported');
    await expect(authenticatedPage.locator('[data-testid="import-summary"]')).toContainText('1 duplicate');
  });

  test('US-040: should skip duplicates without blocking import', async ({ authenticatedPage }) => {
    const csvContent = `Business Name,City,State
Existing Lead,Salt Lake City,UT
New Lead,Provo,UT`;
    
    await authenticatedPage.locator('[data-testid="csv-file-input"]').setInputFiles({
      name: 'test-leads.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });
    
    await authenticatedPage.locator('[data-testid="import-btn"]').click();
    
    // Should import 1 new, skip 1 duplicate
    await expect(authenticatedPage.locator('[data-testid="import-success"]')).toContainText('1 imported');
  });
});
