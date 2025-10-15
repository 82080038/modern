"""
Performance Analytics API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.services.performance_analytics_service import PerformanceAnalyticsService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/performance", tags=["Performance Analytics"])

# Pydantic schemas
class PerformanceMetricsResponse(BaseModel):
    portfolio_id: int
    period: dict
    risk_metrics: dict
    trade_metrics: dict
    var_metrics: dict
    cvar: float
    total_trades: int
    total_pnl: float

class RiskMetricsResponse(BaseModel):
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    recovery_time: int

class TradeMetricsResponse(BaseModel):
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    profit_factor: float
    expectancy: float

class VaRMetricsResponse(BaseModel):
    var_1d: float
    var_1w: float
    var_1m: float
    parametric_var_1d: float
    confidence_level: float

@router.get("/metrics/{portfolio_id}", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    portfolio_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get comprehensive performance metrics untuk portfolio"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
        
        service = PerformanceAnalyticsService(db)
        result = service.get_comprehensive_performance_metrics(portfolio_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return PerformanceMetricsResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-metrics/{portfolio_id}", response_model=RiskMetricsResponse)
async def get_risk_metrics(
    portfolio_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get risk metrics untuk portfolio"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
        
        service = PerformanceAnalyticsService(db)
        result = service.get_comprehensive_performance_metrics(portfolio_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return RiskMetricsResponse(**result["risk_metrics"])
        
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trade-metrics/{portfolio_id}", response_model=TradeMetricsResponse)
async def get_trade_metrics(
    portfolio_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get trade metrics untuk portfolio"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
        
        service = PerformanceAnalyticsService(db)
        result = service.get_comprehensive_performance_metrics(portfolio_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return TradeMetricsResponse(**result["trade_metrics"])
        
    except Exception as e:
        logger.error(f"Error getting trade metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/var-metrics/{portfolio_id}", response_model=VaRMetricsResponse)
async def get_var_metrics(
    portfolio_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(30, description="Number of days to look back"),
    confidence_level: float = Query(0.05, description="Confidence level for VaR"),
    db: Session = Depends(get_db)
):
    """Get Value at Risk metrics untuk portfolio"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
        
        service = PerformanceAnalyticsService(db)
        result = service.get_comprehensive_performance_metrics(portfolio_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return VaRMetricsResponse(**result["var_metrics"])
        
    except Exception as e:
        logger.error(f"Error getting VaR metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/benchmark-comparison/{portfolio_id}")
async def get_benchmark_comparison(
    portfolio_id: int,
    benchmark_symbol: str = Query("^JKSE", description="Benchmark symbol (default: IDX Composite)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    days: Optional[int] = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Compare portfolio performance dengan benchmark"""
    try:
        # Parse dates
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
        
        service = PerformanceAnalyticsService(db)
        
        # Get portfolio performance
        portfolio_result = service.get_comprehensive_performance_metrics(portfolio_id, start_dt, end_dt)
        
        if "error" in portfolio_result:
            raise HTTPException(status_code=400, detail=portfolio_result["error"])
        
        # TODO: Implement benchmark data fetching
        # For now, return portfolio metrics with benchmark comparison placeholder
        return {
            "portfolio_metrics": portfolio_result,
            "benchmark_symbol": benchmark_symbol,
            "comparison": {
                "outperformance": "To be implemented",
                "correlation": "To be implemented",
                "beta": "To be implemented"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting benchmark comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-summary/{portfolio_id}")
async def get_performance_summary(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """Get performance summary untuk portfolio"""
    try:
        service = PerformanceAnalyticsService(db)
        
        # Get metrics for different periods
        periods = {
            "1_week": 7,
            "1_month": 30,
            "3_months": 90,
            "6_months": 180,
            "1_year": 365
        }
        
        summary = {}
        for period_name, days in periods.items():
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=days)
            
            result = service.get_comprehensive_performance_metrics(portfolio_id, start_dt, end_dt)
            if "error" not in result:
                summary[period_name] = {
                    "sharpe_ratio": result["risk_metrics"]["sharpe_ratio"],
                    "max_drawdown": result["risk_metrics"]["max_drawdown"],
                    "win_rate": result["trade_metrics"]["win_rate"],
                    "total_pnl": result["total_pnl"]
                }
        
        return {
            "portfolio_id": portfolio_id,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
