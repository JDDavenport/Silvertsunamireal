import asyncio
import aiohttp
from typing import Optional, Dict
import re

class ContactEnrichmentService:
    """Enrich business data with real contact information"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def enrich_from_website(self, website: str) -> Dict:
        """Extract contact info from business website"""
        if not website:
            return {}
        
        try:
            async with self.session.get(website, timeout=10) as resp:
                if resp.status != 200:
                    return {}
                
                html = await resp.text()
                
                # Extract email
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, html)
                
                # Filter out common false positives
                valid_emails = [
                    e for e in emails 
                    if not any(x in e.lower() for x in ['example', 'domain', 'test', 'email', 'info@domain'])
                ]
                
                # Extract phone
                phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
                phones = re.findall(phone_pattern, html)
                
                return {
                    'email': valid_emails[0] if valid_emails else None,
                    'phone': self._normalize_phone(phones[0]) if phones else None,
                    'emails_found': list(set(valid_emails))[:5],  # Top 5 unique emails
                    'phones_found': list(set(phones))[:3]  # Top 3 unique phones
                }
        except Exception as e:
            print(f"Error enriching from website {website}: {e}")
            return {}
    
    async def enrich_from_google(self, business_name: str, city: str, state: str) -> Dict:
        """Search Google for business contact info"""
        # This would require a Google Places API key
        # For now, return empty - can be implemented with SERP API or similar
        return {}
    
    async def enrich_from_linkedin(self, company_name: str) -> Dict:
        """Find company page on LinkedIn"""
        # This requires LinkedIn API or scraping
        # Return empty for now
        return {}
    
    async def find_owner_name(self, entity_id: str, state: str = "UT") -> Optional[str]:
        """Find business owner name from state records"""
        # For Utah, this would require deeper scraping of the corporation details
        # Many states list officers/registered agents
        return None
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to standard format"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone
    
    async def enrich_lead(self, lead: Dict) -> Dict:
        """Enrich a lead with all available contact methods"""
        print(f"🔍 Enriching {lead.get('name', 'Unknown')}...")
        
        enriched = {
            'email': lead.get('email'),
            'phone': lead.get('phone'),
            'website': lead.get('website'),
            'owner_name': None,
            'linkedin_url': None
        }
        
        # Try website enrichment
        if lead.get('website'):
            website_data = await self.enrich_from_website(lead['website'])
            enriched['email'] = website_data.get('email') or enriched['email']
            enriched['phone'] = website_data.get('phone') or enriched['phone']
        
        # Try Google search enrichment
        google_data = await self.enrich_from_google(
            lead.get('name', ''),
            lead.get('city', ''),
            lead.get('state', '')
        )
        enriched.update(google_data)
        
        # Try LinkedIn
        linkedin_data = await self.enrich_from_linkedin(lead.get('name', ''))
        enriched.update(linkedin_data)
        
        print(f"✅ Enrichment complete: email={enriched.get('email') is not None}, phone={enriched.get('phone') is not None}")
        
        return enriched

# Test
async def test_enrichment():
    """Test the enrichment service"""
    async with ContactEnrichmentService() as service:
        # Test with a known website
        result = await service.enrich_from_website("https://www.google.com")
        print(f"Found: {result}")

if __name__ == "__main__":
    asyncio.run(test_enrichment())
