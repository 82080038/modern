"""
Cache API Endpoints untuk Smart Data Caching
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.database import get_db
from app.services.cache_service import CacheService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cache", tags=["Cache"])

# Pydantic schemas
class PreloadDataRequest(BaseModel):
    symbols: List[str]
    timeframes: Optional[List[str]] = None

class CacheStatsResponse(BaseModel):
    redis_connected: bool
    redis_info: Dict
    cache_keys: int
    memory_usage: str
    database_stats: Dict

@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats(db: Session = Depends(get_db)):
    """Get cache statistics"""
    try:
        cache_service = CacheService(db)
        stats = cache_service.get_cache_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=400, detail=stats["error"])
        
        return CacheStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/coverage/{symbol}")
async def get_data_coverage(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get data coverage for a symbol"""
    try:
        cache_service = CacheService(db)
        coverage = cache_service.get_data_coverage(symbol)
        
        if "error" in coverage:
            raise HTTPException(status_code=400, detail=coverage["error"])
        
        return coverage
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preload")
async def preload_data(
    preload_request: PreloadDataRequest,
    db: Session = Depends(get_db)
):
    """Preload data for multiple symbols"""
    try:
        cache_service = CacheService(db)
        result = cache_service.preload_data(
            symbols=preload_request.symbols,
            timeframes=preload_request.timeframes
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error preloading data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_cache(
    cache_type: Optional[str] = Query(None, description="Cache type to clear (realtime, historical, fundamental, sentiment)"),
    db: Session = Depends(get_db)
):
    """Clear cache"""
    try:
        cache_service = CacheService(db)
        result = cache_service.clear_cache(cache_type)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_old_data(
    days: int = Query(30, description="Number of days to keep data"),
    db: Session = Depends(get_db)
):
    """Clean up old data"""
    try:
        cache_service = CacheService(db)
        result = cache_service.cleanup_old_data(days)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candlestick/{symbol}")
async def get_candlestick_data_cached(
    symbol: str,
    timeframe: str = Query("1D", description="Timeframe"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    force_refresh: bool = Query(False, description="Force refresh from external source"),
    db: Session = Depends(get_db)
):
    """Get candlestick data with smart caching"""
    try:
        # Parse dates
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        else:
            start_dt = datetime.now() - timedelta(days=365)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.now()
        
        cache_service = CacheService(db)
        data = cache_service.get_candlestick_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_dt,
            end_date=end_dt,
            force_refresh=force_refresh
        )
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "data_count": len(data),
            "data": data,
            "cached": not force_refresh
        }
        
    except Exception as e:
        logger.error(f"Error getting cached candlestick data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/{symbol}")
async def get_realtime_price_cached(
    symbol: str,
    force_refresh: bool = Query(False, description="Force refresh from external source"),
    db: Session = Depends(get_db)
):
    """Get real-time price with caching"""
    try:
        cache_service = CacheService(db)
        price_data = cache_service.get_realtime_price(symbol, force_refresh)
        
        if not price_data:
            raise HTTPException(status_code=404, detail="Price data not available")
        
        return {
            "symbol": symbol,
            "price": price_data['price'],
            "timestamp": price_data.get('timestamp', datetime.now().isoformat()),
            "cached": not force_refresh
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cached realtime price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fundamental/{symbol}")
async def get_fundamental_data_cached(
    symbol: str,
    force_refresh: bool = Query(False, description="Force refresh from external source"),
    db: Session = Depends(get_db)
):
    """Get fundamental data with caching"""
    try:
        cache_service = CacheService(db)
        data = cache_service.get_fundamental_data(symbol, force_refresh)
        
        if not data:
            raise HTTPException(status_code=404, detail="Fundamental data not available")
        
        return {
            "symbol": symbol,
            "data": data,
            "cached": not force_refresh
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cached fundamental data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment/{symbol}")
async def get_sentiment_data_cached(
    symbol: str,
    force_refresh: bool = Query(False, description="Force refresh from external source"),
    db: Session = Depends(get_db)
):
    """Get sentiment data with caching"""
    try:
        cache_service = CacheService(db)
        data = cache_service.get_sentiment_data(symbol, force_refresh)
        
        if not data:
            raise HTTPException(status_code=404, detail="Sentiment data not available")
        
        return {
            "symbol": symbol,
            "data": data,
            "cached": not force_refresh
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cached sentiment data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_cache_status(db: Session = Depends(get_db)):
    """Get cache system status"""
    try:
        cache_service = CacheService(db)
        
        # Get basic stats
        stats = cache_service.get_cache_stats()
        
        # Get data coverage for popular symbols
        popular_symbols = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII']
        coverage = {}
        
        for symbol in popular_symbols:
            try:
                coverage[symbol] = cache_service.get_data_coverage(symbol)
            except Exception as e:
                coverage[symbol] = {'error': str(e)}
        
        return {
            "cache_status": "active",
            "redis_connected": stats.get('redis_connected', False),
            "database_stats": stats.get('database_stats', {}),
            "popular_symbols_coverage": coverage,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting cache status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/warmup")
async def warmup_cache(
    symbols: List[str] = Body(..., description="List of symbols to warm up"),
    timeframes: List[str] = Body(['1D', '1W', '1M'], description="Timeframes to warm up"),
    db: Session = Depends(get_db)
):
    """Warm up cache for specific symbols"""
    try:
        cache_service = CacheService(db)
        
        results = {}
        
        for symbol in symbols:
            symbol_results = {}
            
            # Warm up candlestick data
            for tf in timeframes:
                try:
                    data = cache_service.get_candlestick_data(
                        symbol=symbol,
                        timeframe=tf,
                        start_date=datetime.now() - timedelta(days=365),
                        end_date=datetime.now()
                    )
                    symbol_results[tf] = len(data)
                except Exception as e:
                    symbol_results[tf] = f"Error: {str(e)}"
            
            # Warm up realtime price
            try:
                price_data = cache_service.get_realtime_price(symbol)
                symbol_results['realtime'] = 1 if price_data else 0
            except Exception as e:
                symbol_results['realtime'] = f"Error: {str(e)}"
            
            results[symbol] = symbol_results
        
        return {
            "warmed_up_symbols": len(symbols),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error warming up cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
