import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from datetime import datetime
import json

class UtahCorporationsScraper:
    """Scrape Utah Division of Corporations for business entities"""
    
    BASE_URL = "https://secure.utah.gov/bes"
    
    async def search_businesses(
        self, 
        keyword: str = "", 
        entity_type: str = "", 
        min_age_years: int = 15
    ) -> List[Dict]:
        """Search for businesses registered in Utah"""
        businesses = []
        
        # Search parameters
        params = {
            'search': 'true',
            'businessname': keyword,
            'entitytype': entity_type,  # LLC, CORPORATION, etc.
            'status': 'Active'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/search.html", params=params) as resp:
                if resp.status != 200:
                    return []
                
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse search results table
                rows = soup.find_all('tr', class_='searchResult')
                
                for row in rows:
                    try:
                        cells = row.find_all('td')
                        if len(cells) < 4:
                            continue
                        
                        name = cells[0].text.strip()
                        entity_id = cells[1].text.strip()
                        entity_type = cells[2].text.strip()
                        registration_date = cells[3].text.strip()
                        
                        # Parse registration date
                        try:
                            reg_date = datetime.strptime(registration_date, '%m/%d/%Y')
                            age_years = (datetime.now() - reg_date).days / 365
                        except:
                            continue
                        
                        # Filter by age
                        if age_years < min_age_years:
                            continue
                        
                        # Get detailed info
                        detail_url = cells[0].find('a')['href'] if cells[0].find('a') else None
                        
                        business = {
                            'name': name,
                            'entity_id': entity_id,
                            'entity_type': entity_type,
                            'registration_date': registration_date,
                            'age_years': round(age_years, 1),
                            'state': 'UT',
                            'source': 'Utah Division of Corporations',
                            'detail_url': detail_url
                        }
                        
                        businesses.append(business)
                        
                    except Exception as e:
                        print(f"Error parsing row: {e}")
                        continue
        
        return businesses
    
    async def get_business_details(self, entity_id: str) -> Optional[Dict]:
        """Get detailed information about a specific business"""
        url = f"{self.BASE_URL}/details.html?entity={entity_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                details = {
                    'entity_id': entity_id,
                    'principal_address': '',
                    'mailing_address': '',
                    'registered_agent': '',
                    'officers': [],
                    'status': ''
                }
                
                # Parse details table
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            label = cells[0].text.strip().lower()
                            value = cells[1].text.strip()
                            
                            if 'principal' in label and 'address' in label:
                                details['principal_address'] = value
                            elif 'mailing' in label and 'address' in label:
                                details['mailing_address'] = value
                            elif 'registered agent' in label:
                                details['registered_agent'] = value
                            elif 'status' in label:
                                details['status'] = value
                
                return details

class BizBuySellScraper:
    """Scrape BizBuySell for businesses for sale"""
    
    BASE_URL = "https://www.bizbuysell.com"
    
    async def search_listings(
        self,
        state: str = "utah",
        industry: str = "",
        min_revenue: int = 0,
        max_revenue: int = 10000000,
        page: int = 1
    ) -> List[Dict]:
        """Search for business listings on BizBuySell"""
        listings = []
        
        # Construct search URL
        url = f"{self.BASE_URL}/{state}-businesses-for-sale/"
        if industry:
            url = f"{self.BASE_URL}/{state}/{industry}-businesses-for-sale/"
        
        params = {
            'page': page,
            'q': f'RevenueMin={min_revenue}&RevenueMax={max_revenue}'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch: {resp.status}")
                    return []
                
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find listing cards
                cards = soup.find_all('div', class_='listing-card') or soup.find_all('div', {'data-listing-id': True})
                
                for card in cards:
                    try:
                        # Extract listing data
                        title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='title')
                        title = title_elem.text.strip() if title_elem else 'Unknown'
                        
                        link_elem = card.find('a', href=True)
                        listing_url = link_elem['href'] if link_elem else ''
                        if listing_url and not listing_url.startswith('http'):
                            listing_url = f"{self.BASE_URL}{listing_url}"
                        
                        # Extract financials
                        price_elem = card.find('div', class_='price') or card.find('span', class_='asking-price')
                        price_text = price_elem.text.strip() if price_elem else ''
                        price = self._parse_price(price_text)
                        
                        revenue_elem = card.find('div', class_='revenue') or card.find('span', class_='revenue')
                        revenue_text = revenue_elem.text.strip() if revenue_elem else ''
                        revenue = self._parse_price(revenue_text)
                        
                        # Extract location
                        location_elem = card.find('div', class_='location') or card.find('span', class_='location')
                        location = location_elem.text.strip() if location_elem else state
                        
                        # Extract description
                        desc_elem = card.find('div', class_='description') or card.find('p')
                        description = desc_elem.text.strip()[:200] if desc_elem else ''
                        
                        listing = {
                            'name': title,
                            'listing_url': listing_url,
                            'asking_price': price,
                            'revenue': revenue,
                            'location': location,
                            'state': state.upper(),
                            'description': description,
                            'industry': industry or 'Business Services',
                            'source': 'BizBuySell',
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        listings.append(listing)
                        
                    except Exception as e:
                        print(f"Error parsing listing: {e}")
                        continue
        
        return listings
    
    def _parse_price(self, price_text: str) -> int:
        """Parse price text like '$1,250,000' or '$1.2M' to integer"""
        try:
            # Remove $ and commas
            clean = price_text.replace('$', '').replace(',', '').strip()
            
            # Handle K/M suffixes
            if 'M' in clean.upper():
                return int(float(clean.upper().replace('M', '')) * 1000000)
            elif 'K' in clean.upper():
                return int(float(clean.upper().replace('K', '')) * 1000)
            else:
                return int(float(clean))
        except:
            return 0

class LinkedInScraper:
    """Scrape LinkedIn for business intelligence (requires authentication)"""
    
    BASE_URL = "https://www.linkedin.com"
    
    async def search_companies(
        self,
        keywords: List[str],
        location: str = "Utah",
        company_size: str = "11-50"  # 11-50, 51-200, 201-500, etc.
    ) -> List[Dict]:
        """Search for companies on LinkedIn"""
        # Note: LinkedIn scraping requires session cookies/authentication
        # This is a placeholder for the structure
        
        companies = []
        
        # Would need to:
        # 1. Authenticate with LinkedIn credentials
        # 2. Navigate to company search
        # 3. Apply filters
        # 4. Extract company data
        
        return companies

class IndustryDirectoryScraper:
    """Scrape industry-specific directories"""
    
    async def search_construction_companies(self, state: str = "UT") -> List[Dict]:
        """Search construction companies from industry directories"""
        # Example: BlueBook, Dodge Data, etc.
        return []
    
    async def search_manufacturing_companies(self, state: str = "UT") -> List[Dict]:
        """Search manufacturing companies from industry directories"""
        # Example: ThomasNet, MFG.com, etc.
        return []
    
    async def search_healthcare_providers(self, state: str = "UT") -> List[Dict]:
        """Search healthcare businesses"""
        # Example: CMS databases, state health dept
        return []

# Test function
async def test_scrapers():
    """Test the scrapers"""
    print("Testing Utah Corporations Scraper...")
    utah = UtahCorporationsScraper()
    
    # Search for LLCs registered 15+ years ago
    businesses = await utah.search_businesses(
        keyword="",
        entity_type="LLC",
        min_age_years=15
    )
    
    print(f"Found {len(businesses)} Utah LLCs 15+ years old")
    for b in businesses[:3]:
        print(f"  - {b['name']} ({b['age_years']} years)")
    
    print("\nTesting BizBuySell Scraper...")
    bbs = BizBuySellScraper()
    
    listings = await bbs.search_listings(
        state="utah",
        min_revenue=1000000,
        page=1
    )
    
    print(f"Found {len(listings)} BizBuySell listings")
    for l in listings[:3]:
        print(f"  - {l['name']} - ${l['revenue']:,.0f} revenue")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
