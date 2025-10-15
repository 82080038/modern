"""
Technical Analysis API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models.market_data import TechnicalIndicators
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/technical", tags=["Technical Analysis"])

# Pydantic schemas
class TechnicalIndicatorsResponse(BaseModel):
    symbol: str
    date: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    williams_r: Optional[float] = None
    cci: Optional[float] = None
    obv: Optional[int] = None
    trend: Optional[str] = None
    ai_pattern_strength: Optional[float] = None
    ai_gap_accuracy: Optional[float] = None
    ai_order_book_efficiency: Optional[float] = None
    ai_mean_reversion_score: Optional[float] = None
    ai_overall_score: Optional[float] = None

class TechnicalSummaryResponse(BaseModel):
    symbol: str
    trend: str
    momentum: str
    volatility: str
    volume: str
    ai_score: float
    recommendation: str
    confidence: float

@router.get("/indicators/{symbol}")
async def get_technical_indicators(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date for indicators"),
    end_date: Optional[date] = Query(None, description="End date for indicators"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get technical indicators for a symbol"""
    try:
        query = db.query(TechnicalIndicators).filter(TechnicalIndicators.symbol == symbol)
        
        if start_date:
            query = query.filter(TechnicalIndicators.date >= start_date)
        if end_date:
            query = query.filter(TechnicalIndicators.date <= end_date)
        
        indicators = query.order_by(TechnicalIndicators.date.desc()).limit(limit).all()
        
        if not indicators:
            raise HTTPException(status_code=404, detail="No technical indicators found for symbol")
        
        results = []
        for indicator in indicators:
            results.append({
                "symbol": indicator.symbol,
                "date": indicator.date.isoformat(),
                "rsi": float(indicator.rsi) if indicator.rsi else None,
                "macd": float(indicator.macd) if indicator.macd else None,
                "macd_signal": float(indicator.macd_signal) if indicator.macd_signal else None,
                "macd_histogram": float(indicator.macd_histogram) if indicator.macd_histogram else None,
                "sma_20": float(indicator.sma_20) if indicator.sma_20 else None,
                "sma_50": float(indicator.sma_50) if indicator.sma_50 else None,
                "sma_200": float(indicator.sma_200) if indicator.sma_200 else None,
                "ema_12": float(indicator.ema_12) if indicator.ema_12 else None,
                "ema_26": float(indicator.ema_26) if indicator.ema_26 else None,
                "bollinger_upper": float(indicator.bollinger_upper) if indicator.bollinger_upper else None,
                "bollinger_middle": float(indicator.bollinger_middle) if indicator.bollinger_middle else None,
                "bollinger_lower": float(indicator.bollinger_lower) if indicator.bollinger_lower else None,
                "atr": float(indicator.atr) if indicator.atr else None,
                "adx": float(indicator.adx) if indicator.adx else None,
                "stochastic_k": float(indicator.stochastic_k) if indicator.stochastic_k else None,
                "stochastic_d": float(indicator.stochastic_d) if indicator.stochastic_d else None,
                "williams_r": float(indicator.williams_r) if indicator.williams_r else None,
                "cci": float(indicator.cci) if indicator.cci else None,
                "obv": int(indicator.obv) if indicator.obv else None,
                "trend": indicator.trend,
                "ai_pattern_strength": float(indicator.ai_pattern_strength) if indicator.ai_pattern_strength else None,
                "ai_gap_accuracy": float(indicator.ai_gap_accuracy) if indicator.ai_gap_accuracy else None,
                "ai_order_book_efficiency": float(indicator.ai_order_book_efficiency) if indicator.ai_order_book_efficiency else None,
                "ai_mean_reversion_score": float(indicator.ai_mean_reversion_score) if indicator.ai_mean_reversion_score else None,
                "ai_overall_score": float(indicator.ai_overall_score) if indicator.ai_overall_score else None
            })
        
        return {
            "symbol": symbol,
            "total_indicators": len(results),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "indicators": results
        }
        
    except Exception as e:
        logger.error(f"Error getting technical indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{symbol}")
async def get_technical_summary(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get technical analysis summary for a symbol"""
    try:
        # Get latest technical indicators
        latest = db.query(TechnicalIndicators).filter(
            TechnicalIndicators.symbol == symbol
        ).order_by(TechnicalIndicators.date.desc()).first()
        
        if not latest:
            raise HTTPException(status_code=404, detail="No technical data found for symbol")
        
        # Analyze trend
        trend = "NEUTRAL"
        if latest.sma_20 and latest.sma_50 and latest.sma_200:
            if latest.sma_20 > latest.sma_50 > latest.sma_200:
                trend = "BULLISH"
            elif latest.sma_20 < latest.sma_50 < latest.sma_200:
                trend = "BEARISH"
        
        # Analyze momentum
        momentum = "NEUTRAL"
        if latest.rsi:
            if latest.rsi > 70:
                momentum = "OVERBOUGHT"
            elif latest.rsi < 30:
                momentum = "OVERSOLD"
        
        # Analyze volatility
        volatility = "NORMAL"
        if latest.atr and latest.bollinger_upper and latest.bollinger_lower:
            bb_width = (latest.bollinger_upper - latest.bollinger_lower) / latest.bollinger_middle
            if bb_width > 0.1:
                volatility = "HIGH"
            elif bb_width < 0.05:
                volatility = "LOW"
        
        # Analyze volume
        volume = "NORMAL"
        if latest.obv and latest.volume_sma:
            if latest.obv > latest.volume_sma * 1.5:
                volume = "HIGH"
            elif latest.obv < latest.volume_sma * 0.5:
                volume = "LOW"
        
        # AI Score
        ai_score = 0.0
        if latest.ai_overall_score:
            ai_score = float(latest.ai_overall_score)
        
        # Generate recommendation
        recommendation = "HOLD"
        confidence = 0.5
        
        if trend == "BULLISH" and momentum == "OVERSOLD" and ai_score > 0.7:
            recommendation = "BUY"
            confidence = 0.8
        elif trend == "BEARISH" and momentum == "OVERBOUGHT" and ai_score < 0.3:
            recommendation = "SELL"
            confidence = 0.8
        elif ai_score > 0.6:
            recommendation = "BUY"
            confidence = 0.7
        elif ai_score < 0.4:
            recommendation = "SELL"
            confidence = 0.7
        
        return {
            "symbol": symbol,
            "date": latest.date.isoformat(),
            "trend": trend,
            "momentum": momentum,
            "volatility": volatility,
            "volume": volume,
            "ai_score": ai_score,
            "recommendation": recommendation,
            "confidence": confidence,
            "indicators": {
                "rsi": float(latest.rsi) if latest.rsi else None,
                "macd": float(latest.macd) if latest.macd else None,
                "sma_20": float(latest.sma_20) if latest.sma_20 else None,
                "sma_50": float(latest.sma_50) if latest.sma_50 else None,
                "sma_200": float(latest.sma_200) if latest.sma_200 else None,
                "bollinger_upper": float(latest.bollinger_upper) if latest.bollinger_upper else None,
                "bollinger_lower": float(latest.bollinger_lower) if latest.bollinger_lower else None,
                "atr": float(latest.atr) if latest.atr else None,
                "adx": float(latest.adx) if latest.adx else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting technical summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screener")
async def technical_screener(
    min_rsi: Optional[float] = Query(None, description="Minimum RSI"),
    max_rsi: Optional[float] = Query(None, description="Maximum RSI"),
    trend: Optional[str] = Query(None, description="Trend filter (BULLISH, BEARISH, NEUTRAL)"),
    min_ai_score: Optional[float] = Query(None, description="Minimum AI score"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Screen stocks based on technical criteria"""
    try:
        query = db.query(TechnicalIndicators).filter(
            TechnicalIndicators.date == db.query(TechnicalIndicators.date).filter(
                TechnicalIndicators.symbol == TechnicalIndicators.symbol
            ).order_by(TechnicalIndicators.date.desc()).limit(1).subquery().c.date
        )
        
        if min_rsi is not None:
            query = query.filter(TechnicalIndicators.rsi >= min_rsi)
        if max_rsi is not None:
            query = query.filter(TechnicalIndicators.rsi <= max_rsi)
        if trend:
            query = query.filter(TechnicalIndicators.trend == trend)
        if min_ai_score is not None:
            query = query.filter(TechnicalIndicators.ai_overall_score >= min_ai_score)
        
        results = query.order_by(TechnicalIndicators.ai_overall_score.desc()).limit(limit).all()
        
        screened_stocks = []
        for result in results:
            screened_stocks.append({
                "symbol": result.symbol,
                "date": result.date.isoformat(),
                "rsi": float(result.rsi) if result.rsi else None,
                "macd": float(result.macd) if result.macd else None,
                "sma_20": float(result.sma_20) if result.sma_20 else None,
                "sma_50": float(result.sma_50) if result.sma_50 else None,
                "trend": result.trend,
                "ai_score": float(result.ai_overall_score) if result.ai_overall_score else None,
                "ai_pattern_strength": float(result.ai_pattern_strength) if result.ai_pattern_strength else None
            })
        
        return {
            "total_results": len(screened_stocks),
            "criteria": {
                "min_rsi": min_rsi,
                "max_rsi": max_rsi,
                "trend": trend,
                "min_ai_score": min_ai_score
            },
            "stocks": screened_stocks
        }
        
    except Exception as e:
        logger.error(f"Error in technical screener: {e}")
        raise HTTPException(status_code=500, detail=str(e))
