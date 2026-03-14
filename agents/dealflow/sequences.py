"""Email/SMS sequence templates for DEALFLOW outreach.

Provides pre-built outreach sequences with personalization:
- Sequence A: Direct Owner Outreach (4 emails over 14 days)
- Sequence B: Broker Outreach (3 emails)
- Sequence C: Landing Page Inbound (3-step)
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta

from config import get_config


logger = logging.getLogger(__name__)


class SequenceType(Enum):
    """Types of outreach sequences."""
    DIRECT_OWNER = "direct_owner"      # Sequence A: 4 emails over 14 days
    BROKER = "broker"                   # Sequence B: 3 emails
    LANDING_PAGE = "landing_page"       # Sequence C: 3-step inbound


class ChannelType(Enum):
    """Communication channel types."""
    EMAIL = "email"
    SMS = "sms"


@dataclass
class SequenceStep:
    """A single step in an outreach sequence."""
    step_number: int
    channel: ChannelType
    delay_days: int  # Days after previous step (or start)
    subject_template: str
    body_template: str
    sms_template: Optional[str] = None  # Shorter version for SMS


@dataclass
class LeadData:
    """Data structure for lead information used in personalization."""
    lead_id: int
    business_name: str
    owner_name: Optional[str]
    industry: Optional[str]
    location: Optional[str]
    revenue: Optional[str]
    employees: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    year_founded: Optional[int]
    custom_fields: Dict[str, Any]
    
    @classmethod
    def from_qualify_record(cls, record: Dict[str, Any]) -> "LeadData":
        """Create LeadData from a QUALIFY module record."""
        return cls(
            lead_id=record.get("id", 0),
            business_name=record.get("business_name", ""),
            owner_name=record.get("owner_name"),
            industry=record.get("industry"),
            location=record.get("location"),
            revenue=record.get("revenue"),
            employees=record.get("employees"),
            email=record.get("email"),
            phone=record.get("phone"),
            website=record.get("website"),
            year_founded=record.get("year_founded"),
            custom_fields=record.get("custom_fields", {}),
        )
    
    def get_first_name(self) -> str:
        """Extract first name from owner_name."""
        if not self.owner_name:
            return "there"
        return self.owner_name.split()[0]
    
    def get_company_age(self) -> Optional[int]:
        """Calculate company age in years."""
        if not self.year_founded:
            return None
        return datetime.now().year - self.year_founded


class SequenceTemplate:
    """Base class for outreach sequences."""
    
    def __init__(self, sequence_type: SequenceType):
        self.sequence_type = sequence_type
        self.steps: List[SequenceStep] = []
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load sequence steps - to be implemented by subclasses."""
        raise NotImplementedError
    
    def personalize(self, template: str, lead: LeadData) -> str:
        """Replace template variables with lead data.
        
        Available variables:
        - {business_name} - Company name
        - {owner_name} - Full owner name
        - {first_name} - First name only
        - {industry} - Industry category
        - {location} - City/region
        - {revenue} - Revenue range
        - {employees} - Employee count
        - {website} - Company website
        - {company_age} - Years in business
        - {day_of_week} - Current day name
        - {current_month} - Current month name
        
        Args:
            template: Template string with placeholders
            lead: LeadData with personalization values
            
        Returns:
            Personalized string with variables replaced
        """
        # Build replacement mapping
        now = datetime.now()
        replacements = {
            "{business_name}": lead.business_name or "your company",
            "{owner_name}": lead.owner_name or "Business Owner",
            "{first_name}": lead.get_first_name(),
            "{industry}": lead.industry or "your industry",
            "{location}": lead.location or "your area",
            "{revenue}": lead.revenue or "your revenue level",
            "{employees}": lead.employees or "your team",
            "{website}": lead.website or "your website",
            "{company_age}": str(lead.get_company_age()) if lead.get_company_age() else "many",
            "{day_of_week}": now.strftime("%A"),
            "{current_month}": now.strftime("%B"),
        }
        
        # Add custom fields
        for key, value in lead.custom_fields.items():
            replacements[f"{{{key}}}"] = str(value) if value else ""
        
        # Apply replacements
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def get_step(
        self,
        step_number: int,
        lead: LeadData,
    ) -> Optional[Dict[str, str]]:
        """Get a personalized step from the sequence.
        
        Args:
            step_number: Which step (1-indexed)
            lead: Lead data for personalization
            
        Returns:
            Dict with 'subject', 'body', 'channel', 'sms_body' keys
        """
        for step in self.steps:
            if step.step_number == step_number:
                return {
                    "subject": self.personalize(step.subject_template, lead),
                    "body": self.personalize(step.body_template, lead),
                    "channel": step.channel.value,
                    "sms_body": self.personalize(step.sms_template, lead) if step.sms_template else None,
                    "delay_days": step.delay_days,
                }
        return None
    
    def get_all_steps(self, lead: LeadData) -> List[Dict[str, Any]]:
        """Get all steps personalized for a lead.
        
        Args:
            lead: Lead data for personalization
            
        Returns:
            List of step dicts with scheduling info
        """
        result = []
        cumulative_days = 0
        
        for step in self.steps:
            cumulative_days += step.delay_days
            scheduled_date = datetime.now() + timedelta(days=cumulative_days)
            
            result.append({
                "step_number": step.step_number,
                "channel": step.channel.value,
                "subject": self.personalize(step.subject_template, lead),
                "body": self.personalize(step.body_template, lead),
                "sms_body": self.personalize(step.sms_template, lead) if step.sms_template else None,
                "delay_days": step.delay_days,
                "scheduled_date": scheduled_date.isoformat(),
            })
        
        return result


class DirectOwnerSequence(SequenceTemplate):
    """Sequence A: Direct Owner Outreach - 4 emails over 14 days.
    
    Designed for reaching business owners directly with a consultative,
    value-first approach to acquisition conversations.
    """
    
    def __init__(self):
        super().__init__(SequenceType.DIRECT_OWNER)
    
    def _load_templates(self) -> None:
        """Load the 4-step direct owner sequence."""
        self.steps = [
            SequenceStep(
                step_number=1,
                channel=ChannelType.EMAIL,
                delay_days=0,  # Send immediately
                subject_template="Quick question about {business_name}",
                body_template="""Hi {first_name},

I came across {business_name} while researching successful {industry} companies in {location}. Impressive {company_age}-year track record.

I'm helping a small group of investors acquire established businesses like yours—not to flip or dismantle, but to grow for the long term.

Would you be open to a brief conversation about your succession plans? No pressure, just exploring if there might be a fit.

Best regards,
ACQUISITOR Team

P.S. If now isn't the right time, I completely understand. Just reply "not now" and I'll check back in 6 months.
""",
            ),
            SequenceStep(
                step_number=2,
                channel=ChannelType.EMAIL,
                delay_days=3,  # 3 days after step 1
                subject_template="Re: {business_name} - succession planning insights",
                body_template="""Hi {first_name},

Following up on my note from {day_of_week}. I wanted to share something that might be relevant:

We recently helped a {industry} owner in a similar situation transition their business while keeping 20% equity and staying involved operationally. They got liquidity plus upside, their employees kept their jobs, and the business continues to thrive.

Every situation is different, but I thought you might find the approach interesting.

Worth a 15-minute call to explore what options might exist for {business_name}?

Best,
ACQUISITOR Team

---
Book directly: [Cal.com link]
Or reply to this email with a time that works.
""",
            ),
            SequenceStep(
                step_number=3,
                channel=ChannelType.EMAIL,
                delay_days=5,  # 5 days after step 2 (Day 8 total)
                subject_template="One thing most owners overlook",
                body_template="""{first_name},

Most business owners we speak with have one thing in common: they've spent so much time *in* the business, they haven't planned for life *after* the business.

The result?
- Suboptimal exit timing
- Unnecessary tax burden
- Deals that fall through at the last minute

We've put together a simple 1-page checklist: "5 Things to Do Before You Sell"—no registration required.

Want me to send it over? Takes 2 minutes to read, could save you months of headaches.

Just reply "send it" and I'll forward it along.

Respectfully,
ACQUISITOR Team
""",
            ),
            SequenceStep(
                step_number=4,
                channel=ChannelType.EMAIL,
                delay_days=6,  # 6 days after step 3 (Day 14 total)
                subject_template="Final note - keeping the door open",
                body_template="""Hi {first_name},

This is my final note in this series—I don't believe in pestering busy people.

I'll keep {business_name} on our radar, and if circumstances change on your end, feel free to reach out anytime. We're actively acquiring {industry} businesses and would welcome a conversation whenever the timing is right for you.

Wishing you continued success,

ACQUISITOR Team

---
Unsubscribe: Reply "remove"
Check back later: Reply "follow up in 6 months"
""",
            ),
        ]


class BrokerSequence(SequenceTemplate):
    """Sequence B: Broker Outreach - 3 emails.
    
    Designed for establishing relationships with business brokers
    and intermediaries who represent sellers.
    """
    
    def __init__(self):
        super().__init__(SequenceType.BROKER)
    
    def _load_templates(self) -> None:
        """Load the 3-step broker sequence."""
        self.steps = [
            SequenceStep(
                step_number=1,
                channel=ChannelType.EMAIL,
                delay_days=0,
                subject_template="Partnership opportunity - qualified buyers ready",
                body_template="""Hi {first_name},

I'm reaching out from ACQUISITOR, where we're building a portfolio of {industry} businesses through strategic acquisitions.

Unlike traditional PE or rollup shops, we:
- Keep local management in place
- Don't load companies with debt
- Hold for 7-10 years, not 2-3

We currently have acquisition capacity in the {location} market and are looking to connect with quality brokers representing sellers in the $1M-$10M revenue range.

Would you be open to a brief call to discuss how we might work together? We pay market-rate commissions and close reliably.

Best regards,
ACQUISITOR Team
""",
            ),
            SequenceStep(
                step_number=2,
                channel=ChannelType.EMAIL,
                delay_days=4,
                subject_template="Re: {industry} deals in {location}",
                body_template="""Hi {first_name},

Following up on my note from earlier this week.

To save you time, here's what we're actively looking for:

✓ Industries: {industry}, manufacturing, professional services
✓ Revenue: $1M - $10M annually
✓ EBITDA: $300K+ preferred
✓ Geography: {location} and surrounding areas
✓ Owner involvement: Flexible (can stay or transition out)

We can move quickly—LOI within 2 weeks of receiving materials, close in 60-90 days.

Do you have any current or upcoming listings that might fit?

Best,
ACQUISITOR Team

P.S. We're happy to sign NDAs and provide proof of funds upfront.
""",
            ),
            SequenceStep(
                step_number=3,
                channel=ChannelType.EMAIL,
                delay_days=7,
                subject_template="One last try - keeping you in our network",
                body_template="""Hi {first_name},

I know you're busy with multiple deals, so this is my last outreach on this thread.

I'll add you to our broker network and send you our buyer profile for your files. When you have a listing that might be a fit, feel free to reach out directly.

In the meantime, if you'd ever like to grab coffee in {location} and compare notes on the market, I'm always happy to buy.

Thanks for your time,

ACQUISITOR Team

---
Direct line: [phone]
Deal submissions: deals@acquisitor.com
""",
            ),
        ]


class LandingPageSequence(SequenceTemplate):
    """Sequence C: Landing Page Inbound - 3-step nurture.
    
    For leads who have submitted an inquiry through the landing page.
    Fast, responsive follow-up with multiple touchpoints.
    """
    
    def __init__(self):
        super().__init__(SequenceType.LANDING_PAGE)
    
    def _load_templates(self) -> None:
        """Load the 3-step landing page sequence."""
        self.steps = [
            SequenceStep(
                step_number=1,
                channel=ChannelType.EMAIL,
                delay_days=0,
                subject_template="Thanks for reaching out about {business_name}",
                body_template="""Hi {first_name},

Thanks for submitting your information about {business_name}. We've received your inquiry and are reviewing the details.

Here's what happens next:
1. Our team reviews your business profile (24-48 hours)
2. If it's a potential fit, we'll send you our standard NDA and request basic financials
3. We'll schedule a confidential call to discuss your goals and timeline

In the meantime, if you have any questions, just reply to this email.

Talk soon,

ACQUISITOR Team

---
Book a call now: [Cal.com link]
""",
                sms_template="""Hi {first_name}, thanks for your interest in selling {business_name}. We've received your info and will review within 24-48hrs. Questions? Just reply. -ACQUISITOR""",
            ),
            SequenceStep(
                step_number=2,
                channel=ChannelType.EMAIL,
                delay_days=2,
                subject_template="Quick question about your timeline",
                body_template="""Hi {first_name},

I wanted to follow up on your inquiry about {business_name}.

A couple of quick questions to help us move efficiently:

1. What's your ideal timeline for a sale? (ASAP / 6 months / 1-2 years / just exploring)
2. Are you the sole owner, or are there partners/investors involved?
3. Roughly what does annual revenue look like? (ballpark is fine)

No need for detailed financials yet—just trying to understand if we're in the same ballpark.

If you'd prefer to talk instead of email, grab a time here: [Cal.com link]

Best,
ACQUISITOR Team
""",
                sms_template="""Hi {first_name}, following up on {business_name}. Quick question: what's your ideal timeline for a sale? Reply here or book a call: [link] -ACQUISITOR""",
            ),
            SequenceStep(
                step_number=3,
                channel=ChannelType.EMAIL,
                delay_days=5,
                subject_template="Final follow-up - still interested?",
                body_template="""Hi {first_name},

I haven't heard back on my previous notes, so I wanted to check in one more time about {business_name}.

If you're still interested in exploring a sale or partnership, just reply "still interested" and I'll prioritize your inquiry.

If the timing has changed or you're no longer exploring options, reply "not now" and I'll check back in a few months.

Either way, no pressure—just want to make sure I'm not leaving you hanging.

Best,
ACQUISITOR Team
""",
                sms_template="""Hi {first_name}, haven't heard back on {business_name}. Still interested in exploring a sale? Reply YES and I'll prioritize your inquiry. -ACQUISITOR""",
            ),
        ]


class SequenceManager:
    """Manages all sequence templates and routing."""
    
    def __init__(self):
        self.sequences: Dict[SequenceType, SequenceTemplate] = {
            SequenceType.DIRECT_OWNER: DirectOwnerSequence(),
            SequenceType.BROKER: BrokerSequence(),
            SequenceType.LANDING_PAGE: LandingPageSequence(),
        }
    
    def get_sequence(self, sequence_type: SequenceType) -> SequenceTemplate:
        """Get a sequence template by type.
        
        Args:
            sequence_type: Which sequence to retrieve
            
        Returns:
            The requested SequenceTemplate
        """
        return self.sequences[sequence_type]
    
    def generate_sequence_for_lead(
        self,
        lead: LeadData,
        sequence_type: SequenceType,
    ) -> List[Dict[str, Any]]:
        """Generate a complete personalized sequence for a lead.
        
        Args:
            lead: Lead data for personalization
            sequence_type: Which sequence to use
            
        Returns:
            List of personalized steps ready for scheduling
        """
        sequence = self.sequences[sequence_type]
        steps = sequence.get_all_steps(lead)
        
        logger.info(
            f"Generated {len(steps)}-step {sequence_type.value} sequence "
            f"for lead {lead.lead_id} ({lead.business_name})"
        )
        
        return steps
    
    def determine_sequence_type(self, lead: LeadData) -> SequenceType:
        """Determine the best sequence type for a lead.
        
        Args:
            lead: Lead data
            
        Returns:
            Recommended SequenceType
        """
        # If source is landing page or inbound marker, use landing page sequence
        if lead.custom_fields.get("source") == "landing_page":
            return SequenceType.LANDING_PAGE
        
        # If contact is a broker/intermediary, use broker sequence
        if lead.custom_fields.get("contact_type") == "broker":
            return SequenceType.BROKER
        
        # Default: direct owner outreach
        return SequenceType.DIRECT_OWNER


# Global sequence manager instance
_sequence_manager: Optional[SequenceManager] = None


def get_sequence_manager() -> SequenceManager:
    """Get or create global sequence manager."""
    global _sequence_manager
    if _sequence_manager is None:
        _sequence_manager = SequenceManager()
    return _sequence_manager


def generate_sequence(
    lead: LeadData,
    sequence_type: Optional[SequenceType] = None,
) -> List[Dict[str, Any]]:
    """Convenience function to generate a sequence for a lead.
    
    Args:
        lead: Lead data for personalization
        sequence_type: Which sequence (auto-detected if None)
        
    Returns:
        List of personalized steps
    """
    manager = get_sequence_manager()
    
    if sequence_type is None:
        sequence_type = manager.determine_sequence_type(lead)
    
    return manager.generate_sequence_for_lead(lead, sequence_type)
