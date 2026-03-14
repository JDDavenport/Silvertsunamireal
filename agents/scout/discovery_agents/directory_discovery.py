"""Directory discovery - Google Maps style business listings."""
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from models import CandidateBusiness, DataSource, SearchQuery

logger = logging.getLogger(__name__)


class DirectoryDiscovery:
    """Discovers businesses from directory listings."""
    
    def __init__(self):
        self.candidates: List[CandidateBusiness] = []
    
    def search(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Execute directory search for given query.
        
        Args:
            query: Search query with parameters
            
        Returns:
            List of CandidateBusiness objects
        """
        logger.info(f"Directory search: {query.query}")
        
        # In production, this would call Google Places API, Yelp, etc.
        # For now, return simulated results based on query
        candidates = self._simulate_directory_results(query)
        
        self.candidates.extend(candidates)
        logger.info(f"Directory search returned {len(candidates)} candidates")
        
        return candidates
    
    def _simulate_directory_results(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Simulate directory search results."""
        candidates = []
        
        # Extract industry and location from query
        parts = query.query.split(" in ")
        industry = parts[0] if len(parts) > 0 else "business"
        location = parts[1] if len(parts) > 1 else query.location or "Unknown"
        
        # Generate 5-15 simulated results
        import random
        num_results = random.randint(5, 15)
        
        business_types = {
            "plumbing": ["Mike's Plumbing", "Fast Flow Plumbing", "Premier Pipes"],
            "electrician": ["Bright Spark Electric", "PowerUp Electric", "Wired Right"],
            "hvac": ["Cool Air Systems", "Comfort Heating & Cooling", "Climate Control"],
            "restaurant": ["Bistro Central", "The Corner Table", "Savory Spot"],
            "salon": ["Elegance Hair Studio", "Style Masters", "Cut Above"],
            "auto repair": ["Quick Fix Auto", "Reliable Motors", "Precision Auto Care"],
        }
        
        base_names = business_types.get(industry, [f"{industry.title()} Solutions", f"Premier {industry.title()}"])
        
        for i in range(num_results):
            name = f"{random.choice(base_names)} {random.choice(['LLC', 'Inc', ''])}".strip()
            
            candidate = CandidateBusiness(
                id=str(uuid.uuid4()),
                name=name,
                address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Park Rd', 'Market St'])}",
                city=location.split(",")[0].strip() if "," in location else location,
                state=location.split(",")[1].strip() if "," in location else random.choice(["CA", "TX", "FL", "NY"]),
                zip_code=f"{random.randint(10000, 99999)}",
                phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                website=f"https://www.{name.lower().replace(' ', '').replace('\u0026', 'and')}.com" if random.random() > 0.2 else None,
                email=None,  # Will be discovered later
                industry=industry.title(),
                naics_code=None,
                year_founded=random.randint(1990, 2020) if random.random() > 0.3 else None,
                employee_count=random.randint(2, 50) if random.random() > 0.4 else None,
                source=DataSource.DIRECTORY,
                source_url=f"https://maps.google.com/search?q={query.query.replace(' ', '+')}",
                discovered_at=datetime.utcnow(),
                raw_data={"query": query.query, "location": query.location}
            )
            candidates.append(candidate)
        
        return candidates
    
    def extract_details(self, place_id: str) -> Optional[CandidateBusiness]:
        """Extract detailed business information from directory.
        
        Args:
            place_id: Directory-specific place identifier
            
        Returns:
            Enriched CandidateBusiness or None
        """
        logger.info(f"Extracting details for place: {place_id}")
        
        # In production, call directory API for full details
        # For now, return None (simulating no additional data)
        return None
    
    def parse_phone(self, phone_str: str) -> Optional[str]:
        """Normalize phone number format.
        
        Args:
            phone_str: Raw phone string
            
        Returns:
            Normalized phone number or None
        """
        digits = re.sub(r'\D', '', phone_str)
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
        return None
    
    def extract_website(self, listing_data: Dict[str, Any]) -> Optional[str]:
        """Extract and validate website URL.
        
        Args:
            listing_data: Raw listing data
            
        Returns:
            Validated URL or None
        """
        url = listing_data.get("website") or listing_data.get("url")
        if not url:
            return None
        
        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        # Simple regex check
        if re.match(r'^https?://[^\s/$.?#].[^\s]*$', url, re.IGNORECASE):
            return url
        
        return None


def discover_from_directory(queries: List[SearchQuery]) -> List[CandidateBusiness]:
    """Convenience function for directory discovery.
    
    Args:
        queries: List of search queries
        
    Returns:
        Combined list of candidates from all queries
    """
    discovery = DirectoryDiscovery()
    all_candidates = []
    
    for query in queries:
        if query.source == DataSource.DIRECTORY:
            candidates = discovery.search(query)
            all_candidates.extend(candidates)
    
    return all_candidates
