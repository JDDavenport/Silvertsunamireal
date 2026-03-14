"""Website discovery - Company website scraping."""
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid
from urllib.parse import urljoin, urlparse

from models import CandidateBusiness, DataSource, SearchQuery

logger = logging.getLogger(__name__)


class WebsiteDiscovery:
    """Discovers and scrapes business information from websites."""
    
    def __init__(self):
        self.candidates: List[CandidateBusiness] = []
        self.visited_urls: set = set()
    
    def search(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Execute website discovery for given query.
        
        Args:
            query: Search query with website discovery parameters
            
        Returns:
            List of CandidateBusiness objects
        """
        logger.info(f"Website discovery: {query.query}")
        
        # In production, this would:
        # 1. Search Google for matching websites
        # 2. Visit and scrape each website
        candidates = self._simulate_website_results(query)
        
        self.candidates.extend(candidates)
        logger.info(f"Website discovery returned {len(candidates)} candidates")
        
        return candidates
    
    def _simulate_website_results(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Simulate website discovery results."""
        candidates = []
        
        import random
        num_results = random.randint(3, 10)
        
        keyword = query.filters.get("keyword", "business")
        location = query.location or "US"
        
        domains = [
            f"{keyword.replace(' ', '')}co.com",
            f"{keyword.replace(' ', '')}solutions.net",
            f"best{keyword.replace(' ', '')}.com",
            f"{keyword.replace(' ', '')}pros.com",
        ]
        
        for i in range(num_results):
            domain = random.choice(domains)
            
            candidate = CandidateBusiness(
                id=str(uuid.uuid4()),
                name=f"{keyword.title()} Company {i+1}",
                address=f"{random.randint(100, 9999)} {random.choice(['Commerce Dr', 'Enterprise Way', 'Business Pkwy'])}",
                city=location.split(",")[0] if "," in location else location,
                state=random.choice(["CA", "TX", "FL", "NY", "IL"]),
                zip_code=f"{random.randint(10000, 99999)}",
                phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                website=f"https://www.{domain}",
                email=f"info@{domain}",
                industry=keyword.title(),
                naics_code=None,
                year_founded=random.randint(1990, 2015),
                employee_count=random.randint(5, 100),
                source=DataSource.WEBSITE,
                source_url=f"https://www.{domain}",
                discovered_at=datetime.utcnow(),
                raw_data={
                    "keyword": keyword,
                    "pages_found": random.randint(5, 50),
                    "has_about_page": True,
                    "has_contact_page": True,
                }
            )
            candidates.append(candidate)
        
        return candidates
    
    def scrape_website(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape business information from a website.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Scraped data dict or None
        """
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        logger.info(f"Scraping website: {url}")
        
        # In production:
        # - Use requests + BeautifulSoup
        # - Respect robots.txt
        # - Handle rate limiting
        # - Extract structured data
        
        return None
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text.
        
        Args:
            text: Text to search
            
        Returns:
            List of valid email addresses
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return list(set(emails))  # Deduplicate
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text.
        
        Args:
            text: Text to search
            
        Returns:
            List of normalized phone numbers
        """
        patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (555) 123-4567
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 555-123-4567
        ]
        
        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Normalize
        normalized = []
        for phone in phones:
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10:
                normalized.append(f"{digits[:3]}-{digits[3:6]}-{digits[6:]}")
            elif len(digits) == 11 and digits[0] == '1':
                normalized.append(f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}")
        
        return list(set(normalized))
    
    def extract_year_founded(self, text: str) -> Optional[int]:
        """Extract year founded from website text.
        
        Args:
            text: Website text content
            
        Returns:
            Year founded or None
        """
        patterns = [
            r'(?:founded|established|since)\s+(?:in\s+)?(\d{4})',
            r'\b(\d{4})\s+(?:founded|established)\b',
            r'(?:since|for)\s+(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    year = int(match.group(1))
                    if 1900 <= year <= datetime.now().year:
                        return year
                except ValueError:
                    pass
        
        return None
    
    def extract_employee_count(self, text: str) -> Optional[int]:
        """Extract employee count from website text.
        
        Args:
            text: Website text content
            
        Returns:
            Employee count or None
        """
        patterns = [
            r'(\d+)\+?\s+(?:employees|team members|staff)',
            r'(?:team of|over|more than)\s+(\d+)',
            r'(\d+)-\d+\s+employees',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        # Check for ranges like "10-50 employees"
        range_match = re.search(r'(\d+)\s*-\s*(\d+)\s+employees', text, re.IGNORECASE)
        if range_match:
            try:
                low = int(range_match.group(1))
                high = int(range_match.group(2))
                return (low + high) // 2
            except ValueError:
                pass
        
        return None
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and scrapable.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
        """
        try:
            parsed = urlparse(url)
            return parsed.scheme in ('http', 'https') and parsed.netloc
        except Exception:
            return False


def discover_from_websites(queries: List[SearchQuery]) -> List[CandidateBusiness]:
    """Convenience function for website discovery.
    
    Args:
        queries: List of search queries
        
    Returns:
        Combined list of candidates from all queries
    """
    discovery = WebsiteDiscovery()
    all_candidates = []
    
    for query in queries:
        if query.source == DataSource.WEBSITE:
            candidates = discovery.search(query)
            all_candidates.extend(candidates)
    
    return all_candidates
