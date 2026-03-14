"""Core Pydantic schemas for the Discovery Agent."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class Geography(BaseModel):
    """Geographic constraints for persona."""
    countries: List[str] = Field(default_factory=lambda: ["US"])
    states: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    zip_codes: Optional[List[str]] = None
    radius_miles: Optional[int] = Field(default=None, ge=0, le=500)
    exclude_territories: bool = True


class FinancialTarget(BaseModel):
    """Financial constraints for acquisition."""
    revenue_min: Optional[Decimal] = None
    revenue_max: Optional[Decimal] = None
    sde_min: Optional[Decimal] = None
    sde_max: Optional[Decimal] = None
    asking_price_min: Optional[Decimal] = None
    asking_price_max: Optional[Decimal] = None
    multiple_min: Optional[Decimal] = Field(None, ge=1.0, le=20.0)
    multiple_max: Optional[Decimal] = Field(None, ge=1.0, le=20.0)


class IndustryRule(BaseModel):
    """Industry inclusion/exclusion rules."""
    include: List[str] = Field(default_factory=list)
    exclude: List[str] = Field(default_factory=list)
    naics_codes: Optional[List[str]] = None
    sic_codes: Optional[List[str]] = None
    keywords: List[str] = Field(default_factory=list)


class OperationalCriteria(BaseModel):
    """Operational business criteria."""
    years_in_business_min: Optional[int] = Field(None, ge=0)
    employee_count_min: Optional[int] = Field(None, ge=0)
    employee_count_max: Optional[int] = Field(None, ge=0)
    owner_operator_required: bool = False
    absentee_ok: bool = True
    real_estate_included: Optional[bool] = None


class BuyerPersona(BaseModel):
    """Complete buyer persona for acquisition targeting."""
    id: str = Field(..., description="Unique persona identifier")
    name: str = Field(..., description="Persona name")
    geography: Geography
    financial_target: FinancialTarget
    industry_rules: IndustryRule
    operational_criteria: OperationalCriteria
    deal_structure: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=5, ge=1, le=10)


class NormalizedConstraints(BaseModel):
    """Validated and normalized persona constraints."""
    persona_id: str
    valid: bool
    errors: List[str] = Field(default_factory=list)
    geography: Optional[Geography] = None
    financial_target: Optional[FinancialTarget] = None
    industry_rules: Optional[IndustryRule] = None
    operational_criteria: Optional[OperationalCriteria] = None
    normalized_at: datetime = Field(default_factory=datetime.utcnow)


class DataSource(Enum):
    """Enumeration of discovery data sources."""
    DIRECTORY = "directory"
    REGISTRY = "registry"
    MARKETPLACE = "marketplace"
    WEBSITE = "website"
    MANUAL = "manual"


class SearchQuery(BaseModel):
    """Individual search query for a data source."""
    source: DataSource
    query: str
    location: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    estimated_results: int = Field(default=100, ge=0)


class SearchPlan(BaseModel):
    """Complete search strategy."""
    persona_id: str
    queries: List[SearchQuery]
    sources: List[DataSource]
    estimated_total_results: int
    geographic_coverage: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContactRole(str, Enum):
    """Priority order for contact roles."""
    OWNER = "owner"
    FOUNDER = "founder"
    PRESIDENT = "president"
    MANAGING_PARTNER = "managing_partner"
    OPERATOR = "operator"
    GENERAL_MANAGER = "general_manager"
    MANAGER = "manager"
    UNKNOWN = "unknown"


class ContactInfo(BaseModel):
    """Contact information for a business."""
    name: Optional[str] = None
    role: ContactRole = ContactRole.UNKNOWN
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = "unknown"


class CandidateBusiness(BaseModel):
    """Raw business candidate from discovery."""
    id: str = Field(..., description="Unique candidate ID")
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "US"
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    industry: Optional[str] = None
    naics_code: Optional[str] = None
    year_founded: Optional[int] = None
    employee_count: Optional[int] = None
    revenue_estimate: Optional[Decimal] = None
    sde_estimate: Optional[Decimal] = None
    source: DataSource
    source_url: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class EnrichmentData(BaseModel):
    """Enriched business data."""
    candidate_id: str
    revenue_estimate: Optional[Decimal] = None
    revenue_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    sde_estimate: Optional[Decimal] = None
    sde_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    employee_count: Optional[int] = None
    employee_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    years_in_business: Optional[int] = None
    owner_dependency_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    enriched_at: datetime = Field(default_factory=datetime.utcnow)
    sources: List[str] = Field(default_factory=list)


class ScoreCategory(BaseModel):
    """Individual scoring category."""
    name: str
    weight: int
    score: float = Field(..., ge=0.0, le=1.0)
    raw_score: float
    max_score: int
    explanation: str


class LeadScore(BaseModel):
    """Complete lead scoring result."""
    candidate_id: str
    total_score: int = Field(..., ge=0, le=100)
    threshold: int = 70
    qualified: bool
    categories: List[ScoreCategory]
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('total_score')
    def validate_score(cls, v):
        return max(0, min(100, v))


class ProvenanceMetadata(BaseModel):
    """Data lineage and provenance."""
    persona_id: str
    discovery_sources: List[str]
    discovery_timestamp: datetime
    enrichment_sources: List[str]
    enrichment_timestamp: Optional[datetime] = None
    contact_sources: List[str] = Field(default_factory=list)
    score_version: str = "1.0"


class QualifiedLead(BaseModel):
    """Final qualified acquisition lead."""
    id: str
    persona_id: str
    business_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    industry: Optional[str] = None
    year_founded: Optional[int] = None
    employee_count: Optional[int] = None
    revenue_estimate: Optional[Decimal] = None
    sde_estimate: Optional[Decimal] = None
    contact_name: Optional[str] = None
    contact_role: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_linkedin: Optional[str] = None
    lead_score: int
    score_breakdown: Dict[str, Any]
    owner_dependency_signals: List[str] = Field(default_factory=list)
    deal_structure_fit: Dict[str, Any] = Field(default_factory=dict)
    provenance: ProvenanceMetadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiscoveryResult(BaseModel):
    """Complete discovery operation result."""
    persona_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    candidates_scanned: int = 0
    candidates_deduplicated: int = 0
    candidates_enriched: int = 0
    leads_qualified: int = 0
    qualified_leads: List[QualifiedLead] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    runtime_seconds: float = 0.0
