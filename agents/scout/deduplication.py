"""Deduplication - removes duplicate candidates across sources."""
import logging
from typing import List, Set, Tuple
from difflib import SequenceMatcher

from models import CandidateBusiness

logger = logging.getLogger(__name__)


class Deduplicator:
    """Deduplicates business candidates from multiple sources."""
    
    def __init__(self, 
                 name_similarity_threshold: float = 0.85,
                 phone_match_weight: float = 1.0,
                 domain_match_weight: float = 1.0,
                 name_address_match_weight: float = 0.9):
        self.name_similarity_threshold = name_similarity_threshold
        self.phone_match_weight = phone_match_weight
        self.domain_match_weight = domain_match_weight
        self.name_address_match_weight = name_address_match_weight
    
    def dedupe_candidates(self, candidates: List[CandidateBusiness]) -> List[CandidateBusiness]:
        """Deduplicate a list of candidate businesses.
        
        Args:
            candidates: List of candidates (potentially with duplicates)
            
        Returns:
            Deduplicated list with best version of each business
        """
        if not candidates:
            return []
        
        logger.info(f"Starting deduplication of {len(candidates)} candidates")
        
        # Group candidates by potential matches
        groups = self._group_candidates(candidates)
        
        # For each group, select the best candidate
        deduplicated = []
        for group in groups:
            best = self._select_best_candidate(group)
            deduplicated.append(best)
        
        removed = len(candidates) - len(deduplicated)
        logger.info(f"Deduplication complete: {removed} duplicates removed, {len(deduplicated)} unique")
        
        return deduplicated
    
    def _group_candidates(self, candidates: List[CandidateBusiness]) -> List[List[CandidateBusiness]]:
        """Group candidates into duplicate sets.
        
        Args:
            candidates: List of all candidates
            
        Returns:
            List of groups (each group is a list of duplicates)
        """
        groups: List[List[CandidateBusiness]] = []
        assigned: Set[str] = set()
        
        for i, candidate in enumerate(candidates):
            if candidate.id in assigned:
                continue
            
            # Start new group
            group = [candidate]
            assigned.add(candidate.id)
            
            # Find all matching candidates
            for j, other in enumerate(candidates[i+1:], start=i+1):
                if other.id in assigned:
                    continue
                
                if self._is_duplicate(candidate, other):
                    group.append(other)
                    assigned.add(other.id)
            
            groups.append(group)
        
        return groups
    
    def _is_duplicate(self, a: CandidateBusiness, b: CandidateBusiness) -> bool:
        """Check if two candidates are duplicates.
        
        Args:
            a: First candidate
            b: Second candidate
            
        Returns:
            True if candidates are duplicates
        """
        # Rule 1: Identical domain
        if a.website and b.website:
            domain_a = self._extract_domain(a.website)
            domain_b = self._extract_domain(b.website)
            if domain_a and domain_b and domain_a == domain_b:
                return True
        
        # Rule 2: Identical phone
        if a.phone and b.phone:
            phone_a = self._normalize_phone(a.phone)
            phone_b = self._normalize_phone(b.phone)
            if phone_a and phone_b and phone_a == phone_b:
                return True
        
        # Rule 3: Fuzzy name match + same city
        if a.city and b.city and a.city.lower() == b.city.lower():
            name_sim = self.similarity_score(a.name, b.name)
            if name_sim >= self.name_similarity_threshold:
                return True
        
        # Rule 4: Name + address match
        if a.address and b.address:
            addr_sim = self.similarity_score(a.address, b.address)
            name_sim = self.similarity_score(a.name, b.name)
            if addr_sim >= 0.8 and name_sim >= 0.7:
                return True
        
        return False
    
    def similarity_score(self, a: str, b: str) -> float:
        """Calculate similarity score between two strings.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not a or not b:
            return 0.0
        
        # Normalize strings
        a_norm = a.lower().strip()
        b_norm = b.lower().strip()
        
        if a_norm == b_norm:
            return 1.0
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, a_norm, b_norm).ratio()
    
    def _select_best_candidate(self, group: List[CandidateBusiness]) -> CandidateBusiness:
        """Select the best candidate from a duplicate group.
        
        Args:
            group: List of duplicate candidates
            
        Returns:
            Best candidate (most complete data)
        """
        def score_candidate(c: CandidateBusiness) -> int:
            """Score completeness of candidate data."""
            score = 0
            if c.website: score += 3
            if c.phone: score += 2
            if c.email: score += 2
            if c.address: score += 2
            if c.year_founded: score += 1
            if c.employee_count: score += 1
            if c.revenue_estimate: score += 1
            if c.sde_estimate: score += 1
            # Prefer marketplace sources (often have more financial data)
            if c.source.value == "marketplace": score += 2
            return score
        
        return max(group, key=score_candidate)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain string
        """
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ""
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison.
        
        Args:
            phone: Raw phone number
            
        Returns:
            Normalized phone (digits only)
        """
        import re
        digits = re.sub(r'\D', '', phone)
        # Remove leading 1 for US numbers
        if len(digits) == 11 and digits[0] == '1':
            digits = digits[1:]
        return digits


def dedupe_candidates(candidates: List[CandidateBusiness]) -> List[CandidateBusiness]:
    """Convenience function for deduplication.
    
    Args:
        candidates: List of candidates to deduplicate
        
    Returns:
        Deduplicated list
    """
    deduplicator = Deduplicator()
    return deduplicator.dedupe_candidates(candidates)
