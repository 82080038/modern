"""
Backtesting Models untuk Strategy Testing
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime, date
from decimal import Decimal

class StrategyType(enum.Enum):
    """Strategy types"""
    MOVING_AVERAGE = "moving_average"
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER_BANDS = "bollinger_bands"
    CUSTOM = "custom"

class BacktestStatus(enum.Enum):
    """Backtest status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Backtest(Base):
    """Backtest execution records"""
    __tablename__ = "backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Strategy details
    strategy_name = Column(String(100), nullable=False)
    strategy_type = Column(Enum(StrategyType), nullable=False)
    strategy_params = Column(JSON, nullable=True)
    
    # Backtest configuration
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Initial conditions
    initial_capital = Column(Float, nullable=False)
    commission_rate = Column(Float, default=0.001)  # 0.1%
    slippage_rate = Column(Float, default=0.0005)   # 0.05%
    
    # Results
    status = Column(Enum(BacktestStatus), default=BacktestStatus.PENDING)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    
    # Performance metrics
    total_return = Column(Float, default=0.0)
    annualized_return = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    sortino_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    
    # Final values
    final_capital = Column(Float, default=0.0)
    total_commission = Column(Float, default=0.0)
    total_slippage = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    equity_curve = Column(JSON, nullable=True)  # Daily equity values
    trade_log = Column(JSON, nullable=True)     # All trades executed

class Strategy(Base):
    """Trading strategies"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Strategy details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(Enum(StrategyType), nullable=False)
    
    # Strategy parameters
    parameters = Column(JSON, nullable=True)
    buy_conditions = Column(JSON, nullable=True)
    sell_conditions = Column(JSON, nullable=True)
    
    # Strategy settings
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Performance tracking
    total_backtests = Column(Integer, default=0)
    avg_return = Column(Float, default=0.0)
    best_return = Column(Float, default=0.0)
    worst_return = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BacktestTrade(Base):
    """Individual trades from backtests"""
    __tablename__ = "backtest_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(50), unique=True, nullable=False, index=True)
    backtest_id = Column(String(50), nullable=False, index=True)
    
    # Trade details
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    
    # Timestamps
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    
    # Trade results
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    
    # Trade metadata
    entry_reason = Column(String(200), nullable=True)
    exit_reason = Column(String(200), nullable=True)
    duration_hours = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BacktestMetrics(Base):
    """Detailed backtest performance metrics"""
    __tablename__ = "backtest_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(50), nullable=False, index=True)
    
    # Date for daily metrics
    date = Column(Date, nullable=False, index=True)
    
    # Daily values
    equity = Column(Float, nullable=False)
    daily_return = Column(Float, default=0.0)
    cumulative_return = Column(Float, default=0.0)
    drawdown = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    # Rolling metrics
    rolling_sharpe = Column(Float, nullable=True)
    rolling_sortino = Column(Float, nullable=True)
    rolling_volatility = Column(Float, nullable=True)
    
    # Trade metrics
    trades_count = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    avg_win = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StrategyOptimization(Base):
    """Strategy parameter optimization results"""
    __tablename__ = "strategy_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    optimization_id = Column(String(50), unique=True, nullable=False, index=True)
    strategy_id = Column(String(50), nullable=False, index=True)
    
    # Optimization details
    optimization_type = Column(String(50), nullable=False)  # grid_search, genetic, bayesian
    parameter_ranges = Column(JSON, nullable=True)
    optimization_metric = Column(String(50), nullable=False)  # sharpe, return, max_dd
    
    # Results
    best_parameters = Column(JSON, nullable=True)
    best_score = Column(Float, nullable=True)
    total_combinations = Column(Integer, default=0)
    tested_combinations = Column(Integer, default=0)
    
    # Status
    status = Column(Enum(BacktestStatus), default=BacktestStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results data
    optimization_results = Column(JSON, nullable=True)  # All parameter combinations tested
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MonteCarloSimulation(Base):
    """Monte Carlo simulation results"""
    __tablename__ = "monte_carlo_simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String(50), unique=True, nullable=False, index=True)
    backtest_id = Column(String(50), nullable=False, index=True)
    
    # Simulation parameters
    num_simulations = Column(Integer, nullable=False)
    simulation_length = Column(Integer, nullable=False)  # days
    
    # Results
    confidence_levels = Column(JSON, nullable=True)  # 95%, 99% confidence intervals
    worst_case_scenario = Column(Float, nullable=True)
    best_case_scenario = Column(Float, nullable=True)
    expected_value = Column(Float, nullable=True)
    
    # Risk metrics
    var_95 = Column(Float, nullable=True)  # Value at Risk 95%
    var_99 = Column(Float, nullable=True)  # Value at Risk 99%
    cvar_95 = Column(Float, nullable=True)  # Conditional VaR 95%
    cvar_99 = Column(Float, nullable=True)  # Conditional VaR 99%
    
    # Simulation data
    simulation_paths = Column(JSON, nullable=True)  # Sample of simulation paths
    distribution_stats = Column(JSON, nullable=True)  # Statistical distribution
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
