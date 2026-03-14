"""DEALFLOW configuration module.

Handles all configuration for the outreach engine including
Gmail API credentials, Twilio settings, Cal.com integration,
and send window/rate limiting parameters.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass(frozen=True)
class GmailConfig:
    """Gmail API OAuth2 configuration."""
    client_id: str
    client_secret: str
    refresh_token: str
    sender_email: str
    sender_name: str = "ACQUISITOR"
    
    @classmethod
    def from_env(cls) -> "GmailConfig":
        """Load Gmail config from environment variables."""
        return cls(
            client_id=os.getenv("GMAIL_CLIENT_ID", ""),
            client_secret=os.getenv("GMAIL_CLIENT_SECRET", ""),
            refresh_token=os.getenv("GMAIL_REFRESH_TOKEN", ""),
            sender_email=os.getenv("GMAIL_SENDER_EMAIL", ""),
            sender_name=os.getenv("GMAIL_SENDER_NAME", "ACQUISITOR"),
        )
    
    def is_configured(self) -> bool:
        """Check if all required Gmail credentials are present."""
        return all([
            self.client_id,
            self.client_secret,
            self.refresh_token,
            self.sender_email,
        ])


@dataclass(frozen=True)
class TwilioConfig:
    """Twilio SMS configuration."""
    account_sid: str
    auth_token: str
    from_number: str
    
    @classmethod
    def from_env(cls) -> "TwilioConfig":
        """Load Twilio config from environment variables."""
        return cls(
            account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
            auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
            from_number=os.getenv("TWILIO_FROM_NUMBER", ""),
        )
    
    def is_configured(self) -> bool:
        """Check if all required Twilio credentials are present."""
        return all([
            self.account_sid,
            self.auth_token,
            self.from_number,
        ])


@dataclass(frozen=True)
class CalComConfig:
    """Cal.com scheduling integration configuration."""
    api_key: str
    event_type_id: str
    username: str
    base_url: str = "https://api.cal.com/v1"
    
    @classmethod
    def from_env(cls) -> "CalComConfig":
        """Load Cal.com config from environment variables."""
        return cls(
            api_key=os.getenv("CALCOM_API_KEY", ""),
            event_type_id=os.getenv("CALCOM_EVENT_TYPE_ID", ""),
            username=os.getenv("CALCOM_USERNAME", ""),
            base_url=os.getenv("CALCOM_BASE_URL", "https://api.cal.com/v1"),
        )
    
    def is_configured(self) -> bool:
        """Check if all required Cal.com credentials are present."""
        return all([
            self.api_key,
            self.event_type_id,
            self.username,
        ])


@dataclass(frozen=True)
class SendWindow:
    """Defines when outreach can be sent (timezone-aware)."""
    start_hour: int = 9   # 9 AM
    end_hour: int = 17    # 5 PM
    timezone: str = "America/New_York"
    
    # Days of week: 0=Monday, 6=Sunday
    allowed_days: tuple = (0, 1, 2, 3, 4)  # Mon-Fri only


@dataclass(frozen=True)
class RateLimits:
    """Rate limiting configuration for outreach."""
    max_emails_per_day: int = 25
    max_sms_per_day: int = 15
    max_total_per_day: int = 25
    
    # Minimum time between sends (seconds)
    min_delay_between_sends: int = 60
    
    # Maximum retries for failed sends
    max_retries: int = 3
    retry_backoff_seconds: int = 300  # 5 minutes


@dataclass(frozen=True)
class DatabaseConfig:
    """SQLite database configuration."""
    db_path: str = "~/projects/silver-tsunami-real/agents/dealflow/dealflow.db"
    
    @property
    def resolved_path(self) -> Path:
        """Get resolved database path."""
        return Path(self.db_path).expanduser()


@dataclass(frozen=True)
class DealflowConfig:
    """Main DEALFLOW configuration container."""
    gmail: GmailConfig
    twilio: TwilioConfig
    calcom: CalComConfig
    send_window: SendWindow
    rate_limits: RateLimits
    database: DatabaseConfig
    
    # Debug/test mode
    dry_run: bool = False  # If True, don't actually send
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "DealflowConfig":
        """Load complete configuration from environment."""
        return cls(
            gmail=GmailConfig.from_env(),
            twilio=TwilioConfig.from_env(),
            calcom=CalComConfig.from_env(),
            send_window=SendWindow(),
            rate_limits=RateLimits(),
            database=DatabaseConfig(),
            dry_run=os.getenv("DEALFLOW_DRY_RUN", "false").lower() == "true",
            log_level=os.getenv("DEALFLOW_LOG_LEVEL", "INFO"),
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.gmail.is_configured():
            errors.append("Gmail configuration incomplete")
        
        if not self.twilio.is_configured():
            errors.append("Twilio configuration incomplete")
        
        if not self.calcom.is_configured():
            errors.append("Cal.com configuration incomplete")
        
        if self.rate_limits.max_emails_per_day > 100:
            errors.append("Daily email limit too high (>100)")
        
        return errors


# Global config instance (lazy-loaded)
_config: Optional[DealflowConfig] = None


def get_config() -> DealflowConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = DealflowConfig.from_env()
    return _config


def set_config(config: DealflowConfig) -> None:
    """Set global config instance (useful for testing)."""
    global _config
    _config = config
