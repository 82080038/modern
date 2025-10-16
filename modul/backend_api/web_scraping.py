"""
Web Scraping API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date, timedelta
from app.database import get_db
from app.services.web_scraping_service import WebScrapingService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/web-scraping", tags=["Web Scraping"])

# Pydantic schemas
class ScrapeUrlsRequest(BaseModel):
    urls: List[str]
    delay: Optional[float] = None
    max_concurrent: int = 5

class ScrapeFinancialStatementsRequest(BaseModel):
    symbol: str
    source: str = "idx"  # idx, investing

@router.post("/scrape-urls")
async def scrape_multiple_urls(
    scrape_request: ScrapeUrlsRequest,
    db: Session = Depends(get_db)
):
    """Scrape multiple URLs"""
    try:
        web_scraping_service = WebScrapingService(db)
        results = web_scraping_service.scrape_multiple_urls(
            urls=scrape_request.urls,
            delay=scrape_request.delay,
            max_concurrent=scrape_request.max_concurrent
        )
        
        return {
            "results": [
                {
                    "url": result.url,
                    "status": result.status.value,
                    "data": result.data,
                    "error": result.error,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in results
            ],
            "total_urls": len(results),
            "successful": len([r for r in results if r.status.value == "completed"]),
            "failed": len([r for r in results if r.status.value == "failed"])
        }
        
    except Exception as e:
        logger.error(f"Error scraping multiple URLs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrape-url/{url:path}")
async def scrape_single_url(
    url: str,
    delay: Optional[float] = Query(None, description="Delay between requests"),
    db: Session = Depends(get_db)
):
    """Scrape a single URL"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_url(url, delay=delay)
        
        return {
            "url": result.url,
            "status": result.status.value,
            "data": result.data,
            "error": result.error,
            "timestamp": result.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scraping single URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/idx-data/{symbol}")
async def scrape_idx_data(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Scrape IDX data for a symbol"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_idx_data(symbol)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping IDX data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/idx-data")
async def scrape_idx_market_data(db: Session = Depends(get_db)):
    """Scrape IDX market overview data"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_idx_data()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping IDX market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investing-data/{symbol}")
async def scrape_investing_data(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Scrape investing.com data for a symbol"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_investing_com(symbol)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping investing.com data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investing-data")
async def scrape_investing_market_data(db: Session = Depends(get_db)):
    """Scrape investing.com market overview data"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_investing_com()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping investing.com market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/financial-statements")
async def scrape_financial_statements(
    financial_request: ScrapeFinancialStatementsRequest,
    db: Session = Depends(get_db)
):
    """Scrape financial statements for a symbol"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_financial_statements(
            symbol=financial_request.symbol,
            source=financial_request.source
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping financial statements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news-articles/{symbol}")
async def scrape_news_articles(
    symbol: str,
    limit: int = Query(20, description="Maximum number of articles to return"),
    db: Session = Depends(get_db)
):
    """Scrape news articles for a symbol"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_news_articles(symbol, limit)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping news articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/economic-calendar")
async def scrape_economic_calendar(
    start_date: Optional[date] = Query(None, description="Start date for calendar"),
    end_date: Optional[date] = Query(None, description="End date for calendar"),
    db: Session = Depends(get_db)
):
    """Scrape economic calendar data"""
    try:
        web_scraping_service = WebScrapingService(db)
        result = web_scraping_service.scrape_economic_calendar(start_date, end_date)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping economic calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_scraping_status(db: Session = Depends(get_db)):
    """Get current scraping status and statistics"""
    try:
        web_scraping_service = WebScrapingService(db)
        status = web_scraping_service.get_scraping_status()
        
        if "error" in status:
            raise HTTPException(status_code=400, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scraping status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
async def get_available_sources(db: Session = Depends(get_db)):
    """Get available scraping sources"""
    try:
        sources = [
            {
                "name": "idx.co.id",
                "description": "Indonesia Stock Exchange official website",
                "endpoints": ["/idx-data/{symbol}", "/idx-data"],
                "rate_limit": "1 request per second",
                "data_types": ["company_profile", "financial_statements", "market_data"]
            },
            {
                "name": "investing.com",
                "description": "Global financial data and news",
                "endpoints": ["/investing-data/{symbol}", "/investing-data"],
                "rate_limit": "1 request per second",
                "data_types": ["stock_data", "market_data", "news"]
            },
            {
                "name": "forexfactory.com",
                "description": "Economic calendar and forex data",
                "endpoints": ["/economic-calendar"],
                "rate_limit": "1 request per second",
                "data_types": ["economic_events", "forex_data"]
            }
        ]
        
        return {
            "sources": sources,
            "total_count": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Error getting available sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rate-limits")
async def get_rate_limits(db: Session = Depends(get_db)):
    """Get rate limiting information"""
    try:
        rate_limits = {
            "default_delay": 1.0,
            "fast_delay": 0.5,
            "slow_delay": 2.0,
            "max_concurrent": 5,
            "retry_attempts": 3,
            "exponential_backoff": True
        }
        
        return rate_limits
        
    except Exception as e:
        logger.error(f"Error getting rate limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-agents")
async def get_user_agents(db: Session = Depends(get_db)):
    """Get available user agents for rotation"""
    try:
        web_scraping_service = WebScrapingService(db)
        user_agents = web_scraping_service.user_agents
        
        return {
            "user_agents": user_agents,
            "total_count": len(user_agents),
            "rotation_enabled": True
        }
        
    except Exception as e:
        logger.error(f"Error getting user agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-scrape")
async def batch_scrape_data(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    sources: str = Query("idx,investing", description="Comma-separated list of sources"),
    db: Session = Depends(get_db)
):
    """Batch scrape data for multiple symbols"""
    try:
        # Parse symbols and sources
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        source_list = [s.strip() for s in sources.split(',')]
        
        web_scraping_service = WebScrapingService(db)
        
        batch_results = []
        
        for symbol in symbol_list:
            symbol_results = {}
            
            for source in source_list:
                try:
                    if source == "idx":
                        result = web_scraping_service.scrape_idx_data(symbol)
                    elif source == "investing":
                        result = web_scraping_service.scrape_investing_com(symbol)
                    else:
                        result = {"error": f"Unsupported source: {source}"}
                    
                    symbol_results[source] = result
                    
                except Exception as e:
                    symbol_results[source] = {"error": str(e)}
            
            batch_results.append({
                "symbol": symbol,
                "results": symbol_results
            })
        
        return {
            "batch_results": batch_results,
            "total_symbols": len(symbol_list),
            "sources_used": source_list,
            "scraped_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error batch scraping data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-quality")
async def get_data_quality_metrics(db: Session = Depends(get_db)):
    """Get data quality metrics"""
    try:
        # This would query database for data quality metrics in production
        metrics = {
            "total_scraped": 10000,
            "successful_scrapes": 9500,
            "failed_scrapes": 500,
            "data_completeness": 0.95,
            "data_accuracy": 0.98,
            "last_quality_check": datetime.now().isoformat(),
            "quality_score": 0.96
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting data quality metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
