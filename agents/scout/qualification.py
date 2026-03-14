"""Qualification - lead scoring for acquisition suitability."""
import logging
from typing import List, Dict, Any
from decimal import Decimal

from models import (
    CandidateBusiness, EnrichmentData, ContactInfo, 
    LeadScore, ScoreCategory, NormalizedConstraints
)

logger = logging.getLogger(__name__)


class LeadQualifier:
    """Scores and qualifies acquisition leads."""
    
    # Scoring weights (must sum to 100)
    CATEGORY_WEIGHTS = {
        "persona_match": 25,
        "contactability": 20,
        "operational_independence": 20,
        "financial_suitability": 15,
        "deal_structure_fit": 10,
        "data_confidence": 10,
    }
    
    QUALIFIED_THRESHOLD = 70
    
    def __init__(self, constraints: NormalizedConstraints):
        self.constraints = constraints
    
    def calculate_score(self, 
                       candidate: CandidateBusiness,
                       enrichment: EnrichmentData,
                       contact: ContactInfo) -> LeadScore:
        """Calculate lead score for a candidate.
        
        Args:
            candidate: Business candidate
            enrichment: Enrichment data
            contact: Contact information
            
        Returns:
            LeadScore with breakdown
        """
        logger.info(f"Calculating score for: {candidate.name}")
        
        categories: List[ScoreCategory] = []
        total_score = 0
        
        # Category 1: Persona Match (25 points)
        persona_score, persona_exp = self._score_persona_match(candidate, enrichment)
        categories.append(ScoreCategory(
            name="persona_match",
            weight=self.CATEGORY_WEIGHTS["persona_match"],
            score=persona_score,
            raw_score=persona_score * self.CATEGORY_WEIGHTS["persona_match"],
            max_score=self.CATEGORY_WEIGHTS["persona_match"],
            explanation=persona_exp
        ))
        total_score += int(persona_score * self.CATEGORY_WEIGHTS["persona_match"])
        
        # Category 2: Contactability (20 points)
        contact_score, contact_exp = self._score_contactability(contact)
        categories.append(ScoreCategory(
            name="contactability",
            weight=self.CATEGORY_WEIGHTS["contactability"],
            score=contact_score,
            raw_score=contact_score * self.CATEGORY_WEIGHTS["contactability"],
            max_score=self.CATEGORY_WEIGHTS["contactability"],
            explanation=contact_exp
        ))
        total_score += int(contact_score * self.CATEGORY_WEIGHTS["contactability"])
        
        # Category 3: Operational Independence (20 points)
        op_score, op_exp = self._score_operational_independence(candidate, enrichment)
        categories.append(ScoreCategory(
            name="operational_independence",
            weight=self.CATEGORY_WEIGHTS["operational_independence"],
            score=op_score,
            raw_score=op_score * self.CATEGORY_WEIGHTS["operational_independence"],
            max_score=self.CATEGORY_WEIGHTS["operational_independence"],
            explanation=op_exp
        ))
        total_score += int(op_score * self.CATEGORY_WEIGHTS["operational_independence"])
        
        # Category 4: Financial Suitability (15 points)
        fin_score, fin_exp = self._score_financial_suitability(candidate, enrichment)
        categories.append(ScoreCategory(
            name="financial_suitability",
            weight=self.CATEGORY_WEIGHTS["financial_suitability"],
            score=fin_score,
            raw_score=fin_score * self.CATEGORY_WEIGHTS["financial_suitability"],
            max_score=self.CATEGORY_WEIGHTS["financial_suitability"],
            explanation=fin_exp
        ))
        total_score += int(fin_score * self.CATEGORY_WEIGHTS["financial_suitability"])
        
        # Category 5: Deal Structure Fit (10 points)
        deal_score, deal_exp = self._score_deal_structure(candidate, enrichment)
        categories.append(ScoreCategory(
            name="deal_structure_fit",
            weight=self.CATEGORY_WEIGHTS["deal_structure_fit"],
            score=deal_score,
            raw_score=deal_score * self.CATEGORY_WEIGHTS["deal_structure_fit"],
            max_score=self.CATEGORY_WEIGHTS["deal_structure_fit"],
            explanation=deal_exp
        ))
        total_score += int(deal_score * self.CATEGORY_WEIGHTS["deal_structure_fit"])
        
        # Category 6: Data Confidence (10 points)
        conf_score, conf_exp = self._score_data_confidence(enrichment, contact)
        categories.append(ScoreCategory(
            name="data_confidence",
            weight=self.CATEGORY_WEIGHTS["data_confidence"],
            score=conf_score,
            raw_score=conf_score * self.CATEGORY_WEIGHTS["data_confidence"],
            max_score=self.CATEGORY_WEIGHTS["data_confidence"],
            explanation=conf_exp
        ))
        total_score += int(conf_score * self.CATEGORY_WEIGHTS["data_confidence"])
        
        qualified = total_score >= self.QUALIFIED_THRESHOLD
        
        logger.info(f"Score for {candidate.name}: {total_score}/100 (qualified: {qualified})")
        
        return LeadScore(
            candidate_id=candidate.id,
            total_score=total_score,
            threshold=self.QUALIFIED_THRESHOLD,
            qualified=qualified,
            categories=categories
        )
    
    def _score_persona_match(self, 
                            candidate: CandidateBusiness,
                            enrichment: EnrichmentData) -> tuple[float, str]:
        """Score how well candidate matches persona criteria."""
        score = 0.5  # Base score
        reasons = []
        
        # Geography match
        if self.constraints.geography:
            geo = self.constraints.geography
            if geo.states and candidate.state in (geo.states or []):
                score += 0.2
                reasons.append("state match")
            elif geo.cities and candidate.city in (geo.cities or []):
                score += 0.2
                reasons.append("city match")
            else:
                reasons.append("geography unclear")
        
        # Industry match
        if self.constraints.industry_rules and candidate.industry:
            include = self.constraints.industry_rules.include
            exclude = self.constraints.industry_rules.exclude
            
            ind_lower = candidate.industry.lower()
            if any(inc in ind_lower for inc in include):
                score += 0.3
                reasons.append("industry match")
            elif any(exc in ind_lower for exc in exclude):
                score -= 0.5
                reasons.append("excluded industry")
        
        return min(1.0, max(0.0, score)), "; ".join(reasons) if reasons else "baseline match"
    
    def _score_contactability(self, contact: ContactInfo) -> tuple[float, str]:
        """Score how contactable the business is."""
        score = 0.0
        reasons = []
        
        if not contact:
            return 0.0, "no contact found"
        
        # Email available
        if contact.email:
            score += 0.4
            reasons.append("email available")
        
        # Phone available
        if contact.phone:
            score += 0.2
            reasons.append("phone available")
        
        # Role identified
        if contact.role and contact.role.value != "unknown":
            score += 0.2
            reasons.append(f"role identified: {contact.role.value}")
        
        # Name available
        if contact.name:
            score += 0.2
            reasons.append("contact name available")
        
        return min(1.0, score), "; ".join(reasons)
    
    def _score_operational_independence(self,
                                       candidate: CandidateBusiness,
                                       enrichment: EnrichmentData) -> tuple[float, str]:
        """Score operational independence (lower owner dependency is better)."""
        score = 0.5
        reasons = []
        
        # Years in business
        if enrichment.years_in_business:
            if enrichment.years_in_business >= 10:
                score += 0.25
                reasons.append(f"established {enrichment.years_in_business} years")
            elif enrichment.years_in_business >= 5:
                score += 0.1
                reasons.append(f"operating {enrichment.years_in_business} years")
            else:
                score -= 0.1
                reasons.append("relatively new")
        
        # Employee count
        if enrichment.employee_count:
            if enrichment.employee_count >= 10:
                score += 0.15
                reasons.append("decent team size")
            elif enrichment.employee_count <= 2:
                score -= 0.2
                reasons.append("very small operation")
        
        # Owner dependency
        if enrichment.owner_dependency_score is not None:
            # Invert - lower dependency = higher score
            independence = 1.0 - enrichment.owner_dependency_score
            score += independence * 0.1
            if enrichment.owner_dependency_score > 0.7:
                reasons.append("high owner dependency")
            elif enrichment.owner_dependency_score < 0.4:
                reasons.append("operationally independent")
        
        return min(1.0, max(0.0, score)), "; ".join(reasons)
    
    def _score_financial_suitability(self,
                                     candidate: CandidateBusiness,
                                     enrichment: EnrichmentData) -> tuple[float, str]:
        """Score financial suitability against targets."""
        score = 0.5
        reasons = []
        
        if not self.constraints.financial_target:
            return score, "no financial targets set"
        
        ft = self.constraints.financial_target
        
        # Revenue check
        revenue = enrichment.revenue_estimate or candidate.revenue_estimate
        if revenue:
            if ft.revenue_min and revenue >= ft.revenue_min:
                score += 0.15
                reasons.append("revenue above minimum")
            elif ft.revenue_max and revenue > ft.revenue_max:
                score -= 0.2
                reasons.append("revenue above maximum")
            
            if ft.revenue_max and revenue <= ft.revenue_max:
                score += 0.1
                reasons.append("revenue within range")
        
        # SDE check
        sde = enrichment.sde_estimate or candidate.sde_estimate
        if sde:
            if ft.sde_min and sde >= ft.sde_min:
                score += 0.15
                reasons.append("SDE above minimum")
            if ft.sde_max and sde <= ft.sde_max:
                score += 0.1
                reasons.append("SDE within range")
        
        return min(1.0, max(0.0, score)), "; ".join(reasons) if reasons else "financial data limited"
    
    def _score_deal_structure(self,
                             candidate: CandidateBusiness,
                             enrichment: EnrichmentData) -> tuple[float, str]:
        """Score fit with deal structure preferences."""
        score = 0.5
        reasons = []
        
        # Check for asking price data (marketplace listings)
        if candidate.source.value == "marketplace":
            raw = candidate.raw_data
            if "asking_price" in raw:
                score += 0.2
                reasons.append("pricing data available")
        
        # Check owner-operator requirements
        if self.constraints.operational_criteria:
            oc = self.constraints.operational_criteria
            if oc.absentee_ok and enrichment.employee_count and enrichment.employee_count >= 5:
                score += 0.2
                reasons.append("suitable for absentee ownership")
            elif oc.owner_operator_required:
                score += 0.1
                reasons.append("owner-operator model")
        
        return min(1.0, score), "; ".join(reasons) if reasons else "standard deal structure"
    
    def _score_data_confidence(self,
                              enrichment: EnrichmentData,
                              contact: ContactInfo) -> tuple[float, str]:
        """Score confidence in the data quality."""
        score = 0.0
        reasons = []
        
        # Revenue confidence
        score += enrichment.revenue_confidence * 0.3
        if enrichment.revenue_confidence >= 0.7:
            reasons.append("high revenue confidence")
        
        # SDE confidence
        score += enrichment.sde_confidence * 0.3
        if enrichment.sde_confidence >= 0.7:
            reasons.append("high SDE confidence")
        
        # Contact confidence
        if contact and contact.confidence >= 0.5:
            score += contact.confidence * 0.2
            reasons.append("contact verified")
        
        # Multiple sources
        if len(enrichment.sources) >= 2:
            score += 0.2
            reasons.append("multiple data sources")
        
        return min(1.0, score), "; ".join(reasons) if reasons else "data confidence baseline"
    
    def explain_score(self, score: LeadScore) -> str:
        """Generate human-readable score explanation.
        
        Args:
            score: LeadScore object
            
        Returns:
            Formatted explanation string
        """
        lines = [
            f"Lead Score: {score.total_score}/100 (Threshold: {score.threshold})",
            f"Qualified: {'YES' if score.qualified else 'NO'}",
            "",
            "Category Breakdown:",
        ]
        
        for cat in score.categories:
            lines.append(f"  {cat.name}: {cat.raw_score:.0f}/{cat.max_score} - {cat.explanation}")
        
        return "\n".join(lines)


def qualify_lead(candidate: CandidateBusiness,
                enrichment: EnrichmentData,
                contact: ContactInfo,
                constraints: NormalizedConstraints) -> LeadScore:
    """Convenience function to qualify a lead.
    
    Args:
        candidate: Business candidate
        enrichment: Enrichment data
        contact: Contact info
        constraints: Persona constraints
        
    Returns:
        LeadScore
    """
    qualifier = LeadQualifier(constraints)
    return qualifier.calculate_score(candidate, enrichment, contact)
