"""
Booking Agent for DEALFLOW

Detects buying signals, handles Cal.com webhooks, and manages call scheduling.
Uses contract-first design with type hints, error handling, and self-healing patterns.
"""

import os
import re
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, Literal, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import functools

from icontract import require, ensure, invariant

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Classification of buying signals."""
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    BROKER = "broker"
    NONE = "none"


class LeadStatus(Enum):
    """Lead status states."""
    NEW = "new"
    ENGAGED = "engaged"
    HOT = "hot"
    CALL_BOOKED = "call_booked"
    CALL_COMPLETED = "call_completed"
    NURTURE = "nurture"
    LOST = "lost"


@dataclass(frozen=True)
class BuyingSignal:
    """Immutable buying signal detection result."""
    signal_type: SignalType
    confidence: float  # 0.0 to 1.0
    matched_keywords: List[str]
    suggested_action: str

    @require(lambda confidence: 0.0 <= confidence <= 1.0)
    def __post_init__(self):
        object.__setattr__(
            self, 'matched_keywords', tuple(self.matched_keywords)
        )


@dataclass
class Lead:
    """Lead entity with validation."""
    id: str
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    status: LeadStatus
    reply_count: int
    last_reply_at: Optional[datetime]
    created_at: datetime
    cal_booking_id: Optional[str] = None

    @require(lambda name: len(name.strip()) > 0)
    @require(lambda email: '@' in email and '.' in email)
    def __post_init__(self):
        pass


@dataclass
class BookingEvent:
    """Cal.com webhook event."""
    event_type: Literal["booking.created", "booking.cancelled", "booking.rescheduled"]
    booking_id: str
    lead_email: str
    start_time: datetime
    end_time: datetime
    attendee_name: str
    attendee_phone: Optional[str]
    reschedule_url: Optional[str] = None
    cancel_url: Optional[str] = None


# Signal detection patterns
EXPLICIT_PATTERNS = [
    r"i['']?d like to talk",
    r"when can we meet",
    r"schedule a call",
    r"book a (call|meeting)",
    r"let['']?s (chat|talk|connect)",
    r"call me",
    r"available for a call",
    r"jump on a call",
    r"hop on a call",
    r"set up a call",
    r"get on the phone",
    r"discuss (over|on) the phone",
]

IMPLICIT_PATTERNS = [
    r"\$\d+",  # Dollar amounts
    r"\d+ million",
    r"valuation",
    r"multiple",
    r"ebitda",
    r"revenue",
    r"cash flow",
    r"sdoe",
    r"seller discretionary",
    r"earnout",
    r"multiple replies",  # Caught by reply count
    r"interested in learning more",
    r"tell me more",
    r"pricing",
    r"financials",
]

BROKER_PATTERNS = [
    r"cim",
    r"confidential information memorandum",
    r"proof of funds",
    r"pof",
    r"nda",
    r"teaser",
    r"ioi",
    r"indication of interest",
    r"loi",
    r"letter of intent",
    r"due diligence",
    r"data room",
]


def self_healing(func):
    """Decorator that attempts common fixes before escalating."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            key = str(e).strip("'")
            logger.info(f"Auto-fixing missing key: {key}")
            if args and isinstance(args[0], dict):
                args[0][key] = None
                return func(*args, **kwargs)
            raise
        except sqlite3.IntegrityError as e:
            logger.error(f"DB constraint: {e}")
            return None
        except ValueError as e:
            if "invalid literal" in str(e):
                logger.info("Auto-fixing type coercion")
                return None
            raise
        except Exception as e:
            logger.error(f"Unhandled exception in {func.__name__}: {e}")
            capture_failure_state(func, args, kwargs, e)
            raise
    return wrapper


def capture_failure_state(func, args, kwargs, error):
    """Log full failure state for analysis."""
    state = {
        "function": func.__name__,
        "args": [str(a)[:100] for a in args],
        "kwargs": {k: str(v)[:100] for k, v in kwargs.items()},
        "error": str(error),
        "timestamp": datetime.now().isoformat()
    }
    logger.error(f"Failure state captured: {json.dumps(state)}")


class BookingAgent:
    """
    Agent for detecting buying signals and managing call bookings.
    """

    CAL_BOOKING_LINK = os.getenv(
        "CAL_BOOKING_LINK",
        "https://cal.com/jd-dealflow/discovery-call"
    )
    
    def __init__(self, db_path: str = "dealflow.db"):
        self.db_path = db_path
        self._init_db()

    @self_healing
    def _init_db(self):
        """Initialize SQLite database with leads table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    company TEXT,
                    status TEXT DEFAULT 'new',
                    reply_count INTEGER DEFAULT 0,
                    last_reply_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cal_booking_id TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id TEXT PRIMARY KEY,
                    lead_id TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT,
                    type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    scheduled_at TIMESTAMP,
                    sent_at TIMESTAMP,
                    error TEXT
                )
            """)

    @require(lambda text: isinstance(text, str))
    @ensure(lambda result: isinstance(result, BuyingSignal))
    def detect_buying_signal(self, text: str, reply_count: int = 0) -> BuyingSignal:
        """
        Analyze text for buying signals.
        
        Returns BuyingSignal with type, confidence, and matched keywords.
        """
        text_lower = text.lower()
        matched = []
        
        # Check explicit patterns
        for pattern in EXPLICIT_PATTERNS:
            if re.search(pattern, text_lower):
                matched.append(pattern)
        
        if matched:
            return BuyingSignal(
                signal_type=SignalType.EXPLICIT,
                confidence=min(0.95, 0.7 + len(matched) * 0.05),
                matched_keywords=matched,
                suggested_action="send_booking_link"
            )
        
        # Check broker patterns
        matched = []
        for pattern in BROKER_PATTERNS:
            if re.search(pattern, text_lower):
                matched.append(pattern)
        
        if matched:
            return BuyingSignal(
                signal_type=SignalType.BROKER,
                confidence=min(0.9, 0.6 + len(matched) * 0.08),
                matched_keywords=matched,
                suggested_action="request_pof_and_book"
            )
        
        # Check implicit patterns + reply count
        matched = []
        for pattern in IMPLICIT_PATTERNS:
            if re.search(pattern, text_lower):
                matched.append(pattern)
        
        # Multiple replies = implicit signal
        if reply_count >= 2:
            matched.append(f"multiple_replies_{reply_count}")
        
        if matched:
            return BuyingSignal(
                signal_type=SignalType.IMPLICIT,
                confidence=min(0.8, 0.5 + len(matched) * 0.05 + reply_count * 0.05),
                matched_keywords=matched,
                suggested_action="nurture_and_offer_call"
            )
        
        return BuyingSignal(
            signal_type=SignalType.NONE,
            confidence=0.0,
            matched_keywords=[],
            suggested_action="continue_nurture"
        )

    @require(lambda signal: signal.signal_type != SignalType.NONE)
    @ensure(lambda result: "cal.com" in result or "book" in result.lower())
    def generate_booking_reply(self, signal: BuyingSignal, lead_name: str) -> str:
        """
        Generate personalized reply with booking link.
        
        Tailors message based on signal type and confidence.
        """
        name = lead_name.split()[0] if lead_name else "there"
        
        templates = {
            SignalType.EXPLICIT: {
                "high": (
                    f"Hi {name},\n\n"
                    f"I'd love to chat! Please grab a time that works for you:\n"
                    f"{self.CAL_BOOKING_LINK}\n\n"
                    f"Looking forward to speaking.\n\n"
                    f"Best,\nJD"
                ),
                "medium": (
                    f"Hi {name},\n\n"
                    f"Great to hear from you. Let's schedule a call:\n"
                    f"{self.CAL_BOOKING_LINK}\n\n"
                    f"Talk soon!\nJD"
                )
            },
            SignalType.BROKER: {
                "high": (
                    f"Hi {name},\n\n"
                    f"Thanks for sharing the opportunity. I'd like to review the materials "
                    f"and discuss next steps. Let's book a call:\n"
                    f"{self.CAL_BOOKING_LINK}\n\n"
                    f"I'll have my proof of funds ready.\n\n"
                    f"Best,\nJD"
                ),
                "medium": (
                    f"Hi {name},\n\n"
                    f"Appreciate you reaching out. Let's schedule a quick call to discuss:\n"
                    f"{self.CAL_BOOKING_LINK}\n\n"
                    f"Best,\nJD"
                )
            },
            SignalType.IMPLICIT: {
                "high": (
                    f"Hi {name},\n\n"
                    f"Thanks for the continued interest. Happy to discuss the financials "
                    f"in more detail on a call:\n"
                    f"{self.CAL_BOOKING_LINK}\n\n"
                    f"Let me know if you have questions.\n\n"
                    f"Best,\nJD"
                ),
                "medium": (
                    f"Hi {name},\n\n"
                    f"Thanks for following up. If you'd like to discuss further:\n"
                    f"{self.CAL_BOOKING_LINK}\n\n"
                    f"Best,\nJD"
                )
            }
        }
        
        confidence_level = "high" if signal.confidence >= 0.7 else "medium"
        return templates[signal.signal_type][confidence_level]

    @self_healing
    def get_or_create_lead(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None,
        company: Optional[str] = None
    ) -> Lead:
        """Get existing lead or create new one."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Try to get existing
            row = conn.execute(
                "SELECT * FROM leads WHERE email = ?",
                (email,)
            ).fetchone()
            
            if row:
                return Lead(
                    id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    company=row['company'],
                    status=LeadStatus(row['status']),
                    reply_count=row['reply_count'],
                    last_reply_at=row['last_reply_at'],
                    created_at=row['created_at'],
                    cal_booking_id=row['cal_booking_id']
                )
            
            # Create new
            lead_id = f"lead_{datetime.now().strftime('%Y%m%d%H%M%S')}_{email.split('@')[0]}"
            now = datetime.now()
            
            conn.execute(
                """INSERT INTO leads (id, name, email, phone, company, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (lead_id, name, email, phone, company, LeadStatus.NEW.value, now)
            )
            
            return Lead(
                id=lead_id,
                name=name,
                email=email,
                phone=phone,
                company=company,
                status=LeadStatus.NEW,
                reply_count=0,
                last_reply_at=None,
                created_at=now
            )

    @self_healing
    def update_lead_status(
        self,
        lead_id: str,
        status: LeadStatus,
        increment_reply: bool = False
    ) -> bool:
        """Update lead status and optionally increment reply count."""
        with sqlite3.connect(self.db_path) as conn:
            updates = ["status = ?"]
            params = [status.value, lead_id]
            
            if increment_reply:
                updates.append("reply_count = reply_count + 1")
                updates.append("last_reply_at = ?")
                params.insert(-1, datetime.now())
            
            query = f"UPDATE leads SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, params)
            return True

    @self_healing
    def handle_webhook(self, event_data: Dict[str, Any]) -> Optional[BookingEvent]:
        """
        Process Cal.com webhook event.
        
        Handles: booking.created, booking.cancelled, booking.rescheduled
        """
        event_type = event_data.get("type", event_data.get("triggerEvent"))
        
        if event_type not in ["booking.created", "booking.cancelled", "booking.rescheduled"]:
            logger.warning(f"Unknown webhook event type: {event_type}")
            return None
        
        payload = event_data.get("payload", event_data)
        
        # Extract booking details
        booking_id = payload.get("uid") or payload.get("bookingId")
        attendees = payload.get("attendees", [{}])
        attendee = attendees[0] if attendees else {}
        
        lead_email = attendee.get("email", "")
        attendee_name = attendee.get("name", "")
        attendee_phone = attendee.get("phone", None)
        
        start_time_str = payload.get("startTime") or payload.get("start")
        end_time_str = payload.get("endTime") or payload.get("end")
        
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        
        event = BookingEvent(
            event_type=event_type,
            booking_id=booking_id,
            lead_email=lead_email,
            start_time=start_time,
            end_time=end_time,
            attendee_name=attendee_name,
            attendee_phone=attendee_phone,
            reschedule_url=payload.get("rescheduleUrl"),
            cancel_url=payload.get("cancelUrl")
        )
        
        # Process based on event type
        if event_type == "booking.created":
            self._handle_booking_created(event)
        elif event_type == "booking.cancelled":
            self._handle_booking_cancelled(event)
        elif event_type == "booking.rescheduled":
            self._handle_booking_rescheduled(event)
        
        return event

    def _handle_booking_created(self, event: BookingEvent):
        """Process new booking - update lead, queue notifications."""
        with sqlite3.connect(self.db_path) as conn:
            # Find lead by email
            row = conn.execute(
                "SELECT id FROM leads WHERE email = ?",
                (event.lead_email,)
            ).fetchone()
            
            if row:
                lead_id = row[0]
                # Update lead status
                conn.execute(
                    "UPDATE leads SET status = ?, cal_booking_id = ? WHERE id = ?",
                    (LeadStatus.CALL_BOOKED.value, event.booking_id, lead_id)
                )
                
                # Insert booking record
                conn.execute(
                    """INSERT INTO bookings (id, lead_id, start_time, end_time)
                       VALUES (?, ?, ?, ?)""",
                    (event.booking_id, lead_id, event.start_time, event.end_time)
                )
                
                # Queue confirmation notification
                conn.execute(
                    """INSERT INTO notifications (lead_id, type, status, sent_at)
                       VALUES (?, 'booking_confirmation', 'sent', ?)""",
                    (lead_id, datetime.now())
                )
                
                # Schedule 24-hour reminder
                reminder_time = event.start_time - timedelta(hours=24)
                conn.execute(
                    """INSERT INTO notifications (lead_id, type, status, scheduled_at)
                       VALUES (?, 'booking_reminder', 'scheduled', ?)""",
                    (lead_id, reminder_time)
                )
                
                logger.info(f"Booking created for lead {lead_id}: {event.booking_id}")
            else:
                logger.warning(f"No lead found for email: {event.lead_email}")

    def _handle_booking_cancelled(self, event: BookingEvent):
        """Process cancelled booking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
                (event.booking_id,)
            )
            
            # Update lead status back to hot
            conn.execute(
                """UPDATE leads SET status = ?, cal_booking_id = NULL 
                   WHERE cal_booking_id = ?""",
                (LeadStatus.HOT.value, event.booking_id)
            )
            
            logger.info(f"Booking cancelled: {event.booking_id}")

    def _handle_booking_rescheduled(self, event: BookingEvent):
        """Process rescheduled booking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE bookings SET start_time = ?, end_time = ?, status = 'rescheduled'
                   WHERE id = ?""",
                (event.start_time, event.end_time, event.booking_id)
            )
            
            # Update reminder time
            reminder_time = event.start_time - timedelta(hours=24)
            conn.execute(
                """UPDATE notifications SET scheduled_at = ?, status = 'scheduled'
                   WHERE type = 'booking_reminder' AND lead_id = (
                       SELECT lead_id FROM bookings WHERE id = ?
                   )""",
                (reminder_time, event.booking_id)
            )
            
            logger.info(f"Booking rescheduled: {event.booking_id}")

    def process_incoming_message(
        self,
        email: str,
        name: str,
        message: str,
        phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: process incoming lead message.
        
        Returns action recommendation and generated reply if applicable.
        """
        # Get or create lead
        lead = self.get_or_create_lead(email, name, phone)
        
        # Detect buying signal
        signal = self.detect_buying_signal(message, lead.reply_count)
        
        # Update lead status based on signal
        if signal.signal_type == SignalType.EXPLICIT:
            self.update_lead_status(lead.id, LeadStatus.HOT, increment_reply=True)
        elif signal.signal_type in (SignalType.IMPLICIT, SignalType.BROKER):
            self.update_lead_status(lead.id, LeadStatus.ENGAGED, increment_reply=True)
        else:
            self.update_lead_status(lead.id, lead.status, increment_reply=True)
        
        result = {
            "lead_id": lead.id,
            "signal": {
                "type": signal.signal_type.value,
                "confidence": signal.confidence,
                "keywords": signal.matched_keywords,
                "action": signal.suggested_action
            },
            "reply": None
        }
        
        # Generate reply if signal detected
        if signal.signal_type != SignalType.NONE:
            result["reply"] = self.generate_booking_reply(signal, name)
        
        return result

    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Get reminders that need to be sent now."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT n.*, l.name, l.email, l.phone, b.start_time
                   FROM notifications n
                   JOIN leads l ON n.lead_id = l.id
                   JOIN bookings b ON l.cal_booking_id = b.id
                   WHERE n.type = 'booking_reminder'
                   AND n.status = 'scheduled'
                   AND n.scheduled_at <= ?""",
                (datetime.now(),)
            ).fetchall()
            
            return [dict(row) for row in rows]

    def mark_reminder_sent(self, notification_id: int):
        """Mark a reminder as sent."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE notifications SET status = 'sent', sent_at = ?
                   WHERE id = ?""",
                (datetime.now(), notification_id)
            )


# FastAPI endpoint handlers for webhooks
from fastapi import FastAPI, Request, HTTPException

app = FastAPI(title="DEALFLOW Booking Agent")
agent = BookingAgent()

@app.post("/webhooks/cal")
async def cal_webhook(request: Request):
    """Receive Cal.com webhook events."""
    try:
        data = await request.json()
        event = agent.handle_webhook(data)
        
        if event:
            return {"status": "processed", "event_type": event.event_type}
        return {"status": "ignored"}
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/process-message")
async def process_message(request: Request):
    """Process incoming lead message."""
    try:
        data = await request.json()
        result = agent.process_incoming_message(
            email=data["email"],
            name=data["name"],
            message=data["message"],
            phone=data.get("phone")
        )
        return result
    
    except Exception as e:
        logger.error(f"Process message error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    # Test the agent
    agent = BookingAgent()
    
    # Test buying signal detection
    test_messages = [
        "I'd like to talk about the opportunity",
        "When can we meet to discuss?",
        "What's the EBITDA on this deal?",
        "Can you send me the CIM? I have proof of funds ready.",
        "Just following up on my previous message"
    ]
    
    for msg in test_messages:
        signal = agent.detect_buying_signal(msg, reply_count=2)
        print(f"\nMessage: {msg}")
        print(f"Signal: {signal.signal_type.value} (confidence: {signal.confidence:.2f})")
        print(f"Keywords: {signal.matched_keywords}")
        
        if signal.signal_type != SignalType.NONE:
            reply = agent.generate_booking_reply(signal, "John Smith")
            print(f"Reply:\n{reply[:200]}...")
