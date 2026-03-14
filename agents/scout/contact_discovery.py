"""Contact discovery - finds owner contact information."""
import logging
import re
from typing import List, Optional, Dict, Any
from enum import Enum

from models import CandidateBusiness, ContactInfo, ContactRole

logger = logging.getLogger(__name__)


class ContactDiscovery:
    """Discovers contact information for business owners/executives."""
    
    # Role priority (highest first)
    ROLE_PRIORITY = [
        ContactRole.OWNER,
        ContactRole.FOUNDER,
        ContactRole.PRESIDENT,
        ContactRole.MANAGING_PARTNER,
        ContactRole.OPERATOR,
        ContactRole.GENERAL_MANAGER,
        ContactRole.MANAGER,
    ]
    
    # Patterns to identify roles in text
    ROLE_PATTERNS = {
        ContactRole.OWNER: [
            r'\bowner\b', r'\bproprietor\b', r'\bsole proprietor\b',
            r'\bprincipal owner\b', r'\bmanaging owner\b'
        ],
        ContactRole.FOUNDER: [
            r'\bfounder\b', r'\bco-founder\b', r'\bco-founder\b',
            r'\bestablished by\b', r'\bstarted by\b'
        ],
        ContactRole.PRESIDENT: [
            r'\bpresident\b', r'\bceo\b', r'\bc\.e\.o\.\b',
            r'\bchief executive\b'
        ],
        ContactRole.MANAGING_PARTNER: [
            r'\bmanaging partner\b', r'\bgeneral partner\b',
            r'\bsenior partner\b'
        ],
        ContactRole.OPERATOR: [
            r'\boperator\b', r'\bdirector\b', r'\bprincipal\b'
        ],
        ContactRole.GENERAL_MANAGER: [
            r'\bgeneral manager\b', r'\bg\.m\.\b', r'\boperations manager\b'
        ],
        ContactRole.MANAGER: [
            r'\bmanager\b', r'\bdirector\b'
        ],
    }
    
    def __init__(self):
        self.contacts_found: List[ContactInfo] = []
    
    def find_contact(self, candidate: CandidateBusiness) -> Optional[ContactInfo]:
        """Find best contact for a business candidate.
        
        Priority: owner > founder > president > managing partner > operator > GM
        
        Args:
            candidate: Business candidate
            
        Returns:
            Best contact info or None
        """
        logger.info(f"Finding contact for: {candidate.name}")
        
        all_contacts: List[ContactInfo] = []
        
        # Try website extraction
        if candidate.website:
            website_contact = self.extract_from_website(candidate.website)
            if website_contact:
                all_contacts.append(website_contact)
        
        # Try raw data from discovery source
        if candidate.raw_data:
            raw_contacts = self._extract_from_raw_data(candidate.raw_data)
            all_contacts.extend(raw_contacts)
        
        # Try email domain matching
        if candidate.email:
            contact = ContactInfo(
                email=candidate.email,
                role=ContactRole.UNKNOWN,
                source="business_email"
            )
            all_contacts.append(contact)
        
        # Select best contact by role priority
        best_contact = self._select_best_contact(all_contacts)
        
        if best_contact:
            logger.info(f"Found contact: {best_contact.name or best_contact.email} ({best_contact.role.value})")
        else:
            logger.info(f"No contact found for: {candidate.name}")
        
        return best_contact
    
    def extract_from_website(self, website_url: str) -> Optional[ContactInfo]:
        """Extract owner/executive contact from website.
        
        Args:
            website_url: Business website URL
            
        Returns:
            Contact info or None
        """
        logger.info(f"Extracting contact from website: {website_url}")
        
        # In production:
        # - Fetch /about, /team, /contact pages
        # - Parse for names and roles
        # - Look for LinkedIn links
        # - Extract contact forms
        
        # Simulate finding a contact
        import random
        if random.random() > 0.5:
            roles = [ContactRole.OWNER, ContactRole.FOUNDER, ContactRole.PRESIDENT]
            return ContactInfo(
                name=f"Contact at {website_url}",
                role=random.choice(roles),
                source="website",
                confidence=0.6
            )
        
        return None
    
    def _extract_from_raw_data(self, raw_data: Dict[str, Any]) -> List[ContactInfo]:
        """Extract contacts from raw discovery data.
        
        Args:
            raw_data: Raw data from discovery source
            
        Returns:
            List of contact info
        """
        contacts = []
        
        # Check for explicit contact fields
        if "contact_name" in raw_data:
            role = self._detect_role(raw_data.get("contact_title", ""))
            contacts.append(ContactInfo(
                name=raw_data["contact_name"],
                role=role,
                email=raw_data.get("contact_email"),
                phone=raw_data.get("contact_phone"),
                source="raw_data"
            ))
        
        # Check for registered agent (registry data)
        if "registered_agent" in raw_data:
            contacts.append(ContactInfo(
                name=raw_data["registered_agent"],
                role=ContactRole.UNKNOWN,
                source="registry"
            ))
        
        return contacts
    
    def _detect_role(self, text: str) -> ContactRole:
        """Detect contact role from text.
        
        Args:
            text: Text to analyze (title, description, etc.)
            
        Returns:
            Detected role
        """
        text_lower = text.lower()
        
        for role in self.ROLE_PRIORITY:
            patterns = self.ROLE_PATTERNS.get(role, [])
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return role
        
        return ContactRole.UNKNOWN
    
    def _select_best_contact(self, contacts: List[ContactInfo]) -> Optional[ContactInfo]:
        """Select best contact by role priority.
        
        Args:
            contacts: List of potential contacts
            
        Returns:
            Best contact or None
        """
        if not contacts:
            return None
        
        # Score each contact by role priority and data completeness
        def score_contact(contact: ContactInfo) -> int:
            score = 0
            
            # Role priority (higher index = higher priority in ROLE_PRIORITY)
            try:
                role_index = self.ROLE_PRIORITY.index(contact.role)
                score += (len(self.ROLE_PRIORITY) - role_index) * 10
            except ValueError:
                pass
            
            # Data completeness
            if contact.email: score += 5
            if contact.phone: score += 3
            if contact.name: score += 2
            if contact.linkedin: score += 2
            
            # Confidence boost
            score += int(contact.confidence * 10)
            
            return score
        
        return max(contacts, key=score_contact)
    
    def extract_linkedin_profile(self, name: str, company: str) -> Optional[str]:
        """Find LinkedIn profile for a person.
        
        Args:
            name: Person's name
            company: Company name
            
        Returns:
            LinkedIn URL or None
        """
        # In production, this would:
        # - Search LinkedIn API
        # - Use Google search
        # - Match profiles by company and name
        
        logger.info(f"Searching LinkedIn for: {name} at {company}")
        return None
    
    def verify_email(self, email: str, domain: str) -> bool:
        """Verify if email is likely valid.
        
        Args:
            email: Email address
            domain: Expected domain
            
        Returns:
            True if likely valid
        """
        if not email or "@" not in email:
            return False
        
        email_domain = email.split("@")[1].lower()
        
        # Check if email domain matches or is common variation
        if email_domain == domain.lower():
            return True
        
        # Allow common email providers for small businesses
        common_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com"}
        if email_domain in common_domains:
            return True
        
        return False


def find_business_contact(candidate: CandidateBusiness) -> Optional[ContactInfo]:
    """Convenience function to find contact for a business.
    
    Args:
        candidate: Business candidate
        
    Returns:
        Best contact info or None
    """
    discovery = ContactDiscovery()
    return discovery.find_contact(candidate)
