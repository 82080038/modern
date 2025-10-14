"""
Fundamental Analysis API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.core.fundamental import FundamentalAnalysisEngine
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fundamental", tags=["Fundamental Analysis"])

# Pydantic schemas
class FinancialRatiosResponse(BaseModel):
    symbol: str
    period_date: str
    profitability: dict
    liquidity: dict
    leverage: dict
    efficiency: dict
    valuation: dict
    growth: dict

class DCFResponse(BaseModel):
    symbol: str
    intrinsic_value: float
    current_price: float
    margin_of_safety: float
    upside_potential: float
    terminal_growth_rate: float
    discount_rate: float

class FundamentalScoreResponse(BaseModel):
    symbol: str
    fundamental_score: float
    rating: str
    factors: List[str]
    max_possible: int

class PeerComparisonResponse(BaseModel):
    symbol: str
    sector: str
    company_metrics: dict
    sector_averages: dict
    relative_performance: dict
    peer_count: int

@router.get("/ratios/{symbol}", response_model=FinancialRatiosResponse)
async def get_financial_ratios(
    symbol: str,
    period_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get financial ratios for a symbol"""
    try:
        if not period_date:
            period_date = date.today()
        
        engine = FundamentalAnalysisEngine(db)
        ratios = engine.calculate_financial_ratios(symbol, period_date)
        
        if "error" in ratios:
            raise HTTPException(status_code=404, detail=ratios["error"])
        
        # Organize ratios by category
        response = {
            "symbol": symbol,
            "period_date": period_date.isoformat(),
            "profitability": {
                "roe": ratios.get("roe"),
                "roa": ratios.get("roa"),
                "profit_margin": ratios.get("profit_margin"),
                "operating_margin": ratios.get("operating_margin"),
                "gross_margin": ratios.get("gross_margin")
            },
            "liquidity": {
                "current_ratio": ratios.get("current_ratio"),
                "cash_ratio": ratios.get("cash_ratio")
            },
            "leverage": {
                "debt_to_equity": ratios.get("debt_to_equity"),
                "debt_to_assets": ratios.get("debt_to_assets")
            },
            "efficiency": {
                "asset_turnover": ratios.get("asset_turnover")
            },
            "valuation": {},
            "growth": {}
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting financial ratios for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dcf/{symbol}", response_model=DCFResponse)
async def get_dcf_valuation(
    symbol: str,
    current_price: float = Query(..., description="Current stock price"),
    db: Session = Depends(get_db)
):
    """Get DCF valuation for a symbol"""
    try:
        engine = FundamentalAnalysisEngine(db)
        dcf_result = engine.calculate_dcf_valuation(symbol, current_price)
        
        if "error" in dcf_result:
            raise HTTPException(status_code=404, detail=dcf_result["error"])
        
        return DCFResponse(
            symbol=symbol,
            intrinsic_value=dcf_result["intrinsic_value"],
            current_price=dcf_result["current_price"],
            margin_of_safety=dcf_result["margin_of_safety"],
            upside_potential=dcf_result["upside_potential"],
            terminal_growth_rate=dcf_result["terminal_growth_rate"],
            discount_rate=dcf_result["discount_rate"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating DCF for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graham/{symbol}")
async def get_graham_number(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get Graham Number for a symbol"""
    try:
        engine = FundamentalAnalysisEngine(db)
        graham_result = engine.calculate_graham_number(symbol)
        
        if "error" in graham_result:
            raise HTTPException(status_code=404, detail=graham_result["error"])
        
        return graham_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating Graham Number for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/earnings-quality/{symbol}")
async def get_earnings_quality(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get earnings quality analysis for a symbol"""
    try:
        engine = FundamentalAnalysisEngine(db)
        quality_result = engine.analyze_earnings_quality(symbol)
        
        if "error" in quality_result:
            raise HTTPException(status_code=404, detail=quality_result["error"])
        
        return quality_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing earnings quality for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score/{symbol}", response_model=FundamentalScoreResponse)
async def get_fundamental_score(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get overall fundamental score for a symbol"""
    try:
        engine = FundamentalAnalysisEngine(db)
        score_result = engine.get_fundamental_score(symbol)
        
        if "error" in score_result:
            raise HTTPException(status_code=404, detail=score_result["error"])
        
        return FundamentalScoreResponse(
            symbol=symbol,
            fundamental_score=score_result["fundamental_score"],
            rating=score_result["rating"],
            factors=score_result["factors"],
            max_possible=score_result["max_possible"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating fundamental score for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peer-comparison/{symbol}")
async def get_peer_comparison(
    symbol: str,
    sector: str = Query(..., description="Sector for peer comparison"),
    db: Session = Depends(get_db)
):
    """Get peer comparison analysis for a symbol"""
    try:
        engine = FundamentalAnalysisEngine(db)
        comparison_result = engine.get_peer_comparison(symbol, sector)
        
        if "error" in comparison_result:
            raise HTTPException(status_code=404, detail=comparison_result["error"])
        
        return comparison_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in peer comparison for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screener")
async def fundamental_screener(
    min_roe: Optional[float] = Query(None, description="Minimum ROE %"),
    max_pe: Optional[float] = Query(None, description="Maximum PE ratio"),
    min_profit_margin: Optional[float] = Query(None, description="Minimum profit margin %"),
    max_debt_equity: Optional[float] = Query(None, description="Maximum debt-to-equity ratio"),
    min_current_ratio: Optional[float] = Query(None, description="Minimum current ratio"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Screen stocks based on fundamental criteria"""
    try:
        from app.models.fundamental import FinancialRatios, CompanyProfile
        
        # Build query
        query = db.query(FinancialRatios).join(CompanyProfile)
        
        if sector:
            query = query.filter(CompanyProfile.sector == sector)
        
        if min_roe is not None:
            query = query.filter(FinancialRatios.roe >= min_roe)
        
        if max_pe is not None:
            query = query.filter(FinancialRatios.pe_ratio <= max_pe)
        
        if min_profit_margin is not None:
            query = query.filter(FinancialRatios.profit_margin >= min_profit_margin)
        
        if max_debt_equity is not None:
            query = query.filter(FinancialRatios.debt_to_equity <= max_debt_equity)
        
        if min_current_ratio is not None:
            query = query.filter(FinancialRatios.current_ratio >= min_current_ratio)
        
        # Get results
        results = query.limit(limit).all()
        
        # Format response
        screened_stocks = []
        for ratio in results:
            screened_stocks.append({
                "symbol": ratio.symbol,
                "roe": ratio.roe,
                "pe_ratio": ratio.pe_ratio,
                "profit_margin": ratio.profit_margin,
                "debt_to_equity": ratio.debt_to_equity,
                "current_ratio": ratio.current_ratio,
                "period_date": ratio.period_date.isoformat()
            })
        
        return {
            "total_results": len(screened_stocks),
            "criteria": {
                "min_roe": min_roe,
                "max_pe": max_pe,
                "min_profit_margin": min_profit_margin,
                "max_debt_equity": max_debt_equity,
                "min_current_ratio": min_current_ratio,
                "sector": sector
            },
            "stocks": screened_stocks
        }
        
    except Exception as e:
        logger.error(f"Error in fundamental screener: {e}")
        raise HTTPException(status_code=500, detail=str(e))
