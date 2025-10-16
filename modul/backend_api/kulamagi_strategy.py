"""
API endpoints untuk Christian Kulamagi Trading Strategy
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.kulamagi_strategy_service import KulamagiStrategyService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kulamagi", tags=["Kulamagi Strategy"])

@router.get("/market-condition")
async def check_market_condition(db: Session = Depends(get_db)):
    """
    Check market condition berdasarkan NASDAQ > EMA 10 > EMA 20
    """
    try:
        service = KulamagiStrategyService(db)
        result = await service.check_market_condition()
        return result
    except Exception as e:
        logger.error(f"Error checking market condition: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/momentum-stocks")
async def screen_momentum_stocks(
    min_performance_1m: float = Query(0.20, description="Minimum 1 month performance"),
    min_performance_3m: float = Query(0.30, description="Minimum 3 months performance"),
    min_performance_6m: float = Query(0.50, description="Minimum 6 months performance"),
    db: Session = Depends(get_db)
):
    """
    Screen stocks dengan momentum kuat berdasarkan performance 1M, 3M, 6M
    """
    try:
        service = KulamagiStrategyService(db)
        result = await service.screen_momentum_stocks(
            min_performance_1m, min_performance_3m, min_performance_6m
        )
        return {
            "momentum_stocks": result,
            "count": len(result),
            "criteria": {
                "min_1m": min_performance_1m,
                "min_3m": min_performance_3m,
                "min_6m": min_performance_6m
            }
        }
    except Exception as e:
        logger.error(f"Error screening momentum stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/breakout-setup/{symbol}")
async def analyze_breakout_setup(symbol: str, db: Session = Depends(get_db)):
    """
    Analyze breakout setup untuk saham tertentu
    """
    try:
        service = KulamagiStrategyService(db)
        result = await service.analyze_breakout_setup(symbol)
        return result
    except Exception as e:
        logger.error(f"Error analyzing breakout setup for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/position-size")
async def calculate_position_size(
    portfolio_id: int,
    symbol: str,
    entry_price: float,
    stop_loss: float,
    db: Session = Depends(get_db)
):
    """
    Calculate position size berdasarkan risk per trade (0.25%-1%)
    """
    try:
        service = KulamagiStrategyService(db)
        result = await service.calculate_position_size(
            portfolio_id, symbol, entry_price, stop_loss
        )
        return result
    except Exception as e:
        logger.error(f"Error calculating position size: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trading-signals/{portfolio_id}")
async def generate_trading_signals(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Generate trading signals berdasarkan strategi Kulamagi
    """
    try:
        service = KulamagiStrategyService(db)
        result = await service.generate_trading_signals(portfolio_id)
        return {
            "signals": result,
            "count": len(result),
            "strategy": "Christian Kulamagi Momentum Breakout"
        }
    except Exception as e:
        logger.error(f"Error generating trading signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exit-strategy/{position_id}")
async def manage_exit_strategy(position_id: int, db: Session = Depends(get_db)):
    """
    Manage exit strategy dengan trailing stop berdasarkan EMA 10/20
    """
    try:
        from app.models.trading import Position
        
        position = db.query(Position).filter(Position.id == position_id).first()
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        service = KulamagiStrategyService(db)
        result = await service.manage_exit_strategy(position)
        return result
    except Exception as e:
        logger.error(f"Error managing exit strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategy-overview")
async def get_strategy_overview(db: Session = Depends(get_db)):
    """
    Get overview of Kulamagi strategy implementation
    """
    try:
        service = KulamagiStrategyService(db)
        
        # Check market condition
        market_condition = await service.check_market_condition()
        
        # Get momentum stocks
        momentum_stocks = await service.screen_momentum_stocks()
        
        return {
            "strategy_name": "Christian Kulamagi Momentum Breakout Strategy",
            "description": "Strategy that turned $5,000 into $100+ million with 30% win rate",
            "key_components": {
                "market_filter": "NASDAQ > EMA 10 > EMA 20",
                "momentum_screener": "1M, 3M, 6M performance filter",
                "breakout_strategy": "Momentum leg -> Consolidation -> Breakout",
                "position_sizing": "0.25%-1% risk per trade",
                "exit_strategy": "Trailing stop based on EMA 10/20"
            },
            "current_market_condition": market_condition,
            "momentum_stocks_count": len(momentum_stocks),
            "top_momentum_stocks": momentum_stocks[:5] if momentum_stocks else []
        }
    except Exception as e:
        logger.error(f"Error getting strategy overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
