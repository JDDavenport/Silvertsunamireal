"""Send time optimization and queue management for DEALFLOW.

Handles:
- Optimal send time determination per recipient
- Queue management and prioritization
- Daily send limits (max 25 leads/day)
- Scheduling with timezone awareness
"""

import logging
import sqlite3
import random
from datetime import datetime, timedelta, time as dt_time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from config import get_config, DealflowConfig, SendWindow
from sequences import LeadData, ChannelType


logger = logging.getLogger(__name__)


class Priority(Enum):
    """Message priority levels."""
    HIGH = "high"       # Hot leads, inbound inquiries
    MEDIUM = "medium"   # Standard outreach
    LOW = "low"         # Follow-ups, nurture


@dataclass
class ScheduledSend:
    """A scheduled outreach send."""
    message_id: int
    lead_id: int
    lead_data: LeadData
    channel: ChannelType
    scheduled_at: datetime
    priority: Priority
    sequence_step: int
    subject: str
    body: str


class SendTimeOptimizer:
    """Determines optimal send times for recipients."""
    
    # Best hours for B2B outreach (based on industry data)
    BEST_EMAIL_HOURS = [10, 14, 16]  # 10am, 2pm, 4pm
    BEST_SMS_HOURS = [11, 13, 15]    # 11am, 1pm, 3pm
    
    # Avoid these hours
    AVOID_HOURS = [0, 1, 2, 3, 4, 5, 6, 7, 20, 21, 22, 23]
    
    def __init__(self, config: Optional[SendWindow] = None):
        self.config = config or SendWindow()
    
    def get_optimal_send_time(
        self,
        lead: LeadData,
        channel: ChannelType,
        min_delay_hours: int = 1,
    ) -> datetime:
        """Calculate the optimal send time for a recipient.
        
        Args:
            lead: Lead data (used for timezone, industry, etc.)
            channel: EMAIL or SMS
            min_delay_hours: Minimum hours from now before sending
            
        Returns:
            Recommended datetime for sending
        """
        now = datetime.now()
        candidate = now + timedelta(hours=min_delay_hours)
        
        # Ensure we're within business hours
        candidate = self._adjust_to_business_hours(candidate)
        
        # Adjust for channel preferences
        if channel == ChannelType.EMAIL:
            candidate = self._optimize_for_email(candidate)
        else:
            candidate = self._optimize_for_sms(candidate)
        
        # Ensure we respect the send window
        candidate = self._respect_send_window(candidate)
        
        logger.debug(
            f"Optimal send time for lead {lead.lead_id}: "
            f"{candidate.isoformat()} ({channel.value})"
        )
        
        return candidate
    
    def _adjust_to_business_hours(self, dt: datetime) -> datetime:
        """Adjust datetime to fall within business hours."""
        # If weekend, move to Monday
        while dt.weekday() >= 5:  # 5=Saturday, 6=Sunday
            dt = dt + timedelta(days=1)
            dt = dt.replace(hour=9, minute=0, second=0)
        
        # If before 9am, move to 9am
        if dt.hour < 9:
            dt = dt.replace(hour=9, minute=random.randint(0, 30))
        
        # If after 5pm, move to next business day 9am
        if dt.hour >= 17:
            dt = dt + timedelta(days=1)
            dt = dt.replace(hour=9, minute=random.randint(0, 30))
            # Handle weekend
            while dt.weekday() >= 5:
                dt = dt + timedelta(days=1)
        
        return dt
    
    def _optimize_for_email(self, dt: datetime) -> datetime:
        """Optimize datetime for email sending."""
        # Pick one of the best hours
        best_hour = random.choice(self.BEST_EMAIL_HOURS)
        
        # If current hour is already good, maybe keep it with jitter
        if dt.hour in self.BEST_EMAIL_HOURS and random.random() > 0.3:
            return dt.replace(minute=random.randint(0, 59))
        
        return dt.replace(hour=best_hour, minute=random.randint(0, 59))
    
    def _optimize_for_sms(self, dt: datetime) -> datetime:
        """Optimize datetime for SMS sending."""
        best_hour = random.choice(self.BEST_SMS_HOURS)
        
        if dt.hour in self.BEST_SMS_HOURS and random.random() > 0.3:
            return dt.replace(minute=random.randint(0, 59))
        
        return dt.replace(hour=best_hour, minute=random.randint(0, 59))
    
    def _respect_send_window(self, dt: datetime) -> datetime:
        """Ensure datetime respects the configured send window."""
        # Check if day is allowed
        if dt.weekday() not in self.config.allowed_days:
            # Move to next allowed day
            while dt.weekday() not in self.config.allowed_days:
                dt = dt + timedelta(days=1)
            dt = dt.replace(
                hour=max(self.config.start_hour, 9),
                minute=random.randint(0, 30)
            )
        
        # Clamp to send window hours
        if dt.hour < self.config.start_hour:
            dt = dt.replace(
                hour=self.config.start_hour,
                minute=random.randint(0, 30)
            )
        elif dt.hour >= self.config.end_hour:
            # Move to next allowed day
            dt = dt + timedelta(days=1)
            while dt.weekday() not in self.config.allowed_days:
                dt = dt + timedelta(days=1)
            dt = dt.replace(
                hour=self.config.start_hour,
                minute=random.randint(0, 30)
            )
        
        return dt
    
    def batch_optimize(
        self,
        leads: List[LeadData],
        channel: ChannelType,
        spread_days: int = 1,
    ) -> Dict[int, datetime]:
        """Optimize send times for a batch of leads.
        
        Distributes sends across the spread_days to avoid spikes.
        
        Args:
            leads: List of leads to schedule
            channel: Channel type
            spread_days: Number of days to spread sends across
            
        Returns:
            Dict mapping lead_id to scheduled datetime
        """
        if not leads:
            return {}
        
        # Calculate slots
        slots_per_day = 8  # Reasonable slots per day
        total_slots = spread_days * slots_per_day
        
        # Distribute leads across slots
        schedule = {}
        base_time = datetime.now()
        
        for i, lead in enumerate(leads):
            # Calculate which slot this lead goes in
            slot = i % total_slots
            day_offset = slot // slots_per_day
            hour_offset = (slot % slots_per_day) + 9  # Start at 9am
            
            candidate = base_time + timedelta(days=day_offset)
            candidate = candidate.replace(hour=hour_offset, minute=random.randint(0, 59))
            candidate = self._adjust_to_business_hours(candidate)
            
            # Final optimization
            if channel == ChannelType.EMAIL:
                candidate = self._optimize_for_email(candidate)
            else:
                candidate = self._optimize_for_sms(candidate)
            
            schedule[lead.lead_id] = candidate
        
        return schedule


class QueueManager:
    """Manages the outreach queue with prioritization and limits."""
    
    def __init__(self, config: Optional[DealflowConfig] = None):
        self.config = config or get_config()
        self.optimizer = SendTimeOptimizer(self.config.send_window)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize queue tracking tables."""
        db_path = self.config.database.resolved_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS send_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    lead_id INTEGER NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    scheduled_at TIMESTAMP NOT NULL,
                    channel TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    locked_at TIMESTAMP,
                    locked_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES outreach_messages(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_queue_status_scheduled 
                ON send_queue(status, scheduled_at);
                
                CREATE INDEX IF NOT EXISTS idx_queue_priority 
                ON send_queue(priority, scheduled_at);
                
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    emails_sent INTEGER DEFAULT 0,
                    sms_sent INTEGER DEFAULT 0,
                    total_sent INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
    
    def get_daily_counts(self, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get send counts for a specific date.
        
        Args:
            date: Date to check (default: today)
            
        Returns:
            Dict with 'emails', 'sms', 'total' counts
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "SELECT emails_sent, sms_sent, total_sent FROM daily_stats WHERE date = ?",
                (date_str,)
            )
            row = cursor.fetchone()
            
            if row:
                return {"emails": row[0], "sms": row[1], "total": row[2]}
            else:
                return {"emails": 0, "sms": 0, "total": 0}
    
    def can_send_today(self, channel: ChannelType) -> bool:
        """Check if we can send more messages today.
        
        Args:
            channel: Which channel to check
            
        Returns:
            True if under limits, False otherwise
        """
        counts = self.get_daily_counts()
        limits = self.config.rate_limits
        
        # Check total limit
        if counts["total"] >= limits.max_total_per_day:
            logger.info(f"Daily total limit reached ({counts['total']}/{limits.max_total_per_day})")
            return False
        
        # Check channel-specific limits
        if channel == ChannelType.EMAIL:
            if counts["emails"] >= limits.max_emails_per_day:
                logger.info(f"Daily email limit reached ({counts['emails']}/{limits.max_emails_per_day})")
                return False
        elif channel == ChannelType.SMS:
            if counts["sms"] >= limits.max_sms_per_day:
                logger.info(f"Daily SMS limit reached ({counts['sms']}/{limits.max_sms_per_day})")
                return False
        
        return True
    
    def remaining_capacity(self) -> Dict[str, int]:
        """Get remaining send capacity for today.
        
        Returns:
            Dict with 'emails', 'sms', 'total' remaining
        """
        counts = self.get_daily_counts()
        limits = self.config.rate_limits
        
        return {
            "emails": max(0, limits.max_emails_per_day - counts["emails"]),
            "sms": max(0, limits.max_sms_per_day - counts["sms"]),
            "total": max(0, limits.max_total_per_day - counts["total"]),
        }
    
    def queue_message(
        self,
        message_id: int,
        lead_id: int,
        channel: ChannelType,
        priority: Priority = Priority.MEDIUM,
        scheduled_at: Optional[datetime] = None,
    ) -> int:
        """Add a message to the send queue.
        
        Args:
            message_id: ID of the outreach message
            lead_id: Associated lead ID
            channel: EMAIL or SMS
            priority: Message priority
            scheduled_at: When to send (default: optimized time)
            
        Returns:
            Queue entry ID
        """
        if scheduled_at is None:
            # Create minimal lead data for optimization
            lead_data = LeadData(
                lead_id=lead_id,
                business_name="",
                owner_name=None,
                industry=None,
                location=None,
                revenue=None,
                employees=None,
                email=None,
                phone=None,
                website=None,
                year_founded=None,
                custom_fields={},
            )
            scheduled_at = self.optimizer.get_optimal_send_time(lead_data, channel)
        
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO send_queue 
                   (message_id, lead_id, priority, scheduled_at, channel, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (message_id, lead_id, priority.value, scheduled_at.isoformat(), 
                 channel.value, "queued")
            )
            queue_id = cursor.lastrowid
        
        logger.info(f"Queued message {message_id} for lead {lead_id} at {scheduled_at}")
        return queue_id
    
    def get_ready_messages(
        self,
        limit: int = 25,
        respect_limits: bool = True,
    ) -> List[Dict[str, Any]]:
        """Get messages ready to be sent now.
        
        Args:
            limit: Maximum messages to return
            respect_limits: Whether to enforce daily limits
            
        Returns:
            List of message dicts ready for sending
        """
        now = datetime.now().isoformat()
        db_path = self.config.database.resolved_path
        
        # If respecting limits, adjust limit based on remaining capacity
        if respect_limits:
            capacity = self.remaining_capacity()
            limit = min(limit, capacity["total"])
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT sq.*, om.subject, om.body, om.to_email, om.to_phone
                   FROM send_queue sq
                   JOIN outreach_messages om ON sq.message_id = om.id
                   WHERE sq.status = 'queued'
                   AND sq.scheduled_at <= ?
                   AND (sq.locked_at IS NULL OR sq.locked_at < datetime('now', '-5 minutes'))
                   ORDER BY 
                     CASE sq.priority
                       WHEN 'high' THEN 1
                       WHEN 'medium' THEN 2
                       WHEN 'low' THEN 3
                     END,
                     sq.scheduled_at ASC
                   LIMIT ?""",
                (now, limit)
            )
            rows = cursor.fetchall()
        
        # Lock these messages
        ready = []
        for row in rows:
            message = dict(row)
            self._lock_message(message["id"], "scheduler")
            ready.append(message)
        
        return ready
    
    def _lock_message(self, queue_id: int, locked_by: str) -> None:
        """Lock a message to prevent duplicate sends."""
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """UPDATE send_queue 
                   SET locked_at = ?, locked_by = ?
                   WHERE id = ?""",
                (datetime.now().isoformat(), locked_by, queue_id)
            )
    
    def mark_sent(self, queue_id: int, channel: ChannelType) -> None:
        """Mark a queued message as sent and update stats."""
        db_path = self.config.database.resolved_path
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        with sqlite3.connect(db_path) as conn:
            # Update queue status
            conn.execute(
                "UPDATE send_queue SET status = 'sent' WHERE id = ?",
                (queue_id,)
            )
            
            # Update daily stats
            if channel == ChannelType.EMAIL:
                conn.execute(
                    """INSERT INTO daily_stats (date, emails_sent, total_sent)
                       VALUES (?, 1, 1)
                       ON CONFLICT(date) DO UPDATE SET
                       emails_sent = emails_sent + 1,
                       total_sent = total_sent + 1,
                       last_updated = CURRENT_TIMESTAMP""",
                    (date_str,)
                )
            else:
                conn.execute(
                    """INSERT INTO daily_stats (date, sms_sent, total_sent)
                       VALUES (?, 1, 1)
                       ON CONFLICT(date) DO UPDATE SET
                       sms_sent = sms_sent + 1,
                       total_sent = total_sent + 1,
                       last_updated = CURRENT_TIMESTAMP""",
                    (date_str,)
                )
    
    def mark_failed(self, queue_id: int, error: str) -> None:
        """Mark a queued message as failed."""
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """UPDATE send_queue 
                   SET status = 'failed', locked_at = NULL, locked_by = NULL
                   WHERE id = ?""",
                (queue_id,)
            )
    
    def requeue_failed(self, queue_id: int, delay_minutes: int = 30) -> bool:
        """Requeue a failed message for retry.
        
        Args:
            queue_id: Queue entry ID
            delay_minutes: Minutes to wait before retry
            
        Returns:
            True if requeued, False if max retries exceeded
        """
        db_path = self.config.database.resolved_path
        new_time = (datetime.now() + timedelta(minutes=delay_minutes)).isoformat()
        
        with sqlite3.connect(db_path) as conn:
            # Get retry count from outreach_messages
            cursor = conn.execute(
                """SELECT om.retry_count FROM outreach_messages om
                   JOIN send_queue sq ON om.id = sq.message_id
                   WHERE sq.id = ?""",
                (queue_id,)
            )
            row = cursor.fetchone()
            
            if row and row[0] >= self.config.rate_limits.max_retries:
                logger.warning(f"Max retries exceeded for queue entry {queue_id}")
                return False
            
            # Requeue
            conn.execute(
                """UPDATE send_queue 
                   SET status = 'queued', scheduled_at = ?, locked_at = NULL, locked_by = NULL
                   WHERE id = ?""",
                (new_time, queue_id)
            )
        
        logger.info(f"Requeued message {queue_id} for retry at {new_time}")
        return True


class Scheduler:
    """Main scheduler that coordinates timing, queue, and sending."""
    
    def __init__(self, config: Optional[DealflowConfig] = None):
        self.config = config or get_config()
        self.optimizer = SendTimeOptimizer(self.config.send_window)
        self.queue = QueueManager(self.config)
    
    def schedule_lead_sequence(
        self,
        lead: LeadData,
        sequence_steps: List[Dict[str, Any]],
        priority: Priority = Priority.MEDIUM,
    ) -> List[int]:
        """Schedule an entire sequence for a lead.
        
        Args:
            lead: Lead data
            sequence_steps: List of sequence steps from sequences.py
            priority: Message priority
            
        Returns:
            List of queued message IDs
        """
        from outbox import Outbox
        
        outbox = Outbox(self.config)
        queue_ids = []
        
        for step in sequence_steps:
            channel = ChannelType(step["channel"])
            
            # Queue in outbox
            message_id = outbox.queue_message(
                lead_id=lead.lead_id,
                channel=channel,
                subject=step.get("subject", ""),
                body=step["body"],
                to_email=lead.email,
                to_phone=lead.phone,
                sequence_step=step["step_number"],
                scheduled_at=datetime.fromisoformat(step["scheduled_date"]),
            )
            
            # Add to scheduler queue
            queue_id = self.queue.queue_message(
                message_id=message_id,
                lead_id=lead.lead_id,
                channel=channel,
                priority=priority,
                scheduled_at=datetime.fromisoformat(step["scheduled_date"]),
            )
            
            queue_ids.append(queue_id)
        
        logger.info(f"Scheduled {len(queue_ids)} messages for lead {lead.lead_id}")
        return queue_ids
    
    def process_queue(self, limit: int = 25) -> Dict[str, int]:
        """Process the send queue - send ready messages.
        
        Args:
            limit: Maximum messages to process
            
        Returns:
            Stats dict with 'sent', 'failed', 'skipped' counts
        """
        from outbox import Outbox
        
        outbox = Outbox(self.config)
        stats = {"sent": 0, "failed": 0, "skipped": 0}
        
        # Get ready messages
        ready = self.queue.get_ready_messages(limit=limit, respect_limits=True)
        
        for message in ready:
            channel = ChannelType(message["channel"])
            
            # Check if we can still send
            if not self.queue.can_send_today(channel):
                stats["skipped"] += 1
                continue
            
            # Send based on channel
            if channel == ChannelType.EMAIL and message["to_email"]:
                result = outbox.send_email(
                    to=message["to_email"],
                    subject=message["subject"],
                    body=message["body"],
                    lead_id=message["lead_id"],
                )
            elif channel == ChannelType.SMS and message["to_phone"]:
                result = outbox.send_sms(
                    to=message["to_phone"],
                    body=message["body"],
                    lead_id=message["lead_id"],
                )
            else:
                logger.warning(f"No valid recipient for message {message['id']}")
                self.queue.mark_failed(message["id"], "No valid recipient")
                stats["failed"] += 1
                continue
            
            # Update status
            if result.get("success"):
                self.queue.mark_sent(message["id"], channel)
                outbox.mark_sent(message["message_id"])
                stats["sent"] += 1
            else:
                self.queue.mark_failed(message["id"], result.get("error", "Unknown error"))
                outbox.mark_failed(message["message_id"], result.get("error", "Unknown error"))
                stats["failed"] += 1
        
        return stats
    
    def get_schedule_summary(self) -> Dict[str, Any]:
        """Get a summary of the current schedule.
        
        Returns:
            Dict with queue status, daily capacity, etc.
        """
        capacity = self.queue.remaining_capacity()
        counts = self.queue.get_daily_counts()
        
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            # Count queued messages
            cursor = conn.execute(
                "SELECT COUNT(*) FROM send_queue WHERE status = 'queued'"
            )
            queued = cursor.fetchone()[0]
            
            # Count by priority
            cursor = conn.execute(
                """SELECT priority, COUNT(*) FROM send_queue 
                   WHERE status = 'queued' GROUP BY priority"""
            )
            by_priority = dict(cursor.fetchall())
        
        return {
            "queued": queued,
            "by_priority": by_priority,
            "sent_today": counts,
            "remaining_capacity": capacity,
            "limits": {
                "max_emails": self.config.rate_limits.max_emails_per_day,
                "max_sms": self.config.rate_limits.max_sms_per_day,
                "max_total": self.config.rate_limits.max_total_per_day,
            },
            "send_window": {
                "start_hour": self.config.send_window.start_hour,
                "end_hour": self.config.send_window.end_hour,
                "timezone": self.config.send_window.timezone,
            },
        }


# Convenience functions
def schedule_lead(
    lead: LeadData,
    sequence_steps: List[Dict[str, Any]],
    priority: Priority = Priority.MEDIUM,
) -> List[int]:
    """Schedule a sequence for a lead."""
    scheduler = Scheduler()
    return scheduler.schedule_lead_sequence(lead, sequence_steps, priority)


def process_outbox(limit: int = 25) -> Dict[str, int]:
    """Process the outbox queue."""
    scheduler = Scheduler()
    return scheduler.process_queue(limit=limit)


def get_optimal_time(
    lead: LeadData,
    channel: ChannelType,
    min_delay_hours: int = 1,
) -> datetime:
    """Get optimal send time for a lead."""
    optimizer = SendTimeOptimizer()
    return optimizer.get_optimal_send_time(lead, channel, min_delay_hours)
