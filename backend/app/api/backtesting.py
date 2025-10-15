"""
Backtesting Framework API Endpoints
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
router = APIRouter(prefix="/backtesting", tags=["Backtesting Framework"])

# Pydantic schemas
class BacktestResponse(BaseModel):
    backtest_id: str
    strategy_name: str
    strategy_type: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    status: str

class BacktestTradeResponse(BaseModel):
    trade_id: str
    symbol: str
    side: str
    quantity: int
    entry_price: float
    exit_price: float
    entry_time: str
    exit_time: str
    pnl: float
    pnl_percent: float
    commission: float
    slippage: float
    entry_reason: str
    exit_reason: str
    duration_hours: float

class BacktestMetricsResponse(BaseModel):
    date: str
    equity: float
    daily_return: float
    cumulative_return: float
    drawdown: float
    max_drawdown: float
    rolling_sharpe: float
    rolling_sortino: float
    rolling_volatility: float
    trades_count: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float

@router.get("/backtests")
async def get_backtests(
    strategy_name: Optional[str] = Query(None, description="Filter by strategy name"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get list of backtests"""
    try:
        query_parts = ["SELECT * FROM backtests WHERE 1=1"]
        params = {}
        
        if strategy_name:
            query_parts.append("AND strategy_name LIKE :strategy_name")
            params["strategy_name"] = f"%{strategy_name}%"
        if symbol:
            query_parts.append("AND symbol = :symbol")
            params["symbol"] = symbol
        if status:
            query_parts.append("AND status = :status")
            params["status"] = status
        
        query_parts.append("ORDER BY created_at DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        backtests = []
        for row in rows:
            backtests.append({
                "backtest_id": row.backtest_id,
                "strategy_name": row.strategy_name,
                "strategy_type": row.strategy_type,
                "symbol": row.symbol,
                "timeframe": row.timeframe,
                "start_date": row.start_date.isoformat(),
                "end_date": row.end_date.isoformat(),
                "initial_capital": float(row.initial_capital) if row.initial_capital else None,
                "final_capital": float(row.final_capital) if row.final_capital else None,
                "total_return": float(row.total_return) if row.total_return else None,
                "annualized_return": float(row.annualized_return) if row.annualized_return else None,
                "sharpe_ratio": float(row.sharpe_ratio) if row.sharpe_ratio else None,
                "sortino_ratio": float(row.sortino_ratio) if row.sortino_ratio else None,
                "max_drawdown": float(row.max_drawdown) if row.max_drawdown else None,
                "win_rate": float(row.win_rate) if row.win_rate else None,
                "profit_factor": float(row.profit_factor) if row.profit_factor else None,
                "total_trades": row.total_trades,
                "winning_trades": row.winning_trades,
                "losing_trades": row.losing_trades,
                "status": row.status,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return {
            "total_backtests": len(backtests),
            "filters": {
                "strategy_name": strategy_name,
                "symbol": symbol,
                "status": status
            },
            "backtests": backtests
        }
        
    except Exception as e:
        logger.error(f"Error getting backtests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtests/{backtest_id}")
async def get_backtest_details(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed backtest results"""
    try:
        # Get backtest info
        backtest_query = "SELECT * FROM backtests WHERE backtest_id = :backtest_id"
        backtest_result = db.execute(text(backtest_query), {"backtest_id": backtest_id})
        backtest = backtest_result.fetchone()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        # Get backtest trades
        trades_query = """
            SELECT * FROM backtest_trades 
            WHERE backtest_id = :backtest_id 
            ORDER BY entry_time DESC
        """
        trades_result = db.execute(text(trades_query), {"backtest_id": backtest_id})
        trades = trades_result.fetchall()
        
        # Get backtest metrics
        metrics_query = """
            SELECT * FROM backtest_metrics 
            WHERE backtest_id = :backtest_id 
            ORDER BY date ASC
        """
        metrics_result = db.execute(text(metrics_query), {"backtest_id": backtest_id})
        metrics = metrics_result.fetchall()
        
        return {
            "backtest": {
                "backtest_id": backtest.backtest_id,
                "strategy_name": backtest.strategy_name,
                "strategy_type": backtest.strategy_type,
                "symbol": backtest.symbol,
                "timeframe": backtest.timeframe,
                "start_date": backtest.start_date.isoformat(),
                "end_date": backtest.end_date.isoformat(),
                "initial_capital": float(backtest.initial_capital) if backtest.initial_capital else None,
                "final_capital": float(backtest.final_capital) if backtest.final_capital else None,
                "total_return": float(backtest.total_return) if backtest.total_return else None,
                "annualized_return": float(backtest.annualized_return) if backtest.annualized_return else None,
                "sharpe_ratio": float(backtest.sharpe_ratio) if backtest.sharpe_ratio else None,
                "sortino_ratio": float(backtest.sortino_ratio) if backtest.sortino_ratio else None,
                "max_drawdown": float(backtest.max_drawdown) if backtest.max_drawdown else None,
                "win_rate": float(backtest.win_rate) if backtest.win_rate else None,
                "profit_factor": float(backtest.profit_factor) if backtest.profit_factor else None,
                "total_trades": backtest.total_trades,
                "winning_trades": backtest.winning_trades,
                "losing_trades": backtest.losing_trades,
                "status": backtest.status,
                "created_at": backtest.created_at.isoformat() if backtest.created_at else None
            },
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "quantity": t.quantity,
                    "entry_price": float(t.entry_price) if t.entry_price else None,
                    "exit_price": float(t.exit_price) if t.exit_price else None,
                    "entry_time": t.entry_time.isoformat() if t.entry_time else None,
                    "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                    "pnl": float(t.pnl) if t.pnl else None,
                    "pnl_percent": float(t.pnl_percent) if t.pnl_percent else None,
                    "commission": float(t.commission) if t.commission else None,
                    "slippage": float(t.slippage) if t.slippage else None,
                    "entry_reason": t.entry_reason,
                    "exit_reason": t.exit_reason,
                    "duration_hours": float(t.duration_hours) if t.duration_hours else None
                } for t in trades
            ],
            "metrics": [
                {
                    "date": m.date.isoformat(),
                    "equity": float(m.equity) if m.equity else None,
                    "daily_return": float(m.daily_return) if m.daily_return else None,
                    "cumulative_return": float(m.cumulative_return) if m.cumulative_return else None,
                    "drawdown": float(m.drawdown) if m.drawdown else None,
                    "max_drawdown": float(m.max_drawdown) if m.max_drawdown else None,
                    "rolling_sharpe": float(m.rolling_sharpe) if m.rolling_sharpe else None,
                    "rolling_sortino": float(m.rolling_sortino) if m.rolling_sortino else None,
                    "rolling_volatility": float(m.rolling_volatility) if m.rolling_volatility else None,
                    "trades_count": m.trades_count,
                    "winning_trades": m.winning_trades,
                    "losing_trades": m.losing_trades,
                    "avg_win": float(m.avg_win) if m.avg_win else None,
                    "avg_loss": float(m.avg_loss) if m.avg_loss else None
                } for m in metrics
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting backtest details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-summary")
async def get_backtest_performance_summary(
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get backtest performance summary"""
    try:
        query = """
            SELECT 
                strategy_name,
                COUNT(*) as total_backtests,
                AVG(total_return) as avg_return,
                AVG(sharpe_ratio) as avg_sharpe,
                AVG(max_drawdown) as avg_max_drawdown,
                AVG(win_rate) as avg_win_rate,
                MAX(total_return) as best_return,
                MIN(total_return) as worst_return
            FROM backtests 
            WHERE status = 'COMPLETED'
            GROUP BY strategy_name
            ORDER BY avg_return DESC
            LIMIT :limit
        """
        
        result = db.execute(text(query), {"limit": limit})
        rows = result.fetchall()
        
        performance_summary = []
        for row in rows:
            performance_summary.append({
                "strategy_name": row.strategy_name,
                "total_backtests": row.total_backtests,
                "avg_return": float(row.avg_return) if row.avg_return else None,
                "avg_sharpe": float(row.avg_sharpe) if row.avg_sharpe else None,
                "avg_max_drawdown": float(row.avg_max_drawdown) if row.avg_max_drawdown else None,
                "avg_win_rate": float(row.avg_win_rate) if row.avg_win_rate else None,
                "best_return": float(row.best_return) if row.best_return else None,
                "worst_return": float(row.worst_return) if row.worst_return else None
            })
        
        return {
            "total_strategies": len(performance_summary),
            "performance_summary": performance_summary
        }
        
    except Exception as e:
        logger.error(f"Error getting backtest performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-backtest")
async def run_backtest(
    strategy_name: str,
    symbol: str,
    start_date: date,
    end_date: date,
    initial_capital: float = 100000.0,
    db: Session = Depends(get_db)
):
    """Run a new backtest (placeholder for future implementation)"""
    try:
        # This is a placeholder - in a real implementation, this would:
        # 1. Validate the strategy
        # 2. Run the backtest algorithm
        # 3. Store results in database
        # 4. Return the backtest_id
        
        return {
            "message": "Backtest execution initiated",
            "strategy_name": strategy_name,
            "symbol": symbol,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "initial_capital": initial_capital,
            "status": "PENDING",
            "note": "This is a placeholder endpoint. Full backtesting implementation would be added here."
        }
        
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))