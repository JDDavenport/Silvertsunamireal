#!/usr/bin/env python3
"""
DEALFLOW Integration Example

Shows how to wire together inbox_monitor and response_agent.
"""

import os
from datetime import datetime
from pathlib import Path

# Import both components
from inbox_monitor import (
    EmailCategory,
    EmailMessage,
    create_inbox_monitor,
)
from response_agent import (
    ResponseAgent,
    LeadData,
    ConversationMessage,
    ResponseAgentHandler,
    create_response_agent,
)


def setup_dealflow_agents(
    anthropic_api_key: str = None,
    canspam_config: dict = None,
    db_path: str = ":memory:"
):
    """
    Set up the complete DEALFLOW inbox and response system.
    
    Args:
        anthropic_api_key: Claude API key
        canspam_config: CAN-SPAM compliance config
        db_path: Path to deduplication database
        
    Returns:
        Tuple of (inbox_handler, response_agent)
    """
    api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
    
    # Create inbox monitor
    inbox_handler, router, classifier = create_inbox_monitor(
        anthropic_api_key=api_key,
        db_path=db_path
    )
    
    # Create response agent
    response_agent = create_response_agent(
        anthropic_api_key=api_key,
        soul_path=Path("SOUL.md"),
        canspam_config=canspam_config
    )
    
    # Create handler bridge
    response_handler = ResponseAgentHandler(response_agent)
    
    # Register response handlers for each category
    router.register_handler(
        EmailCategory.INTERESTED,
        response_handler.handle_interested
    )
    router.register_handler(
        EmailCategory.QUESTION,
        response_handler.handle_question
    )
    router.register_handler(
        EmailCategory.NOT_INTERESTED,
        response_handler.handle_not_interested
    )
    
    # Register simple handlers for other categories
    def handle_unsubscribe(email, category, context):
        print(f"🚫 UNSUBSCRIBE from {email.sender}")
        return {"action": "unsubscribe", "email": email.sender}
    
    def handle_bounce(email, category, context):
        print(f"📧 BOUNCE from {email.sender}")
        return {"action": "mark_bounced", "email": email.sender}
    
    def handle_auto_reply(email, category, context):
        print(f"🤖 AUTO_REPLY from {email.sender}")
        return {"action": "ignore", "reason": "auto_reply"}
    
    def handle_broker_reply(email, category, context):
        print(f"🏢 BROKER_REPLY from {email.sender}")
        # Could escalate to human team
        return {"action": "escalate", "reason": "broker_involved"}
    
    def handle_not_now(email, category, context):
        print(f"⏰ NOT_NOW from {email.sender}")
        # Schedule follow-up
        return {"action": "schedule_followup", "delay_days": 90}
    
    router.register_handler(EmailCategory.UNSUBSCRIBE, handle_unsubscribe)
    router.register_handler(EmailCategory.BOUNCE, handle_bounce)
    router.register_handler(EmailCategory.AUTO_REPLY, handle_auto_reply)
    router.register_handler(EmailCategory.BROKER_REPLY, handle_broker_reply)
    router.register_handler(EmailCategory.NOT_NOW, handle_not_now)
    
    return inbox_handler, response_agent


def example_email_flow():
    """Demonstrate the complete email processing flow."""
    
    canspam_config = {
        "company_name": "Acquisitions LLC",
        "physical_address": "123 Business Ave, Suite 100, Denver, CO 80202",
        "unsubscribe_link": "https://example.com/unsubscribe"
    }
    
    # Set up agents
    inbox, responder = setup_dealflow_agents(
        canspam_config=canspam_config,
        db_path="dealflow.db"
    )
    
    # Example emails to process
    test_emails = [
        EmailMessage(
            message_id="msg001",
            thread_id="thread001",
            sender="john.smith@manufacturing.com",
            subject="Re: Acquisition Interest",
            body="Yes, I'd be interested in discussing this further. What would the process look like?",
            timestamp=datetime.now()
        ),
        EmailMessage(
            message_id="msg002",
            thread_id="thread002",
            sender="jane.doe@techcorp.com",
            subject="Re: Business Sale",
            body="Thanks but we're not looking to sell at this time. Maybe next year.",
            timestamp=datetime.now()
        ),
        EmailMessage(
            message_id="msg003",
            thread_id="thread003",
            sender="broker@businessbrokers.com",
            subject="Re: Your Inquiry",
            body="I represent the owner and would like to discuss terms.",
            timestamp=datetime.now()
        ),
        EmailMessage(
            message_id="msg001",  # Duplicate - should be skipped
            thread_id="thread001",
            sender="john.smith@manufacturing.com",
            subject="Re: Acquisition Interest",
            body="Yes, I'd be interested...",
            timestamp=datetime.now()
        ),
    ]
    
    print("=" * 60)
    print("DEALFLOW Inbox Monitor Demo")
    print("=" * 60)
    
    for email in test_emails:
        print(f"\n📨 Processing: {email.subject} from {email.sender}")
        print("-" * 40)
        
        result = inbox.process_email(email)
        
        print(f"Status: {result['status']}")
        if result['status'] == 'processed':
            print(f"Category: {result['category']}")
            if result.get('routing_results'):
                for rr in result['routing_results']:
                    if isinstance(rr, dict):
                        print(f"Action: {rr.get('action')}")
                        if rr.get('response'):
                            print(f"\nGenerated Response:\n{rr['response'][:200]}...")
        elif result.get('reason'):
            print(f"Reason: {result['reason']}")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)


def example_direct_response():
    """Demonstrate direct response generation."""
    
    agent = create_response_agent()
    
    lead = LeadData(
        name="Robert Johnson",
        company_name="Johnson Construction",
        industry="Construction",
        location="Austin, TX",
        previous_interactions=2
    )
    
    history = [
        ConversationMessage(
            role="system",
            content="Hi Robert, I noticed Johnson Construction has been growing steadily. We're interested in acquiring construction businesses.",
            timestamp=datetime.now()
        ),
        ConversationMessage(
            role="lead",
            content="Thanks for reaching out. What's your typical acquisition process?",
            timestamp=datetime.now()
        ),
        ConversationMessage(
            role="system",
            content="We start with a friendly conversation about your goals and timeline. No pressure, just exploring fit.",
            timestamp=datetime.now()
        ),
    ]
    
    print("\n" + "=" * 60)
    print("Direct Response Generation Demo")
    print("=" * 60)
    
    # Example 1: Standard response
    print("\n📝 Standard Response:")
    result = agent.generate_response(
        current_message="That sounds reasonable. I'm potentially interested but need to know - are you an AI or a real person?",
        conversation_history=history,
        lead_data=lead
    )
    print(result['response'])
    print(f"\nEscalate: {result['escalate']}")
    print(f"Acknowledged AI: {result['acknowledged_ai']}")
    
    # Example 2: SMS response
    print("\n📱 SMS Response:")
    result = agent.generate_sms_response(
        current_message="Can we talk tomorrow?",
        conversation_history=history[-2:],  # Last 2 messages
        lead_data=lead
    )
    print(result['response'])
    
    # Example 3: Complex negotiation
    print("\n💼 Complex Negotiation Response:")
    from response_agent import ResponseType
    result = agent.generate_response(
        current_message="We're open to selling for $5M with a 2-year earnout. Can you do that?",
        conversation_history=history,
        lead_data=lead,
        response_type=ResponseType.COMPLEX_NEGOTIATION
    )
    print(result['response'])
    print(f"Escalate: {result['escalate']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not set. Classification/response generation will fail.")
        print("Set it with: export ANTHROPIC_API_KEY=your_key_here")
        print()
    
    # Run examples
    try:
        example_email_flow()
    except Exception as e:
        print(f"Email flow demo error (expected without API key): {e}")
    
    try:
        example_direct_response()
    except Exception as e:
        print(f"Direct response demo error (expected without API key): {e}")
