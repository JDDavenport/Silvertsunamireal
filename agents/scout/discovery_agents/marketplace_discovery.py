"""Marketplace discovery - BizBuySell, BizQuest, etc."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from models import CandidateBusiness, DataSource, SearchQuery

logger = logging.getLogger(__name__)


class MarketplaceDiscovery:
    """Discovers businesses from sale marketplaces."""
    
    MARKETPLACES = {
        "bizbuysell": "https://www.bizbuysell.com",
        "bizquest": "https://www.bizquest.com",
        "businessforsale": "https://www.businessesforsale.com",
    }
    
    def __init__(self):
        self.candidates: List[CandidateBusiness] = []
    
    def search(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Execute marketplace search for given query.
        
        Args:
            query: Search query with filters
            
        Returns:
            List of CandidateBusiness objects
        """
        logger.info(f"Marketplace search: {query.query}")
        
        # In production, scrape marketplace listings
        candidates = self._simulate_marketplace_results(query)
        
        self.candidates.extend(candidates)
        logger.info(f"Marketplace search returned {len(candidates)} candidates")
        
        return candidates
    
    def _simulate_marketplace_results(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Simulate marketplace search results."""
        candidates = []
        
        import random
        num_results = random.randint(3, 20)
        
        location = query.location or "Nationwide"
        industry = query.filters.get("industry", "Services")
        
        price_min = query.filters.get("price_min", 100000)
        price_max = query.filters.get("price_max", 5000000)
        
        revenue_min = query.filters.get("revenue_min", 200000)
        revenue_max = query.filters.get("revenue_max", 10000000)
        
        business_templates = [
            f"Profitable {industry} Business",
            f"Established {industry} Company",
            f"Growing {industry} Opportunity",
            f"Turnkey {industry} Operation",
        ]
        
        cities = ["Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
                  "San Antonio", "San Diego", "Dallas", "San Jose", "Austin"]
        
        for i in range(num_results):
            asking_price = Decimal(random.randint(int(price_min), int(price_max)))
            revenue = Decimal(random.randint(int(revenue_min), int(revenue_max)))
            cash_flow = revenue * Decimal(random.uniform(0.15, 0.35))
            
            template = random.choice(business_templates)
            listing_num = random.randint(1000, 999999)
            name = f"{template} #{listing_num}"
            
            city = random.choice(cities)
            
            candidate = CandidateBusiness(
                id=str(uuid.uuid4()),
                name=name,
                address=None,  # Often not disclosed publicly
                city=city,
                state=random.choice(["CA", "TX", "FL", "NY", "IL"]),
                zip_code=None,
                phone=None,  # Contact through broker
                website=None,  # Confidential
                email=None,
                industry=industry,
                naics_code=None,
                year_founded=random.randint(1995, 2018),
                employee_count=random.randint(3, 75),
                revenue_estimate=revenue,
                sde_estimate=cash_flow,
                source=DataSource.MARKETPLACE,
                source_url=f"{self.MARKETPLACES['bizbuysell']}/{industry.lower().replace(' ', '-')}-listings",
                discovered_at=datetime.utcnow(),
                raw_data={
                    "asking_price": float(asking_price),
                    "cash_flow": float(cash_flow),
                    "listing_id": listing_num,
                    "broker": f"Business Broker {random.randint(1, 100)}",
                    "reason_selling": random.choice(["Retirement", "Relocation", "New Venture", "Health"]),
                }
            )
            candidates.append(candidate)
        
        return candidates
    
    def get_listing_details(self, marketplace: str, listing_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed listing information.
        
        Args:
            marketplace: Marketplace name
            listing_id: Listing identifier
            
        Returns:
            Listing details dict or None
        """
        logger.info(f"Fetching listing details: {marketplace}/{listing_id}")
        
        # In production, scrape listing page
        return None
    
    def parse_financials(self, financial_text: str) -> Dict[str, Optional[Decimal]]:
        """Parse financial data from listing text.
        
        Args:
            financial_text: Raw financial text
            
        Returns:
            Dict with revenue, cash_flow, etc.
        """
        import re
        
        results = {
            "revenue": None,
            "cash_flow": None,
            "asking_price": None,
        }
        
        # Pattern matching for financial data
        patterns = {
            "revenue": r'(?:Gross Revenue|Revenue)[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            "cash_flow": r'(?:Cash Flow|SDE|Seller Discretionary)[:\s]*\$?([\d,]+(?:\.\d{2})?)',
            "asking_price": r'(?:Asking Price|Price)[:\s]*\$?([\d,]+(?:\.\d{2})?)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, financial_text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace(",", "")
                    results[key] = Decimal(value_str)
                except (ValueError, IndexError):
                    pass
        
        return results


def discover_from_marketplace(queries: List[SearchQuery]) -> List[CandidateBusiness]:
    """Convenience function for marketplace discovery.
    
    Args:
        queries: List of search queries
        
    Returns:
        Combined list of candidates from all queries
    """
    discovery = MarketplaceDiscovery()
    all_candidates = []
    
    for query in queries:
        if query.source == DataSource.MARKETPLACE:
            candidates = discovery.search(query)
            all_candidates.extend(candidates)
    
    return all_candidates
