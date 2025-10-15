"""
Trading Models untuk Order Management dan Portfolio
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, BigInteger, Enum, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum

class OrderType(enum.Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"  # One-Cancels-Other
    BRACKET = "bracket"

class OrderSide(enum.Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(enum.Enum):
    """Order status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TradingMode(enum.Enum):
    """Trading modes"""
    TRAINING = "training"
    REAL_TIME = "real_time"

class Order(Base):
    """Order management"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Order details
    order_type = Column(Enum(OrderType), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)  # For limit orders
    stop_price = Column(Float, nullable=True)  # For stop orders
    trailing_distance = Column(Float, nullable=True)  # For trailing stop
    
    # Order status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    filled_quantity = Column(Integer, default=0)
    average_price = Column(Float, nullable=True)
    remaining_quantity = Column(Integer, nullable=True)
    
    # Trading mode
    trading_mode = Column(Enum(TradingMode), nullable=False)
    auto_trading = Column(Boolean, default=False)  # For real-time mode
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    filled_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # For custom tags
    parent_order_id = Column(String(50), nullable=True)  # For bracket orders
    
    # Risk management
    max_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)

class Position(Base):
    """Portfolio positions"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Position details
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    
    # P&L tracking
    unrealized_pnl = Column(Float, nullable=True)
    realized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, nullable=True)
    
    # Position metadata
    first_buy_date = Column(Date, nullable=True)
    last_trade_date = Column(Date, nullable=True)
    trading_mode = Column(Enum(TradingMode), nullable=False)
    
    # Tax tracking (Indonesia format)
    tax_lots = Column(JSON, nullable=True)  # FIFO/LIFO tracking
    total_cost_basis = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Trade(Base):
    """Executed trades"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Trade details
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)  # Indonesian tax
    
    # P&L calculation
    cost_basis = Column(Float, nullable=True)
    realized_pnl = Column(Float, nullable=True)
    
    # Trading mode
    trading_mode = Column(Enum(TradingMode), nullable=False)
    
    # Timestamps
    executed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional data
    notes = Column(Text, nullable=True)

class Portfolio(Base):
    """Portfolio management"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Portfolio metrics
    total_value = Column(Float, default=0.0)
    cash_balance = Column(Float, default=0.0)
    invested_value = Column(Float, default=0.0)
    
    # Performance tracking
    total_pnl = Column(Float, default=0.0)
    daily_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    # Risk management
    max_position_size = Column(Float, default=0.1)  # 10% max per position
    daily_loss_limit = Column(Float, default=0.02)  # 2% daily loss limit
    max_drawdown_limit = Column(Float, default=0.15)  # 15% max drawdown
    
    # Trading mode
    trading_mode = Column(Enum(TradingMode), nullable=False)
    auto_trading_enabled = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TaxLot(Base):
    """Tax lot tracking untuk FIFO/LIFO (Indonesia format)"""
    __tablename__ = "tax_lots"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    position_id = Column(Integer, nullable=False, index=True)
    
    # Tax lot details
    quantity = Column(Integer, nullable=False)
    cost_basis = Column(Float, nullable=False)
    purchase_date = Column(Date, nullable=False)
    
    # Sale tracking
    sold_quantity = Column(Integer, default=0)
    remaining_quantity = Column(Integer, nullable=False)
    
    # Indonesian tax calculation
    capital_gain = Column(Float, default=0.0)
    tax_liability = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TradingSession(Base):
    """Trading session tracking"""
    __tablename__ = "trading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Session details
    trading_mode = Column(Enum(TradingMode), nullable=False)
    auto_trading = Column(Boolean, default=False)
    start_balance = Column(Float, nullable=False)
    end_balance = Column(Float, nullable=True)
    
    # Session metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskMetrics(Base):
    """Risk management metrics"""
    __tablename__ = "risk_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    portfolio_id = Column(Integer, nullable=True)
    
    # Risk metrics
    portfolio_value = Column(Float, nullable=False)
    daily_pnl = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    current_drawdown = Column(Float, nullable=False)
    
    # VaR calculations
    var_1d = Column(Float, nullable=True)  # 1-day VaR
    var_1w = Column(Float, nullable=True)  # 1-week VaR
    cvar_1d = Column(Float, nullable=True)  # Conditional VaR
    
    # Position metrics
    total_exposure = Column(Float, nullable=False)
    sector_exposure = Column(JSON, nullable=True)
    position_count = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())