"""Email/SMS sending logic for DEALFLOW outreach.

Handles Gmail API integration (OAuth2), Twilio SMS integration,
rate limiting, and send scheduling.
"""

import logging
import json
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import sqlite3
import time

import requests
from config import get_config, DealflowConfig, GmailConfig, TwilioConfig


logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """Communication channel types."""
    EMAIL = "email"
    SMS = "sms"


class SendStatus(Enum):
    """Status of an outreach attempt."""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    REPLIED = "replied"
    UNSUBSCRIBED = "unsubscribed"


@dataclass
class OutreachMessage:
    """Represents an outreach message to be sent."""
    id: Optional[int]
    lead_id: int
    channel: ChannelType
    sequence_step: int
    subject: str
    body: str
    to_email: Optional[str]
    to_phone: Optional[str]
    status: SendStatus
    scheduled_at: datetime
    sent_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "channel": self.channel.value,
            "sequence_step": self.sequence_step,
            "subject": self.subject,
            "body": self.body,
            "to_email": self.to_email,
            "to_phone": self.to_phone,
            "status": self.status.value,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GmailClient:
    """Gmail API client with OAuth2 authentication."""
    
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"
    
    def __init__(self, config: GmailConfig):
        self.config = config
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    def _refresh_access_token(self) -> str:
        """Refresh OAuth2 access token using refresh token."""
        logger.debug("Refreshing Gmail access token")
        
        response = requests.post(
            self.TOKEN_URL,
            data={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "refresh_token": self.config.refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=30,
        )
        response.raise_for_status()
        
        data = response.json()
        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
        
        logger.debug(f"Token refreshed, expires in {expires_in} seconds")
        return self._access_token
    
    def _get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        if self._access_token is None or (
            self._token_expires_at and datetime.now() >= self._token_expires_at
        ):
            return self._refresh_access_token()
        return self._access_token
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> Dict[str, Any]:
        """Send an email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            body: Email body content
            html: Whether body is HTML (default: plain text)
            
        Returns:
            Dict with 'success', 'message_id', and 'error' keys
        """
        try:
            token = self._get_access_token()
            
            # Create MIME message
            msg = MIMEText(body, "html" if html else "plain", "utf-8")
            msg["to"] = to
            msg["from"] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg["subject"] = subject
            
            # Encode for Gmail API
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
            
            # Send via Gmail API
            response = requests.post(
                f"{self.GMAIL_API_BASE}/users/me/messages/send",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={"raw": raw_message},
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Email sent to {to}, message_id: {result.get('id')}")
            
            return {
                "success": True,
                "message_id": result.get("id"),
                "error": None,
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to}: {e}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e),
            }


class TwilioClient:
    """Twilio SMS client."""
    
    TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"
    
    def __init__(self, config: TwilioConfig):
        self.config = config
    
    def send_sms(
        self,
        to: str,
        body: str,
    ) -> Dict[str, Any]:
        """Send an SMS via Twilio API.
        
        Args:
            to: Recipient phone number (E.164 format recommended)
            body: SMS body content (max 1600 chars)
            
        Returns:
            Dict with 'success', 'message_sid', and 'error' keys
        """
        try:
            # Clean phone number
            to = self._normalize_phone(to)
            
            url = (
                f"{self.TWILIO_API_BASE}/Accounts/"
                f"{self.config.account_sid}/Messages.json"
            )
            
            response = requests.post(
                url,
                auth=(self.config.account_sid, self.config.auth_token),
                data={
                    "From": self.config.from_number,
                    "To": to,
                    "Body": body[:1600],  # Twilio limit
                },
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"SMS sent to {to}, sid: {result.get('sid')}")
            
            return {
                "success": True,
                "message_sid": result.get("sid"),
                "error": None,
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send SMS to {to}: {e}")
            return {
                "success": False,
                "message_sid": None,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to}: {e}")
            return {
                "success": False,
                "message_sid": None,
                "error": str(e),
            }
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalize phone number to E.164 format."""
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
        if not cleaned.startswith("+") and len(cleaned) == 10:
            cleaned = "+1" + cleaned  # Assume US
        return cleaned


class Outbox:
    """Main outbox manager for email and SMS sending."""
    
    def __init__(self, config: Optional[DealflowConfig] = None):
        self.config = config or get_config()
        self.gmail = GmailClient(self.config.gmail)
        self.twilio = TwilioClient(self.config.twilio)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for tracking sends."""
        db_path = self.config.database.resolved_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS outreach_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    sequence_step INTEGER NOT NULL,
                    subject TEXT,
                    body TEXT NOT NULL,
                    to_email TEXT,
                    to_phone TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    scheduled_at TIMESTAMP NOT NULL,
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_status_scheduled 
                ON outreach_messages(status, scheduled_at);
                
                CREATE INDEX IF NOT EXISTS idx_lead_id 
                ON outreach_messages(lead_id);
                
                CREATE TABLE IF NOT EXISTS send_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    channel TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    response_data TEXT,
                    error_message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES outreach_messages(id)
                );
            """)
        logger.debug(f"Database initialized at {db_path}")
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        lead_id: int,
        sequence_step: int = 1,
        html: bool = False,
    ) -> Dict[str, Any]:
        """Send an email and log the result.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            lead_id: Associated lead ID
            sequence_step: Step in the sequence (1-4)
            html: Whether body is HTML
            
        Returns:
            Result dict with success status and message_id
        """
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would send email to {to}: {subject}")
            return {"success": True, "message_id": "dry-run", "error": None}
        
        result = self.gmail.send_email(to, subject, body, html)
        
        # Log the send attempt
        self._log_send(
            channel=ChannelType.EMAIL,
            recipient=to,
            success=result["success"],
            response_data=result.get("message_id"),
            error_message=result.get("error"),
        )
        
        return result
    
    def send_sms(
        self,
        to: str,
        body: str,
        lead_id: int,
        sequence_step: int = 1,
    ) -> Dict[str, Any]:
        """Send an SMS and log the result.
        
        Args:
            to: Recipient phone number
            body: SMS body
            lead_id: Associated lead ID
            sequence_step: Step in the sequence
            
        Returns:
            Result dict with success status and message_sid
        """
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would send SMS to {to}: {body[:50]}...")
            return {"success": True, "message_sid": "dry-run", "error": None}
        
        result = self.twilio.send_sms(to, body)
        
        # Log the send attempt
        self._log_send(
            channel=ChannelType.SMS,
            recipient=to,
            success=result["success"],
            response_data=result.get("message_sid"),
            error_message=result.get("error"),
        )
        
        return result
    
    def _log_send(
        self,
        channel: ChannelType,
        recipient: str,
        success: bool,
        response_data: Optional[str],
        error_message: Optional[str],
        message_id: Optional[int] = None,
    ) -> None:
        """Log a send attempt to the database."""
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """INSERT INTO send_logs 
                   (message_id, channel, recipient, success, response_data, error_message)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    message_id,
                    channel.value,
                    recipient,
                    success,
                    json.dumps(response_data) if response_data else None,
                    error_message,
                ),
            )
    
    def queue_message(
        self,
        lead_id: int,
        channel: ChannelType,
        subject: str,
        body: str,
        to_email: Optional[str],
        to_phone: Optional[str],
        sequence_step: int,
        scheduled_at: Optional[datetime] = None,
    ) -> int:
        """Queue a message for later sending.
        
        Args:
            lead_id: Associated lead ID
            channel: EMAIL or SMS
            subject: Email subject (ignored for SMS)
            body: Message body
            to_email: Recipient email (if channel is EMAIL)
            to_phone: Recipient phone (if channel is SMS)
            sequence_step: Step in sequence
            scheduled_at: When to send (default: now)
            
        Returns:
            The queued message ID
        """
        if scheduled_at is None:
            scheduled_at = datetime.now()
        
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO outreach_messages 
                   (lead_id, channel, sequence_step, subject, body, to_email, to_phone, 
                    status, scheduled_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    lead_id,
                    channel.value,
                    sequence_step,
                    subject,
                    body,
                    to_email,
                    to_phone,
                    SendStatus.QUEUED.value,
                    scheduled_at.isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            message_id = cursor.lastrowid
        
        logger.info(f"Queued {channel.value} message {message_id} for lead {lead_id}")
        return message_id
    
    def get_pending_outreach(
        self,
        limit: int = 25,
        before: Optional[datetime] = None,
    ) -> List[OutreachMessage]:
        """Get pending outreach messages ready to be sent.
        
        Args:
            limit: Maximum number to return
            before: Only get messages scheduled before this time
            
        Returns:
            List of OutreachMessage objects
        """
        if before is None:
            before = datetime.now()
        
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM outreach_messages 
                   WHERE status IN ('pending', 'queued')
                   AND scheduled_at <= ?
                   AND retry_count < ?
                   ORDER BY scheduled_at ASC
                   LIMIT ?""",
                (before.isoformat(), self.config.rate_limits.max_retries, limit),
            )
            rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            messages.append(OutreachMessage(
                id=row["id"],
                lead_id=row["lead_id"],
                channel=ChannelType(row["channel"]),
                sequence_step=row["sequence_step"],
                subject=row["subject"],
                body=row["body"],
                to_email=row["to_email"],
                to_phone=row["to_phone"],
                status=SendStatus(row["status"]),
                scheduled_at=datetime.fromisoformat(row["scheduled_at"]),
                sent_at=datetime.fromisoformat(row["sent_at"]) if row["sent_at"] else None,
                error_message=row["error_message"],
                retry_count=row["retry_count"],
                created_at=datetime.fromisoformat(row["created_at"]),
            ))
        
        return messages
    
    def mark_sent(self, message_id: int) -> None:
        """Mark a message as sent."""
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """UPDATE outreach_messages 
                   SET status = ?, sent_at = ?
                   WHERE id = ?""",
                (SendStatus.SENT.value, datetime.now().isoformat(), message_id),
            )
    
    def mark_failed(self, message_id: int, error: str) -> None:
        """Mark a message as failed and increment retry count."""
        db_path = self.config.database.resolved_path
        
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """UPDATE outreach_messages 
                   SET status = ?, error_message = ?, retry_count = retry_count + 1
                   WHERE id = ?""",
                (SendStatus.FAILED.value, error, message_id),
            )
    
    def get_daily_send_count(self, channel: Optional[ChannelType] = None) -> int:
        """Get number of messages sent today.
        
        Args:
            channel: Filter by channel type (default: all channels)
            
        Returns:
            Count of messages sent today
        """
        db_path = self.config.database.resolved_path
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        with sqlite3.connect(db_path) as conn:
            if channel:
                cursor = conn.execute(
                    """SELECT COUNT(*) FROM send_logs 
                       WHERE channel = ? AND sent_at >= ?""",
                    (channel.value, today.isoformat()),
                )
            else:
                cursor = conn.execute(
                    """SELECT COUNT(*) FROM send_logs 
                       WHERE sent_at >= ?""",
                    (today.isoformat(),),
                )
            return cursor.fetchone()[0]


def send_email(
    to: str,
    subject: str,
    body: str,
    lead_id: int = 0,
    html: bool = False,
) -> Dict[str, Any]:
    """Convenience function to send an email."""
    outbox = Outbox()
    return outbox.send_email(to, subject, body, lead_id, html=html)


def send_sms(
    to: str,
    body: str,
    lead_id: int = 0,
) -> Dict[str, Any]:
    """Convenience function to send an SMS."""
    outbox = Outbox()
    return outbox.send_sms(to, body, lead_id)


def get_pending_outreach(limit: int = 25) -> List[OutreachMessage]:
    """Convenience function to get pending outreach."""
    outbox = Outbox()
    return outbox.get_pending_outreach(limit=limit)
