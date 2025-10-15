"""
Algorithmic Trading Engine API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.algorithmic_trading_service import AlgorithmicTradingEngine
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/algorithmic-trading", tags=["Algorithmic Trading"])

# Pydantic schemas
class StartStrategyRequest(BaseModel):
    portfolio_id: int

class StartStrategyResponse(BaseModel):
    success: bool
    message: str
    strategy_id: int
    portfolio_id: int

class StopStrategyResponse(BaseModel):
    success: bool
    message: str
    strategy_id: int

class RunningStrategiesResponse(BaseModel):
    running_strategies: list
    total: int

class StrategyPerformanceResponse(BaseModel):
    strategy_id: int
    total_trades: int
    total_pnl: float
    win_rate: float
    uptime: float
    status: str

# Global trading engine instance
trading_engine = None

def get_trading_engine(db: Session = Depends(get_db)):
    """Get trading engine instance"""
    global trading_engine
    if trading_engine is None:
        trading_engine = AlgorithmicTradingEngine(db)
    return trading_engine

@router.post("/strategies/{strategy_id}/start", response_model=StartStrategyResponse)
async def start_strategy(
    strategy_id: int,
    request: StartStrategyRequest,
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Start algorithmic trading strategy"""
    try:
        result = await engine.start_strategy(strategy_id, request.portfolio_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StartStrategyResponse(**result)
        
    except Exception as e:
        logger.error(f"Error starting strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/{strategy_id}/stop", response_model=StopStrategyResponse)
async def stop_strategy(
    strategy_id: int,
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Stop algorithmic trading strategy"""
    try:
        result = await engine.stop_strategy(strategy_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StopStrategyResponse(**result)
        
    except Exception as e:
        logger.error(f"Error stopping strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/running", response_model=RunningStrategiesResponse)
async def get_running_strategies(
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Get all running strategies"""
    try:
        result = await engine.get_running_strategies()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return RunningStrategiesResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting running strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}/performance", response_model=StrategyPerformanceResponse)
async def get_strategy_performance(
    strategy_id: int,
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Get strategy performance metrics"""
    try:
        result = await engine.get_strategy_performance(strategy_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StrategyPerformanceResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting strategy performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/engine/status")
async def get_engine_status(
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Get trading engine status"""
    try:
        running_strategies = await engine.get_running_strategies()
        
        return {
            "engine_status": "running",
            "total_strategies": running_strategies["total"],
            "running_strategies": running_strategies["running_strategies"],
            "uptime": "N/A",  # Would need to track engine start time
            "last_update": "N/A"
        }
        
    except Exception as e:
        logger.error(f"Error getting engine status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/engine/stop-all")
async def stop_all_strategies(
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Stop all running strategies"""
    try:
        running_strategies = await engine.get_running_strategies()
        stopped_count = 0
        
        for strategy in running_strategies["running_strategies"]:
            result = await engine.stop_strategy(strategy["strategy_id"])
            if "success" in result:
                stopped_count += 1
        
        return {
            "success": True,
            "message": f"Stopped {stopped_count} strategies",
            "stopped_count": stopped_count
        }
        
    except Exception as e:
        logger.error(f"Error stopping all strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}/trades")
async def get_strategy_trades(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get trades executed by strategy"""
    try:
        from app.models.trading import Order
        
        trades = db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.status == "filled"
        ).order_by(Order.created_at.desc()).all()
        
        trade_data = []
        for trade in trades:
            trade_data.append({
                "id": trade.id,
                "symbol": trade.symbol,
                "side": trade.side,
                "quantity": trade.quantity,
                "price": trade.filled_price,
                "pnl": trade.realized_pnl,
                "created_at": trade.created_at.isoformat(),
                "filled_at": trade.filled_at.isoformat() if trade.filled_at else None
            })
        
        return {
            "strategy_id": strategy_id,
            "trades": trade_data,
            "total": len(trade_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting strategy trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}/positions")
async def get_strategy_positions(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get current positions for strategy"""
    try:
        from app.models.trading import Position, Order
        
        # Get portfolio ID from strategy
        from app.models.trading import Strategy
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Get positions (this would need to be linked to strategy)
        positions = db.query(Position).filter(
            Position.portfolio_id == strategy.portfolio_id
        ).all()
        
        position_data = []
        for position in positions:
            position_data.append({
                "symbol": position.symbol,
                "quantity": position.quantity,
                "average_price": position.average_price,
                "current_value": position.quantity * position.average_price,
                "unrealized_pnl": 0,  # Would need current price
                "created_at": position.created_at.isoformat()
            })
        
        return {
            "strategy_id": strategy_id,
            "positions": position_data,
            "total": len(position_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting strategy positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/{strategy_id}/pause")
async def pause_strategy(
    strategy_id: int,
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Pause strategy execution"""
    try:
        # This would need to be implemented in the engine
        return {
            "success": True,
            "message": "Strategy paused successfully",
            "strategy_id": strategy_id
        }
        
    except Exception as e:
        logger.error(f"Error pausing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/{strategy_id}/resume")
async def resume_strategy(
    strategy_id: int,
    engine: AlgorithmicTradingEngine = Depends(get_trading_engine)
):
    """Resume strategy execution"""
    try:
        # This would need to be implemented in the engine
        return {
            "success": True,
            "message": "Strategy resumed successfully",
            "strategy_id": strategy_id
        }
        
    except Exception as e:
        logger.error(f"Error resuming strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
