"""
Earnings Calendar dan Corporate Actions Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime, date

class EventType(enum.Enum):
    """Event types"""
    EARNINGS = "earnings"
    DIVIDEND = "dividend"
    STOCK_SPLIT = "stock_split"
    STOCK_DIVIDEND = "stock_dividend"
    RIGHTS_ISSUE = "rights_issue"
    BONUS_ISSUE = "bonus_issue"
    MERGER = "merger"
    ACQUISITION = "acquisition"
    SPIN_OFF = "spin_off"
    IPO = "ipo"
    DELISTING = "delisting"

class EventStatus(enum.Enum):
    """Event status"""
    UPCOMING = "upcoming"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class EarningsEvent(Base):
    """Earnings events"""
    __tablename__ = "earnings_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Event details
    symbol = Column(String(20), nullable=False, index=True)
    company_name = Column(String(200), nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    
    # Timing
    announcement_date = Column(Date, nullable=False, index=True)
    ex_date = Column(Date, nullable=True, index=True)
    record_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)
    
    # Event data
    event_status = Column(Enum(EventStatus), default=EventStatus.UPCOMING)
    description = Column(Text, nullable=True)
    
    # Earnings specific
    quarter = Column(String(10), nullable=True)  # Q1, Q2, Q3, Q4
    fiscal_year = Column(Integer, nullable=True)
    earnings_per_share = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    
    # Dividend specific
    dividend_amount = Column(Float, nullable=True)
    dividend_currency = Column(String(3), nullable=True)
    dividend_frequency = Column(String(20), nullable=True)  # quarterly, semi-annual, annual
    
    # Stock split specific
    split_ratio = Column(String(20), nullable=True)  # 2:1, 3:1, etc.
    split_factor = Column(Float, nullable=True)
    
    # Additional data
    source = Column(String(100), nullable=True)
    source_url = Column(String(500), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    is_estimated = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CorporateAction(Base):
    """Corporate actions"""
    __tablename__ = "corporate_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Action details
    symbol = Column(String(20), nullable=False, index=True)
    company_name = Column(String(200), nullable=True)
    action_type = Column(Enum(EventType), nullable=False)
    
    # Timing
    announcement_date = Column(Date, nullable=False, index=True)
    ex_date = Column(Date, nullable=True, index=True)
    record_date = Column(Date, nullable=True)
    effective_date = Column(Date, nullable=True)
    
    # Action data
    action_status = Column(Enum(EventStatus), default=EventStatus.UPCOMING)
    description = Column(Text, nullable=True)
    
    # Action specific data
    action_data = Column(JSON, nullable=True)  # Flexible data storage
    
    # Impact
    impact_on_price = Column(String(20), nullable=True)  # positive, negative, neutral
    impact_magnitude = Column(Float, nullable=True)  # 0-1 scale
    
    # Additional data
    source = Column(String(100), nullable=True)
    source_url = Column(String(500), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    is_estimated = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EarningsAlert(Base):
    """Earnings alerts"""
    __tablename__ = "earnings_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Alert details
    symbol = Column(String(20), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    
    # Alert settings
    days_before = Column(Integer, default=1)  # Alert X days before event
    is_active = Column(Boolean, default=True)
    
    # Notification settings
    notify_email = Column(Boolean, default=False)
    notify_in_app = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EarningsCalendar(Base):
    """Earnings calendar views"""
    __tablename__ = "earnings_calendar"
    
    id = Column(Integer, primary_key=True, index=True)
    calendar_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Calendar details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Filter settings
    symbols = Column(JSON, nullable=True)  # List of symbols to include
    event_types = Column(JSON, nullable=True)  # List of event types to include
    date_range_start = Column(Date, nullable=True)
    date_range_end = Column(Date, nullable=True)
    
    # Display settings
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EarningsNotification(Base):
    """Earnings notifications"""
    __tablename__ = "earnings_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Notification details
    event_id = Column(String(50), nullable=False, index=True)
    alert_id = Column(String(50), nullable=True, index=True)
    
    # Notification data
    notification_type = Column(String(50), nullable=False)  # email, in_app, sms
    message = Column(Text, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EarningsAnalytics(Base):
    """Earnings analytics"""
    __tablename__ = "earnings_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Analytics data
    date = Column(Date, nullable=False, index=True)
    total_events = Column(Integer, default=0)
    earnings_events = Column(Integer, default=0)
    dividend_events = Column(Integer, default=0)
    other_events = Column(Integer, default=0)
    
    # Performance metrics
    avg_price_change = Column(Float, nullable=True)
    positive_events = Column(Integer, default=0)
    negative_events = Column(Integer, default=0)
    neutral_events = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
