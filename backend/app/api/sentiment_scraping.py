"""
Sentiment Scraping API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.database import get_db
from app.services.sentiment_scraping_service import SentimentScrapingService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sentiment-scraping", tags=["Sentiment Scraping"])

# Pydantic schemas
class ScrapeRedditRequest(BaseModel):
    symbol: str
    subreddits: Optional[List[str]] = None
    limit: int = 100

class ScrapeTwitterRequest(BaseModel):
    symbol: str
    limit: int = 100

class ScrapeNewsRequest(BaseModel):
    symbol: str
    limit: int = 50

@router.post("/reddit")
async def scrape_reddit_sentiment(
    reddit_request: ScrapeRedditRequest,
    db: Session = Depends(get_db)
):
    """Scrape Reddit sentiment for a symbol"""
    try:
        sentiment_service = SentimentScrapingService(db)
        result = sentiment_service.scrape_reddit_sentiment(
            symbol=reddit_request.symbol,
            subreddits=reddit_request.subreddits,
            limit=reddit_request.limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping Reddit sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twitter")
async def scrape_twitter_sentiment(
    twitter_request: ScrapeTwitterRequest,
    db: Session = Depends(get_db)
):
    """Scrape Twitter sentiment for a symbol"""
    try:
        sentiment_service = SentimentScrapingService(db)
        result = sentiment_service.scrape_twitter_sentiment(
            symbol=twitter_request.symbol,
            limit=twitter_request.limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping Twitter sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/news")
async def scrape_news_sentiment(
    news_request: ScrapeNewsRequest,
    db: Session = Depends(get_db)
):
    """Scrape news sentiment for a symbol"""
    try:
        sentiment_service = SentimentScrapingService(db)
        result = sentiment_service.scrape_news_sentiment(
            symbol=news_request.symbol,
            limit=news_request.limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping news sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/google-trends/{symbol}")
async def scrape_google_trends(
    symbol: str,
    timeframe: str = Query('1m', description="Timeframe for trends (1m, 3m, 6m, 1y, 2y, 5y)"),
    db: Session = Depends(get_db)
):
    """Scrape Google Trends data for a symbol"""
    try:
        sentiment_service = SentimentScrapingService(db)
        result = sentiment_service.scrape_google_trends(symbol, timeframe)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping Google Trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comprehensive/{symbol}")
async def get_comprehensive_sentiment(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive sentiment from all sources"""
    try:
        sentiment_service = SentimentScrapingService(db)
        result = sentiment_service.get_comprehensive_sentiment(symbol)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comprehensive sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
async def get_available_sources(db: Session = Depends(get_db)):
    """Get available sentiment sources"""
    try:
        sources = [
            {
                "name": "reddit",
                "description": "Reddit sentiment analysis from various subreddits",
                "endpoints": ["/reddit"],
                "rate_limit": "1 request per second",
                "data_types": ["posts", "comments", "sentiment_score"]
            },
            {
                "name": "twitter",
                "description": "Twitter sentiment analysis from tweets",
                "endpoints": ["/twitter"],
                "rate_limit": "1 request per second",
                "data_types": ["tweets", "sentiment_score"]
            },
            {
                "name": "news",
                "description": "News sentiment analysis from articles",
                "endpoints": ["/news"],
                "rate_limit": "1 request per second",
                "data_types": ["articles", "sentiment_score"]
            },
            {
                "name": "google_trends",
                "description": "Google Trends data for search interest",
                "endpoints": ["/google-trends/{symbol}"],
                "rate_limit": "1 request per second",
                "data_types": ["interest_over_time", "related_queries", "interest_by_region"]
            }
        ]
        
        return {
            "sources": sources,
            "total_count": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Error getting available sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reddit/subreddits")
async def get_available_subreddits(db: Session = Depends(get_db)):
    """Get available subreddits for sentiment analysis"""
    try:
        subreddits = [
            {
                "name": "wallstreetbets",
                "description": "WallStreetBets - High risk, high reward trading",
                "sentiment_focus": "Meme stocks, high volatility",
                "activity_level": "Very High"
            },
            {
                "name": "stocks",
                "description": "General stock discussion and analysis",
                "sentiment_focus": "Fundamental analysis, long-term investing",
                "activity_level": "High"
            },
            {
                "name": "investing",
                "description": "Investment strategies and portfolio management",
                "sentiment_focus": "Conservative investing, diversification",
                "activity_level": "High"
            },
            {
                "name": "SecurityAnalysis",
                "description": "Fundamental analysis and value investing",
                "sentiment_focus": "Deep analysis, financial statements",
                "activity_level": "Medium"
            },
            {
                "name": "options",
                "description": "Options trading strategies and analysis",
                "sentiment_focus": "Options strategies, derivatives",
                "activity_level": "Medium"
            },
            {
                "name": "cryptocurrency",
                "description": "Cryptocurrency discussion and analysis",
                "sentiment_focus": "Crypto markets, blockchain",
                "activity_level": "High"
            }
        ]
        
        return {
            "subreddits": subreddits,
            "total_count": len(subreddits)
        }
        
    except Exception as e:
        logger.error(f"Error getting available subreddits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeframes")
async def get_available_timeframes(db: Session = Depends(get_db)):
    """Get available timeframes for Google Trends"""
    try:
        timeframes = [
            {
                "value": "1m",
                "description": "Past 1 month",
                "data_points": "Daily"
            },
            {
                "value": "3m",
                "description": "Past 3 months",
                "data_points": "Daily"
            },
            {
                "value": "6m",
                "description": "Past 6 months",
                "data_points": "Daily"
            },
            {
                "value": "1y",
                "description": "Past 1 year",
                "data_points": "Weekly"
            },
            {
                "value": "2y",
                "description": "Past 2 years",
                "data_points": "Weekly"
            },
            {
                "value": "5y",
                "description": "Past 5 years",
                "data_points": "Monthly"
            }
        ]
        
        return {
            "timeframes": timeframes,
            "total_count": len(timeframes)
        }
        
    except Exception as e:
        logger.error(f"Error getting available timeframes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-analysis/{symbol}")
async def get_sentiment_analysis(
    symbol: str,
    sources: Optional[str] = Query(None, description="Comma-separated list of sources (reddit,twitter,news,google_trends)"),
    db: Session = Depends(get_db)
):
    """Get sentiment analysis for a symbol from specified sources"""
    try:
        # Parse sources
        source_list = None
        if sources:
            source_list = [s.strip() for s in sources.split(',')]
        
        sentiment_service = SentimentScrapingService(db)
        
        # Get data from specified sources
        results = {}
        
        if not source_list or 'reddit' in source_list:
            try:
                reddit_data = sentiment_service.scrape_reddit_sentiment(symbol)
                if 'error' not in reddit_data:
                    results['reddit'] = reddit_data
            except Exception as e:
                logger.error(f"Error getting Reddit data: {e}")
        
        if not source_list or 'twitter' in source_list:
            try:
                twitter_data = sentiment_service.scrape_twitter_sentiment(symbol)
                if 'error' not in twitter_data:
                    results['twitter'] = twitter_data
            except Exception as e:
                logger.error(f"Error getting Twitter data: {e}")
        
        if not source_list or 'news' in source_list:
            try:
                news_data = sentiment_service.scrape_news_sentiment(symbol)
                if 'error' not in news_data:
                    results['news'] = news_data
            except Exception as e:
                logger.error(f"Error getting news data: {e}")
        
        if not source_list or 'google_trends' in source_list:
            try:
                trends_data = sentiment_service.scrape_google_trends(symbol)
                if 'error' not in trends_data:
                    results['google_trends'] = trends_data
            except Exception as e:
                logger.error(f"Error getting Google Trends data: {e}")
        
        # Combine sentiment analysis
        sentiment_analyses = []
        for source, data in results.items():
            if 'sentiment_analysis' in data:
                sentiment_analyses.append(data['sentiment_analysis'])
        
        combined_sentiment = sentiment_service._combine_sentiment_analysis(sentiment_analyses)
        
        return {
            "symbol": symbol,
            "sources_analyzed": list(results.keys()),
            "combined_sentiment": combined_sentiment,
            "source_data": results,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch-analysis")
async def get_batch_sentiment_analysis(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    sources: Optional[str] = Query(None, description="Comma-separated list of sources"),
    db: Session = Depends(get_db)
):
    """Get sentiment analysis for multiple symbols"""
    try:
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Parse sources
        source_list = None
        if sources:
            source_list = [s.strip() for s in sources.split(',')]
        
        sentiment_service = SentimentScrapingService(db)
        
        batch_results = []
        
        for symbol in symbol_list:
            try:
                # Get comprehensive sentiment for each symbol
                result = sentiment_service.get_comprehensive_sentiment(symbol)
                
                if 'error' not in result:
                    batch_results.append({
                        "symbol": symbol,
                        "status": "success",
                        "data": result
                    })
                else:
                    batch_results.append({
                        "symbol": symbol,
                        "status": "error",
                        "error": result["error"]
                    })
                
            except Exception as e:
                batch_results.append({
                    "symbol": symbol,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "batch_results": batch_results,
            "total_symbols": len(symbol_list),
            "successful_analyses": len([r for r in batch_results if r["status"] == "success"]),
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting batch sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
