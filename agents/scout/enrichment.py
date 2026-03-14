"""Enrichment - data enrichment for business candidates."""
import logging
import random
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from models import CandidateBusiness, EnrichmentData

logger = logging.getLogger(__name__)


class DataEnricher:
    """Enriches business candidates with additional data."""
    
    def __init__(self):
        self.enrichment_cache: Dict[str, EnrichmentData] = {}
    
    def enrich(self, candidate: CandidateBusiness) -> EnrichmentData:
        """Enrich a business candidate with additional data.
        
        Args:
            candidate: Business candidate to enrich
            
        Returns:
            Enrichment data
        """
        logger.info(f"Enriching candidate: {candidate.name}")
        
        # Check cache
        if candidate.id in self.enrichment_cache:
            return self.enrichment_cache[candidate.id]
        
        # Gather enrichment from multiple sources
        sources: List[str] = []
        
        # Revenue estimate
        revenue, rev_confidence = self._estimate_revenue(candidate)
        if revenue:
            sources.append("revenue_model")
        
        # SDE estimate
        sde, sde_confidence = self._estimate_sde(candidate, revenue)
        if sde:
            sources.append("sde_model")
        
        # Employee count
        employees, emp_confidence = self._estimate_employees(candidate)
        if employees:
            sources.append("employee_model")
        
        # Years in business
        years = self._calculate_years_in_business(candidate)
        
        # Owner dependency signals
        owner_dep = self._assess_owner_dependency(candidate)
        
        enrichment = EnrichmentData(
            candidate_id=candidate.id,
            revenue_estimate=revenue,
            revenue_confidence=rev_confidence,
            sde_estimate=sde,
            sde_confidence=sde_confidence,
            employee_count=employees,
            employee_confidence=emp_confidence,
            years_in_business=years,
            owner_dependency_score=owner_dep,
            enriched_at=datetime.utcnow(),
            sources=sources
        )
        
        # Cache result
        self.enrichment_cache[candidate.id] = enrichment
        
        logger.info(f"Enrichment complete for {candidate.name}: "
                   f"revenue={revenue}, sde={sde}, employees={employees}")
        
        return enrichment
    
    def _estimate_revenue(self, candidate: CandidateBusiness) -> tuple[Optional[Decimal], float]:
        """Estimate annual revenue.
        
        Args:
            candidate: Business candidate
            
        Returns:
            Tuple of (revenue estimate, confidence 0-1)
        """
        # If already have revenue data, use it with high confidence
        if candidate.revenue_estimate:
            return candidate.revenue_estimate, 0.9
        
        # Estimate based on available data
        import random
        
        # Industry revenue per employee benchmarks (simplified)
        revenue_per_employee = {
            "construction": Decimal("150000"),
            "manufacturing": Decimal("200000"),
            "retail": Decimal("180000"),
            "services": Decimal("120000"),
            "healthcare": Decimal("100000"),
            "technology": Decimal("250000"),
        }
        
        if candidate.employee_count:
            industry = (candidate.industry or "").lower()
            multiplier = revenue_per_employee.get(industry, Decimal("150000"))
            estimated = Decimal(candidate.employee_count) * multiplier
            
            # Add some variance
            variance = Decimal(random.uniform(0.8, 1.2))
            estimated = estimated * variance
            
            return estimated.quantize(Decimal("1000")), 0.6
        
        # Very rough estimate based on years in business
        if candidate.year_founded:
            years = datetime.now().year - candidate.year_founded
            base_revenue = Decimal("500000") + (Decimal("50000") * years)
            return base_revenue.quantize(Decimal("10000")), 0.4
        
        # Fallback estimate
        return Decimal("500000"), 0.3
    
    def _estimate_sde(self, candidate: CandidateBusiness, 
                      revenue: Optional[Decimal]) -> tuple[Optional[Decimal], float]:
        """Estimate Seller's Discretionary Earnings.
        
        Args:
            candidate: Business candidate
            revenue: Estimated revenue
            
        Returns:
            Tuple of (SDE estimate, confidence 0-1)
        """
        # If already have SDE data, use it
        if candidate.sde_estimate:
            return candidate.sde_estimate, 0.9
        
        if not revenue:
            revenue, _ = self._estimate_revenue(candidate)
        
        if revenue:
            # Industry SDE margin estimates
            margins = {
                "construction": 0.12,
                "manufacturing": 0.10,
                "retail": 0.08,
                "services": 0.18,
                "healthcare": 0.15,
                "technology": 0.20,
            }
            
            industry = (candidate.industry or "").lower()
            margin = margins.get(industry, 0.12)
            
            sde = revenue * Decimal(str(margin))
            return sde.quantize(Decimal("1000")), 0.5
        
        return None, 0.0
    
    def _estimate_employees(self, candidate: CandidateBusiness) -> tuple[Optional[int], float]:
        """Estimate employee count.
        
        Args:
            candidate: Business candidate
            
        Returns:
            Tuple of (employee count, confidence 0-1)
        """
        # If already have employee data, use it
        if candidate.employee_count:
            return candidate.employee_count, 0.9
        
        # Estimate based on revenue if available
        if candidate.revenue_estimate:
            revenue = float(candidate.revenue_estimate)
            # Assume $150k per employee on average
            estimated = int(revenue / 150000)
            return max(1, estimated), 0.5
        
        # Estimate based on years in business
        if candidate.year_founded:
            years = datetime.now().year - candidate.year_founded
            if years < 5:
                return random.randint(1, 5), 0.3
            elif years < 10:
                return random.randint(3, 15), 0.3
            else:
                return random.randint(5, 50), 0.3
        
        return None, 0.0
    
    def _calculate_years_in_business(self, candidate: CandidateBusiness) -> Optional[int]:
        """Calculate years in business.
        
        Args:
            candidate: Business candidate
            
        Returns:
            Years in business or None
        """
        if candidate.year_founded:
            return datetime.now().year - candidate.year_founded
        return None
    
    def _assess_owner_dependency(self, candidate: CandidateBusiness) -> Optional[float]:
        """Assess owner dependency score.
        
        Higher score = more owner dependent (worse for acquisition)
        
        Args:
            candidate: Business candidate
            
        Returns:
            Owner dependency score 0-1 or None
        """
        import random
        
        signals = []
        
        # Small businesses are more owner dependent
        employees = candidate.employee_count
        if employees:
            if employees <= 2:
                signals.append(("very_small_team", 0.8))
            elif employees <= 5:
                signals.append(("small_team", 0.6))
            elif employees >= 20:
                signals.append(("larger_team", -0.3))
        
        # Service businesses tend to be more owner dependent
        service_industries = ["consulting", "legal", "accounting", "medical", "dental"]
        if candidate.industry and candidate.industry.lower() in service_industries:
            signals.append(("service_business", 0.4))
        
        # Newer businesses more dependent
        if candidate.year_founded:
            years = datetime.now().year - candidate.year_founded
            if years < 3:
                signals.append(("new_business", 0.5))
            elif years > 20:
                signals.append(("established_business", -0.2))
        
        # Calculate score
        if signals:
            total = sum(s[1] for s in signals)
            # Normalize to 0-1 range
            score = max(0.0, min(1.0, 0.4 + (total * 0.2)))
            return round(score, 2)
        
        return None


def enrich_candidate(candidate: CandidateBusiness) -> EnrichmentData:
    """Convenience function to enrich a candidate.
    
    Args:
        candidate: Business candidate
        
    Returns:
        Enrichment data
    """
    enricher = DataEnricher()
    return enricher.enrich(candidate)
