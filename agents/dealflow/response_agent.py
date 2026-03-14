#!/usr/bin/env python3
"""
DEALFLOW Response Agent
AI-powered reply generation with guardrails and personalization.
"""

import json
import logging
import re
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path

import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of responses to generate."""
    STANDARD = "standard"
    COMPLEX_NEGOTIATION = "complex_negotiation"
    SMS = "sms"
    FOLLOW_UP = "follow_up"
    DECLINE_ACK = "decline_ack"
    QUESTION_ANSWER = "question_answer"


class ModelRouter:
    """Routes requests to appropriate Claude models."""
    
    MODELS = {
        ResponseType.STANDARD: "claude-3-sonnet-20240229",
        ResponseType.COMPLEX_NEGOTIATION: "claude-3-opus-20240229",
        ResponseType.SMS: "claude-3-haiku-20240307",
        ResponseType.FOLLOW_UP: "claude-3-sonnet-20240229",
        ResponseType.DECLINE_ACK: "claude-3-haiku-20240307",
        ResponseType.QUESTION_ANSWER: "claude-3-sonnet-20240229",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self._lock = threading.RLock()
        self._usage_stats: Dict[str, int] = {}
    
    def get_model(self, response_type: ResponseType) -> str:
        """Get the appropriate model for a response type."""
        return self.MODELS.get(response_type, "claude-3-sonnet-20240229")
    
    def generate(
        self,
        response_type: ResponseType,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a response using the appropriate model.
        
        Args:
            response_type: Type of response needed
            prompt: The formatted prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        model = self.get_model(response_type)
        
        with self._lock:
            self._usage_stats[model] = self._usage_stats.get(model, 0) + 1
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Generation failed with model {model}: {e}")
            raise


@dataclass
class LeadData:
    """Lead information for personalization."""
    name: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    revenue_range: Optional[str] = None
    previous_interactions: int = 0
    notes: Optional[str] = None
    
    def to_context(self) -> str:
        """Convert to context string for prompts."""
        parts = [f"Name: {self.name}"]
        if self.company_name:
            parts.append(f"Company: {self.company_name}")
        if self.industry:
            parts.append(f"Industry: {self.industry}")
        if self.location:
            parts.append(f"Location: {self.location}")
        if self.previous_interactions > 0:
            parts.append(f"Previous interactions: {self.previous_interactions}")
        if self.notes:
            parts.append(f"Notes: {self.notes}")
        return "\n".join(parts)


@dataclass
class ConversationMessage:
    """A single message in conversation history."""
    role: str  # 'lead' or 'system'
    content: str
    timestamp: datetime
    message_id: Optional[str] = None


class GuardrailChecker:
    """Validates responses against safety guardrails."""
    
    # Patterns that indicate problematic content
    PROBLEMATIC_PATTERNS = {
        "price_commitment": [
            r"\$\d+[,\d]*\s*(million|m|k|thousand)",
            r"offer\s+(of\s+)?\$\d+",
            r"will\s+pay\s+\$\d+",
            r"guarantee\s+\$\d+",
        ],
        "deal_commitment": [
            r"we\s+will\s+(definitely|certainly|absolutely)\s+buy",
            r"deal\s+is\s+done",
            r"you\s+have\s+a\s+deal",
            r"offer\s+accepted",
        ],
        "pressure_language": [
            r"you\s+must\s+respond",
            r"urgent\s+action\s+required",
            r"limited\s+time",
            r"don't\s+miss\s+out",
            r"act\s+now",
        ],
        "legal_financial_advice": [
            r"you\s+should\s+(consult|get)\s+a\s+lawyer",
            r"tax\s+(benefit|advantage|implication)",
            r"legal\s+(requirement|obligation)",
        ],
    }
    
    # Escalation triggers
    ESCALATION_PATTERNS = [
        r"lawyer",
        r"attorney",
        r"legal\s+(action|notice|threat)",
        r"lawsuit",
        r"sue",
        r"regulatory",
        r"sec",
        r"fraud",
        r"misrepresentation",
    ]
    
    def check_response(self, response: str) -> Tuple[bool, List[str], bool]:
        """
        Check response against guardrails.
        
        Returns:
            Tuple of (is_valid, violations, needs_escalation)
        """
        violations = []
        needs_escalation = False
        response_lower = response.lower()
        
        # Check each violation category
        for category, patterns in self.PROBLEMATIC_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, response_lower, re.IGNORECASE):
                    violations.append(category)
                    break
        
        # Check escalation triggers
        for pattern in self.ESCALATION_PATTERNS:
            if re.search(pattern, response_lower, re.IGNORECASE):
                needs_escalation = True
                violations.append("legal_financial_question")
                break
        
        is_valid = len(violations) == 0
        
        return is_valid, list(set(violations)), needs_escalation
    
    def check_for_ai_question(self, message: str) -> bool:
        """Check if the user is asking if we're an AI."""
        patterns = [
            r"are\s+you\s+(an?\s+)?(ai|bot|robot|computer)",
            r"are\s+you\s+human",
            r"is\s+this\s+(an?\s+)?(ai|bot|automated)",
            r"am\s+i\s+talking\s+to\s+(an?\s+)?(ai|bot|human)",
        ]
        message_lower = message.lower()
        return any(re.search(p, message_lower) for p in patterns)


class SoulLoader:
    """Loads and applies SOUL.md tone/personality."""
    
    DEFAULT_TONE = """You are a professional, friendly acquisition specialist.
Tone: Professional but approachable, concise but warm.
Style: Direct, no fluff, respectful of the lead's time."""
    
    def __init__(self, soul_path: Optional[Path] = None):
        self.soul_path = soul_path or Path("SOUL.md")
        self._tone: Optional[str] = None
        self._lock = threading.RLock()
    
    def load(self) -> str:
        """Load SOUL.md content."""
        with self._lock:
            if self._tone is not None:
                return self._tone
            
            if self.soul_path.exists():
                try:
                    content = self.soul_path.read_text()
                    # Extract tone section if structured
                    self._tone = self._extract_tone(content)
                    logger.info(f"Loaded SOUL.md from {self.soul_path}")
                except Exception as e:
                    logger.warning(f"Failed to load SOUL.md: {e}, using default")
                    self._tone = self.DEFAULT_TONE
            else:
                self._tone = self.DEFAULT_TONE
            
            return self._tone
    
    def _extract_tone(self, content: str) -> str:
        """Extract tone/personality section from SOUL.md."""
        # Look for tone section
        tone_match = re.search(
            r'(?:#+\s*(?:Tone|Personality|Voice)|Tone:|Personality:)\s*\n?(.*?)(?:\n#|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if tone_match:
            return tone_match.group(1).strip()
        
        # If no specific section, use the whole content
        return content.strip()
    
    def reload(self) -> None:
        """Force reload of SOUL.md."""
        with self._lock:
            self._tone = None


class CANSPAMCompliance:
    """Handles CAN-SPAM compliance requirements."""
    
    def __init__(
        self,
        company_name: str,
        physical_address: str,
        unsubscribe_link: Optional[str] = None,
        reply_to: Optional[str] = None
    ):
        self.company_name = company_name
        self.physical_address = physical_address
        self.unsubscribe_link = unsubscribe_link
        self.reply_to = reply_to
    
    def add_footer(self, email_body: str, is_marketing: bool = False) -> str:
        """
        Add CAN-SPAM compliant footer to email.
        
        Args:
            email_body: The main email content
            is_marketing: Whether this is a marketing email
            
        Returns:
            Email with compliant footer
        """
        footer_parts = [
            "",
            "---",
            f"{self.company_name}",
            f"{self.physical_address}",
        ]
        
        if is_marketing:
            footer_parts.append("")
            if self.unsubscribe_link:
                footer_parts.append(f"Unsubscribe: {self.unsubscribe_link}")
            else:
                footer_parts.append('Reply with "UNSUBSCRIBE" to opt out.')
        
        footer = "\n".join(footer_parts)
        return email_body + footer
    
    def validate(self, email_body: str) -> Tuple[bool, List[str]]:
        """
        Validate that email meets CAN-SPAM requirements.
        
        Returns:
            Tuple of (is_valid, missing_requirements)
        """
        missing = []
        body_lower = email_body.lower()
        
        # Check for physical address
        address_indicators = ["ave", "street", "st.", "blvd", "suite", "floor", "city", "state"]
        has_address = any(ind in body_lower for ind in address_indicators)
        
        if not has_address:
            missing.append("physical_address")
        
        # Check for unsubscribe option
        if "unsubscribe" not in body_lower and "opt out" not in body_lower:
            missing.append("unsubscribe_option")
        
        return len(missing) == 0, missing


class ResponseAgent:
    """
    Main response generation agent with guardrails and personalization.
    """
    
    SYSTEM_PROMPT_TEMPLATE = """{tone}

You are responding to a potential seller who has expressed interest in discussing the acquisition of their business.

LEAD INFORMATION:
{lead_info}

CONVERSATION HISTORY:
{conversation_history}

GUARDRAILS (CRITICAL - DO NOT VIOLATE):
1. NEVER commit to specific deal terms, prices, or timelines
2. NEVER provide legal, tax, or financial advice
3. NEVER pressure the lead or use urgency tactics
4. ALWAYS respect a clear "no" or "not interested"
5. ALWAYS escalate legal/financial questions to human team
6. {ai_acknowledgment}

RESPONSE GUIDELINES:
- Keep responses concise and professional
- Address specific questions directly
- Show genuine interest in their business
- Move toward a phone call when appropriate
- Be helpful without being pushy

Generate a response to the following message:

CURRENT MESSAGE FROM LEAD:
{current_message}

{response_specific_instructions}

Your response:"""
    
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        soul_path: Optional[Path] = None,
        canspam_config: Optional[Dict[str, str]] = None
    ):
        self.model_router = ModelRouter(api_key=anthropic_api_key)
        self.guardrails = GuardrailChecker()
        self.soul = SoulLoader(soul_path)
        self.canspam = CANSPAMCompliance(
            company_name=canspam_config.get("company_name", "Acquisition Co.") if canspam_config else "Acquisition Co.",
            physical_address=canspam_config.get("physical_address", "123 Business Ave") if canspam_config else "123 Business Ave",
            unsubscribe_link=canspam_config.get("unsubscribe_link") if canspam_config else None
        ) if canspam_config else None
        self._lock = threading.RLock()
    
    def generate_response(
        self,
        current_message: str,
        conversation_history: List[ConversationMessage],
        lead_data: Optional[LeadData] = None,
        response_type: ResponseType = ResponseType.STANDARD,
        is_marketing: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response with full guardrails and compliance.
        
        Args:
            current_message: The message to respond to
            conversation_history: Previous messages in the conversation
            lead_data: Personalization data for the lead
            response_type: Type of response needed
            is_marketing: Whether this is a marketing email
            
        Returns:
            Dict with response text, metadata, and any flags
        """
        # Check if user asked if we're AI
        ai_question = self.guardrails.check_for_ai_question(current_message)
        ai_acknowledgment = (
            "If asked if you are an AI, acknowledge honestly that you are an AI assistant helping with initial conversations, but a human will handle the actual transaction."
            if ai_question else ""
        )
        
        # Build prompt
        prompt = self._build_prompt(
            current_message=current_message,
            conversation_history=conversation_history,
            lead_data=lead_data,
            response_type=response_type,
            ai_acknowledgment=ai_acknowledgment
        )
        
        # Generate response
        try:
            raw_response = self.model_router.generate(
                response_type=response_type,
                prompt=prompt,
                max_tokens=self._get_max_tokens(response_type),
                temperature=0.7
            )
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "escalate": True
            }
        
        # Apply guardrails
        is_valid, violations, needs_escalation = self.guardrails.check_response(raw_response)
        
        if not is_valid:
            logger.warning(f"Guardrail violations: {violations}")
            # Regenerate with stronger guardrails
            prompt += f"\n\nWARNING: Previous response violated these rules: {', '.join(violations)}. Please regenerate avoiding these issues."
            try:
                raw_response = self.model_router.generate(
                    response_type=response_type,
                    prompt=prompt,
                    max_tokens=self._get_max_tokens(response_type),
                    temperature=0.5  # Lower temperature for more control
                )
                # Re-check
                is_valid, violations, needs_escalation = self.guardrails.check_response(raw_response)
            except Exception as e:
                logger.error(f"Regeneration failed: {e}")
                needs_escalation = True
        
        # Add CAN-SPAM footer if configured
        final_response = raw_response
        if self.canspam and is_marketing:
            final_response = self.canspam.add_footer(raw_response, is_marketing=True)
        
        return {
            "success": True,
            "response": final_response,
            "violations": violations if violations else None,
            "escalate": needs_escalation,
            "model_used": self.model_router.get_model(response_type),
            "acknowledged_ai": ai_question
        }
    
    def generate_sms_response(
        self,
        current_message: str,
        conversation_history: List[ConversationMessage],
        lead_data: Optional[LeadData] = None
    ) -> Dict[str, Any]:
        """Generate a short SMS response."""
        return self.generate_response(
            current_message=current_message,
            conversation_history=conversation_history,
            lead_data=lead_data,
            response_type=ResponseType.SMS,
            is_marketing=False
        )
    
    def _build_prompt(
        self,
        current_message: str,
        conversation_history: List[ConversationMessage],
        lead_data: Optional[LeadData],
        response_type: ResponseType,
        ai_acknowledgment: str
    ) -> str:
        """Build the complete prompt for response generation."""
        tone = self.soul.load()
        lead_info = lead_data.to_context() if lead_data else "Name: Unknown"
        
        # Format conversation history
        history_str = self._format_history(conversation_history)
        
        # Type-specific instructions
        type_instructions = {
            ResponseType.STANDARD: "Write a natural, professional response.",
            ResponseType.COMPLEX_NEGOTIATION: "This is a complex negotiation. Be very careful not to commit to anything. Ask clarifying questions.",
            ResponseType.SMS: "Write a brief SMS response (under 160 characters if possible, max 320).",
            ResponseType.FOLLOW_UP: "This is a follow-up. Reference previous conversation briefly.",
            ResponseType.DECLINE_ACK: "The lead declined. Acknowledge respectfully and leave the door open for future contact.",
            ResponseType.QUESTION_ANSWER: "The lead has questions. Answer clearly and concisely. If you don't know, say you'll have someone follow up.",
        }
        
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            tone=tone,
            lead_info=lead_info,
            conversation_history=history_str,
            current_message=current_message,
            ai_acknowledgment=ai_acknowledgment,
            response_specific_instructions=type_instructions.get(response_type, "")
        )
    
    def _format_history(self, history: List[ConversationMessage]) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return "No previous messages."
        
        lines = []
        for msg in sorted(history, key=lambda m: m.timestamp):
            speaker = "Lead" if msg.role == "lead" else "Us"
            lines.append(f"[{speaker}]: {msg.content[:300]}")
        
        return "\n".join(lines[-10:])  # Last 10 messages
    
    def _get_max_tokens(self, response_type: ResponseType) -> int:
        """Get appropriate max tokens for response type."""
        token_limits = {
            ResponseType.SMS: 150,
            ResponseType.DECLINE_ACK: 200,
            ResponseType.STANDARD: 400,
            ResponseType.FOLLOW_UP: 400,
            ResponseType.QUESTION_ANSWER: 500,
            ResponseType.COMPLEX_NEGOTIATION: 800,
        }
        return token_limits.get(response_type, 400)
    
    def validate_response(self, response: str, is_marketing: bool = False) -> Dict[str, Any]:
        """Validate a response against all requirements."""
        guardrail_valid, violations, escalate = self.guardrails.check_response(response)
        
        result = {
            "guardrail_valid": guardrail_valid,
            "guardrail_violations": violations,
            "needs_escalation": escalate,
        }
        
        if self.canspam and is_marketing:
            canspam_valid, missing = self.canspam.validate(response)
            result["canspam_valid"] = canspam_valid
            result["canspam_missing"] = missing
        
        return result


# Integration helper for inbox_monitor
class ResponseAgentHandler:
    """Handler that integrates ResponseAgent with inbox_monitor router."""
    
    def __init__(self, agent: ResponseAgent):
        self.agent = agent
    
    def handle_interested(
        self,
        email: Any,
        category: Any,
        context: Any
    ) -> Dict[str, Any]:
        """Handle interested leads."""
        lead_data = self._extract_lead_data(context)
        history = self._extract_history(context)
        
        result = self.agent.generate_response(
            current_message=email.body,
            conversation_history=history,
            lead_data=lead_data,
            response_type=ResponseType.STANDARD
        )
        
        return {
            "action": "send_response",
            "response": result.get("response"),
            "escalate": result.get("escalate", False),
            "metadata": result
        }
    
    def handle_question(
        self,
        email: Any,
        category: Any,
        context: Any
    ) -> Dict[str, Any]:
        """Handle question emails."""
        lead_data = self._extract_lead_data(context)
        history = self._extract_history(context)
        
        result = self.agent.generate_response(
            current_message=email.body,
            conversation_history=history,
            lead_data=lead_data,
            response_type=ResponseType.QUESTION_ANSWER
        )
        
        return {
            "action": "send_response",
            "response": result.get("response"),
            "escalate": result.get("escalate", False),
            "metadata": result
        }
    
    def handle_not_interested(
        self,
        email: Any,
        category: Any,
        context: Any
    ) -> Dict[str, Any]:
        """Handle not interested responses."""
        lead_data = self._extract_lead_data(context)
        history = self._extract_history(context)
        
        result = self.agent.generate_response(
            current_message=email.body,
            conversation_history=history,
            lead_data=lead_data,
            response_type=ResponseType.DECLINE_ACK
        )
        
        return {
            "action": "send_response",
            "response": result.get("response"),
            "escalate": False,
            "metadata": result
        }
    
    def _extract_lead_data(self, context: Any) -> Optional[LeadData]:
        """Extract lead data from context."""
        if context and context.lead_data:
            return LeadData(
                name=context.lead_data.get("name", "Unknown"),
                company_name=context.lead_data.get("company_name"),
                industry=context.lead_data.get("industry"),
                location=context.lead_data.get("location"),
                notes=context.lead_data.get("notes")
            )
        return None
    
    def _extract_history(self, context: Any) -> List[ConversationMessage]:
        """Extract conversation history from context."""
        history = []
        if context and context.messages:
            for msg in context.messages[:-1]:  # Exclude current message
                history.append(ConversationMessage(
                    role="lead",
                    content=msg.body,
                    timestamp=msg.timestamp,
                    message_id=msg.message_id
                ))
        return history


def create_response_agent(
    anthropic_api_key: Optional[str] = None,
    soul_path: Optional[Path] = None,
    canspam_config: Optional[Dict[str, str]] = None
) -> ResponseAgent:
    """Factory function to create a configured ResponseAgent."""
    return ResponseAgent(
        anthropic_api_key=anthropic_api_key,
        soul_path=soul_path,
        canspam_config=canspam_config
    )


if __name__ == "__main__":
    # Example usage
    agent = create_response_agent()
    
    lead = LeadData(
        name="John Smith",
        company_name="Smith Manufacturing",
        industry="Manufacturing",
        location="Denver, CO"
    )
    
    history = [
        ConversationMessage(
            role="system",
            content="Hi John, I came across Smith Manufacturing and was impressed by your 20-year track record. We're actively acquiring manufacturing businesses and I'd love to learn more about your goals.",
            timestamp=datetime.now()
        )
    ]
    
    result = agent.generate_response(
        current_message="Thanks for reaching out. I'm potentially interested in selling but want to understand the process better. How does this work?",
        conversation_history=history,
        lead_data=lead,
        response_type=ResponseType.STANDARD
    )
    
    print("Generated Response:")
    print(result.get("response"))
    print(f"\nEscalate: {result.get('escalate')}")
