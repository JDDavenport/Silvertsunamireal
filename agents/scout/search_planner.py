"""Search planner - generates search strategies from normalized constraints."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models import (
    NormalizedConstraints, SearchPlan, SearchQuery, DataSource,
    Geography, IndustryRule
)

logger = logging.getLogger(__name__)


class SearchPlanner:
    """Generates search strategies for business discovery."""
    
    DATA_SOURCE_WEIGHTS = {
        DataSource.DIRECTORY: 8,
        DataSource.REGISTRY: 7,
        DataSource.MARKETPLACE: 9,
        DataSource.WEBSITE: 6,
    }
    
    def __init__(self):
        self.queries: List[SearchQuery] = []
    
    def generate_plan(self, constraints: NormalizedConstraints) -> SearchPlan:
        """Generate complete search plan from constraints.
        
        Args:
            constraints: Normalized and validated persona constraints
            
        Returns:
            SearchPlan with queries and sources
        """
        self.queries = []
        
        if not constraints.valid:
            logger.error(f"Cannot generate plan for invalid constraints: {constraints.persona_id}")
            return SearchPlan(
                persona_id=constraints.persona_id,
                queries=[],
                sources=[],
                estimated_total_results=0,
                geographic_coverage=[]
            )
        
        # Determine geographic coverage
        geo_coverage = self._plan_geographic_coverage(constraints.geography)
        
        # Generate queries for each data source
        self._generate_directory_queries(constraints, geo_coverage)
        self._generate_registry_queries(constraints, geo_coverage)
        self._generate_marketplace_queries(constraints, geo_coverage)
        self._generate_website_queries(constraints, geo_coverage)
        
        # Calculate totals
        estimated_total = sum(q.estimated_results for q in self.queries)
        sources_used = list(set(q.source for q in self.queries))
        
        logger.info(f"Generated search plan for {constraints.persona_id}: "
                   f"{len(self.queries)} queries, {estimated_total} estimated results")
        
        return SearchPlan(
            persona_id=constraints.persona_id,
            queries=self.queries,
            sources=sources_used,
            estimated_total_results=estimated_total,
            geographic_coverage=geo_coverage
        )
    
    def _plan_geographic_coverage(self, geography: Geography) -> List[str]:
        """Determine geographic areas to cover.
        
        Args:
            geography: Normalized geography constraints
            
        Returns:
            List of geographic search areas
        """
        coverage = []
        
        if geography.zip_codes:
            coverage.extend(geography.zip_codes)
        
        if geography.cities:
            for city in geography.cities:
                state_suffix = ""
                if geography.states and len(geography.states) == 1:
                    state_suffix = f", {geography.states[0]}"
                coverage.append(f"{city}{state_suffix}")
        
        if geography.states and not coverage:
            coverage.extend(geography.states)
        
        if not coverage and geography.countries:
            coverage = geography.countries
        
        return coverage
    
    def _generate_directory_queries(
        self, 
        constraints: NormalizedConstraints,
        geo_coverage: List[str]
    ) -> None:
        """Generate queries for directory sources (Google Maps, Yelp, etc.)."""
        if not constraints.industry_rules:
            return
        
        industries = constraints.industry_rules.include
        if not industries:
            industries = constraints.industry_rules.keywords
        
        for location in geo_coverage[:10]:  # Limit to top 10 locations
            for industry in industries[:5]:  # Limit to top 5 industries
                query = f"{industry} in {location}"
                self.queries.append(SearchQuery(
                    source=DataSource.DIRECTORY,
                    query=query,
                    location=location,
                    filters={
                        "industry": industry,
                        "has_website": True
                    },
                    priority=self.DATA_SOURCE_WEIGHTS[DataSource.DIRECTORY],
                    estimated_results=50
                ))
        
        # Add keyword-based queries
        for keyword in constraints.industry_rules.keywords[:3]:
            for location in geo_coverage[:5]:
                self.queries.append(SearchQuery(
                    source=DataSource.DIRECTORY,
                    query=f"{keyword} business {location}",
                    location=location,
                    filters={"keyword": keyword},
                    priority=self.DATA_SOURCE_WEIGHTS[DataSource.DIRECTORY] - 1,
                    estimated_results=30
                ))
    
    def _generate_registry_queries(
        self,
        constraints: NormalizedConstraints,
        geo_coverage: List[str]
    ) -> None:
        """Generate queries for state business registries."""
        if not constraints.geography or not constraints.geography.states:
            return
        
        states = constraints.geography.states[:10]
        
        for state in states:
            filters: Dict[str, Any] = {"state": state}
            
            if constraints.industry_rules and constraints.industry_rules.naics_codes:
                for naics in constraints.industry_rules.naics_codes[:3]:
                    filters["naics_code"] = naics
                    self.queries.append(SearchQuery(
                        source=DataSource.REGISTRY,
                        query=f"businesses in {state} NAICS {naics}",
                        location=state,
                        filters=filters.copy(),
                        priority=self.DATA_SOURCE_WEIGHTS[DataSource.REGISTRY],
                        estimated_results=100
                    ))
            else:
                self.queries.append(SearchQuery(
                    source=DataSource.REGISTRY,
                    query=f"active businesses in {state}",
                    location=state,
                    filters=filters,
                    priority=self.DATA_SOURCE_WEIGHTS[DataSource.REGISTRY],
                    estimated_results=500
                ))
    
    def _generate_marketplace_queries(
        self,
        constraints: NormalizedConstraints,
        geo_coverage: List[str]
    ) -> None:
        """Generate queries for business marketplaces (BizBuySell, BizQuest)."""
        filters: Dict[str, Any] = {"status": "active"}
        
        if constraints.financial_target:
            ft = constraints.financial_target
            if ft.asking_price_min:
                filters["price_min"] = float(ft.asking_price_min)
            if ft.asking_price_max:
                filters["price_max"] = float(ft.asking_price_max)
            if ft.revenue_min:
                filters["revenue_min"] = float(ft.revenue_min)
            if ft.revenue_max:
                filters["revenue_max"] = float(ft.revenue_max)
        
        if constraints.industry_rules and constraints.industry_rules.include:
            for industry in constraints.industry_rules.include[:3]:
                filters["industry"] = industry
                for location in geo_coverage[:5]:
                    self.queries.append(SearchQuery(
                        source=DataSource.MARKETPLACE,
                        query=f"{industry} for sale {location}",
                        location=location,
                        filters=filters.copy(),
                        priority=self.DATA_SOURCE_WEIGHTS[DataSource.MARKETPLACE],
                        estimated_results=25
                    ))
        else:
            for location in geo_coverage[:5]:
                self.queries.append(SearchQuery(
                    source=DataSource.MARKETPLACE,
                    query=f"business for sale {location}",
                    location=location,
                    filters=filters,
                    priority=self.DATA_SOURCE_WEIGHTS[DataSource.MARKETPLACE],
                    estimated_results=50
                ))
    
    def _generate_website_queries(
        self,
        constraints: NormalizedConstraints,
        geo_coverage: List[str]
    ) -> None:
        """Generate queries for website discovery."""
        if not constraints.industry_rules:
            return
        
        # Generate search patterns for finding company websites
        keywords = constraints.industry_rules.keywords[:3]
        
        for location in geo_coverage[:5]:
            for keyword in keywords:
                self.queries.append(SearchQuery(
                    source=DataSource.WEBSITE,
                    query=f'"{keyword}" "{location}" "about us" OR "our story"',
                    location=location,
                    filters={
                        "keyword": keyword,
                        "search_type": "website_discovery"
                    },
                    priority=self.DATA_SOURCE_WEIGHTS[DataSource.WEBSITE],
                    estimated_results=20
                ))


def create_search_plan(constraints: NormalizedConstraints) -> SearchPlan:
    """Convenience function to create a search plan.
    
    Args:
        constraints: Normalized persona constraints
        
    Returns:
        SearchPlan
    """
    planner = SearchPlanner()
    return planner.generate_plan(constraints)
