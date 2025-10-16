"""
Enhanced Market Data API Endpoints
==================================

Enhanced market data module dengan real-time data source,
validation, dan quality checks untuk mencapai akurasi >80%.

Author: AI Assistant
Date: 2025-01-16
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.services.enhanced_market_data_service import EnhancedMarketDataService
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/enhanced-market-data", tags=["Enhanced Market Data"])

# Enhanced Pydantic schemas
class EnhancedMarketDataRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"  # 1m, 5m, 15m, 1h, 1d, 1w, 1M
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_indicators: bool = True
    include_volume: bool = True
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v) < 1 or len(v) > 10:
            raise ValueError('Symbol must be 1-10 characters')
        return v.upper()
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
        if v not in valid_timeframes:
            raise ValueError(f'Invalid timeframe. Must be one of: {valid_timeframes}')
        return v

class EnhancedMarketDataResponse(BaseModel):
    symbol: str
    timeframe: str
    data_points: int
    start_date: datetime
    end_date: datetime
    data_quality: str  # excellent, good, fair, poor
    data_source: str
    last_updated: datetime
    price_data: List[Dict[str, Any]]
    indicators: Optional[Dict[str, Any]] = None
    volume_data: Optional[List[Dict[str, Any]]] = None

class DataQualityResponse(BaseModel):
    symbol: str
    data_quality_score: float
    completeness: float
    accuracy: float
    timeliness: float
    consistency: float
    issues: List[str]
    recommendations: List[str]

class RealTimePriceResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    data_source: str
    confidence: float

@router.get("/data", response_model=EnhancedMarketDataResponse)
async def get_enhanced_market_data(
    request: EnhancedMarketDataRequest,
    db: Session = Depends(get_db)
):
    """Get enhanced market data dengan quality validation"""
    try:
        # Initialize enhanced market data service
        market_data_service = EnhancedMarketDataService(db)
        
        # Get market data dengan enhanced validation
        data_result = await market_data_service.get_enhanced_market_data(
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            include_indicators=request.include_indicators,
            include_volume=request.include_volume
        )
        
        if "error" in data_result:
            raise HTTPException(status_code=400, detail=data_result["error"])
        
        return EnhancedMarketDataResponse(
            symbol=data_result["symbol"],
            timeframe=data_result["timeframe"],
            data_points=data_result["data_points"],
            start_date=data_result["start_date"],
            end_date=data_result["end_date"],
            data_quality=data_result["data_quality"],
            data_source=data_result["data_source"],
            last_updated=data_result["last_updated"],
            price_data=data_result["price_data"],
            indicators=data_result.get("indicators"),
            volume_data=data_result.get("volume_data")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enhanced market data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/real-time/{symbol}", response_model=RealTimePriceResponse)
async def get_real_time_price(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get real-time price dengan enhanced validation"""
    try:
        market_data_service = EnhancedMarketDataService(db)
        
        # Get real-time price
        price_result = await market_data_service.get_real_time_price(symbol)
        
        if "error" in price_result:
            raise HTTPException(status_code=400, detail=price_result["error"])
        
        return RealTimePriceResponse(
            symbol=price_result["symbol"],
            price=price_result["price"],
            change=price_result["change"],
            change_percent=price_result["change_percent"],
            volume=price_result["volume"],
            timestamp=price_result["timestamp"],
            data_source=price_result["data_source"],
            confidence=price_result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting real-time price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality/{symbol}", response_model=DataQualityResponse)
async def assess_data_quality(
    symbol: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Assess data quality untuk symbol"""
    try:
        market_data_service = EnhancedMarketDataService(db)
        
        # Assess data quality
        quality_result = await market_data_service.assess_data_quality(symbol, days)
        
        if "error" in quality_result:
            raise HTTPException(status_code=400, detail=quality_result["error"])
        
        return DataQualityResponse(
            symbol=quality_result["symbol"],
            data_quality_score=quality_result["data_quality_score"],
            completeness=quality_result["completeness"],
            accuracy=quality_result["accuracy"],
            timeliness=quality_result["timeliness"],
            consistency=quality_result["consistency"],
            issues=quality_result["issues"],
            recommendations=quality_result["recommendations"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing data quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{symbol}")
async def get_technical_indicators(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe for indicators"),
    days: int = Query(30, description="Number of days"),
    db: Session = Depends(get_db)
):
    """Get technical indicators dengan enhanced calculation"""
    try:
        market_data_service = EnhancedMarketDataService(db)
        
        # Get technical indicators
        indicators_result = await market_data_service.get_technical_indicators(
            symbol=symbol,
            timeframe=timeframe,
            days=days
        )
        
        if "error" in indicators_result:
            raise HTTPException(status_code=400, detail=indicators_result["error"])
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "indicators": indicators_result["indicators"],
            "calculated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technical indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/screener")
async def get_market_screener(
    criteria: str = Query("volume>1000000", description="Screening criteria"),
    limit: int = Query(50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """Get market screener dengan enhanced filtering"""
    try:
        market_data_service = EnhancedMarketDataService(db)
        
        # Get screened results
        screener_result = await market_data_service.get_market_screener(
            criteria=criteria,
            limit=limit
        )
        
        if "error" in screener_result:
            raise HTTPException(status_code=400, detail=screener_result["error"])
        
        return {
            "criteria": criteria,
            "results": screener_result["results"],
            "total_found": screener_result["total_found"],
            "screened_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market screener: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_enhanced_market_data_health():
    """Get enhanced market data module health status"""
    try:
        return {
            "status": "healthy",
            "module": "enhanced_market_data",
            "version": "2.0.0",
            "features": [
                "real_time_data",
                "data_validation",
                "quality_assessment",
                "technical_indicators",
                "market_screener"
            ],
            "data_sources": [
                "primary_source",
                "backup_source_1",
                "backup_source_2"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
