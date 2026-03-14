"""Payload interpreter - validates and normalizes buyer persona payloads."""
import logging
import re
from typing import List, Optional, Tuple
from decimal import Decimal

from models import BuyerPersona, NormalizedConstraints, Geography, FinancialTarget, IndustryRule, OperationalCriteria

logger = logging.getLogger(__name__)


class PayloadInterpreter:
    """Validates and normalizes buyer persona payloads."""
    
    VALID_COUNTRIES = {"US", "USA", "United States", "CA", "Canada"}
    VALID_US_STATES = {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "DC", "PR", "VI", "GU", "AS", "MP"
    }
    US_TERRITORIES = {"PR", "VI", "GU", "AS", "MP"}
    
    def __init__(self):
        self.errors: List[str] = []
    
    def validate(self, persona: BuyerPersona) -> NormalizedConstraints:
        """Validate a complete buyer persona.
        
        Args:
            persona: Raw buyer persona to validate
            
        Returns:
            NormalizedConstraints with validation results
        """
        self.errors = []
        
        # Validate required fields
        if not persona.id or not persona.id.strip():
            self.errors.append("Persona ID is required")
        
        if not persona.name or not persona.name.strip():
            self.errors.append("Persona name is required")
        
        # Validate geography
        geography = self.normalize_geography(persona.geography)
        if not geography:
            self.errors.append("Geography validation failed")
        
        # Validate financial targets
        financial = self._validate_financial(persona.financial_target)
        
        # Validate industry rules
        industries = self.normalize_industries(persona.industry_rules)
        
        # Validate operational criteria
        operational = persona.operational_criteria
        
        valid = len(self.errors) == 0
        
        if valid:
            logger.info(f"Persona {persona.id} validated successfully")
        else:
            logger.warning(f"Persona {persona.id} validation failed: {self.errors}")
        
        return NormalizedConstraints(
            persona_id=persona.id,
            valid=valid,
            errors=self.errors.copy(),
            geography=geography,
            financial_target=financial,
            industry_rules=industries,
            operational_criteria=operational
        )
    
    def normalize_geography(self, geography: Geography) -> Optional[Geography]:
        """Normalize and validate geographic constraints.
        
        Args:
            geography: Raw geography constraints
            
        Returns:
            Normalized Geography or None if invalid
        """
        normalized_countries = []
        for country in geography.countries:
            country_upper = country.upper()
            if country_upper in {"US", "USA", "UNITED STATES"}:
                normalized_countries.append("US")
            elif country_upper in {"CA", "CANADA"}:
                normalized_countries.append("CA")
            else:
                self.errors.append(f"Unsupported country: {country}")
        
        if not normalized_countries:
            self.errors.append("At least one valid country required")
            return None
        
        # Validate states
        normalized_states = None
        if geography.states:
            normalized_states = []
            for state in geography.states:
                state_clean = state.upper().strip()
                if state_clean in self.VALID_US_STATES:
                    if geography.exclude_territories and state_clean in self.US_TERRITORIES:
                        continue
                    normalized_states.append(state_clean)
                else:
                    self.errors.append(f"Invalid US state: {state}")
        
        # Validate cities (basic cleanup)
        normalized_cities = None
        if geography.cities:
            normalized_cities = [c.strip().title() for c in geography.cities if c.strip()]
        
        # Validate ZIP codes
        normalized_zips = None
        if geography.zip_codes:
            normalized_zips = []
            for zip_code in geography.zip_codes:
                zip_clean = zip_code.strip()
                if re.match(r'^\d{5}(-\d{4})?$', zip_clean):
                    normalized_zips.append(zip_clean)
                else:
                    self.errors.append(f"Invalid ZIP code format: {zip_code}")
        
        return Geography(
            countries=list(set(normalized_countries)),
            states=list(set(normalized_states)) if normalized_states else None,
            cities=list(set(normalized_cities)) if normalized_cities else None,
            zip_codes=list(set(normalized_zips)) if normalized_zips else None,
            radius_miles=geography.radius_miles,
            exclude_territories=geography.exclude_territories
        )
    
    def normalize_industries(self, industry_rules: IndustryRule) -> IndustryRule:
        """Normalize industry inclusion/exclusion rules.
        
        Args:
            industry_rules: Raw industry rules
            
        Returns:
            Normalized IndustryRule
        """
        # Normalize include list
        normalized_include = []
        for industry in industry_rules.include:
            cleaned = industry.strip().lower()
            if cleaned:
                normalized_include.append(cleaned)
        
        # Normalize exclude list
        normalized_exclude = []
        for industry in industry_rules.exclude:
            cleaned = industry.strip().lower()
            if cleaned:
                normalized_exclude.append(cleaned)
        
        # Check for conflicts
        conflicts = set(normalized_include) & set(normalized_exclude)
        if conflicts:
            self.errors.append(f"Industry conflicts (in both include and exclude): {conflicts}")
        
        # Validate NAICS codes
        valid_naics = None
        if industry_rules.naics_codes:
            valid_naics = []
            for code in industry_rules.naics_codes:
                code_clean = code.strip()
                if re.match(r'^\d{2,6}$', code_clean):
                    valid_naics.append(code_clean)
                else:
                    self.errors.append(f"Invalid NAICS code: {code}")
        
        # Validate SIC codes
        valid_sic = None
        if industry_rules.sic_codes:
            valid_sic = []
            for code in industry_rules.sic_codes:
                code_clean = code.strip()
                if re.match(r'^\d{4}$', code_clean):
                    valid_sic.append(code_clean)
                else:
                    self.errors.append(f"Invalid SIC code: {code}")
        
        # Normalize keywords
        normalized_keywords = []
        for keyword in industry_rules.keywords:
            cleaned = keyword.strip().lower()
            if cleaned:
                normalized_keywords.append(cleaned)
        
        return IndustryRule(
            include=list(set(normalized_include)),
            exclude=list(set(normalized_exclude)),
            naics_codes=list(set(valid_naics)) if valid_naics else None,
            sic_codes=list(set(valid_sic)) if valid_sic else None,
            keywords=list(set(normalized_keywords))
        )
    
    def _validate_financial(self, financial: FinancialTarget) -> FinancialTarget:
        """Validate financial constraints.
        
        Args:
            financial: Financial target constraints
            
        Returns:
            Validated FinancialTarget
        """
        # Check min/max consistency
        if financial.revenue_min and financial.revenue_max:
            if financial.revenue_min > financial.revenue_max:
                self.errors.append("Revenue min cannot exceed revenue max")
        
        if financial.sde_min and financial.sde_max:
            if financial.sde_min > financial.sde_max:
                self.errors.append("SDE min cannot exceed SDE max")
        
        if financial.asking_price_min and financial.asking_price_max:
            if financial.asking_price_min > financial.asking_price_max:
                self.errors.append("Asking price min cannot exceed max")
        
        if financial.multiple_min and financial.multiple_max:
            if financial.multiple_min > financial.multiple_max:
                self.errors.append("Multiple min cannot exceed max")
        
        return financial


def validate_payload(raw_data: dict) -> Tuple[bool, NormalizedConstraints]:
    """Convenience function to validate raw persona data.
    
    Args:
        raw_data: Raw dictionary containing persona data
        
    Returns:
        Tuple of (is_valid, normalized_constraints)
    """
    try:
        persona = BuyerPersona(**raw_data)
        interpreter = PayloadInterpreter()
        result = interpreter.validate(persona)
        return result.valid, result
    except Exception as e:
        logger.error(f"Payload validation error: {e}")
        return False, NormalizedConstraints(
            persona_id=raw_data.get("id", "unknown"),
            valid=False,
            errors=[str(e)]
        )
