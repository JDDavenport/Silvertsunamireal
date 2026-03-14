"""DEALFLOW Outreach Engine for ACQUISITOR.

Handles email/SMS outreach, sequence management, scheduling,
and delivery for qualified acquisition leads.

Modules:
- config: Configuration management (Gmail, Twilio, Cal.com)
- outbox: Email/SMS sending with Gmail API and Twilio
- sequences: Outreach sequence templates with personalization
- scheduler: Send time optimization and queue management

Usage:
    from dealflow import Outbox, generate_sequence, schedule_lead
    
    # Create outbox
    outbox = Outbox()
    
    # Generate sequence for a lead
    from sequences import LeadData, SequenceType
    lead = LeadData.from_qualify_record(lead_record)
    steps = generate_sequence(lead, SequenceType.DIRECT_OWNER)
    
    # Schedule the sequence
    queue_ids = schedule_lead(lead, steps)
    
    # Process the queue
    from scheduler import process_outbox
    stats = process_outbox(limit=25)
"""

from config import (
    DealflowConfig,
    GmailConfig,
    TwilioConfig,
    CalComConfig,
    get_config,
)

from outbox import (
    Outbox,
    GmailClient,
    TwilioClient,
    OutreachMessage,
    ChannelType as OutboxChannel,
    SendStatus,
    send_email,
    send_sms,
    get_pending_outreach,
)

from sequences import (
    SequenceTemplate,
    SequenceType,
    LeadData,
    ChannelType,
    DirectOwnerSequence,
    BrokerSequence,
    LandingPageSequence,
    SequenceManager,
    generate_sequence,
)

from scheduler import (
    Scheduler,
    QueueManager,
    SendTimeOptimizer,
    Priority,
    schedule_lead,
    process_outbox,
    get_optimal_time,
)

__version__ = "1.0.0"
__all__ = [
    # Config
    "DealflowConfig",
    "GmailConfig",
    "TwilioConfig",
    "CalComConfig",
    "get_config",
    # Outbox
    "Outbox",
    "GmailClient",
    "TwilioClient",
    "OutreachMessage",
    "OutboxChannel",
    "SendStatus",
    "send_email",
    "send_sms",
    "get_pending_outreach",
    # Sequences
    "SequenceTemplate",
    "SequenceType",
    "LeadData",
    "ChannelType",
    "DirectOwnerSequence",
    "BrokerSequence",
    "LandingPageSequence",
    "SequenceManager",
    "generate_sequence",
    # Scheduler
    "Scheduler",
    "QueueManager",
    "SendTimeOptimizer",
    "Priority",
    "schedule_lead",
    "process_outbox",
    "get_optimal_time",
]
