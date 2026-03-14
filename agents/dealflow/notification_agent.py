"""
Notification Agent for DEALFLOW

Sends alerts to JD via Telegram and email with structured formatting.
Handles different priority levels and notification types.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Literal
from dataclasses import dataclass, asdict
from enum import Enum
import functools

import telegram
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from icontract import require, ensure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Notification priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationType(Enum):
    """Types of notifications that can be sent."""
    CALL_BOOKED = "call_booked"
    HOT_LEAD_REPLY = "hot_lead_reply"
    LEAD_ESCALATION = "lead_escalation"
    DAILY_SUMMARY = "daily_summary"
    SYSTEM_ERROR = "system_error"
    BOOKING_REMINDER = "booking_reminder"
    BOOKING_CANCELLED = "booking_cancelled"


@dataclass
class Notification:
    """Notification entity with all required fields."""
    type: NotificationType
    priority: Priority
    title: str
    message: str
    lead_context: Optional[Dict[str, Any]] = None
    conversation_summary: Optional[str] = None
    action_required: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class LeadContext:
    """Contextual information about a lead."""
    lead_id: str
    name: str
    email: str
    company: Optional[str]
    status: str
    reply_count: int
    last_activity: Optional[datetime]
    deal_size: Optional[str] = None
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "name": self.name,
            "email": self.email,
            "company": self.company,
            "status": self.status,
            "reply_count": self.reply_count,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "deal_size": self.deal_size,
            "source": self.source
        }


def self_healing(func):
    """Decorator for auto-fixing common notification errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except telegram.error.NetworkError as e:
            logger.warning(f"Telegram network error, will retry: {e}")
            # Return None to indicate failure but allow continuation
            return None
        except telegram.error.BadRequest as e:
            logger.error(f"Telegram bad request: {e}")
            # Try with truncated message
            if "message is too long" in str(e) and args:
                truncated = str(args[0])[:3000] + "..."
                return func(truncated, *args[1:], **kwargs)
            return None
        except telegram.error.Unauthorized as e:
            logger.error(f"Telegram unauthorized - check bot token: {e}")
            raise
        except Exception as e:
            logger.error(f"Notification error in {func.__name__}: {e}")
            return None
    return wrapper


class NotificationAgent:
    """
    Agent for sending notifications to JD via Telegram and email.
    Handles different priorities and formats messages appropriately.
    """
    
    # Priority emojis for visual distinction
    PRIORITY_EMOJI = {
        Priority.CRITICAL: "🚨",
        Priority.HIGH: "⚡",
        Priority.MEDIUM: "📊",
        Priority.LOW: "ℹ️"
    }
    
    # Type emojis
    TYPE_EMOJI = {
        NotificationType.CALL_BOOKED: "📅",
        NotificationType.HOT_LEAD_REPLY: "🔥",
        NotificationType.LEAD_ESCALATION: "⬆️",
        NotificationType.DAILY_SUMMARY: "📈",
        NotificationType.SYSTEM_ERROR: "💥",
        NotificationType.BOOKING_REMINDER: "⏰",
        NotificationType.BOOKING_CANCELLED: "❌"
    }
    
    def __init__(
        self,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_pass: Optional[str] = None,
        email_to: Optional[str] = None
    ):
        self.telegram_token = telegram_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_pass = smtp_pass or os.getenv("SMTP_PASS")
        self.email_to = email_to or os.getenv("NOTIFICATION_EMAIL")
        
        self._bot: Optional[Bot] = None
        self._email_available = all([self.smtp_host, self.smtp_user, self.smtp_pass])
        
        if self.telegram_token:
            try:
                self._bot = Bot(token=self.telegram_token)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")

    @property
    def telegram_available(self) -> bool:
        """Check if Telegram is configured and available."""
        return self._bot is not None and self.telegram_chat_id is not None

    def _format_telegram_message(self, notification: Notification) -> str:
        """
        Format notification for Telegram with structured layout.
        
        Uses Markdown formatting for readability.
        """
        priority_emoji = self.PRIORITY_EMOJI.get(notification.priority, "📌")
        type_emoji = self.TYPE_EMOJI.get(notification.type, "📋")
        
        lines = [
            f"{priority_emoji} {type_emoji} *{notification.title}*",
            ""
        ]
        
        # Lead context section
        if notification.lead_context:
            ctx = notification.lead_context
            lines.append("👤 *Lead Info*")
            lines.append(f"• Name: {ctx.get('name', 'N/A')}")
            lines.append(f"• Email: {ctx.get('email', 'N/A')}")
            if ctx.get('company'):
                lines.append(f"• Company: {ctx['company']}")
            if ctx.get('status'):
                lines.append(f"• Status: {ctx['status']}")
            if ctx.get('deal_size'):
                lines.append(f"• Deal Size: {ctx['deal_size']}")
            lines.append("")
        
        # Message section
        lines.append(f"📝 *Details*")
        lines.append(notification.message)
        lines.append("")
        
        # Conversation summary
        if notification.conversation_summary:
            lines.append(f"💬 *Conversation*")
            lines.append(f"_{notification.conversation_summary}_")
            lines.append("")
        
        # Action required
        if notification.action_required:
            lines.append(f"⚠️ *Action Required*")
            lines.append(f"`{notification.action_required}`")
            lines.append("")
        
        # Timestamp
        time_str = notification.timestamp.strftime("%Y-%m-%d %H:%M %Z")
        lines.append(f"🕐 {time_str}")
        
        return "\n".join(lines)

    def _format_email_message(self, notification: Notification) -> tuple:
        """
        Format notification for email (HTML + plain text).
        
        Returns (subject, html_body, text_body)
        """
        priority_emoji = self.PRIORITY_EMOJI.get(notification.priority, "📌")
        type_emoji = self.TYPE_EMOJI.get(notification.type, "📋")
        
        subject = f"[{notification.priority.value.upper()}] {notification.title}"
        
        # Plain text version
        text_lines = [
            f"{priority_emoji} {type_emoji} {notification.title}",
            "=" * 50,
            ""
        ]
        
        if notification.lead_context:
            ctx = notification.lead_context
            text_lines.append("LEAD INFO:")
            for key, value in ctx.items():
                text_lines.append(f"  {key}: {value}")
            text_lines.append("")
        
        text_lines.extend([
            "DETAILS:",
            notification.message,
            ""
        ])
        
        if notification.conversation_summary:
            text_lines.extend([
                "CONVERSATION SUMMARY:",
                notification.conversation_summary,
                ""
            ])
        
        if notification.action_required:
            text_lines.extend([
                "ACTION REQUIRED:",
                notification.action_required,
                ""
            ])
        
        text_lines.append(f"Time: {notification.timestamp.isoformat()}")
        
        # HTML version
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><style>",
            "body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }",
            ".header { background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }",
            ".section { margin: 15px 0; }",
            ".label { font-weight: bold; color: #666; }",
            ".critical { color: #d32f2f; }",
            ".high { color: #f57c00; }",
            ".medium { color: #1976d2; }",
            ".low { color: #388e3c; }",
            ".action-box { background: #fff3e0; padding: 10px; border-left: 4px solid #ff9800; margin: 10px 0; }",
            "</style></head>",
            "<body>",
            f"<div class='header {notification.priority.value}'>",
            f"<h2>{priority_emoji} {type_emoji} {notification.title}</h2>",
            f"<span class='{notification.priority.value}'>{notification.priority.value.upper()}</span>",
            "</div>"
        ]
        
        if notification.lead_context:
            html_parts.append("<div class='section'>")
            html_parts.append("<p class='label'>Lead Information</p>")
            html_parts.append("<ul>")
            for key, value in notification.lead_context.items():
                html_parts.append(f"<li><strong>{key}:</strong> {value}</li>")
            html_parts.append("</ul></div>")
        
        html_parts.extend([
            "<div class='section'>",
            "<p class='label'>Details</p>",
            f"<p>{notification.message.replace(chr(10), '<br>')}</p>",
            "</div>"
        ])
        
        if notification.conversation_summary:
            html_parts.extend([
                "<div class='section'>",
                "<p class='label'>Conversation Summary</p>",
                f"<p><em>{notification.conversation_summary}</em></p>",
                "</div>"
            ])
        
        if notification.action_required:
            html_parts.extend([
                "<div class='action-box'>",
                "<p class='label'>Action Required</p>",
                f"<p>{notification.action_required}</p>",
                "</div>"
            ])
        
        html_parts.extend([
            "<div class='section' style='color: #999; font-size: 12px; margin-top: 30px;'>",
            f"<p>Sent at {notification.timestamp.isoformat()}</p>",
            "</div>",
            "</body></html>"
        ])
        
        return subject, "\n".join(html_parts), "\n".join(text_lines)

    @self_healing
    @require(lambda notification: notification.title and notification.message)
    async def send_telegram(
        self,
        notification: Notification,
        pin_critical: bool = True
    ) -> Optional[int]:
        """
        Send notification via Telegram.
        
        Pins critical messages. Returns message_id on success.
        """
        if not self.telegram_available:
            logger.warning("Telegram not configured, skipping")
            return None
        
        message_text = self._format_telegram_message(notification)
        
        # Build inline keyboard for actions
        keyboard = []
        if notification.type == NotificationType.CALL_BOOKED:
            keyboard.append([
                InlineKeyboardButton("📅 View Calendar", url="https://cal.com"),
                InlineKeyboardButton("👤 View Lead", callback_data=f"lead:{notification.lead_context.get('lead_id', 'unknown')}")
            ])
        elif notification.type == NotificationType.LEAD_ESCALATION:
            keyboard.append([
                InlineKeyboardButton("✏️ Reply", callback_data="reply"),
                InlineKeyboardButton("🗑️ Dismiss", callback_data="dismiss")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        try:
            sent = await self._bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            # Pin critical messages
            if notification.priority == Priority.CRITICAL and pin_critical:
                await self._bot.pin_chat_message(
                    chat_id=self.telegram_chat_id,
                    message_id=sent.message_id
                )
                logger.info(f"Pinned critical message: {sent.message_id}")
            
            logger.info(f"Telegram message sent: {sent.message_id}")
            return sent.message_id
            
        except telegram.error.BadRequest as e:
            if "message is too long" in str(e):
                # Truncate and retry
                notification.message = notification.message[:500] + "..."
                return await self.send_telegram(notification, pin_critical)
            raise

    @self_healing
    async def send_email(self, notification: Notification) -> bool:
        """
        Send notification via email (backup channel).
        
        Returns True on success.
        """
        if not self._email_available:
            logger.debug("Email not configured, skipping")
            return False
        
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            subject, html_body, text_body = self._format_email_message(notification)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = self.email_to
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def notify(
        self,
        notification: Notification,
        channels: List[Literal["telegram", "email", "all"]] = ["all"],
        pin_critical: bool = True
    ) -> Dict[str, Any]:
        """
        Send notification through specified channels.
        
        Returns status of each channel attempt.
        """
        results = {"telegram": None, "email": None}
        
        use_telegram = "telegram" in channels or "all" in channels
        use_email = "email" in channels or "all" in channels
        
        # Telegram for all priorities except low
        if use_telegram and notification.priority != Priority.LOW:
            results["telegram"] = await self.send_telegram(notification, pin_critical)
        
        # Email as backup for critical and high priority
        if use_email and notification.priority in (Priority.CRITICAL, Priority.HIGH):
            results["email"] = await self.send_email(notification)
        
        return results

    # Convenience methods for specific notification types

    async def notify_call_booked(
        self,
        lead_context: LeadContext,
        call_time: datetime,
        calendar_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notify when a call is booked (CRITICAL priority)."""
        notification = Notification(
            type=NotificationType.CALL_BOOKED,
            priority=Priority.CRITICAL,
            title="Call Booked! 🎉",
            message=f"New discovery call scheduled for {call_time.strftime('%A, %B %d at %I:%M %p')}",
            lead_context=lead_context.to_dict(),
            action_required="Review lead details before the call",
            metadata={"call_time": call_time.isoformat(), "calendar_link": calendar_link}
        )
        return await self.notify(notification, pin_critical=True)

    async def notify_hot_lead_reply(
        self,
        lead_context: LeadContext,
        reply_preview: str
    ) -> Dict[str, Any]:
        """Notify when a hot lead replies (HIGH priority)."""
        notification = Notification(
            type=NotificationType.HOT_LEAD_REPLY,
            priority=Priority.HIGH,
            title="Hot Lead Replied",
            message=f"Received reply from engaged lead",
            lead_context=lead_context.to_dict(),
            conversation_summary=reply_preview[:200] if len(reply_preview) > 200 else reply_preview,
            action_required="Review and respond within 2 hours"
        )
        return await self.notify(notification)

    async def notify_lead_escalation(
        self,
        lead_context: LeadContext,
        reason: str,
        conversation_history: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notify when a lead needs manual intervention (HIGH priority)."""
        notification = Notification(
            type=NotificationType.LEAD_ESCALATION,
            priority=Priority.HIGH,
            title="Lead Needs Attention",
            message=f"Escalation reason: {reason}",
            lead_context=lead_context.to_dict(),
            conversation_summary=conversation_history,
            action_required="Manual review and response needed"
        )
        return await self.notify(notification)

    async def notify_system_error(
        self,
        error_message: str,
        component: str,
        traceback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Notify on system errors (CRITICAL priority)."""
        notification = Notification(
            type=NotificationType.SYSTEM_ERROR,
            priority=Priority.CRITICAL,
            title=f"System Error: {component}",
            message=error_message,
            action_required="Check system logs and restart if necessary",
            metadata={"component": component, "traceback": traceback[:500] if traceback else None}
        )
        return await self.notify(notification)

    async def notify_booking_cancelled(
        self,
        lead_context: LeadContext,
        cancelled_at: datetime
    ) -> Dict[str, Any]:
        """Notify when a booking is cancelled."""
        notification = Notification(
            type=NotificationType.BOOKING_CANCELLED,
            priority=Priority.HIGH,
            title="Call Cancelled",
            message=f"Discovery call cancelled at {cancelled_at.strftime('%Y-%m-%d %H:%M')}",
            lead_context=lead_context.to_dict(),
            action_required="Follow up to reschedule if lead is still qualified"
        )
        return await self.notify(notification)

    async def send_daily_summary(
        self,
        stats: Dict[str, Any],
        hot_leads: List[Dict[str, Any]],
        upcoming_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Send daily pipeline summary (MEDIUM priority)."""
        lines = [
            f"📊 *Daily Pipeline Summary*",
            f"📅 {datetime.now().strftime('%A, %B %d, %Y')}",
            ""
        ]
        
        # Stats
        lines.append("*Activity (Last 24h)*")
        lines.append(f"• New leads: {stats.get('new_leads', 0)}")
        lines.append(f"• Replies received: {stats.get('replies', 0)}")
        lines.append(f"• Calls booked: {stats.get('calls_booked', 0)}")
        lines.append(f"• Calls completed: {stats.get('calls_completed', 0)}")
        lines.append("")
        
        # Hot leads
        if hot_leads:
            lines.append(f"🔥 *Hot Leads ({len(hot_leads)})*")
            for lead in hot_leads[:5]:  # Top 5
                lines.append(f"• {lead.get('name')} - {lead.get('company', 'No company')}")
            if len(hot_leads) > 5:
                lines.append(f"  ... and {len(hot_leads) - 5} more")
            lines.append("")
        
        # Upcoming calls
        if upcoming_calls:
            lines.append(f"📅 *Upcoming Calls ({len(upcoming_calls)})*")
            for call in upcoming_calls[:5]:
                time_str = call.get('time', 'TBD')
                name = call.get('lead_name', 'Unknown')
                lines.append(f"• {time_str} - {name}")
            lines.append("")
        
        lines.append("Have a great day! 💪")
        
        notification = Notification(
            type=NotificationType.DAILY_SUMMARY,
            priority=Priority.MEDIUM,
            title="Daily Pipeline Summary",
            message="\n".join(lines),
            metadata=stats
        )
        
        return await self.notify(notification, pin_critical=False)

    async def send_booking_reminder(
        self,
        lead_context: LeadContext,
        call_time: datetime
    ) -> bool:
        """Send 24-hour booking reminder (only via Telegram, no email)."""
        hours_until = (call_time - datetime.now()).total_seconds() / 3600
        
        notification = Notification(
            type=NotificationType.BOOKING_REMINDER,
            priority=Priority.MEDIUM,
            title="Call Reminder",
            message=f"Discovery call with {lead_context.name} in {hours_until:.0f} hours",
            lead_context=lead_context.to_dict(),
            action_required="Review lead profile and prepare talking points"
        )
        
        result = await self.notify(notification, channels=["telegram"])
        return result.get("telegram") is not None


# FastAPI endpoint for testing
from fastapi import FastAPI, HTTPException

app = FastAPI(title="DEALFLOW Notification Agent")
agent = NotificationAgent()

@app.post("/notify/call-booked")
async def api_call_booked(lead: Dict[str, Any], call_time: str):
    """API endpoint for call booked notification."""
    try:
        ctx = LeadContext(**lead)
        dt = datetime.fromisoformat(call_time)
        result = await agent.notify_call_booked(ctx, dt)
        return {"status": "sent", "channels": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/notify/hot-lead")
async def api_hot_lead(lead: Dict[str, Any], reply: str):
    """API endpoint for hot lead reply notification."""
    try:
        ctx = LeadContext(**lead)
        result = await agent.notify_hot_lead_reply(ctx, reply)
        return {"status": "sent", "channels": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/notify/daily-summary")
async def api_daily_summary(
    stats: Dict[str, Any],
    hot_leads: List[Dict[str, Any]] = [],
    upcoming_calls: List[Dict[str, Any]] = []
):
    """API endpoint for daily summary."""
    try:
        result = await agent.send_daily_summary(stats, hot_leads, upcoming_calls)
        return {"status": "sent", "channels": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    # Test the notification agent
    import asyncio
    
    async def test():
        agent = NotificationAgent()
        
        # Create test lead context
        test_lead = LeadContext(
            lead_id="lead_test_001",
            name="John Smith",
            email="john@example.com",
            company="Acme Corp",
            status="hot",
            reply_count=3,
            last_activity=datetime.now(),
            deal_size="$2.5M - $3M"
        )
        
        # Test call booked notification
        print("Testing call booked notification...")
        result = await agent.notify_call_booked(
            test_lead,
            datetime.now() + timedelta(days=2)
        )
        print(f"Result: {result}")
        
        # Test hot lead reply
        print("\nTesting hot lead reply notification...")
        result = await agent.notify_hot_lead_reply(
            test_lead,
            "I'm very interested in the business. Can we schedule a call to discuss the financials?"
        )
        print(f"Result: {result}")
        
        # Test daily summary
        print("\nTesting daily summary...")
        result = await agent.send_daily_summary(
            stats={"new_leads": 5, "replies": 12, "calls_booked": 2, "calls_completed": 1},
            hot_leads=[
                {"name": "Jane Doe", "company": "TechCo"},
                {"name": "Bob Wilson", "company": "Manufacturing Inc"}
            ],
            upcoming_calls=[
                {"time": "2:00 PM", "lead_name": "Alice Johnson"},
                {"time": "4:30 PM", "lead_name": "Charlie Brown"}
            ]
        )
        print(f"Result: {result}")
    
    asyncio.run(test())
