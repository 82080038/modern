"""
Portfolio Optimization API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from sqlalchemy import text
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio", tags=["Portfolio Optimization"])

# Pydantic schemas
class PortfolioResponse(BaseModel):
    symbol: str
    position_type: str
    quantity: int
    entry_price: float
    entry_date: str
    current_price: float
    stop_loss: float
    take_profit: float
    trailing_stop: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    commission_paid: float
    status: str
    close_price: float
    close_date: str
    realized_pnl: float
    realized_pnl_pct: float
    holding_days: int

class PortfolioHistoryResponse(BaseModel):
    timestamp: str
    total_value: float
    cash: float
    positions_value: float
    daily_pnl: float
    daily_return: float
    unrealized_pnl: float
    realized_pnl: float

class PerformanceMetricsResponse(BaseModel):
    strategy: str
    period_start: str
    period_end: str
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int

class PerformanceAttributionResponse(BaseModel):
    attribution_date: str
    total_return: float
    benchmark_return: float
    excess_return: float
    fundamental_attribution: float
    technical_attribution: float
    sentiment_attribution: float
    macro_attribution: float
    risk_attribution: float
    banking_attribution: float
    telecom_attribution: float
    consumer_attribution: float
    mining_attribution: float
    other_attribution: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float

@router.get("/positions")
async def get_portfolio_positions(
    position_type: Optional[str] = Query(None, description="Filter by position type (LONG, SHORT)"),
    status: Optional[str] = Query(None, description="Filter by status (OPEN, CLOSED)"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get portfolio positions"""
    try:
        query_parts = ["SELECT * FROM portfolio WHERE 1=1"]
        params = {}
        
        if position_type:
            query_parts.append("AND position_type = :position_type")
            params["position_type"] = position_type
        if status:
            query_parts.append("AND status = :status")
            params["status"] = status
        
        query_parts.append("ORDER BY entry_date DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No portfolio positions found")
        
        positions = []
        for row in rows:
            positions.append({
                "symbol": row.symbol,
                "position_type": row.position_type,
                "quantity": row.quantity,
                "entry_price": float(row.entry_price) if row.entry_price else None,
                "entry_date": row.entry_date.isoformat() if row.entry_date else None,
                "current_price": float(row.current_price) if row.current_price else None,
                "stop_loss": float(row.stop_loss) if row.stop_loss else None,
                "take_profit": float(row.take_profit) if row.take_profit else None,
                "trailing_stop": float(row.trailing_stop) if row.trailing_stop else None,
                "unrealized_pnl": float(row.unrealized_pnl) if row.unrealized_pnl else None,
                "unrealized_pnl_pct": float(row.unrealized_pnl_pct) if row.unrealized_pnl_pct else None,
                "commission_paid": float(row.commission_paid) if row.commission_paid else None,
                "status": row.status,
                "close_price": float(row.close_price) if row.close_price else None,
                "close_date": row.close_date.isoformat() if row.close_date else None,
                "realized_pnl": float(row.realized_pnl) if row.realized_pnl else None,
                "realized_pnl_pct": float(row.realized_pnl_pct) if row.realized_pnl_pct else None,
                "holding_days": row.holding_days
            })
        
        return {
            "total_positions": len(positions),
            "filters": {
                "position_type": position_type,
                "status": status
            },
            "positions": positions
        }
        
    except Exception as e:
        logger.error(f"Error getting portfolio positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_portfolio_history(
    start_date: Optional[date] = Query(None, description="Start date for history"),
    end_date: Optional[date] = Query(None, description="End date for history"),
    limit: int = Query(100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get portfolio history"""
    try:
        query_parts = ["SELECT * FROM portfolio_history WHERE 1=1"]
        params = {}
        
        if start_date:
            query_parts.append("AND DATE(timestamp) >= :start_date")
            params["start_date"] = start_date
        if end_date:
            query_parts.append("AND DATE(timestamp) <= :end_date")
            params["end_date"] = end_date
        
        query_parts.append("ORDER BY timestamp DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No portfolio history found")
        
        history = []
        for row in rows:
            history.append({
                "timestamp": row.timestamp.isoformat(),
                "total_value": float(row.total_value) if row.total_value else None,
                "cash": float(row.cash) if row.cash else None,
                "positions_value": float(row.positions_value) if row.positions_value else None,
                "daily_pnl": float(row.daily_pnl) if row.daily_pnl else None,
                "daily_return": float(row.daily_return) if row.daily_return else None,
                "unrealized_pnl": float(row.unrealized_pnl) if row.unrealized_pnl else None,
                "realized_pnl": float(row.realized_pnl) if row.realized_pnl else None
            })
        
        return {
            "total_records": len(history),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Error getting portfolio history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_portfolio_performance(
    strategy: Optional[str] = Query(None, description="Filter by strategy"),
    start_date: Optional[date] = Query(None, description="Start date for performance"),
    end_date: Optional[date] = Query(None, description="End date for performance"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get portfolio performance metrics"""
    try:
        query_parts = ["SELECT * FROM performance_metrics WHERE 1=1"]
        params = {}
        
        if strategy:
            query_parts.append("AND strategy = :strategy")
            params["strategy"] = strategy
        if start_date:
            query_parts.append("AND period_start >= :start_date")
            params["start_date"] = start_date
        if end_date:
            query_parts.append("AND period_end <= :end_date")
            params["end_date"] = end_date
        
        query_parts.append("ORDER BY period_start DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No performance metrics found")
        
        performance = []
        for row in rows:
            performance.append({
                "strategy": row.strategy,
                "period_start": row.period_start.isoformat(),
                "period_end": row.period_end.isoformat(),
                "total_return": float(row.total_return) if row.total_return else None,
                "annualized_return": float(row.annualized_return) if row.annualized_return else None,
                "sharpe_ratio": float(row.sharpe_ratio) if row.sharpe_ratio else None,
                "max_drawdown": float(row.max_drawdown) if row.max_drawdown else None,
                "win_rate": float(row.win_rate) if row.win_rate else None,
                "profit_factor": float(row.profit_factor) if row.profit_factor else None,
                "total_trades": row.total_trades,
                "winning_trades": row.winning_trades,
                "losing_trades": row.losing_trades
            })
        
        return {
            "total_metrics": len(performance),
            "filters": {
                "strategy": strategy,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "performance": performance
        }
        
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attribution")
async def get_performance_attribution(
    start_date: Optional[date] = Query(None, description="Start date for attribution"),
    end_date: Optional[date] = Query(None, description="End date for attribution"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get performance attribution analysis"""
    try:
        query_parts = ["SELECT * FROM performance_attribution WHERE 1=1"]
        params = {}
        
        if start_date:
            query_parts.append("AND attribution_date >= :start_date")
            params["start_date"] = start_date
        if end_date:
            query_parts.append("AND attribution_date <= :end_date")
            params["end_date"] = end_date
        
        query_parts.append("ORDER BY attribution_date DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No performance attribution data found")
        
        attribution = []
        for row in rows:
            attribution.append({
                "attribution_date": row.attribution_date.isoformat(),
                "total_return": float(row.total_return) if row.total_return else None,
                "benchmark_return": float(row.benchmark_return) if row.benchmark_return else None,
                "excess_return": float(row.excess_return) if row.excess_return else None,
                "fundamental_attribution": float(row.fundamental_attribution) if row.fundamental_attribution else None,
                "technical_attribution": float(row.technical_attribution) if row.technical_attribution else None,
                "sentiment_attribution": float(row.sentiment_attribution) if row.sentiment_attribution else None,
                "macro_attribution": float(row.macro_attribution) if row.macro_attribution else None,
                "risk_attribution": float(row.risk_attribution) if row.risk_attribution else None,
                "banking_attribution": float(row.banking_attribution) if row.banking_attribution else None,
                "telecom_attribution": float(row.telecom_attribution) if row.telecom_attribution else None,
                "consumer_attribution": float(row.consumer_attribution) if row.consumer_attribution else None,
                "mining_attribution": float(row.mining_attribution) if row.mining_attribution else None,
                "other_attribution": float(row.other_attribution) if row.other_attribution else None,
                "sharpe_ratio": float(row.sharpe_ratio) if row.sharpe_ratio else None,
                "max_drawdown": float(row.max_drawdown) if row.max_drawdown else None,
                "volatility": float(row.volatility) if row.volatility else None
            })
        
        return {
            "total_attributions": len(attribution),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "attribution": attribution
        }
        
    except Exception as e:
        logger.error(f"Error getting performance attribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_portfolio_dashboard(
    db: Session = Depends(get_db)
):
    """Get portfolio dashboard summary"""
    try:
        # Get latest portfolio value
        latest_value_query = """
            SELECT * FROM portfolio_history 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        value_result = db.execute(text(latest_value_query))
        latest_value = value_result.fetchone()
        
        # Get active positions
        active_positions_query = """
            SELECT COUNT(*) as total_positions,
                   SUM(unrealized_pnl) as total_unrealized_pnl,
                   AVG(unrealized_pnl_pct) as avg_unrealized_pnl_pct
            FROM portfolio 
            WHERE status = 'OPEN'
        """
        positions_result = db.execute(text(active_positions_query))
        positions_summary = positions_result.fetchone()
        
        # Get performance summary
        performance_summary_query = """
            SELECT 
                AVG(total_return) as avg_return,
                AVG(sharpe_ratio) as avg_sharpe,
                AVG(max_drawdown) as avg_max_drawdown,
                AVG(win_rate) as avg_win_rate
            FROM performance_metrics 
            WHERE period_start >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        performance_result = db.execute(text(performance_summary_query))
        performance_summary = performance_result.fetchone()
        
        # Get sector allocation
        sector_allocation_query = """
            SELECT 
                CASE 
                    WHEN symbol LIKE '%BBCA%' OR symbol LIKE '%BBRI%' OR symbol LIKE '%BMRI%' THEN 'Banking'
                    WHEN symbol LIKE '%TLKM%' THEN 'Telecom'
                    WHEN symbol LIKE '%ASII%' THEN 'Consumer'
                    ELSE 'Other'
                END as sector,
                COUNT(*) as position_count,
                SUM(quantity * current_price) as sector_value
            FROM portfolio 
            WHERE status = 'OPEN'
            GROUP BY sector
        """
        sector_result = db.execute(text(sector_allocation_query))
        sector_allocation = sector_result.fetchall()
        
        return {
            "latest_portfolio_value": {
                "timestamp": latest_value.timestamp.isoformat() if latest_value else None,
                "total_value": float(latest_value.total_value) if latest_value and latest_value.total_value else None,
                "cash": float(latest_value.cash) if latest_value and latest_value.cash else None,
                "positions_value": float(latest_value.positions_value) if latest_value and latest_value.positions_value else None,
                "daily_pnl": float(latest_value.daily_pnl) if latest_value and latest_value.daily_pnl else None,
                "daily_return": float(latest_value.daily_return) if latest_value and latest_value.daily_return else None
            } if latest_value else None,
            "active_positions": {
                "total_positions": positions_summary.total_positions if positions_summary else 0,
                "total_unrealized_pnl": float(positions_summary.total_unrealized_pnl) if positions_summary and positions_summary.total_unrealized_pnl else None,
                "avg_unrealized_pnl_pct": float(positions_summary.avg_unrealized_pnl_pct) if positions_summary and positions_summary.avg_unrealized_pnl_pct else None
            } if positions_summary else None,
            "performance_summary": {
                "avg_return": float(performance_summary.avg_return) if performance_summary and performance_summary.avg_return else None,
                "avg_sharpe": float(performance_summary.avg_sharpe) if performance_summary and performance_summary.avg_sharpe else None,
                "avg_max_drawdown": float(performance_summary.avg_max_drawdown) if performance_summary and performance_summary.avg_max_drawdown else None,
                "avg_win_rate": float(performance_summary.avg_win_rate) if performance_summary and performance_summary.avg_win_rate else None
            } if performance_summary else None,
            "sector_allocation": [
                {
                    "sector": s.sector,
                    "position_count": s.position_count,
                    "sector_value": float(s.sector_value) if s.sector_value else None
                } for s in sector_allocation
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting portfolio dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def optimize_portfolio(
    symbols: List[str],
    risk_tolerance: float = 0.5,
    expected_return: Optional[float] = None,
    max_weight: float = 0.3,
    db: Session = Depends(get_db)
):
    """Optimize portfolio allocation (placeholder for future implementation)"""
    try:
        # This is a placeholder - in a real implementation, this would:
        # 1. Get historical data for the symbols
        # 2. Calculate expected returns and covariance matrix
        # 3. Run optimization algorithm (e.g., Markowitz, Black-Litterman)
        # 4. Return optimal weights and risk metrics
        
        return {
            "message": "Portfolio optimization initiated",
            "symbols": symbols,
            "risk_tolerance": risk_tolerance,
            "expected_return": expected_return,
            "max_weight": max_weight,
            "status": "PENDING",
            "note": "This is a placeholder endpoint. Full portfolio optimization implementation would be added here."
        }
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
