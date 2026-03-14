"""Registry discovery - State business registries."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models import CandidateBusiness, DataSource, SearchQuery

logger = logging.getLogger(__name__)


class RegistryDiscovery:
    """Discovers businesses from state registries."""
    
    # State registry URLs/API endpoints (simulated)
    REGISTRY_ENDPOINTS = {
        "CA": "https://businesssearch.sos.ca.gov",
        "TX": "https://mycpa.cpa.state.tx.us/coa",
        "FL": "https://search.sunbiz.org",
        "NY": "https://apps.dos.ny.gov/publicInquiry",
        "CO": "https://www.sos.state.co.us/biz/BusinessEntityCriteriaExt.do",
    }
    
    def __init__(self):
        self.candidates: List[CandidateBusiness] = []
    
    def search(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Execute registry search for given query.
        
        Args:
            query: Search query with state filter
            
        Returns:
            List of CandidateBusiness objects
        """
        logger.info(f"Registry search: {query.query}")
        
        # In production, scrape or query state registry APIs
        candidates = self._simulate_registry_results(query)
        
        self.candidates.extend(candidates)
        logger.info(f"Registry search returned {len(candidates)} candidates")
        
        return candidates
    
    def _simulate_registry_results(self, query: SearchQuery) -> List[CandidateBusiness]:
        """Simulate registry search results."""
        candidates = []
        
        state = query.filters.get("state", "CA")
        naics = query.filters.get("naics_code")
        
        import random
        num_results = random.randint(10, 50)
        
        # Business entity suffixes by state
        suffixes = {
            "CA": ["Inc.", "LLC", "Corp.", "Ltd."],
            "TX": ["Inc.", "LLC", "Co.", "Company"],
            "FL": ["Inc.", "LLC", "Corp."],
            "NY": ["Inc.", "LLC", "Corp.", "Ltd."],
            "CO": ["LLC", "Inc.", "Ltd."],
        }.get(state, ["LLC", "Inc."])
        
        cities_by_state = {
            "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
            "TX": ["Houston", "Dallas", "Austin", "San Antonio"],
            "FL": ["Miami", "Orlando", "Tampa", "Jacksonville"],
            "NY": ["New York", "Buffalo", "Rochester", "Albany"],
            "CO": ["Denver", "Colorado Springs", "Boulder", "Fort Collins"],
        }
        
        cities = cities_by_state.get(state, ["Unknown City"])
        
        industries_by_naics = {
            "23": "Construction",
            "31": "Manufacturing",
            "42": "Wholesale Trade",
            "44": "Retail Trade",
            "51": "Information",
            "54": "Professional Services",
            "62": "Healthcare",
            "72": "Accommodation/Food",
        }
        
        industry = industries_by_naics.get(naics[:2] if naics else "54", "Services")
        
        for i in range(num_results):
            suffix = random.choice(suffixes)
            company_num = random.randint(1, 9999)
            name = f"{industry} {suffix} {company_num}"
            
            candidate = CandidateBusiness(
                id=str(uuid.uuid4()),
                name=name,
                address=f"{random.randint(100, 9999)} Business Blvd" if random.random() > 0.3 else None,
                city=random.choice(cities),
                state=state,
                zip_code=f"{random.randint(10000, 99999)}",
                phone=None,  # Often not in registry
                website=None,
                email=None,
                industry=industry,
                naics_code=naics,
                year_founded=random.randint(1980, 2022),
                employee_count=None,  # Not typically in registry
                source=DataSource.REGISTRY,
                source_url=self.REGISTRY_ENDPOINTS.get(state, ""),
                discovered_at=datetime.utcnow(),
                raw_data={
                    "state": state,
                    "naics": naics,
                    "entity_type": suffix.replace(".", ""),
                    "filing_status": "Active"
                }
            )
            candidates.append(candidate)
        
        return candidates
    
    def get_entity_details(self, state: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed entity information from registry.
        
        Args:
            state: State code
            entity_id: Registry entity identifier
            
        Returns:
            Entity details dict or None
        """
        logger.info(f"Fetching entity details: {state}/{entity_id}")
        
        # In production, scrape registry page or call API
        return None
    
    def parse_registry_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse business data from registry HTML.
        
        Args:
            html_content: Raw HTML from registry
            
        Returns:
            List of parsed business records
        """
        # In production, use BeautifulSoup or similar
        # For now, return empty list
        return []


def discover_from_registry(queries: List[SearchQuery]) -> List[CandidateBusiness]:
    """Convenience function for registry discovery.
    
    Args:
        queries: List of search queries
        
    Returns:
        Combined list of candidates from all queries
    """
    discovery = RegistryDiscovery()
    all_candidates = []
    
    for query in queries:
        if query.source == DataSource.REGISTRY:
            candidates = discovery.search(query)
            all_candidates.extend(candidates)
    
    return all_candidates
