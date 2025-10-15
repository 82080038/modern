"""
Strategy Builder API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.services.strategy_builder_service import StrategyBuilderService
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/strategy-builder", tags=["Strategy Builder"])

# Pydantic schemas
class StrategyRule(BaseModel):
    type: str
    condition: str
    action: str
    parameters: dict = {}
    order: int = 0

class StrategyCreate(BaseModel):
    name: str
    description: str = ""
    strategy_type: str = "custom"
    rules: List[StrategyRule]

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    strategy_type: Optional[str] = None
    rules: Optional[List[StrategyRule]] = None

class StrategyResponse(BaseModel):
    id: int
    name: str
    description: str
    strategy_type: str
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    rules: List[dict]

class StrategyListResponse(BaseModel):
    strategies: List[dict]
    total: int

class BacktestParams(BaseModel):
    start_date: str
    end_date: str
    initial_capital: float = 100000
    symbol: str = "AAPL"

class BacktestResponse(BaseModel):
    success: bool
    backtest_id: int
    results: dict

class StrategyTemplate(BaseModel):
    id: str
    name: str
    description: str
    strategy_type: str
    rules: List[dict]

@router.post("/strategies", response_model=dict)
async def create_strategy(
    strategy: StrategyCreate,
    db: Session = Depends(get_db)
):
    """Create new trading strategy"""
    try:
        service = StrategyBuilderService(db)
        
        # Convert Pydantic model to dict
        strategy_data = {
            "name": strategy.name,
            "description": strategy.description,
            "strategy_type": strategy.strategy_type,
            "rules": [rule.dict() for rule in strategy.rules]
        }
        
        result = service.create_strategy(strategy_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get strategy by ID"""
    try:
        service = StrategyBuilderService(db)
        result = service.get_strategy(strategy_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return StrategyResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies", response_model=StrategyListResponse)
async def list_strategies(
    strategy_type: Optional[str] = Query(None, description="Filter by strategy type"),
    db: Session = Depends(get_db)
):
    """List all strategies"""
    try:
        service = StrategyBuilderService(db)
        result = service.list_strategies(strategy_type)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StrategyListResponse(**result)
        
    except Exception as e:
        logger.error(f"Error listing strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/strategies/{strategy_id}", response_model=dict)
async def update_strategy(
    strategy_id: int,
    strategy: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """Update strategy"""
    try:
        service = StrategyBuilderService(db)
        
        # Convert Pydantic model to dict
        strategy_data = {}
        if strategy.name is not None:
            strategy_data["name"] = strategy.name
        if strategy.description is not None:
            strategy_data["description"] = strategy.description
        if strategy.strategy_type is not None:
            strategy_data["strategy_type"] = strategy.strategy_type
        if strategy.rules is not None:
            strategy_data["rules"] = [rule.dict() for rule in strategy.rules]
        
        result = service.update_strategy(strategy_id, strategy_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/strategies/{strategy_id}", response_model=dict)
async def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Delete strategy"""
    try:
        service = StrategyBuilderService(db)
        result = service.delete_strategy(strategy_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error deleting strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/{strategy_id}/backtest", response_model=BacktestResponse)
async def backtest_strategy(
    strategy_id: int,
    backtest_params: BacktestParams,
    db: Session = Depends(get_db)
):
    """Backtest strategy"""
    try:
        service = StrategyBuilderService(db)
        
        # Convert dates
        start_date = datetime.fromisoformat(backtest_params.start_date)
        end_date = datetime.fromisoformat(backtest_params.end_date)
        
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": backtest_params.initial_capital,
            "symbol": backtest_params.symbol
        }
        
        result = service.backtest_strategy(strategy_id, params)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return BacktestResponse(**result)
        
    except Exception as e:
        logger.error(f"Error backtesting strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=dict)
async def get_strategy_templates(
    db: Session = Depends(get_db)
):
    """Get predefined strategy templates"""
    try:
        service = StrategyBuilderService(db)
        result = service.get_strategy_templates()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting strategy templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/{strategy_id}/activate", response_model=dict)
async def activate_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Activate strategy"""
    try:
        from app.models.trading import Strategy
        
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        strategy.is_active = True
        strategy.updated_at = datetime.now()
        db.commit()
        
        return {"success": True, "message": "Strategy activated successfully"}
        
    except Exception as e:
        logger.error(f"Error activating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/{strategy_id}/deactivate", response_model=dict)
async def deactivate_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Deactivate strategy"""
    try:
        from app.models.trading import Strategy
        
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        strategy.is_active = False
        strategy.updated_at = datetime.now()
        db.commit()
        
        return {"success": True, "message": "Strategy deactivated successfully"}
        
    except Exception as e:
        logger.error(f"Error deactivating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/{strategy_id}/backtests")
async def get_strategy_backtests(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get strategy backtest results"""
    try:
        from app.models.trading import StrategyBacktest
        
        backtests = db.query(StrategyBacktest).filter(
            StrategyBacktest.strategy_id == strategy_id
        ).order_by(StrategyBacktest.created_at.desc()).all()
        
        backtest_data = []
        for backtest in backtests:
            backtest_data.append({
                "id": backtest.id,
                "start_date": backtest.start_date.isoformat(),
                "end_date": backtest.end_date.isoformat(),
                "initial_capital": backtest.initial_capital,
                "final_capital": backtest.final_capital,
                "total_return": backtest.total_return,
                "sharpe_ratio": backtest.sharpe_ratio,
                "max_drawdown": backtest.max_drawdown,
                "win_rate": backtest.win_rate,
                "total_trades": backtest.total_trades,
                "created_at": backtest.created_at.isoformat()
            })
        
        return {
            "strategy_id": strategy_id,
            "backtests": backtest_data,
            "total": len(backtest_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting strategy backtests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators")
async def get_available_indicators():
    """Get available technical indicators"""
    try:
        indicators = [
            {
                "name": "Moving Average",
                "type": "trend",
                "parameters": ["period"],
                "description": "Simple moving average"
            },
            {
                "name": "RSI",
                "type": "momentum",
                "parameters": ["period"],
                "description": "Relative Strength Index"
            },
            {
                "name": "MACD",
                "type": "trend",
                "parameters": ["fast_period", "slow_period", "signal_period"],
                "description": "Moving Average Convergence Divergence"
            },
            {
                "name": "Bollinger Bands",
                "type": "volatility",
                "parameters": ["period", "std_dev"],
                "description": "Bollinger Bands"
            },
            {
                "name": "Stochastic",
                "type": "momentum",
                "parameters": ["k_period", "d_period"],
                "description": "Stochastic Oscillator"
            },
            {
                "name": "Williams %R",
                "type": "momentum",
                "parameters": ["period"],
                "description": "Williams %R"
            },
            {
                "name": "CCI",
                "type": "momentum",
                "parameters": ["period"],
                "description": "Commodity Channel Index"
            },
            {
                "name": "ATR",
                "type": "volatility",
                "parameters": ["period"],
                "description": "Average True Range"
            }
        ]
        
        return {
            "indicators": indicators,
            "total": len(indicators)
        }
        
    except Exception as e:
        logger.error(f"Error getting indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))
