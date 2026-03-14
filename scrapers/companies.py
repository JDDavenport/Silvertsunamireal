"""Example company scraper implementation."""

import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from base import BaseScraper


class CompanyScraper(BaseScraper):
    """Scraper for company acquisition data."""
    
    def __init__(self):
        super().__init__(
            name="company_scraper",
            base_url="https://example.com",
            rate_limit=1.5
        )
    
    def extract(self, response) -> Dict[str, Any]:
        """Extract company data from HTML response."""
        soup = BeautifulSoup(response.content, 'lxml')
        
        companies = []
        
        # Example extraction logic
        for item in soup.find_all('div', class_='company-item'):
            company = {
                'name': self._extract_text(item, '.company-name'),
                'industry': self._extract_text(item, '.industry'),
                'revenue': self._extract_revenue(item),
                'employees': self._extract_employees(item),
                'location': self._extract_text(item, '.location'),
                'source_url': response.url,
            }
            companies.append(company)
        
        return {
            'companies': companies,
            'total_found': len(companies),
            'source': self.name,
        }
    
    def _extract_text(self, soup, selector: str) -> str:
        """Safely extract text from element."""
        elem = soup.select_one(selector)
        return elem.get_text(strip=True) if elem else ''
    
    def _extract_revenue(self, soup) -> Optional[float]:
        """Extract and parse revenue value."""
        text = self._extract_text(soup, '.revenue')
        # Parse formats like "$5.2M" or "$1.2 billion"
        match = re.search(r'\$([\d.]+)\s*(M|B|million|billion)?', text, re.I)
        if match:
            value = float(match.group(1))
            multiplier = match.group(2) or ''
            if multiplier.lower() in ('b', 'billion'):
                value *= 1000
            return value
        return None
    
    def _extract_employees(self, soup) -> Optional[int]:
        """Extract employee count."""
        text = self._extract_text(soup, '.employees')
        match = re.search(r'(\d+)', text.replace(',', ''))
        return int(match.group(1)) if match else None


if __name__ == '__main__':
    # Example usage
    with CompanyScraper() as scraper:
        # Replace with actual URL
        data = scraper.scrape('/companies-for-sale')
        print(f"Scraped {data['total_found']} companies")
