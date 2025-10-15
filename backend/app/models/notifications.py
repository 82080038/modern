"""
Notification Models untuk In-App Notifications
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class NotificationType(enum.Enum):
    """Notification types"""
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    PRICE_ALERT = "price_alert"
    SENTIMENT_ALERT = "sentiment_alert"
    RISK_ALERT = "risk_alert"
    SYSTEM_ALERT = "system_alert"
    MARKET_ALERT = "market_alert"

class NotificationPriority(enum.Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(enum.Enum):
    """Notification status"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class Notification(Base):
    """In-app notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Notification details
    type = Column(Enum(NotificationType), nullable=False, index=True)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD)
    
    # Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    icon = Column(String(50), nullable=True)  # Icon class or emoji
    color = Column(String(20), nullable=True)  # Bootstrap color class
    
    # Related data
    symbol = Column(String(20), nullable=True, index=True)
    order_id = Column(String(50), nullable=True, index=True)
    trade_id = Column(String(50), nullable=True, index=True)
    
    # Additional data
    notification_metadata = Column(JSON, nullable=True)  # Additional data for the notification
    action_url = Column(String(200), nullable=True)  # URL for action button
    action_text = Column(String(50), nullable=True)  # Text for action button
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    
    # Expiry
    expires_at = Column(DateTime, nullable=True)
    is_expired = Column(Boolean, default=False)

class AlertRule(Base):
    """Alert rules for automated notifications"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Rule details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Alert conditions
    symbol = Column(String(20), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False)  # price, volume, sentiment, etc.
    condition = Column(String(20), nullable=False)  # above, below, equals, etc.
    threshold_value = Column(Float, nullable=False)
    
    # Notification settings
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    title_template = Column(String(200), nullable=False)
    message_template = Column(Text, nullable=False)
    
    # Frequency control
    cooldown_minutes = Column(Integer, default=60)  # Minimum time between alerts
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NotificationSettings(Base):
    """User notification preferences"""
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)  # For single user, can be "default"
    
    # Notification preferences
    enable_order_notifications = Column(Boolean, default=True)
    enable_price_alerts = Column(Boolean, default=True)
    enable_sentiment_alerts = Column(Boolean, default=True)
    enable_risk_alerts = Column(Boolean, default=True)
    enable_system_alerts = Column(Boolean, default=True)
    enable_market_alerts = Column(Boolean, default=True)
    
    # Priority filters
    min_priority = Column(Enum(NotificationPriority), default=NotificationPriority.LOW)
    
    # Delivery preferences
    enable_sound = Column(Boolean, default=True)
    enable_desktop_notifications = Column(Boolean, default=True)
    auto_archive_after_days = Column(Integer, default=7)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
