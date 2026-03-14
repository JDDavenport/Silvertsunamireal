"""Output formatter - structures final qualified leads."""
import logging
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from models import (
    CandidateBusiness, EnrichmentData, ContactInfo, LeadScore,
    QualifiedLead, ProvenanceMetadata, DataSource
)

logger = logging.getLogger(__name__)


class OutputFormatter:
    """Formats and structures qualified leads for output."""
    
    def __init__(self, persona_id: str):
        self.persona_id = persona_id
    
    def format_lead(self,
                   candidate: CandidateBusiness,
                   enrichment: EnrichmentData,
                   contact: ContactInfo,
                   score: LeadScore) -> QualifiedLead:
        """Format a single qualified lead."""
        logger.info(f"Formatting lead: {candidate.name}")
        
        provenance = self._build_provenance(candidate, enrichment, contact)
        score_breakdown = self._build_score_breakdown(score)
        owner_signals = self._extract_owner_signals(enrichment)
        deal_fit = self._build_deal_structure_fit(candidate, enrichment)
        
        return QualifiedLead(
            id=str(uuid.uuid4()),
            persona_id=self.persona_id,
            business_name=self._normalize_name(candidate.name),
            address=candidate.address,
            city=candidate.city,
            state=candidate.state,
            zip_code=candidate.zip_code,
            phone=candidate.phone,
            website=candidate.website,
            email=candidate.email,
            industry=candidate.industry,
            year_founded=candidate.year_founded,
            employee_count=enrichment.employee_count or candidate.employee_count,
            revenue_estimate=enrichment.revenue_estimate or candidate.revenue_estimate,
            sde_estimate=enrichment.sde_estimate or candidate.sde_estimate,
            contact_name=contact.name if contact else None,
            contact_role=contact.role.value if contact else None,
            contact_email=contact.email if contact else None,
            contact_phone=contact.phone if contact else None,
            contact_linkedin=contact.linkedin if contact else None,
            lead_score=score.total_score,
            score_breakdown=score_breakdown,
            owner_dependency_signals=owner_signals,
            deal_structure_fit=deal_fit,
            provenance=provenance,
            created_at=datetime.utcnow()
        )
    
    def format_leads(self,
                    candidates: List[CandidateBusiness],
                    enrichments: Dict[str, EnrichmentData],
                    contacts: Dict[str, ContactInfo],
                    scores: Dict[str, LeadScore]) -> List[QualifiedLead]:
        """Format multiple qualified leads."""
        leads = []
        
        for candidate in candidates:
            candidate_id = candidate.id
            if candidate_id not in scores:
                continue
            
            score = scores[candidate_id]
            if not score.qualified:
                continue
            
            enrichment = enrichments.get(candidate_id, EnrichmentData(
                candidate_id=candidate_id, sources=[]
            ))
            contact = contacts.get(candidate_id)
            
            lead = self.format_lead(candidate, enrichment, contact, score)
            leads.append(lead)
        
        leads.sort(key=lambda l: l.lead_score, reverse=True)
        logger.info(f"Formatted {len(leads)} qualified leads")
        return leads
    
    def generate_summary(self, leads: List[QualifiedLead]) -> Dict[str, Any]:
        """Generate summary statistics for leads."""
        if not leads:
            return {"count": 0, "avg_score": 0, "industries": {}, "geo": {}}
        
        scores = [l.lead_score for l in leads]
        industries: Dict[str, int] = {}
        geo_dist: Dict[str, int] = {}
        
        for lead in leads:
            if lead.industry:
                industries[lead.industry] = industries.get(lead.industry, 0) + 1
            if lead.state:
                geo_dist[lead.state] = geo_dist.get(lead.state, 0) + 1
        
        return {
            "count": len(leads),
            "avg_score": sum(scores) / len(scores),
            "score_range": {"min": min(scores), "max": max(scores)},
            "industries": industries,
            "geographic_distribution": geo_dist,
        }
    
    def _normalize_name(self, name: str) -> str:
        """Normalize business name."""
        if not name:
            return ""
        return " ".join(name.split())
    
    def _build_provenance(self, candidate: CandidateBusiness,
                         enrichment: EnrichmentData, contact: ContactInfo) -> ProvenanceMetadata:
        """Build provenance metadata."""
        discovery_sources = [candidate.source.value]
        contact_sources = [contact.source] if contact else []
        
        return ProvenanceMetadata(
            persona_id=self.persona_id,
            discovery_sources=list(set(discovery_sources)),
            discovery_timestamp=candidate.discovered_at,
            enrichment_sources=enrichment.sources.copy(),
            enrichment_timestamp=enrichment.enriched_at,
            contact_sources=contact_sources,
            score_version="1.0"
        )
    
    def _build_score_breakdown(self, score: LeadScore) -> Dict[str, Any]:
        """Build score breakdown dict."""
        return {
            "total": score.total_score,
            "threshold": score.threshold,
            "qualified": score.qualified,
            "categories": [
                {
                    "name": cat.name,
                    "weight": cat.weight,
                    "score": round(cat.score, 2),
                    "raw_score": round(cat.raw_score, 1),
                    "explanation": cat.explanation
                }
                for cat in score.categories
            ]
        }
    
    def _extract_owner_signals(self, enrichment: EnrichmentData) -> List[str]:
        """Extract owner dependency signals."""
        signals = []
        if enrichment.owner_dependency_score is not None:
            if enrichment.owner_dependency_score > 0.7:
                signals.append("High owner dependency - key person risk")
            elif enrichment.owner_dependency_score > 0.5:
                signals.append("Moderate owner involvement")
            else:
                signals.append("Operationally independent")
        
        if enrichment.employee_count:
            if enrichment.employee_count <= 2:
                signals.append("Very small team - owner likely critical")
            elif enrichment.employee_count >= 10:
                signals.append("Established team structure")
        
        if enrichment.years_in_business:
            if enrichment.years_in_business < 3:
                signals.append("Young business - owner still building")
            elif enrichment.years_in_business > 15:
                signals.append("Mature business - systems likely in place")
        
        return signals
    
    def _build_deal_structure_fit(self, candidate: CandidateBusiness,
                                  enrichment: EnrichmentData) -> Dict[str, Any]:
        """Build deal structure fit information."""
        fit = {"listing_type": candidate.source.value, "pricing_available": False}
        
        if candidate.source == DataSource.MARKETPLACE:
            raw = candidate.raw_data
            if "asking_price" in raw:
                fit["pricing_available"] = True
                fit["asking_price"] = raw["asking_price"]
                sde = enrichment.sde_estimate or candidate.sde_estimate
                if sde and sde > 0:
                    fit["estimated_multiple"] = round(float(raw["asking_price"]) / float(sde), 2)
        
        if candidate.raw_data.get("reason_selling") == "Retirement":
            fit["seller_motivation"] = "high"
        
        return fit


def format_qualified_leads(persona_id: str,
                          candidates: List[CandidateBusiness],
                          enrichments: Dict[str, EnrichmentData],
                          contacts: Dict[str, ContactInfo],
                          scores: Dict[str, LeadScore]) -> List[QualifiedLead]:
    """Convenience function to format leads."""
    formatter = OutputFormatter(persona_id)
    return formatter.format_leads(candidates, enrichments, contacts, scores)
