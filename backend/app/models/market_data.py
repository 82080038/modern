"""
Market Data Models untuk Real-Time dan Historical Data
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, BigInteger, Index
from sqlalchemy.sql import func
from app.database import Base

class MarketData(Base):
    """Real-time market data"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # OHLCV Data
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    
    # Additional Data
    bid_price = Column(Float, nullable=True)
    ask_price = Column(Float, nullable=True)
    last_price = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(50), nullable=False, default="yfinance")  # yfinance, idx, investing
    is_real_time = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes untuk performance
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
    )

class HistoricalData(Base):
    """Historical market data dengan multiple timeframes"""
    __tablename__ = "historical_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)  # 1m, 5m, 15m, 1h, 4h, 1D, 1W, 1M, 3M, 6M, 1Y
    date = Column(Date, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # OHLCV Data
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    
    # Technical Indicators (akan diisi oleh background task)
    sma_20 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    ema_12 = Column(Float, nullable=True)
    ema_26 = Column(Float, nullable=True)
    rsi_14 = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    bollinger_upper = Column(Float, nullable=True)
    bollinger_middle = Column(Float, nullable=True)
    bollinger_lower = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(50), nullable=False, default="yfinance")
    is_complete = Column(Boolean, default=True)  # True jika data lengkap untuk timeframe
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes untuk performance
    __table_args__ = (
        Index('idx_symbol_timeframe_date', 'symbol', 'timeframe', 'date'),
        Index('idx_timeframe_date', 'timeframe', 'date'),
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
    )

class DataUpdateLog(Base):
    """Log untuk tracking data updates dan menghindari re-download"""
    __tablename__ = "data_update_log"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    last_update = Column(DateTime, nullable=False)
    last_data_date = Column(Date, nullable=True)
    total_records = Column(Integer, nullable=True)
    data_source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="success")  # success, error, partial
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
    )

class MarketStatus(Base):
    """Market status dan trading hours"""
    __tablename__ = "market_status"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    is_trading_day = Column(Boolean, default=True)
    market_open = Column(DateTime, nullable=True)
    market_close = Column(DateTime, nullable=True)
    pre_market_open = Column(DateTime, nullable=True)
    after_hours_close = Column(DateTime, nullable=True)
    
    # Market indicators
    total_volume = Column(BigInteger, nullable=True)
    advancing_stocks = Column(Integer, nullable=True)
    declining_stocks = Column(Integer, nullable=True)
    unchanged_stocks = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SymbolInfo(Base):
    """Symbol information dan metadata"""
    __tablename__ = "symbol_info"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    market_cap = Column(BigInteger, nullable=True)
    shares_outstanding = Column(BigInteger, nullable=True)
    currency = Column(String(10), default="IDR")
    exchange = Column(String(50), default="IDX")
    
    # Trading info
    is_active = Column(Boolean, default=True)
    listing_date = Column(Date, nullable=True)
    delisting_date = Column(Date, nullable=True)
    
    # Data availability
    has_real_time = Column(Boolean, default=False)
    has_historical = Column(Boolean, default=False)
    last_data_update = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
