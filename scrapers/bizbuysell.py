"""
BizBuySell Scraper for ACQUISITOR

Scrapes business listings from BizBuySell with filtering, deduplication,
and PostgreSQL storage.
"""

import argparse
import json
import logging
import random
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import psycopg2
from psycopg2.extras import RealDictCursor
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bizbuysell_scraper.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BusinessListing:
    """Represents a scraped business listing."""
    business_name: str
    asking_price: Optional[float]
    revenue: Optional[float]
    cash_flow: Optional[float]
    location: str
    description: str
    listing_url: str
    broker_name: Optional[str]
    business_type: Optional[str]
    description_embedding: Optional[List[float]] = None
    source: str = "bizbuysell"
    scraped_at: datetime = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()


class DatabaseManager:
    """Manages PostgreSQL connections and operations."""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or self._get_connection_string()
        self.conn = None
        self._connect()
        self._ensure_table_exists()
    
    def _get_connection_string(self) -> str:
        """Get connection string from environment or use default."""
        import os
        return os.getenv(
            'DATABASE_URL',
            'postgresql://localhost:5432/acquisitor'
        )
    
    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Connected to PostgreSQL database")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _ensure_table_exists(self) -> None:
        """Create market_listings table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS market_listings (
            id SERIAL PRIMARY KEY,
            business_name VARCHAR(500) NOT NULL,
            asking_price DECIMAL(15, 2),
            revenue DECIMAL(15, 2),
            cash_flow DECIMAL(15, 2),
            location VARCHAR(255),
            description TEXT,
            listing_url VARCHAR(1000) UNIQUE NOT NULL,
            broker_name VARCHAR(255),
            business_type VARCHAR(255),
            description_embedding JSONB,
            source VARCHAR(50) DEFAULT 'bizbuysell',
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_listing_url ON market_listings(listing_url);
        CREATE INDEX IF NOT EXISTS idx_revenue ON market_listings(revenue);
        CREATE INDEX IF NOT EXISTS idx_location ON market_listings(location);
        CREATE INDEX IF NOT EXISTS idx_business_type ON market_listings(business_type);
        CREATE INDEX IF NOT EXISTS idx_scraped_at ON market_listings(scraped_at);
        """
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_table_sql)
                self.conn.commit()
                logger.info("Ensured market_listings table exists")
        except psycopg2.Error as e:
            logger.error(f"Failed to create table: {e}")
            self.conn.rollback()
            raise
    
    def listing_exists(self, listing_url: str) -> bool:
        """Check if a listing already exists by URL."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM market_listings WHERE listing_url = %s LIMIT 1",
                    (listing_url,)
                )
                return cur.fetchone() is not None
        except psycopg2.Error as e:
            logger.error(f"Error checking listing existence: {e}")
            return False
    
    def save_listing(self, listing: BusinessListing) -> bool:
        """Save a listing to the database. Returns True if saved, False if duplicate."""
        if self.listing_exists(listing.listing_url):
            logger.debug(f"Listing already exists: {listing.listing_url}")
            return False
        
        insert_sql = """
        INSERT INTO market_listings (
            business_name, asking_price, revenue, cash_flow, location,
            description, listing_url, broker_name, business_type,
            description_embedding, source, scraped_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (listing_url) DO NOTHING
        RETURNING id;
        """
        
        try:
            with self.conn.cursor() as cur:
                embedding_json = json.dumps(listing.description_embedding) if listing.description_embedding else None
                cur.execute(insert_sql, (
                    listing.business_name,
                    listing.asking_price,
                    listing.revenue,
                    listing.cash_flow,
                    listing.location,
                    listing.description,
                    listing.listing_url,
                    listing.broker_name,
                    listing.business_type,
                    embedding_json,
                    listing.source,
                    listing.scraped_at
                ))
                result = cur.fetchone()
                self.conn.commit()
                
                if result:
                    logger.info(f"Saved listing: {listing.business_name} (ID: {result[0]})")
                    return True
                return False
                
        except psycopg2.Error as e:
            logger.error(f"Error saving listing: {e}")
            self.conn.rollback()
            return False
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


class BizBuySellScraper:
    """
    Scraper for BizBuySell business listings.
    
    Features:
    - Playwright-based browser automation
    - Configurable filters (revenue, location, business type)
    - Pagination support
    - Rate limiting with random delays
    - Comprehensive error handling and retry logic
    - Deduplication via database checks
    """
    
    BASE_URL = "https://www.bizbuysell.com"
    SEARCH_PATH = "/businesses-for-sale/"
    
    # Default revenue filter: $1M - $10M
    DEFAULT_MIN_REVENUE = 1_000_000
    DEFAULT_MAX_REVENUE = 10_000_000
    
    # Rate limiting defaults (seconds)
    MIN_DELAY = 2.0
    MAX_DELAY = 5.0
    REQUEST_TIMEOUT = 30000  # 30 seconds
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        min_revenue: float = DEFAULT_MIN_REVENUE,
        max_revenue: float = DEFAULT_MAX_REVENUE,
        location: Optional[str] = None,
        business_type: Optional[str] = None,
        headless: bool = True,
        min_delay: float = MIN_DELAY,
        max_delay: float = MAX_DELAY
    ):
        self.db = db_manager or DatabaseManager()
        self.min_revenue = min_revenue
        self.max_revenue = max_revenue
        self.location = location
        self.business_type = business_type
        self.headless = headless
        self.min_delay = min_delay
        self.max_delay = max_delay
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.stats = {
            'pages_scraped': 0,
            'listings_found': 0,
            'listings_saved': 0,
            'listings_duplicate': 0,
            'errors': 0
        }
    
    def _build_search_url(self, page: int = 1) -> str:
        """Build search URL with filters."""
        params: Dict[str, Any] = {}
        
        # Revenue filter
        if self.min_revenue:
            params['minRevenue'] = int(self.min_revenue)
        if self.max_revenue:
            params['maxRevenue'] = int(self.max_revenue)
        
        # Location filter
        if self.location:
            # BizBuySell uses state/city in path or q parameter
            params['q'] = self.location
        
        # Business type filter
        if self.business_type:
            params['industry'] = self.business_type.lower().replace(' ', '-')
        
        # Pagination
        if page > 1:
            params['page'] = page
        
        # Build URL
        base = urljoin(self.BASE_URL, self.SEARCH_PATH)
        if self.location:
            # Location often goes in the path
            location_slug = self.location.lower().replace(' ', '-').replace(',', '')
            base = urljoin(self.BASE_URL, f"/businesses-for-sale/{location_slug}")
        
        if params:
            base += '?' + urlencode(params)
        
        return base
    
    def _init_browser(self) -> None:
        """Initialize Playwright browser."""
        logger.info("Initializing browser...")
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        self.page = context.new_page()
        logger.info("Browser initialized")
    
    def _close_browser(self) -> None:
        """Close browser and cleanup."""
        if self.browser:
            self.browser.close()
            logger.info("Browser closed")
    
    def _random_delay(self) -> None:
        """Apply random delay between requests."""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"Sleeping for {delay:.2f}s")
        time.sleep(delay)
    
    def _parse_money(self, value: Optional[str]) -> Optional[float]:
        """Parse monetary values like '$1,500,000' or '$1.5M' to float."""
        if not value:
            return None
        
        # Remove common prefixes/suffixes
        value = value.strip().lower()
        value = re.sub(r'[\s,]', '', value)
        
        # Handle 'M' suffix (millions)
        if 'm' in value:
            match = re.search(r'[\d.]+', value)
            if match:
                return float(match.group()) * 1_000_000
        
        # Handle 'K' suffix (thousands)
        if 'k' in value:
            match = re.search(r'[\d.]+', value)
            if match:
                return float(match.group()) * 1_000
        
        # Extract numeric value
        match = re.search(r'[\d.]+', value)
        if match:
            return float(match.group())
        
        return None
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate a simple keyword-based embedding placeholder.
        In production, replace with actual embedding model (e.g., OpenAI, sentence-transformers).
        """
        # Simple keyword frequency-based vector
        # This is a placeholder - real implementation would use proper embeddings
        keywords = [
            'manufacturing', 'technology', 'healthcare', 'retail', 'restaurant',
            'construction', 'transportation', 'professional', 'service', 'real estate',
            'e-commerce', 'software', 'franchise', 'wholesale', 'automotive',
            'hospitality', 'entertainment', 'education', 'finance', 'insurance'
        ]
        
        text_lower = text.lower()
        vector = []
        
        for keyword in keywords:
            # Simple frequency count normalized
            count = text_lower.count(keyword)
            # Also check for partial matches
            if keyword in text_lower:
                count += 0.5
            vector.append(min(count / 10.0, 1.0))  # Normalize to [0, 1]
        
        # Pad to fixed size if needed
        while len(vector) < 50:
            vector.append(0.0)
        
        return vector[:50]  # Return fixed-size vector
    
    def _extract_text(self, selector: str, default: Optional[str] = None) -> Optional[str]:
        """Safely extract text from page element."""
        try:
            element = self.page.locator(selector).first
            if element.count() > 0:
                text = element.text_content()
                return text.strip() if text else default
        except Exception as e:
            logger.debug(f"Could not extract text from selector {selector}: {e}")
        return default
    
    def parse_listing(self, listing_element: Any) -> Optional[BusinessListing]:
        """
        Parse a single listing element into a BusinessListing object.
        
        Args:
            listing_element: Playwright locator or element handle for a listing
            
        Returns:
            BusinessListing object or None if parsing fails
        """
        try:
            # Extract listing URL
            link_elem = listing_element.locator('a[href*="/business-for-sale/"]').first
            if link_elem.count() == 0:
                link_elem = listing_element.locator('a').first
            
            href = link_elem.get_attribute('href') if link_elem.count() > 0 else None
            if not href:
                logger.debug("No link found in listing element")
                return None
            
            listing_url = urljoin(self.BASE_URL, href)
            
            # Extract business name
            name_selectors = [
                'h2.title',
                'h3.title',
                '.listing-title',
                'h2',
                'h3',
                '.title',
                '[data-testid="listing-title"]'
            ]
            business_name = None
            for selector in name_selectors:
                business_name = self._extract_text_from_element(listing_element, selector)
                if business_name:
                    break
            
            if not business_name:
                business_name = "Unknown Business"
            
            # Extract financials
            asking_price = self._extract_financial(listing_element, ['asking price', 'price', 'asking'])
            revenue = self._extract_financial(listing_element, ['revenue', 'gross revenue', 'sales'])
            cash_flow = self._extract_financial(listing_element, ['cash flow', 'net income', 'profit', 'discretionary'])
            
            # Extract location
            location_selectors = [
                '.location',
                '.address',
                '[data-testid="location"]',
                '.listing-location'
            ]
            location = self.location or "Unknown"
            for selector in location_selectors:
                loc = self._extract_text_from_element(listing_element, selector)
                if loc:
                    location = loc
                    break
            
            # Extract description
            desc_selectors = [
                '.description',
                '.listing-description',
                'p.description',
                '.summary',
                '[data-testid="description"]'
            ]
            description = ""
            for selector in desc_selectors:
                desc = self._extract_text_from_element(listing_element, selector)
                if desc:
                    description = desc
                    break
            
            # Extract broker name
            broker_selectors = [
                '.broker-name',
                '.agent-name',
                '[data-testid="broker"]',
                '.broker'
            ]
            broker_name = None
            for selector in broker_selectors:
                broker = self._extract_text_from_element(listing_element, selector)
                if broker:
                    broker_name = broker
                    break
            
            # Determine business type
            business_type = self.business_type
            if not business_type:
                # Try to extract from description or categories
                type_selectors = [
                    '.category',
                    '.industry',
                    '.business-type',
                    '[data-testid="category"]'
                ]
                for selector in type_selectors:
                    bt = self._extract_text_from_element(listing_element, selector)
                    if bt:
                        business_type = bt
                        break
            
            # Generate embedding
            description_embedding = self._generate_embedding(description)
            
            listing = BusinessListing(
                business_name=business_name,
                asking_price=asking_price,
                revenue=revenue,
                cash_flow=cash_flow,
                location=location,
                description=description,
                listing_url=listing_url,
                broker_name=broker_name,
                business_type=business_type,
                description_embedding=description_embedding
            )
            
            logger.debug(f"Parsed listing: {business_name}")
            return listing
            
        except Exception as e:
            logger.error(f"Error parsing listing: {e}")
            return None
    
    def _extract_text_from_element(self, element: Any, selector: str) -> Optional[str]:
        """Extract text from a child element."""
        try:
            child = element.locator(selector).first
            if child.count() > 0:
                text = child.text_content()
                return text.strip() if text else None
        except Exception:
            pass
        return None
    
    def _extract_financial(self, element: Any, keywords: List[str]) -> Optional[float]:
        """Extract financial value based on keywords."""
        try:
            # Look for elements containing financial keywords
            all_text = element.text_content() or ""
            all_text_lower = all_text.lower()
            
            for keyword in keywords:
                # Try to find value near keyword
                pattern = rf'{keyword}[:\s]*([\$\d,.km]+)'
                match = re.search(pattern, all_text_lower, re.IGNORECASE)
                if match:
                    return self._parse_money(match.group(1))
            
            # Fallback: look for any money pattern
            money_pattern = r'\$[\d,]+(?:\.\d{2})?(?:\s*[KM])?'
            matches = re.findall(money_pattern, all_text, re.IGNORECASE)
            if matches:
                # Return first match as fallback
                return self._parse_money(matches[0])
                
        except Exception as e:
            logger.debug(f"Error extracting financial: {e}")
        
        return None
    
    def _get_listing_elements(self) -> List[Any]:
        """Get all listing elements from current page."""
        selectors = [
            '[data-testid="listing-card"]',
            '.listing-card',
            '.search-result',
            '.result-item',
            '[class*="listing"]',
            '.business-listing',
            'article'
        ]
        
        for selector in selectors:
            try:
                elements = self.page.locator(selector).all()
                if elements:
                    logger.debug(f"Found {len(elements)} listings with selector: {selector}")
                    return elements
            except Exception:
                continue
        
        return []
    
    def _has_next_page(self, current_page: int) -> bool:
        """Check if there's a next page."""
        next_selectors = [
            'a[rel="next"]',
            '.pagination-next',
            '[data-testid="next-page"]',
            f'a[href*="page={current_page + 1}"]'
        ]
        
        for selector in next_selectors:
            try:
                elem = self.page.locator(selector).first
                if elem.count() > 0 and elem.is_visible():
                    return True
            except Exception:
                continue
        
        return False
    
    def scrape_listings(self, max_pages: int = 5) -> List[BusinessListing]:
        """
        Scrape listings across multiple pages.
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of successfully scraped and saved BusinessListing objects
        """
        all_listings: List[BusinessListing] = []
        
        try:
            self._init_browser()
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"Scraping page {page_num} of {max_pages}")
                
                url = self._build_search_url(page_num)
                logger.info(f"Navigating to: {url}")
                
                # Navigate with retry logic
                success = self._navigate_with_retry(url)
                if not success:
                    logger.error(f"Failed to load page {page_num} after retries")
                    self.stats['errors'] += 1
                    continue
                
                # Wait for content to load
                self._wait_for_content()
                
                # Extract listings
                listing_elements = self._get_listing_elements()
                logger.info(f"Found {len(listing_elements)} listing elements on page {page_num}")
                
                if not listing_elements:
                    logger.warning(f"No listings found on page {page_num}, stopping")
                    break
                
                self.stats['pages_scraped'] += 1
                
                for element in listing_elements:
                    try:
                        listing = self.parse_listing(element)
                        
                        if listing:
                            self.stats['listings_found'] += 1
                            
                            # Check revenue filter
                            if listing.revenue:
                                if not (self.min_revenue <= listing.revenue <= self.max_revenue):
                                    logger.debug(f"Skipping {listing.business_name}: revenue {listing.revenue} outside range")
                                    continue
                            
                            # Save to database
                            if self.db.save_listing(listing):
                                all_listings.append(listing)
                                self.stats['listings_saved'] += 1
                            else:
                                self.stats['listings_duplicate'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing listing element: {e}")
                        self.stats['errors'] += 1
                        continue
                
                # Check for next page
                if page_num < max_pages:
                    if not self._has_next_page(page_num):
                        logger.info("No more pages available")
                        break
                    self._random_delay()
            
            logger.info(f"Scraping complete. Stats: {self.stats}")
            return all_listings
            
        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            raise
        finally:
            self._close_browser()
    
    def _navigate_with_retry(self, url: str) -> bool:
        """Navigate to URL with retry logic."""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                self.page.goto(url, timeout=self.REQUEST_TIMEOUT, wait_until='networkidle')
                
                # Check for common error indicators
                if self.page.locator('text=404').count() > 0:
                    logger.warning(f"Page not found (404): {url}")
                    return False
                
                if self.page.locator('text=blocked').count() > 0:
                    logger.warning("Possible blocking detected")
                
                return True
                
            except PlaywrightTimeout:
                logger.warning(f"Timeout on attempt {attempt}/{self.MAX_RETRIES}")
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)
            except Exception as e:
                logger.error(f"Navigation error on attempt {attempt}: {e}")
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY)
        
        return False
    
    def _wait_for_content(self) -> None:
        """Wait for page content to load."""
        try:
            # Wait for any of these selectors
            selectors = [
                '[data-testid="listing-card"]',
                '.listing-card',
                '.search-result',
                'article'
            ]
            
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=10000)
                    return
                except PlaywrightTimeout:
                    continue
            
            # Fallback: wait for general content
            self.page.wait_for_load_state('domcontentloaded', timeout=15000)
            time.sleep(2)  # Extra wait for dynamic content
            
        except Exception as e:
            logger.warning(f"Error waiting for content: {e}")
    
    def save_to_db(self, listings: List[BusinessListing]) -> Tuple[int, int]:
        """
        Save multiple listings to database.
        
        Args:
            listings: List of BusinessListing objects to save
            
        Returns:
            Tuple of (saved_count, duplicate_count)
        """
        saved = 0
        duplicates = 0
        
        for listing in listings:
            if self.db.save_listing(listing):
                saved += 1
            else:
                duplicates += 1
        
        return saved, duplicates
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        return self.stats.copy()
    
    def close(self) -> None:
        """Cleanup resources."""
        self._close_browser()
        if self.db:
            self.db.close()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape BizBuySell business listings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bizbuysell.py --pages 5 --location "Texas"
  python bizbuysell.py --pages 10 --min-revenue 500000 --max-revenue 5000000
  python bizbuysell.py --pages 3 --business-type "manufacturing" --headless
        """
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        help='Number of pages to scrape (default: 5)'
    )
    parser.add_argument(
        '--location',
        type=str,
        help='Location filter (e.g., "Texas", "California", "New York")'
    )
    parser.add_argument(
        '--business-type',
        type=str,
        help='Business type/industry filter (e.g., "manufacturing", "technology")'
    )
    parser.add_argument(
        '--min-revenue',
        type=float,
        default=1_000_000,
        help='Minimum revenue filter (default: 1000000)'
    )
    parser.add_argument(
        '--max-revenue',
        type=float,
        default=10_000_000,
        help='Maximum revenue filter (default: 10000000)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (disable headless mode)'
    )
    parser.add_argument(
        '--min-delay',
        type=float,
        default=2.0,
        help='Minimum delay between requests in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--max-delay',
        type=float,
        default=5.0,
        help='Maximum delay between requests in seconds (default: 5.0)'
    )
    parser.add_argument(
        '--db-url',
        type=str,
        help='PostgreSQL connection string (default: from DATABASE_URL env var)'
    )
    
    args = parser.parse_args()
    
    # Handle headless flag
    headless = not args.no_headless if args.no_headless else args.headless
    
    # Initialize database manager
    db_manager = DatabaseManager(args.db_url) if args.db_url else None
    
    # Initialize scraper
    scraper = BizBuySellScraper(
        db_manager=db_manager,
        min_revenue=args.min_revenue,
        max_revenue=args.max_revenue,
        location=args.location,
        business_type=args.business_type,
        headless=headless,
        min_delay=args.min_delay,
        max_delay=args.max_delay
    )
    
    try:
        logger.info("Starting BizBuySell scraper...")
        logger.info(f"Configuration: pages={args.pages}, location={args.location}, "
                   f"revenue=${args.min_revenue:,.0f}-${args.max_revenue:,.0f}")
        
        listings = scraper.scrape_listings(max_pages=args.pages)
        
        stats = scraper.get_stats()
        print("\n" + "="*60)
        print("SCRAPING COMPLETE")
        print("="*60)
        print(f"Pages scraped:      {stats['pages_scraped']}")
        print(f"Listings found:     {stats['listings_found']}")
        print(f"Listings saved:     {stats['listings_saved']}")
        print(f"Duplicates skipped: {stats['listings_duplicate']}")
        print(f"Errors:             {stats['errors']}")
        print("="*60)
        
        if listings:
            print(f"\nSample listing:")
            sample = listings[0]
            print(f"  Name:     {sample.business_name}")
            print(f"  Price:    ${sample.asking_price:,.0f}" if sample.asking_price else "  Price:    N/A")
            print(f"  Revenue:  ${sample.revenue:,.0f}" if sample.revenue else "  Revenue:  N/A")
            print(f"  Location: {sample.location}")
            print(f"  URL:      {sample.listing_url}")
        
        return 0 if stats['listings_saved'] > 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return 1
    finally:
        scraper.close()


if __name__ == '__main__':
    sys.exit(main())
