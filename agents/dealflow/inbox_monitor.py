#!/usr/bin/env python3
"""
DEALFLOW Inbox Monitor
Gmail webhook handler for email classification and agent routing.
"""

import json
import logging
import re
import sqlite3
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from functools import lru_cache

import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailCategory(Enum):
    """Email classification categories."""
    INTERESTED = "interested"
    QUESTION = "question"
    NOT_NOW = "not_now"
    NOT_INTERESTED = "not_interested"
    UNSUBSCRIBE = "unsubscribe"
    BOUNCE = "bounce"
    AUTO_REPLY = "auto_reply"
    BROKER_REPLY = "broker_reply"


@dataclass
class EmailMessage:
    """Represents a parsed email message."""
    message_id: str
    thread_id: str
    sender: str
    subject: str
    body: str
    timestamp: datetime
    in_reply_to: Optional[str] = None
    references: List[str] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class ThreadContext:
    """Full conversation context for a thread."""
    thread_id: str
    messages: List[EmailMessage]
    lead_data: Optional[Dict[str, Any]] = None
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation."""
        if not self.messages:
            return "No messages in thread."
        
        lines = []
        for msg in sorted(self.messages, key=lambda m: m.timestamp):
            direction = "Lead" if "lead" in msg.sender.lower() or "seller" in msg.sender.lower() else "Us"
            lines.append(f"[{direction}] {msg.subject}\n{msg.body[:500]}")
        return "\n\n".join(lines)


class DeduplicationStore:
    """Thread-safe message deduplication using SQLite."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the deduplication database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    category TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_thread_id ON processed_messages(thread_id)
            """)
            conn.commit()
    
    def is_processed(self, message_id: str) -> bool:
        """Check if a message has already been processed."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM processed_messages WHERE message_id = ?",
                    (message_id,)
                )
                return cursor.fetchone() is not None
    
    def mark_processed(self, message_id: str, thread_id: str, category: str) -> None:
        """Mark a message as processed."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR IGNORE INTO processed_messages 
                       (message_id, thread_id, category) VALUES (?, ?, ?)""",
                    (message_id, thread_id, category)
                )
                conn.commit()
    
    def get_thread_message_ids(self, thread_id: str) -> List[str]:
        """Get all processed message IDs for a thread."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT message_id FROM processed_messages WHERE thread_id = ?",
                    (thread_id,)
                )
                return [row[0] for row in cursor.fetchall()]


class ClaudeClassifier:
    """Email classification using Claude API."""
    
    CLASSIFICATION_PROMPT = """You are an email classifier for a real estate acquisition system (DEALFLOW).

Classify this email into exactly one category. Respond with ONLY the category name.

Categories:
- INTERESTED: Lead expresses interest in selling or discussing their business/property
- QUESTION: Lead asks questions about the process, company, or offer
- NOT_NOW: Lead is interested but timing is wrong (e.g., "maybe next year")
- NOT_INTERESTED: Lead explicitly declines or is not interested
- UNSUBSCRIBE: Lead requests to be removed from mailing list
- BOUNCE: Email delivery failure, address not found
- AUTO_REPLY: Out-of-office or automated response
- BROKER_REPLY: Response from an intermediary/broker on behalf of owner

Email:
From: {sender}
Subject: {subject}
Body: {body}

Category (respond with only the category name):
"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self._lock = threading.RLock()
        self._cache: Dict[str, EmailCategory] = {}
    
    def classify(self, email: EmailMessage, context: Optional[ThreadContext] = None) -> EmailCategory:
        """
        Classify an email using Claude Haiku.
        
        Args:
            email: The email to classify
            context: Optional thread context for better classification
            
        Returns:
            EmailCategory classification
        """
        # Check cache first
        cache_key = f"{email.message_id}:{hash(email.body)}"
        with self._lock:
            if cache_key in self._cache:
                logger.info(f"Using cached classification for {email.message_id}")
                return self._cache[cache_key]
        
        # Build prompt with context if available
        prompt = self.CLASSIFICATION_PROMPT.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:2000]  # Limit body length
        )
        
        if context and context.messages:
            prompt += f"\n\nPrevious conversation context:\n{context.get_conversation_summary()[:1500]}"
        
        try:
            with self._lock:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=50,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result = response.content[0].text.strip().upper()
                
                # Parse result
                category = self._parse_category(result)
                
                # Cache result
                self._cache[cache_key] = category
                
                logger.info(f"Classified {email.message_id} as {category.value}")
                return category
                
        except Exception as e:
            logger.error(f"Classification failed for {email.message_id}: {e}")
            # Default to QUESTION for safety
            return EmailCategory.QUESTION
    
    def _parse_category(self, result: str) -> EmailCategory:
        """Parse classification result into category enum."""
        result = result.replace("-", "_").replace(" ", "_").strip()
        
        category_map = {
            "INTERESTED": EmailCategory.INTERESTED,
            "QUESTION": EmailCategory.QUESTION,
            "NOT_NOW": EmailCategory.NOT_NOW,
            "NOT_INTERESTED": EmailCategory.NOT_INTERESTED,
            "UNSUBSCRIBE": EmailCategory.UNSUBSCRIBE,
            "BOUNCE": EmailCategory.BOUNCE,
            "AUTO_REPLY": EmailCategory.AUTO_REPLY,
            "BROKER_REPLY": EmailCategory.BROKER_REPLY,
        }
        
        return category_map.get(result, EmailCategory.QUESTION)


class AgentRouter:
    """Routes classified emails to appropriate agents."""
    
    def __init__(self):
        self._handlers: Dict[EmailCategory, List[Callable]] = {
            cat: [] for cat in EmailCategory
        }
        self._lock = threading.RLock()
    
    def register_handler(self, category: EmailCategory, handler: Callable) -> None:
        """Register a handler for a specific category."""
        with self._lock:
            self._handlers[category].append(handler)
    
    def route(self, email: EmailMessage, category: EmailCategory, context: ThreadContext) -> List[Any]:
        """
        Route email to appropriate handlers.
        
        Returns:
            List of handler results
        """
        with self._lock:
            handlers = self._handlers.get(category, [])
        
        results = []
        for handler in handlers:
            try:
                result = handler(email, category, context)
                results.append(result)
                logger.info(f"Handler {handler.__name__} processed {email.message_id}")
            except Exception as e:
                logger.error(f"Handler {handler.__name__} failed for {email.message_id}: {e}")
        
        return results


class GmailWebhookHandler:
    """Handles Gmail webhook push notifications."""
    
    def __init__(
        self,
        classifier: ClaudeClassifier,
        router: AgentRouter,
        dedup_store: DeduplicationStore,
        lead_data_store: Optional[Any] = None
    ):
        self.classifier = classifier
        self.router = router
        self.dedup = dedup_store
        self.lead_data_store = lead_data_store
        self._lock = threading.RLock()
        self._thread_cache: Dict[str, ThreadContext] = {}
    
    def handle_push_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Gmail push notification.
        
        Expected notification format:
        {
            "message": {
                "data": "base64_encoded_json"
            }
        }
        
        Returns:
            Processing result dict
        """
        try:
            import base64
            
            # Decode notification
            data = notification.get("message", {}).get("data", "")
            decoded = base64.b64decode(data).decode("utf-8")
            payload = json.loads(decoded)
            
            history_id = payload.get("historyId")
            email_address = payload.get("emailAddress")
            
            logger.info(f"Received push notification for {email_address}, history_id={history_id}")
            
            # Process new messages (implementation depends on Gmail API client)
            # This would typically fetch new messages since the history_id
            return {"status": "acknowledged", "history_id": history_id}
            
        except Exception as e:
            logger.error(f"Failed to process push notification: {e}")
            return {"status": "error", "error": str(e)}
    
    def process_email(self, email: EmailMessage) -> Dict[str, Any]:
        """
        Process a single email through the full pipeline.
        
        Args:
            email: The email to process
            
        Returns:
            Processing result with classification and routing info
        """
        # Deduplication check
        if self.dedup.is_processed(email.message_id):
            logger.info(f"Skipping duplicate message {email.message_id}")
            return {
                "message_id": email.message_id,
                "status": "skipped",
                "reason": "duplicate"
            }
        
        # Load thread context
        context = self._load_thread_context(email.thread_id)
        
        # Add current message to context
        context.messages.append(email)
        
        # Classify
        category = self.classifier.classify(email, context)
        
        # Mark as processed
        self.dedup.mark_processed(email.message_id, email.thread_id, category.value)
        
        # Route to appropriate agents
        routing_results = self.router.route(email, category, context)
        
        result = {
            "message_id": email.message_id,
            "thread_id": email.thread_id,
            "status": "processed",
            "category": category.value,
            "routing_results": routing_results
        }
        
        logger.info(f"Processed {email.message_id} -> {category.value}")
        return result
    
    def _load_thread_context(self, thread_id: str) -> ThreadContext:
        """Load full thread context from storage."""
        with self._lock:
            if thread_id in self._thread_cache:
                return self._thread_cache[thread_id]
        
        # Build thread context from database
        # This would fetch all messages for the thread from your email storage
        context = ThreadContext(
            thread_id=thread_id,
            messages=[],
            lead_data=self._load_lead_data(thread_id)
        )
        
        with self._lock:
            self._thread_cache[thread_id] = context
        
        return context
    
    def _load_lead_data(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Load lead data associated with this thread."""
        if self.lead_data_store:
            return self.lead_data_store.get_lead_by_thread(thread_id)
        return None
    
    def invalidate_thread_cache(self, thread_id: str) -> None:
        """Invalidate cached thread context."""
        with self._lock:
            self._thread_cache.pop(thread_id, None)


# Convenience factory function
def create_inbox_monitor(
    anthropic_api_key: Optional[str] = None,
    db_path: str = ":memory:"
) -> tuple[GmailWebhookHandler, AgentRouter, ClaudeClassifier]:
    """
    Create and configure the inbox monitor components.
    
    Args:
        anthropic_api_key: API key for Claude
        db_path: Path to deduplication database
        
    Returns:
        Tuple of (handler, router, classifier)
    """
    classifier = ClaudeClassifier(api_key=anthropic_api_key)
    router = AgentRouter()
    dedup = DeduplicationStore(db_path=db_path)
    handler = GmailWebhookHandler(classifier, router, dedup)
    
    return handler, router, classifier


if __name__ == "__main__":
    # Example usage
    handler, router, classifier = create_inbox_monitor()
    
    # Register example handlers
    def handle_interested(email: EmailMessage, cat: EmailCategory, ctx: ThreadContext):
        print(f"INTERESTED lead from {email.sender}: {email.subject}")
        return {"action": "notify_sales_team"}
    
    def handle_unsubscribe(email: EmailMessage, cat: EmailCategory, ctx: ThreadContext):
        print(f"UNSUBSCRIBE request from {email.sender}")
        return {"action": "remove_from_list"}
    
    router.register_handler(EmailCategory.INTERESTED, handle_interested)
    router.register_handler(EmailCategory.UNSUBSCRIBE, handle_unsubscribe)
    
    # Example test email
    test_email = EmailMessage(
        message_id="test123",
        thread_id="thread456",
        sender="seller@example.com",
        subject="Re: Acquisition Inquiry",
        body="Yes, I'm interested in discussing a potential sale. When can we talk?",
        timestamp=datetime.now()
    )
    
    result = handler.process_email(test_email)
    print(f"Result: {result}")
