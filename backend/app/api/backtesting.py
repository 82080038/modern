"""
Backtesting API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date
from app.database import get_db
from app.services.backtesting_service import BacktestingService
from app.models.backtesting import StrategyType, BacktestStatus
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/backtesting", tags=["Backtesting"])

# Pydantic schemas
class CreateBacktestRequest(BaseModel):
    strategy_name: str
    strategy_type: str  # moving_average, rsi, macd, bollinger_bands, custom
    symbol: str
    timeframe: str
    start_date: date
    end_date: date
    initial_capital: float
    strategy_params: Optional[Dict] = None
    commission_rate: float = 0.001
    slippage_rate: float = 0.0005

class RunBacktestRequest(BaseModel):
    backtest_id: str

class MonteCarloRequest(BaseModel):
    backtest_id: str
    num_simulations: int = 1000

class BacktestResponse(BaseModel):
    backtest_id: str
    strategy_name: str
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
    created_at: str
    completed_at: Optional[str]

@router.post("/create")
async def create_backtest(
    backtest_request: CreateBacktestRequest,
    db: Session = Depends(get_db)
):
    """Create new backtest"""
    try:
        # Validate strategy type
        valid_types = [t.value for t in StrategyType]
        if backtest_request.strategy_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid strategy type. Valid options: {valid_types}")
        
        # Convert to enum
        strategy_type = StrategyType(backtest_request.strategy_type)
        
        # Create backtesting service
        backtesting_service = BacktestingService(db)
        
        # Create backtest
        result = backtesting_service.create_backtest(
            strategy_name=backtest_request.strategy_name,
            strategy_type=strategy_type,
            symbol=backtest_request.symbol,
            timeframe=backtest_request.timeframe,
            start_date=backtest_request.start_date,
            end_date=backtest_request.end_date,
            initial_capital=backtest_request.initial_capital,
            strategy_params=backtest_request.strategy_params,
            commission_rate=backtest_request.commission_rate,
            slippage_rate=backtest_request.slippage_rate
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run")
async def run_backtest(
    run_request: RunBacktestRequest,
    db: Session = Depends(get_db)
):
    """Run backtest execution"""
    try:
        backtesting_service = BacktestingService(db)
        result = backtesting_service.run_backtest(run_request.backtest_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{backtest_id}", response_model=BacktestResponse)
async def get_backtest_results(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Get backtest results"""
    try:
        backtesting_service = BacktestingService(db)
        result = backtesting_service.get_backtest_results(backtest_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return BacktestResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting backtest results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_backtests(
    limit: int = Query(50, description="Maximum number of backtests to return"),
    offset: int = Query(0, description="Number of backtests to skip"),
    db: Session = Depends(get_db)
):
    """List backtests"""
    try:
        backtesting_service = BacktestingService(db)
        backtests = backtesting_service.list_backtests(limit=limit, offset=offset)
        
        return {
            "backtests": backtests,
            "total_count": len(backtests)
        }
        
    except Exception as e:
        logger.error(f"Error listing backtests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monte-carlo")
async def run_monte_carlo_simulation(
    monte_carlo_request: MonteCarloRequest,
    db: Session = Depends(get_db)
):
    """Run Monte Carlo simulation"""
    try:
        backtesting_service = BacktestingService(db)
        result = backtesting_service.run_monte_carlo_simulation(
            backtest_id=monte_carlo_request.backtest_id,
            num_simulations=monte_carlo_request.num_simulations
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running Monte Carlo simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_available_strategies(db: Session = Depends(get_db)):
    """Get available trading strategies"""
    try:
        strategies = [
            {
                "type": "moving_average",
                "name": "Moving Average Crossover",
                "description": "Buy when price crosses above SMA, sell when below",
                "parameters": {
                    "period": {"type": "integer", "default": 20, "min": 5, "max": 100}
                }
            },
            {
                "type": "rsi",
                "name": "RSI Strategy",
                "description": "Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)",
                "parameters": {
                    "period": {"type": "integer", "default": 14, "min": 5, "max": 50},
                    "oversold": {"type": "float", "default": 30, "min": 10, "max": 40},
                    "overbought": {"type": "float", "default": 70, "min": 60, "max": 90}
                }
            },
            {
                "type": "macd",
                "name": "MACD Strategy",
                "description": "Buy when MACD crosses above signal line, sell when below",
                "parameters": {
                    "fast_period": {"type": "integer", "default": 12, "min": 5, "max": 50},
                    "slow_period": {"type": "integer", "default": 26, "min": 10, "max": 100},
                    "signal_period": {"type": "integer", "default": 9, "min": 5, "max": 50}
                }
            },
            {
                "type": "bollinger_bands",
                "name": "Bollinger Bands Strategy",
                "description": "Buy when price touches lower band, sell when touches upper band",
                "parameters": {
                    "period": {"type": "integer", "default": 20, "min": 5, "max": 100},
                    "std_dev": {"type": "float", "default": 2, "min": 1, "max": 3}
                }
            }
        ]
        
        return {
            "strategies": strategies,
            "total_count": len(strategies)
        }
        
    except Exception as e:
        logger.error(f"Error getting available strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-metrics/{backtest_id}")
async def get_performance_metrics(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed performance metrics for a backtest"""
    try:
        backtesting_service = BacktestingService(db)
        result = backtesting_service.get_backtest_results(backtest_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        # Calculate additional metrics
        metrics = {
            "basic_metrics": {
                "total_return": result["total_return"],
                "annualized_return": result["annualized_return"],
                "max_drawdown": result["max_drawdown"],
                "sharpe_ratio": result["sharpe_ratio"],
                "sortino_ratio": result["sortino_ratio"]
            },
            "trade_metrics": {
                "total_trades": result["total_trades"],
                "winning_trades": result["winning_trades"],
                "losing_trades": result["losing_trades"],
                "win_rate": result["win_rate"],
                "profit_factor": result["profit_factor"]
            },
            "risk_metrics": {
                "max_drawdown": result["max_drawdown"],
                "sharpe_ratio": result["sharpe_ratio"],
                "sortino_ratio": result["sortino_ratio"]
            },
            "capital_metrics": {
                "initial_capital": result["initial_capital"],
                "final_capital": result["final_capital"],
                "total_return": result["total_return"]
            }
        }
        
        return {
            "backtest_id": backtest_id,
            "metrics": metrics,
            "status": result["status"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/equity-curve/{backtest_id}")
async def get_equity_curve(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Get equity curve data for a backtest"""
    try:
        from app.models.backtesting import BacktestMetrics
        
        # Get equity curve data
        metrics = db.query(BacktestMetrics).filter(
            BacktestMetrics.backtest_id == backtest_id
        ).order_by(BacktestMetrics.date).all()
        
        if not metrics:
            raise HTTPException(status_code=404, detail="No equity curve data found")
        
        equity_curve = []
        for metric in metrics:
            equity_curve.append({
                "date": metric.date.isoformat(),
                "equity": metric.equity,
                "daily_return": metric.daily_return,
                "cumulative_return": metric.cumulative_return,
                "drawdown": metric.drawdown,
                "max_drawdown": metric.max_drawdown
            })
        
        return {
            "backtest_id": backtest_id,
            "equity_curve": equity_curve,
            "total_points": len(equity_curve)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting equity curve: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades/{backtest_id}")
async def get_backtest_trades(
    backtest_id: str,
    limit: int = Query(100, description="Maximum number of trades to return"),
    offset: int = Query(0, description="Number of trades to skip"),
    db: Session = Depends(get_db)
):
    """Get trades for a backtest"""
    try:
        from app.models.backtesting import BacktestTrade
        
        # Get trades
        trades = db.query(BacktestTrade).filter(
            BacktestTrade.backtest_id == backtest_id
        ).order_by(BacktestTrade.entry_time).offset(offset).limit(limit).all()
        
        trade_list = []
        for trade in trades:
            trade_list.append({
                "trade_id": trade.trade_id,
                "symbol": trade.symbol,
                "side": trade.side,
                "quantity": trade.quantity,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "entry_time": trade.entry_time.isoformat(),
                "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
                "pnl": trade.pnl,
                "pnl_percent": trade.pnl_percent,
                "commission": trade.commission,
                "slippage": trade.slippage,
                "entry_reason": trade.entry_reason,
                "exit_reason": trade.exit_reason,
                "duration_hours": trade.duration_hours
            })
        
        return {
            "backtest_id": backtest_id,
            "trades": trade_list,
            "total_count": len(trade_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting backtest trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparison")
async def compare_backtests(
    backtest_ids: str = Query(..., description="Comma-separated list of backtest IDs"),
    db: Session = Depends(get_db)
):
    """Compare multiple backtests"""
    try:
        backtest_id_list = [id.strip() for id in backtest_ids.split(',')]
        
        backtesting_service = BacktestingService(db)
        comparison_data = []
        
        for backtest_id in backtest_id_list:
            result = backtesting_service.get_backtest_results(backtest_id)
            if "error" not in result:
                comparison_data.append(result)
        
        if not comparison_data:
            raise HTTPException(status_code=404, detail="No valid backtests found")
        
        # Create comparison summary
        comparison_summary = {
            "best_return": max(comparison_data, key=lambda x: x["total_return"]),
            "best_sharpe": max(comparison_data, key=lambda x: x["sharpe_ratio"]),
            "lowest_drawdown": min(comparison_data, key=lambda x: x["max_drawdown"]),
            "most_trades": max(comparison_data, key=lambda x: x["total_trades"])
        }
        
        return {
            "backtests": comparison_data,
            "comparison_summary": comparison_summary,
            "total_compared": len(comparison_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing backtests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{backtest_id}")
async def delete_backtest(
    backtest_id: str,
    db: Session = Depends(get_db)
):
    """Delete a backtest"""
    try:
        from app.models.backtesting import Backtest, BacktestTrade, BacktestMetrics
        
        # Delete related records
        db.query(BacktestTrade).filter(BacktestTrade.backtest_id == backtest_id).delete()
        db.query(BacktestMetrics).filter(BacktestMetrics.backtest_id == backtest_id).delete()
        
        # Delete backtest
        deleted_count = db.query(Backtest).filter(Backtest.backtest_id == backtest_id).delete()
        
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        db.commit()
        
        return {
            "message": "Backtest deleted successfully",
            "backtest_id": backtest_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting backtest: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
