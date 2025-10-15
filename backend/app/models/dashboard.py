"""
Dashboard Models untuk Widget-based Dashboard System
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime, date

class WidgetType(enum.Enum):
    """Widget types"""
    CHART = "chart"
    WATCHLIST = "watchlist"
    NEWS = "news"
    ALERTS = "alerts"
    PERFORMANCE = "performance"
    MARKET_OVERVIEW = "market_overview"
    TECHNICAL_INDICATORS = "technical_indicators"
    PATTERN_RECOGNITION = "pattern_recognition"
    BACKTEST_RESULTS = "backtest_results"
    CUSTOM = "custom"

class DashboardLayout(enum.Enum):
    """Dashboard layout types"""
    GRID = "grid"
    FLEXIBLE = "flexible"
    CUSTOM = "custom"

class Dashboard(Base):
    """Dashboard configurations"""
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Dashboard details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    layout_type = Column(Enum(DashboardLayout), default=DashboardLayout.GRID)
    
    # Settings
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    auto_refresh = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=60)  # seconds
    
    # Layout configuration
    grid_columns = Column(Integer, default=4)
    grid_rows = Column(Integer, default=3)
    layout_config = Column(JSON, nullable=True)  # Custom layout configuration
    
    # Theme settings
    theme = Column(String(20), default="light")  # light, dark, auto
    color_scheme = Column(String(20), default="blue")  # blue, green, red, purple
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DashboardWidget(Base):
    """Dashboard widgets"""
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(String(50), unique=True, nullable=False, index=True)
    dashboard_id = Column(String(50), nullable=False, index=True)
    
    # Widget details
    widget_type = Column(Enum(WidgetType), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Position and size
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=1)
    height = Column(Integer, default=1)
    
    # Widget configuration
    config = Column(JSON, nullable=True)  # Widget-specific configuration
    data_source = Column(String(100), nullable=True)
    refresh_interval = Column(Integer, default=60)  # seconds
    
    # Display settings
    is_visible = Column(Boolean, default=True)
    is_resizable = Column(Boolean, default=True)
    is_movable = Column(Boolean, default=True)
    border_style = Column(String(20), default="solid")
    background_color = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WidgetData(Base):
    """Widget data cache"""
    __tablename__ = "widget_data"
    
    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(String(50), nullable=False, index=True)
    
    # Data details
    data_type = Column(String(50), nullable=False)
    data_key = Column(String(100), nullable=False)
    data_value = Column(JSON, nullable=True)
    
    # Cache settings
    expires_at = Column(DateTime, nullable=True)
    is_valid = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DashboardPreset(Base):
    """Dashboard presets"""
    __tablename__ = "dashboard_presets"
    
    id = Column(Integer, primary_key=True, index=True)
    preset_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Preset details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # trading, analysis, monitoring
    
    # Preset configuration
    layout_config = Column(JSON, nullable=True)
    widgets_config = Column(JSON, nullable=True)
    theme_config = Column(JSON, nullable=True)
    
    # Settings
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WidgetTemplate(Base):
    """Widget templates"""
    __tablename__ = "widget_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Template details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    widget_type = Column(Enum(WidgetType), nullable=False)
    
    # Template configuration
    default_config = Column(JSON, nullable=True)
    default_size = Column(JSON, nullable=True)  # {width: 1, height: 1}
    
    # Settings
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DashboardShare(Base):
    """Dashboard sharing"""
    __tablename__ = "dashboard_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(String(50), unique=True, nullable=False, index=True)
    dashboard_id = Column(String(50), nullable=False, index=True)
    
    # Share details
    share_type = Column(String(20), nullable=False)  # public, private, link
    share_token = Column(String(100), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Permissions
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    
    # Access tracking
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DashboardAnalytics(Base):
    """Dashboard usage analytics"""
    __tablename__ = "dashboard_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(String(50), nullable=False, index=True)
    
    # Analytics data
    date = Column(Date, nullable=False, index=True)
    views = Column(Integer, default=0)
    interactions = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    
    # Widget analytics
    most_used_widget = Column(String(50), nullable=True)
    least_used_widget = Column(String(50), nullable=True)
    widget_interactions = Column(JSON, nullable=True)
    
    # Performance metrics
    load_time = Column(Float, nullable=True)
    error_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
