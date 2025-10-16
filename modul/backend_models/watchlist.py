"""
Watchlist Models untuk Advanced Watchlist Features
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime, date

class WatchlistType(enum.Enum):
    """Watchlist types"""
    PERSONAL = "personal"
    SHARED = "shared"
    PUBLIC = "public"

class WatchlistItem(Base):
    """Watchlist items"""
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50), unique=True, nullable=False, index=True)
    watchlist_id = Column(String(50), nullable=False, index=True)
    
    # Symbol details
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=True)
    sector = Column(String(50), nullable=True)
    market_cap = Column(Float, nullable=True)
    
    # Current data
    current_price = Column(Float, nullable=True)
    price_change = Column(Float, nullable=True)
    price_change_percent = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    
    # Technical indicators
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    sma_20 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    
    # Custom metrics
    custom_metrics = Column(JSON, nullable=True)
    
    # Alerts
    price_alert_high = Column(Float, nullable=True)
    price_alert_low = Column(Float, nullable=True)
    volume_alert = Column(Integer, nullable=True)
    rsi_alert_high = Column(Float, nullable=True)
    rsi_alert_low = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Watchlist(Base):
    """Watchlists"""
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Watchlist details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    watchlist_type = Column(Enum(WatchlistType), default=WatchlistType.PERSONAL)
    
    # Settings
    is_public = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    auto_update = Column(Boolean, default=True)
    update_frequency = Column(Integer, default=60)  # seconds
    
    # Display settings
    default_columns = Column(JSON, nullable=True)
    sort_column = Column(String(50), nullable=True)
    sort_direction = Column(String(10), default="asc")
    
    # Performance tracking
    total_items = Column(Integer, default=0)
    last_updated = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WatchlistAlert(Base):
    """Watchlist alerts"""
    __tablename__ = "watchlist_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    watchlist_id = Column(String(50), nullable=False, index=True)
    item_id = Column(String(50), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # price, volume, rsi, custom
    condition = Column(String(20), nullable=False)   # above, below, equals
    threshold_value = Column(Float, nullable=False)
    
    # Alert settings
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    trigger_count = Column(Integer, default=0)
    last_triggered = Column(DateTime, nullable=True)
    
    # Notification settings
    notify_email = Column(Boolean, default=False)
    notify_in_app = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=60)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WatchlistPerformance(Base):
    """Watchlist performance tracking"""
    __tablename__ = "watchlist_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(String(50), nullable=False, index=True)
    
    # Performance metrics
    date = Column(Date, nullable=False, index=True)
    total_value = Column(Float, nullable=False)
    total_change = Column(Float, nullable=False)
    total_change_percent = Column(Float, nullable=False)
    
    # Item performance
    top_performer = Column(String(20), nullable=True)
    worst_performer = Column(String(20), nullable=True)
    top_gain = Column(Float, nullable=True)
    worst_loss = Column(Float, nullable=True)
    
    # Market metrics
    market_correlation = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WatchlistColumn(Base):
    """Custom watchlist columns"""
    __tablename__ = "watchlist_columns"
    
    id = Column(Integer, primary_key=True, index=True)
    column_id = Column(String(50), unique=True, nullable=False, index=True)
    watchlist_id = Column(String(50), nullable=False, index=True)
    
    # Column details
    column_name = Column(String(100), nullable=False)
    column_type = Column(String(50), nullable=False)  # price, volume, indicator, custom
    data_source = Column(String(100), nullable=True)
    
    # Display settings
    is_visible = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    width = Column(Integer, default=100)
    
    # Calculation settings
    calculation_formula = Column(Text, nullable=True)
    update_frequency = Column(Integer, default=60)  # seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WatchlistFilter(Base):
    """Watchlist filters"""
    __tablename__ = "watchlist_filters"
    
    id = Column(Integer, primary_key=True, index=True)
    filter_id = Column(String(50), unique=True, nullable=False, index=True)
    watchlist_id = Column(String(50), nullable=False, index=True)
    
    # Filter details
    filter_name = Column(String(100), nullable=False)
    filter_type = Column(String(50), nullable=False)  # price, volume, sector, custom
    filter_condition = Column(String(20), nullable=False)  # above, below, equals, contains
    filter_value = Column(String(200), nullable=False)
    
    # Filter settings
    is_active = Column(Boolean, default=True)
    is_global = Column(Boolean, default=False)  # Apply to all watchlists
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WatchlistQuickAction(Base):
    """Quick action buttons for watchlist items"""
    __tablename__ = "watchlist_quick_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(50), unique=True, nullable=False, index=True)
    watchlist_id = Column(String(50), nullable=False, index=True)
    
    # Action details
    action_name = Column(String(100), nullable=False)
    action_type = Column(String(50), nullable=False)  # buy, sell, alert, chart, news
    action_url = Column(String(200), nullable=True)
    action_params = Column(JSON, nullable=True)
    
    # Display settings
    button_text = Column(String(50), nullable=False)
    button_color = Column(String(20), default="primary")
    button_icon = Column(String(50), nullable=True)
    is_visible = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
