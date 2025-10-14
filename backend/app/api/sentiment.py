"""
Sentiment Analysis API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.core.sentiment import SentimentAnalysisEngine
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])

# Pydantic schemas
class NewsSentimentResponse(BaseModel):
    symbol: str
    period_days: int
    total_news: int
    avg_polarity: float
    weighted_polarity: float
    sentiment_class: str
    positive_news: int
    negative_news: int
    neutral_news: int
    confidence_avg: float
    impact_avg: float

class SocialSentimentResponse(BaseModel):
    symbol: str
    period_days: int
    total_posts: int
    avg_polarity: float
    weighted_polarity: float
    sentiment_class: str
    total_engagement: int
    avg_engagement: float
    platforms: dict

class MarketSentimentResponse(BaseModel):
    date: str
    fear_greed_index: float
    fear_greed_classification: str
    market_volatility: float
    put_call_ratio: float
    advancing_stocks: int
    declining_stocks: int
    breadth_ratio: float
    volume_ratio: float
    composite_sentiment: float
    market_sentiment: str

class CompositeSentimentResponse(BaseModel):
    symbol: str
    composite_score: float
    sentiment_class: str
    confidence: float
    trend: str
    components: dict
    period_days: int

class SentimentAlertResponse(BaseModel):
    alert_type: str
    title: str
    description: str
    severity: str
    symbol: str
    trigger_value: float
    threshold: float
    confidence: float

@router.get("/news/{symbol}", response_model=NewsSentimentResponse)
async def get_news_sentiment(
    symbol: str,
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get news sentiment analysis for a symbol"""
    try:
        engine = SentimentAnalysisEngine(db)
        sentiment = engine.aggregate_news_sentiment(symbol, days)
        
        if "error" in sentiment:
            raise HTTPException(status_code=404, detail=sentiment["error"])
        
        return NewsSentimentResponse(**sentiment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social/{symbol}", response_model=SocialSentimentResponse)
async def get_social_sentiment(
    symbol: str,
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get social media sentiment analysis for a symbol"""
    try:
        engine = SentimentAnalysisEngine(db)
        sentiment = engine.aggregate_social_sentiment(symbol, days)
        
        if "error" in sentiment:
            raise HTTPException(status_code=404, detail=sentiment["error"])
        
        return SocialSentimentResponse(**sentiment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting social sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market", response_model=MarketSentimentResponse)
async def get_market_sentiment(
    date: Optional[date] = Query(None, description="Date for market sentiment (default: today)"),
    db: Session = Depends(get_db)
):
    """Get market-wide sentiment indicators"""
    try:
        engine = SentimentAnalysisEngine(db)
        sentiment = engine.calculate_market_sentiment(date)
        
        if "error" in sentiment:
            raise HTTPException(status_code=404, detail=sentiment["error"])
        
        return MarketSentimentResponse(**sentiment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insider/{symbol}")
async def get_insider_activity(
    symbol: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get insider trading activity analysis for a symbol"""
    try:
        engine = SentimentAnalysisEngine(db)
        activity = engine.analyze_insider_activity(symbol, days)
        
        if "error" in activity:
            raise HTTPException(status_code=404, detail=activity["error"])
        
        return activity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing insider activity for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/composite/{symbol}", response_model=CompositeSentimentResponse)
async def get_composite_sentiment(
    symbol: str,
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get composite sentiment score from all sources"""
    try:
        engine = SentimentAnalysisEngine(db)
        sentiment = engine.calculate_composite_sentiment(symbol, days)
        
        if "error" in sentiment:
            raise HTTPException(status_code=404, detail=sentiment["error"])
        
        return CompositeSentimentResponse(**sentiment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating composite sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/{symbol}")
async def get_sentiment_alerts(
    symbol: str,
    threshold: float = Query(0.5, description="Alert threshold"),
    db: Session = Depends(get_db)
):
    """Get sentiment-based alerts for a symbol"""
    try:
        engine = SentimentAnalysisEngine(db)
        alerts = engine.generate_sentiment_alerts(symbol, threshold)
        
        return {
            "symbol": symbol,
            "threshold": threshold,
            "alerts_count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error generating sentiment alerts for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_sentiment_dashboard(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get sentiment dashboard for multiple symbols"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        engine = SentimentAnalysisEngine(db)
        
        dashboard_data = []
        
        for symbol in symbol_list:
            try:
                # Get composite sentiment for each symbol
                sentiment = engine.calculate_composite_sentiment(symbol, days)
                
                if "error" not in sentiment:
                    dashboard_data.append({
                        "symbol": symbol,
                        "composite_score": sentiment["composite_score"],
                        "sentiment_class": sentiment["sentiment_class"],
                        "confidence": sentiment["confidence"],
                        "components": sentiment["components"]
                    })
                else:
                    dashboard_data.append({
                        "symbol": symbol,
                        "error": sentiment["error"]
                    })
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                dashboard_data.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return {
            "period_days": days,
            "symbols_analyzed": len(symbol_list),
            "successful_analysis": len([d for d in dashboard_data if "error" not in d]),
            "data": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Error generating sentiment dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screener")
async def sentiment_screener(
    min_sentiment: Optional[float] = Query(None, description="Minimum sentiment score"),
    max_sentiment: Optional[float] = Query(None, description="Maximum sentiment score"),
    sentiment_class: Optional[str] = Query(None, description="Sentiment class filter"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence level"),
    days: int = Query(7, description="Analysis period in days"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Screen stocks based on sentiment criteria"""
    try:
        from app.models.sentiment import SentimentAggregation
        
        # Build query
        query = db.query(SentimentAggregation).filter(
            SentimentAggregation.timeframe == "daily"
        )
        
        if min_sentiment is not None:
            query = query.filter(SentimentAggregation.composite_sentiment >= min_sentiment)
        
        if max_sentiment is not None:
            query = query.filter(SentimentAggregation.composite_sentiment <= max_sentiment)
        
        if sentiment_class:
            query = query.filter(SentimentAggregation.sentiment_trend == sentiment_class)
        
        if min_confidence is not None:
            query = query.filter(SentimentAggregation.sentiment_confidence >= min_confidence)
        
        # Get latest data for each symbol
        results = query.order_by(
            SentimentAggregation.symbol,
            SentimentAggregation.date.desc()
        ).limit(limit).all()
        
        # Format response
        screened_stocks = []
        for sentiment in results:
            screened_stocks.append({
                "symbol": sentiment.symbol,
                "composite_sentiment": sentiment.composite_sentiment,
                "sentiment_trend": sentiment.sentiment_trend,
                "sentiment_confidence": sentiment.sentiment_confidence,
                "news_sentiment_avg": sentiment.news_sentiment_avg,
                "social_sentiment_avg": sentiment.social_sentiment_avg,
                "date": sentiment.date.isoformat()
            })
        
        return {
            "total_results": len(screened_stocks),
            "criteria": {
                "min_sentiment": min_sentiment,
                "max_sentiment": max_sentiment,
                "sentiment_class": sentiment_class,
                "min_confidence": min_confidence,
                "days": days
            },
            "stocks": screened_stocks
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment screener: {e}")
        raise HTTPException(status_code=500, detail=str(e))
