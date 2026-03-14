"""
AI Integration Module - Claude API for ACQUISITOR
Handles lead scoring, email generation, and reply classification
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

# Anthropic API
import anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

class AcquisitorAI:
    """AI assistant for acquisition tasks"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
        self.model = "claude-3-5-sonnet-20241022"  # Use Sonnet for quality
        self.fast_model = "claude-3-haiku-20240307"  # Use Haiku for speed
    
    async def score_lead(self, lead: Dict, buyer_profile: Dict) -> Dict:
        """
        Score a lead based on buyer profile
        Returns: {score: int (0-100), assessment: str, reasons: List[str]}
        """
        if not self.client:
            # Fallback scoring without AI
            return self._fallback_score(lead, buyer_profile)
        
        prompt = f"""You are an expert business acquisition analyst. Score this business opportunity for the buyer.

BUYER PROFILE:
- Background: {buyer_profile.get('background', 'Not specified')}
- Industries of interest: {', '.join(buyer_profile.get('industries', []))}
- Budget: ${buyer_profile.get('budget_min', 0):,} - ${buyer_profile.get('budget_max', 0):,}
- Revenue preference: ${buyer_profile.get('revenue_min', 0):,} - ${buyer_profile.get('revenue_max', 0):,}
- Location preference: {', '.join(buyer_profile.get('location_preference', []))}
- Values: {', '.join(buyer_profile.get('values', []))}

BUSINESS FOR SALE:
- Name: {lead.get('name', 'Unknown')}
- Industry: {lead.get('industry', 'Unknown')}
- Revenue: ${lead.get('revenue', 0):,}
- Employees: {lead.get('employees', 0)}
- Location: {lead.get('city', '')}, {lead.get('state', '')}
- Description: {lead.get('description', 'No description')}

Provide your analysis in this exact format:
SCORE: [number 0-100]
ASSESSMENT: [2-3 sentence summary of why this is/isn't a good fit]
KEY_REASONS:
- [reason 1]
- [reason 2]
- [reason 3]
RISKS:
- [risk 1]
- [risk 2]
QUESTIONS_FOR_CALL:
- [question 1]
- [question 2]
- [question 3]
"""
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.messages.create,
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=10.0
            )
            
            content = response.content[0].text
            
            # Parse response
            score = self._extract_score(content)
            assessment = self._extract_section(content, "ASSESSMENT")
            reasons = self._extract_list(content, "KEY_REASONS")
            risks = self._extract_list(content, "RISKS")
            questions = self._extract_list(content, "QUESTIONS_FOR_CALL")
            
            return {
                "score": score,
                "assessment": assessment,
                "reasons": reasons,
                "risks": risks,
                "questions": questions,
                "raw_response": content
            }
            
        except Exception as e:
            print(f"AI scoring error: {e}")
            return self._fallback_score(lead, buyer_profile)
    
    async def generate_email(self, lead: Dict, buyer_profile: Dict, sequence_step: int = 0) -> Dict:
        """
        Generate personalized outreach email
        Returns: {subject: str, body: str, tone: str}
        """
        if not self.client:
            return self._fallback_email(lead, sequence_step)
        
        sequences = {
            0: "Initial outreach - first contact, establish credibility, ask for conversation",
            1: "Follow-up - 3 days later, reference first email, more direct ask",
            2: "Final attempt - 7 days later, acknowledge they might not be interested, professional close"
        }
        
        sequence_desc = sequences.get(sequence_step, sequences[0])
        
        prompt = f"""Write a personalized cold email from an acquisition entrepreneur to a business owner.

SENDER (Acquisition Entrepreneur):
- Background: {buyer_profile.get('background', 'Business professional')}
- Looking to acquire: {buyer_profile.get('industries', ['business'])[0] if buyer_profile.get('industries') else 'business'} in {buyer_profile.get('location_preference', ['the area'])[0]}
- Values: {', '.join(buyer_profile.get('values', ['growth', 'team retention']))}

RECIPIENT (Business Owner):
- Business: {lead.get('name', 'Their business')}
- Industry: {lead.get('industry', 'Services')}
- Location: {lead.get('city', '')}, {lead.get('state', '')}
- Description: {lead.get('description', '')}

EMAIL SEQUENCE: {sequence_desc}

Requirements:
1. Subject line should be personalized and not salesy
2. Keep email under 150 words
3. Sound like a real person, not marketing copy
4. Reference specific details about their business
5. Clear but low-pressure call to action
6. Professional but conversational tone

Format your response exactly as:
SUBJECT: [subject line]
BODY:
[email body]
"""
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.messages.create,
                    model=self.model,
                    max_tokens=800,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=10.0
            )
            
            content = response.content[0].text
            
            subject = self._extract_line(content, "SUBJECT")
            body = self._extract_section(content, "BODY")
            
            return {
                "subject": subject or f"Question about {lead.get('name', 'your business')}",
                "body": body or self._fallback_email(lead, sequence_step)["body"],
                "tone": "personalized",
                "sequence_step": sequence_step
            }
            
        except Exception as e:
            print(f"Email generation error: {e}")
            return self._fallback_email(lead, sequence_step)
    
    async def classify_reply(self, email_subject: str, email_body: str) -> Dict:
        """
        Classify email reply into categories
        Returns: {category: str, sentiment: str, action_needed: str}
        """
        if not self.client:
            return self._fallback_classification(email_body)
        
        prompt = f"""Classify this email reply from a business owner.

Email Subject: {email_subject}
Email Body:
{email_body}

Classify into ONE of these categories:
1. INTERESTED - Wants to talk, positive about selling
2. INTERESTED_LATER - Interested but not ready now, wants to talk in future
3. CURIOUS - Asking questions but not committed
4. NOT_INTERESTED - Explicitly not interested
5. NOT_SELLING - Says business is not for sale
6. PRICE_TOO_LOW - Interested but thinks offer would be too low
7. BROKER - Forwarded to broker/agent
8. OTHER - Doesn't fit above categories

Also determine:
- Sentiment: positive, neutral, or negative
- Action: what should we do next?

Format:
CATEGORY: [category name]
CONFIDENCE: [high/medium/low]
SENTIMENT: [positive/neutral/negative]
SUMMARY: [1 sentence summary]
ACTION: [specific action to take]
"""
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.messages.create,
                    model=self.fast_model,  # Use fast model for classification
                    max_tokens=300,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=5.0
            )
            
            content = response.content[0].text
            
            return {
                "category": self._extract_line(content, "CATEGORY").upper().replace(" ", "_"),
                "confidence": self._extract_line(content, "CONFIDENCE").lower(),
                "sentiment": self._extract_line(content, "SENTIMENT").lower(),
                "summary": self._extract_line(content, "SUMMARY"),
                "action": self._extract_line(content, "ACTION"),
                "raw": content
            }
            
        except Exception as e:
            print(f"Classification error: {e}")
            return self._fallback_classification(email_body)
    
    async def generate_response(self, email_thread: List[Dict], buyer_profile: Dict) -> str:
        """
        Generate AI response to owner reply
        """
        if not self.client:
            return "Thank you for your response. I'd love to schedule a brief call to discuss further. What time works for you this week?"
        
        # Build conversation history
        history = "\n\n".join([
            f"{'Owner' if i % 2 == 1 else 'Me'}: {msg.get('body', '')}"
            for i, msg in enumerate(email_thread[-3:])  # Last 3 messages
        ])
        
        prompt = f"""Write a reply to this business owner.

CONVERSATION HISTORY:
{history}

MY BACKGROUND:
{buyer_profile.get('background', 'Entrepreneur looking to acquire a business')}

Requirements:
1. Reference specific points from their email
2. Keep it under 100 words
3. Professional but warm tone
4. Move toward scheduling a call
5. Don't be pushy

Write the reply email body only (no subject):
"""
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.messages.create,
                    model=self.model,
                    max_tokens=400,
                    temperature=0.5,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=8.0
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Response generation error: {e}")
            return "Thank you for your response. I'd love to schedule a brief call to discuss further. What time works for you this week?"
    
    # Helper methods
    def _fallback_score(self, lead: Dict, buyer_profile: Dict) -> Dict:
        """Fallback scoring without AI"""
        score = 50
        
        # Simple heuristics
        revenue = lead.get('revenue', 0)
        if revenue >= 2000000:
            score += 20
        elif revenue >= 1000000:
            score += 10
        
        return {
            "score": min(100, score),
            "assessment": f"{lead.get('name', 'This business')} appears to be a moderate match based on revenue and industry.",
            "reasons": ["Revenue in target range", f"{lead.get('industry', 'Industry')} aligns with interests"],
            "risks": ["Need to verify financials", "Owner motivation unclear"],
            "questions": ["What is your timeline for selling?", "Are you open to seller financing?"],
            "raw_response": "Fallback scoring (AI unavailable)"
        }
    
    def _fallback_email(self, lead: Dict, sequence_step: int) -> Dict:
        """Fallback email without AI"""
        templates = [
            {
                "subject": f"Question about {lead.get('name', 'your business')}",
                "body": f"Hi there,\n\nI came across {lead.get('name', 'your business')} and was impressed by your reputation in the {lead.get('industry', 'industry')}.\n\nI'm an entrepreneur looking to acquire a business in {lead.get('city', 'the area')}. Would you be open to a brief conversation about your future plans?\n\nNo pressure - just exploring if there might be a fit.\n\nBest regards,\nJD"
            },
            {
                "subject": f"Follow-up: {lead.get('name', 'your business')}",
                "body": f"Hi there,\n\nQuick follow-up on my note from a few days ago.\n\nI'm still very interested in learning more about {lead.get('name', 'your business')} and would appreciate 15 minutes of your time.\n\nIf now isn't right, I completely understand.\n\nBest,\nJD"
            },
            {
                "subject": f"One last try re: {lead.get('name', 'your business')}",
                "body": f"Hi there,\n\nI'll keep this brief - I know you're busy.\n\nI'm still interested in {lead.get('name', 'your business')} if you're considering a transition. If not, no worries.\n\nBest,\nJD"
            }
        ]
        
        return templates[min(sequence_step, len(templates) - 1)]
    
    def _fallback_classification(self, email_body: str) -> Dict:
        """Fallback classification without AI"""
        body_lower = email_body.lower()
        
        if any(w in body_lower for w in ['interested', 'would love to', 'call', 'talk']):
            return {"category": "INTERESTED", "confidence": "medium", "sentiment": "positive", "action": "Schedule call ASAP"}
        elif any(w in body_lower for w in ['not interested', 'not selling', 'not for sale']):
            return {"category": "NOT_INTERESTED", "confidence": "high", "sentiment": "negative", "action": "Archive and stop outreach"}
        elif any(w in body_lower for w in ['later', 'future', 'not now', 'next year']):
            return {"category": "INTERESTED_LATER", "confidence": "medium", "sentiment": "neutral", "action": "Set reminder for 6 months"}
        elif any(w in body_lower for w in ['question', 'what', 'how much', 'price']):
            return {"category": "CURIOUS", "confidence": "medium", "sentiment": "neutral", "action": "Answer questions and propose call"}
        else:
            return {"category": "OTHER", "confidence": "low", "sentiment": "neutral", "action": "Manual review needed"}
    
    def _extract_score(self, text: str) -> int:
        """Extract score number from text"""
        import re
        match = re.search(r'SCORE:\s*(\d+)', text)
        if match:
            return min(100, max(0, int(match.group(1))))
        return 50
    
    def _extract_section(self, text: str, section: str) -> str:
        """Extract section from text"""
        import re
        pattern = rf'{section}:?\s*\n?(.*?)(?=\n\w+:|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_list(self, text: str, section: str) -> List[str]:
        """Extract bulleted list from section"""
        section_text = self._extract_section(text, section)
        lines = [line.strip().lstrip('-').strip() for line in section_text.split('\n') if line.strip().startswith('-')]
        return lines if lines else ["Item not specified"]
    
    def _extract_line(self, text: str, label: str) -> str:
        """Extract single line value"""
        import re
        pattern = rf'{label}:?\s*(.+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""


# Test functions
if __name__ == "__main__":
    import asyncio
    
    async def test():
        ai = AcquisitorAI()
        
        # Test lead scoring
        lead = {
            "name": "TechFlow Solutions",
            "industry": "Technology",
            "revenue": 2750000,
            "employees": 18,
            "city": "Salt Lake City",
            "state": "UT",
            "description": "SaaS business with recurring revenue"
        }
        
        profile = {
            "background": "Product manager at tech company",
            "industries": ["Technology", "Services"],
            "budget_min": 500000,
            "budget_max": 2000000,
            "revenue_min": 1000000,
            "revenue_max": 5000000,
            "location_preference": ["UT", "CO"],
            "values": ["growth", "team retention"]
        }
        
        print("Testing lead scoring...")
        result = await ai.score_lead(lead, profile)
        print(f"Score: {result['score']}")
        print(f"Assessment: {result['assessment']}")
        
        print("\nTesting email generation...")
        email = await ai.generate_email(lead, profile)
        print(f"Subject: {email['subject']}")
        print(f"Body:\n{email['body']}")
        
        print("\nTesting reply classification...")
        reply = "Thanks for reaching out. I'm not looking to sell right now, but maybe in a year or two."
        classification = await ai.classify_reply("Re: Question", reply)
        print(f"Category: {classification['category']}")
        print(f"Sentiment: {classification['sentiment']}")
        print(f"Action: {classification['action']}")
    
    asyncio.run(test())
