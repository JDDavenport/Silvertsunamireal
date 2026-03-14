"""Discovery Agent - Main orchestrator for ACQUISITOR lead discovery.

This is the Lead Discovery Agent that transforms buyer personas into 
qualified acquisition leads by orchestrating multiple discovery sources,
enrichment, and qualification pipelines.

Target: <60 seconds runtime, ≥500 candidates scanned, ≤25 qualified leads returned.
"""
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import models
from models import (
    BuyerPersona, NormalizedConstraints, SearchPlan, CandidateBusiness,
    EnrichmentData, ContactInfo, LeadScore, QualifiedLead, DiscoveryResult,
    DataSource
)

# Import components
from payload_interpreter import PayloadInterpreter, validate_payload
from search_planner import SearchPlanner, create_search_plan
from deduplication import Deduplicator, dedupe_candidates
from enrichment import DataEnricher, enrich_candidate
from contact_discovery import ContactDiscovery, find_business_contact
from qualification import LeadQualifier, qualify_lead
from output_formatter import OutputFormatter, format_qualified_leads

# Import discovery agents
from discovery_agents.directory_discovery import DirectoryDiscovery, discover_from_directory
from discovery_agents.registry_discovery import RegistryDiscovery, discover_from_registry
from discovery_agents.marketplace_discovery import MarketplaceDiscovery, discover_from_marketplace
from discovery_agents.website_discovery import WebsiteDiscovery, discover_from_websites

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiscoveryAgent:
    """Main discovery orchestrator for ACQUISITOR."""
    
    def __init__(self, 
                 max_candidates: int = 1000,
                 max_leads: int = 25,
                 max_runtime_seconds: int = 60,
                 parallel_workers: int = 4):
        self.max_candidates = max_candidates
        self.max_leads = max_leads
        self.max_runtime = max_runtime_seconds
        self.parallel_workers = parallel_workers
        
        # Component instances
        self.interpreter = PayloadInterpreter()
        self.planner = SearchPlanner()
        self.deduplicator = Deduplicator()
        self.enricher = DataEnricher()
        self.contact_discovery = ContactDiscovery()
        
        # Discovery agents
        self.directory_discovery = DirectoryDiscovery()
        self.registry_discovery = RegistryDiscovery()
        self.marketplace_discovery = MarketplaceDiscovery()
        self.website_discovery = WebsiteDiscovery()
    
    def discover(self, persona: BuyerPersona) -> DiscoveryResult:
        """Execute full discovery pipeline for a buyer persona.
        
        Args:
            persona: Buyer persona defining acquisition criteria
            
        Returns:
            DiscoveryResult with qualified leads
        """
        started_at = datetime.utcnow()
        logger.info(f"Starting discovery for persona: {persona.id}")
        
        result = DiscoveryResult(
            persona_id=persona.id,
            started_at=started_at
        )
        
        try:
            # Phase 1: Validate and normalize persona
            logger.info("Phase 1: Validating persona payload")
            constraints = self.interpreter.validate(persona)
            
            if not constraints.valid:
                result.errors.extend(constraints.errors)
                logger.error(f"Persona validation failed: {constraints.errors}")
                return result
            
            # Phase 2: Generate search plan
            logger.info("Phase 2: Generating search plan")
            search_plan = self.planner.generate_plan(constraints)
            
            if not search_plan.queries:
                result.errors.append("No search queries generated")
                return result
            
            # Phase 3: Execute discovery across sources
            logger.info(f"Phase 3: Executing {len(search_plan.queries)} discovery queries")
            candidates = self._execute_discovery(search_plan)
            result.candidates_scanned = len(candidates)
            
            if len(candidates) > self.max_candidates:
                logger.warning(f"Truncating {len(candidates)} candidates to {self.max_candidates}")
                candidates = candidates[:self.max_candidates]
            
            # Phase 4: Deduplicate candidates
            logger.info("Phase 4: Deduplicating candidates")
            unique_candidates = self.deduplicator.dedupe_candidates(candidates)
            result.candidates_deduplicated = len(unique_candidates)
            
            # Phase 5: Enrich candidates
            logger.info("Phase 5: Enriching candidate data")
            enrichments = self._enrich_candidates(unique_candidates)
            result.candidates_enriched = len(enrichments)
            
            # Phase 6: Discover contacts
            logger.info("Phase 6: Discovering contacts")
            contacts = self._discover_contacts(unique_candidates)
            
            # Phase 7: Qualify leads
            logger.info("Phase 7: Qualifying leads")
            qualifier = LeadQualifier(constraints)
            scores = self._qualify_candidates(unique_candidates, enrichments, contacts, qualifier)
            
            # Phase 8: Format output
            logger.info("Phase 8: Formatting qualified leads")
            formatter = OutputFormatter(persona.id)
            qualified_leads = formatter.format_leads(
                unique_candidates, enrichments, contacts, scores
            )
            
            # Limit to max leads
            if len(qualified_leads) > self.max_leads:
                logger.warning(f"Truncating {len(qualified_leads)} leads to {self.max_leads}")
                qualified_leads = qualified_leads[:self.max_leads]
            
            result.qualified_leads = qualified_leads
            result.leads_qualified = len(qualified_leads)
            
        except Exception as e:
            logger.exception("Discovery pipeline failed")
            result.errors.append(str(e))
        
        finally:
            completed_at = datetime.utcnow()
            result.completed_at = completed_at
            result.runtime_seconds = (completed_at - started_at).total_seconds()
            
            logger.info(f"Discovery complete: {result.leads_qualified} leads in {result.runtime_seconds:.2f}s")
        
        return result
    
    def _execute_discovery(self, search_plan: SearchPlan) -> List[CandidateBusiness]:
        """Execute discovery queries across all sources.
        
        Args:
            search_plan: Generated search plan with queries
            
        Returns:
            Combined list of candidates from all sources
        """
        all_candidates: List[CandidateBusiness] = []
        
        # Group queries by source for efficient execution
        queries_by_source: Dict[DataSource, List[Any]] = {
            DataSource.DIRECTORY: [],
            DataSource.REGISTRY: [],
            DataSource.MARKETPLACE: [],
            DataSource.WEBSITE: [],
        }
        
        for query in search_plan.queries:
            queries_by_source[query.source].append(query)
        
        # Execute in parallel where possible
        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            futures = {}
            
            # Submit discovery tasks
            if queries_by_source[DataSource.DIRECTORY]:
                futures[executor.submit(
                    discover_from_directory, 
                    queries_by_source[DataSource.DIRECTORY]
                )] = DataSource.DIRECTORY
            
            if queries_by_source[DataSource.REGISTRY]:
                futures[executor.submit(
                    discover_from_registry,
                    queries_by_source[DataSource.REGISTRY]
                )] = DataSource.REGISTRY
            
            if queries_by_source[DataSource.MARKETPLACE]:
                futures[executor.submit(
                    discover_from_marketplace,
                    queries_by_source[DataSource.MARKETPLACE]
                )] = DataSource.MARKETPLACE
            
            if queries_by_source[DataSource.WEBSITE]:
                futures[executor.submit(
                    discover_from_websites,
                    queries_by_source[DataSource.WEBSITE]
                )] = DataSource.WEBSITE
            
            # Collect results
            for future in as_completed(futures):
                source = futures[future]
                try:
                    candidates = future.result(timeout=30)
                    all_candidates.extend(candidates)
                    logger.info(f"Discovered {len(candidates)} from {source.value}")
                except Exception as e:
                    logger.error(f"Discovery failed for {source.value}: {e}")
        
        return all_candidates
    
    def _enrich_candidates(self, candidates: List[CandidateBusiness]) -> Dict[str, EnrichmentData]:
        """Enrich all candidates with additional data.
        
        Args:
            candidates: List of unique candidates
            
        Returns:
            Dict mapping candidate_id to enrichment data
        """
        enrichments: Dict[str, EnrichmentData] = {}
        
        # Enrich in parallel for speed
        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            future_to_candidate = {
                executor.submit(self.enricher.enrich, c): c 
                for c in candidates
            }
            
            for future in as_completed(future_to_candidate):
                candidate = future_to_candidate[future]
                try:
                    enrichment = future.result(timeout=10)
                    enrichments[candidate.id] = enrichment
                except Exception as e:
                    logger.error(f"Enrichment failed for {candidate.name}: {e}")
                    # Create empty enrichment
                    enrichments[candidate.id] = EnrichmentData(
                        candidate_id=candidate.id,
                        sources=[]
                    )
        
        return enrichments
    
    def _discover_contacts(self, candidates: List[CandidateBusiness]) -> Dict[str, ContactInfo]:
        """Discover contacts for all candidates.
        
        Args:
            candidates: List of candidates
            
        Returns:
            Dict mapping candidate_id to contact info
        """
        contacts: Dict[str, ContactInfo] = {}
        
        for candidate in candidates:
            try:
                contact = self.contact_discovery.find_contact(candidate)
                if contact:
                    contacts[candidate.id] = contact
            except Exception as e:
                logger.error(f"Contact discovery failed for {candidate.name}: {e}")
        
        return contacts
    
    def _qualify_candidates(self,
                           candidates: List[CandidateBusiness],
                           enrichments: Dict[str, EnrichmentData],
                           contacts: Dict[str, ContactInfo],
                           qualifier: LeadQualifier) -> Dict[str, LeadScore]:
        """Score and qualify all candidates.
        
        Args:
            candidates: List of candidates
            enrichments: Enrichment data by candidate_id
            contacts: Contact info by candidate_id
            qualifier: LeadQualifier instance
            
        Returns:
            Dict mapping candidate_id to lead score
        """
        scores: Dict[str, LeadScore] = {}
        
        for candidate in candidates:
            try:
                enrichment = enrichments.get(candidate.id, EnrichmentData(
                    candidate_id=candidate.id, sources=[]
                ))
                contact = contacts.get(candidate.id)
                
                score = qualifier.calculate_score(candidate, enrichment, contact)
                scores[candidate.id] = score
            except Exception as e:
                logger.error(f"Qualification failed for {candidate.name}: {e}")
        
        return scores


def run_discovery(persona_dict: Dict[str, Any]) -> DiscoveryResult:
    """Convenience function to run discovery from raw persona dict.
    
    Args:
        persona_dict: Raw persona data as dictionary
        
    Returns:
        DiscoveryResult
    """
    # Validate and parse persona
    is_valid, constraints = validate_payload(persona_dict)
    
    if not is_valid:
        return DiscoveryResult(
            persona_id=persona_dict.get("id", "unknown"),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            errors=constraints.errors
        )
    
    # Create persona object from constraints
    persona = BuyerPersona(
        id=constraints.persona_id,
        name=persona_dict.get("name", "Unnamed Persona"),
        geography=constraints.geography,
        financial_target=constraints.financial_target,
        industry_rules=constraints.industry_rules,
        operational_criteria=constraints.operational_criteria
    )
    
    # Run discovery
    agent = DiscoveryAgent()
    return agent.discover(persona)


# Main entry point for CLI/standalone usage
if __name__ == "__main__":
    # Example usage
    example_persona = {
        "id": "test-persona-001",
        "name": "Test Buyer",
        "geography": {
            "countries": ["US"],
            "states": ["CA", "TX"],
            "cities": ["Los Angeles", "Houston"],
            "exclude_territories": True
        },
        "financial_target": {
            "revenue_min": "500000",
            "revenue_max": "5000000",
            "sde_min": "100000",
            "sde_max": "1500000"
        },
        "industry_rules": {
            "include": ["construction", "manufacturing"],
            "exclude": ["retail", "food service"],
            "keywords": ["contractor", "builder"]
        },
        "operational_criteria": {
            "years_in_business_min": 5,
            "absentee_ok": True
        }
    }
    
    result = run_discovery(example_persona)
    
    print(f"\nDiscovery Complete!")
    print(f"Runtime: {result.runtime_seconds:.2f}s")
    print(f"Candidates Scanned: {result.candidates_scanned}")
    print(f"Unique Candidates: {result.candidates_deduplicated}")
    print(f"Qualified Leads: {result.leads_qualified}")
    
    if result.errors:
        print(f"\nErrors: {result.errors}")
    
    for lead in result.qualified_leads[:5]:
        print(f"\n  - {lead.business_name} (Score: {lead.lead_score})")
        print(f"    Contact: {lead.contact_name or 'N/A'} ({lead.contact_role or 'N/A'})")
