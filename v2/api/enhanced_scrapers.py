import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from datetime import datetime
import json
import os

class GoogleSearchScraper:
    """Search Google for businesses (requires SERP API or similar)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search"
    
    async def search_businesses(
        self, 
        query: str,
        location: str = "Utah",
        num_results: int = 10
    ) -> List[Dict]:
        """Search Google for businesses"""
        if not self.api_key:
            print("⚠️ No SERPAPI_KEY found. Set it to use Google Search.")
            return []
        
        params = {
            'engine': 'google',
            'q': query,
            'location': location,
            'num': num_results,
            'api_key': self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as resp:
                if resp.status != 200:
                    print(f"SERP API error: {resp.status}")
                    return []
                
                data = await resp.json()
                results = []
                
                # Parse organic results
                for item in data.get('organic_results', [])[:num_results]:
                    results.append({
                        'name': self._extract_business_name(item.get('title', '')),
                        'title': item.get('title'),
                        'link': item.get('link'),
                        'snippet': item.get('snippet'),
                        'source': 'Google Search'
                    })
                
                return results
    
    def _extract_business_name(self, title: str) -> str:
        """Extract business name from search result title"""
        # Remove common suffixes
        name = re.sub(r'\s*[-|]\s*(Home|Official|Website|Contact).*$', '', title, flags=re.I)
        return name.strip()

class LinkedInCompanyScraper:
    """Scrape LinkedIn for company information"""
    
    BASE_URL = "https://www.linkedin.com"
    
    async def search_companies(
        self,
        industry: str,
        location: str = "Utah",
        company_size: str = "11-50"
    ) -> List[Dict]:
        """Search for companies on LinkedIn"""
        # Note: LinkedIn requires authentication and has strong anti-scraping
        # This is a structure for future implementation
        
        # Would need:
        # 1. LinkedIn session cookies or API access
        # 2. Navigate to /search/results/companies/
        # 3. Apply filters (industry, location, size)
        # 4. Extract company data
        
        return []
    
    async def get_company_info(self, company_slug: str) -> Optional[Dict]:
        """Get detailed company info from LinkedIn"""
        # Would scrape /company/{slug}/about/
        return None

class ThomasNetScraper:
    """Scrape ThomasNet for manufacturing companies"""
    
    BASE_URL = "https://www.thomasnet.com"
    
    async def search_manufacturers(
        self,
        category: str,
        state: str = "UT",
        page: int = 1
    ) -> List[Dict]:
        """Search for manufacturers on ThomasNet"""
        search_url = f"{self.BASE_URL}/search.html"
        
        params = {
            'search': category,
            'state': state,
            'page': page
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    return []
                
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                # Parse manufacturer cards
                cards = soup.find_all('div', class_='supplier-card')
                
                for card in cards:
                    try:
                        name_elem = card.find('h2', class_='supplier-name')
                        name = name_elem.text.strip() if name_elem else 'Unknown'
                        
                        link_elem = card.find('a', href=True)
                        profile_url = link_elem['href'] if link_elem else ''
                        
                        location_elem = card.find('span', class_='location')
                        location = location_elem.text.strip() if location_elem else ''
                        
                        desc_elem = card.find('p', class_='description')
                        description = desc_elem.text.strip() if desc_elem else ''
                        
                        results.append({
                            'name': name,
                            'profile_url': profile_url,
                            'location': location,
                            'description': description,
                            'industry': 'Manufacturing',
                            'source': 'ThomasNet'
                        })
                    except Exception as e:
                        continue
                
                return results

class YelpScraper:
    """Scrape Yelp for local businesses"""
    
    BASE_URL = "https://www.yelp.com"
    
    async def search_businesses(
        self,
        category: str,
        location: str = "Salt Lake City, UT",
        page: int = 0
    ) -> List[Dict]:
        """Search for businesses on Yelp"""
        search_url = f"{self.BASE_URL}/search"
        
        params = {
            'find_desc': category,
            'find_loc': location,
            'start': page * 10
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    return []
                
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                # Parse business listings
                listings = soup.find_all('div', {'data-testid': 'serp-ia-card'})
                
                for listing in listings:
                    try:
                        name_elem = listing.find('a', class_='css-19v1rkv')
                        name = name_elem.text.strip() if name_elem else 'Unknown'
                        
                        link_elem = listing.find('a', href=True)
                        business_url = link_elem['href'] if link_elem else ''
                        
                        rating_elem = listing.find('span', class_='css-gutk1c')
                        rating = rating_elem.text.strip() if rating_elem else ''
                        
                        review_elem = listing.find('span', class_='css-chan6m')
                        reviews = review_elem.text.strip() if review_elem else ''
                        
                        results.append({
                            'name': name,
                            'yelp_url': f"{self.BASE_URL}{business_url}" if business_url else '',
                            'rating': rating,
                            'reviews': reviews,
                            'category': category,
                            'source': 'Yelp'
                        })
                    except Exception as e:
                        continue
                
                return results

class IndustryDatabaseScraper:
    """Scrape various industry databases"""
    
    async def search_healthcare_providers(
        self,
        state: str = "UT",
        specialty: str = ""
    ) -> List[Dict]:
        """Search CMS healthcare provider database"""
        # Would use CMS API or scraping
        return []
    
    async def search_contractors(
        self,
        state: str = "UT",
        trade: str = ""
    ) -> List[Dict]:
        """Search contractor licensing databases"""
        # State-specific contractor databases
        return []
    
    async def search_professional_services(
        self,
        state: str = "UT",
        profession: str = ""
    ) -> List[Dict]:
        """Search state licensing boards (CPAs, attorneys, etc.)"""
        return []

class EnhancedDiscoveryService:
    """Enhanced discovery with multiple real data sources"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.google_search = GoogleSearchScraper()
        self.linkedin = LinkedInCompanyScraper()
        self.thomasnet = ThomasNetScraper()
        self.yelp = YelpScraper()
        self.industry_db = IndustryDatabaseScraper()
    
    async def discover_from_all_sources(
        self,
        user_id: str,
        criteria: Dict
    ) -> Dict[str, List[Dict]]:
        """Discover leads from all available sources"""
        
        results = {
            'utah_corps': [],
            'bizbuysell': [],
            'google_search': [],
            'thomasnet': [],
            'yelp': [],
            'linkedin': []
        }
        
        industries = criteria.get('industries', ['Technology', 'Services'])
        locations = criteria.get('location', ['UT'])
        
        # Run all scrapers in parallel
        tasks = []
        
        # Utah Corps (already implemented)
        from real_scrapers import UtahCorporationsScraper
        utah_scraper = UtahCorporationsScraper()
        tasks.append(self._scrape_utah_corps(utah_scraper, criteria))
        
        # BizBuySell (already implemented)
        from real_scrapers import BizBuySellScraper
        bbs_scraper = BizBuySellScraper()
        tasks.append(self._scrape_bizbuysell(bbs_scraper, criteria))
        
        # Google Search (if API key available)
        if os.getenv('SERPAPI_KEY'):
            tasks.append(self._scrape_google_search(criteria))
        
        # ThomasNet for manufacturing
        if 'Manufacturing' in industries:
            tasks.append(self._scrape_thomasnet(criteria))
        
        # Yelp for local businesses
        tasks.append(self._scrape_yelp(criteria))
        
        # Run all tasks
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def _scrape_utah_corps(self, scraper, criteria):
        """Scrape Utah Division of Corporations"""
        # Implementation from real_scrapers.py
        pass
    
    async def _scrape_bizbuysell(self, scraper, criteria):
        """Scrape BizBuySell"""
        # Implementation from real_scrapers.py
        pass
    
    async def _scrape_google_search(self, criteria):
        """Scrape Google Search"""
        results = []
        for industry in criteria.get('industries', ['business'])[:2]:
            query = f"{industry} companies for sale Utah"
            businesses = await self.google_search.search_businesses(query, "Utah")
            results.extend(businesses)
        return results
    
    async def _scrape_thomasnet(self, criteria):
        """Scrape ThomasNet for manufacturers"""
        results = []
        keywords = ['manufacturing', 'fabrication', 'industrial']
        for keyword in keywords[:2]:
            manufacturers = await self.thomasnet.search_manufacturers(
                keyword, 
                criteria.get('location', ['UT'])[0]
            )
            results.extend(manufacturers)
        return results
    
    async def _scrape_yelp(self, criteria):
        """Scrape Yelp for local businesses"""
        results = []
        categories = ['contractors', 'professional services', 'auto repair']
        location = f"{criteria.get('location', ['Salt Lake City'])[0]}, UT"
        
        for category in categories[:2]:
            businesses = await self.yelp.search_businesses(category, location)
            results.extend(businesses)
        return results

# Export all scrapers
__all__ = [
    'GoogleSearchScraper',
    'LinkedInCompanyScraper',
    'ThomasNetScraper',
    'YelpScraper',
    'IndustryDatabaseScraper',
    'EnhancedDiscoveryService'
]
