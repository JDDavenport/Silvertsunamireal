"""Basic tests for DEALFLOW components."""

import os
import sys
import sqlite3
import tempfile
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dealflow.config import (
    DealflowConfig,
    GmailConfig,
    TwilioConfig,
    CalComConfig,
    RateLimits,
    SendWindow,
)
from dealflow.sequences import (
    LeadData,
    SequenceType,
    DirectOwnerSequence,
    BrokerSequence,
    LandingPageSequence,
    generate_sequence,
)
from dealflow.scheduler import (
    SendTimeOptimizer,
    QueueManager,
    Priority,
    Scheduler,
)


def test_config():
    """Test configuration module."""
    print("Testing config...")
    
    # Test Gmail config
    gmail = GmailConfig(
        client_id="test_client_id",
        client_secret="test_secret",
        refresh_token="test_token",
        sender_email="test@example.com",
    )
    assert gmail.is_configured()
    
    # Test unconfigured
    gmail_empty = GmailConfig.from_env()
    assert not gmail_empty.is_configured()
    
    # Test rate limits
    limits = RateLimits()
    assert limits.max_emails_per_day == 25
    assert limits.max_retries == 3
    
    print("✓ Config tests passed")


def test_sequences():
    """Test sequence templates."""
    print("Testing sequences...")
    
    # Create test lead
    lead = LeadData(
        lead_id=1,
        business_name="Test Corp",
        owner_name="John Smith",
        industry="Manufacturing",
        location="Denver, CO",
        revenue="$5M",
        employees="50",
        email="john@testcorp.com",
        phone="+1234567890",
        website="https://testcorp.com",
        year_founded=2005,
        custom_fields={},
    )
    
    # Test direct owner sequence
    seq = DirectOwnerSequence()
    assert len(seq.steps) == 4
    
    step = seq.get_step(1, lead)
    assert step is not None
    assert "Test Corp" in step["subject"]
    assert "John" in step["body"] or "there" in step["body"]
    
    # Test all steps
    all_steps = seq.get_all_steps(lead)
    assert len(all_steps) == 4
    assert all_steps[0]["step_number"] == 1
    
    # Test broker sequence
    broker_seq = BrokerSequence()
    assert len(broker_seq.steps) == 3
    
    # Test landing page sequence
    lp_seq = LandingPageSequence()
    assert len(lp_seq.steps) == 3
    
    # Test convenience function
    steps = generate_sequence(lead, SequenceType.DIRECT_OWNER)
    assert len(steps) == 4
    
    print("✓ Sequence tests passed")


def test_scheduler():
    """Test scheduler components."""
    print("Testing scheduler...")
    
    lead = LeadData(
        lead_id=1,
        business_name="Test Corp",
        owner_name="John Smith",
        industry="Manufacturing",
        location="Denver, CO",
        revenue="$5M",
        employees="50",
        email="john@testcorp.com",
        phone="+1234567890",
        website="https://testcorp.com",
        year_founded=2005,
        custom_fields={},
    )
    
    # Test optimizer
    optimizer = SendTimeOptimizer()
    from dealflow.sequences import ChannelType
    
    send_time = optimizer.get_optimal_send_time(lead, ChannelType.EMAIL)
    assert send_time > datetime.now()
    assert 9 <= send_time.hour < 17
    
    # Test business hours adjustment
    weekend = datetime(2026, 3, 14, 10, 0)  # Saturday
    adjusted = optimizer._adjust_to_business_hours(weekend)
    assert adjusted.weekday() < 5  # Should be weekday
    
    print("✓ Scheduler tests passed")


def test_queue_manager():
    """Test queue manager with temp database."""
    print("Testing queue manager...")
    
    # Create temp database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        config = DealflowConfig(
            gmail=GmailConfig("", "", "", ""),
            twilio=TwilioConfig("", "", ""),
            calcom=CalComConfig("", "", ""),
            send_window=SendWindow(),
            rate_limits=RateLimits(),
            database=type('obj', (object,), {'db_path': tmp_path, 'resolved_path': __import__('pathlib').Path(tmp_path)})(),
        )
        
        queue = QueueManager(config)
        
        # Test daily counts
        counts = queue.get_daily_counts()
        assert counts["emails"] == 0
        assert counts["total"] == 0
        
        # Test capacity
        capacity = queue.remaining_capacity()
        assert capacity["emails"] == 25
        assert capacity["total"] == 25
        
        print("✓ Queue manager tests passed")
    finally:
        os.unlink(tmp_path)


def test_integration():
    """Integration test - full flow."""
    print("Testing integration flow...")
    
    # Create test lead
    lead = LeadData(
        lead_id=1,
        business_name="Acme Manufacturing",
        owner_name="Jane Doe",
        industry="Manufacturing",
        location="Austin, TX",
        revenue="$3M",
        employees="25",
        email="jane@acme.com",
        phone="+15551234567",
        website="https://acmemfg.com",
        year_founded=2010,
        custom_fields={"source": "scraping"},
    )
    
    # Generate sequence
    from dealflow import generate_sequence, SequenceType
    steps = generate_sequence(lead, SequenceType.DIRECT_OWNER)
    
    assert len(steps) == 4
    assert steps[0]["channel"] == "email"
    assert "Acme Manufacturing" in steps[0]["subject"]
    assert "Jane" in steps[0]["body"] or "there" in steps[0]["body"]
    
    print("✓ Integration tests passed")


if __name__ == "__main__":
    print("="*50)
    print("DEALFLOW Outreach Engine Tests")
    print("="*50)
    
    test_config()
    test_sequences()
    test_scheduler()
    test_queue_manager()
    test_integration()
    
    print("="*50)
    print("All tests passed! ✓")
    print("="*50)
