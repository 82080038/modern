"""
Market Data API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from app.database import get_db
from app.services.data_service import DataService
from app.models.market_data import MarketData, HistoricalData, SymbolInfo
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/market", tags=["Market Data"])

# Pydantic schemas
class HistoricalDataResponse(BaseModel):
    symbol: str
    timeframe: str
    data: List[Dict]
    total_records: int

class RealTimePriceResponse(BaseModel):
    symbol: str
    price: Optional[float]
    change: Optional[float]
    change_percent: Optional[float]
    volume: Optional[int]
    market_cap: Optional[int]
    timestamp: str

class DataUpdateResponse(BaseModel):
    status: str
    message: str
    records_saved: int
    date_range: Optional[str] = None

class SymbolListResponse(BaseModel):
    symbols: List[str]
    total_count: int

@router.get("/symbols", response_model=SymbolListResponse)
async def get_available_symbols(
    active_only: bool = Query(True, description="Only active symbols"),
    db: Session = Depends(get_db)
):
    """Get list of available symbols"""
    try:
        query = db.query(SymbolInfo)
        if active_only:
            query = query.filter(SymbolInfo.is_active == True)
        
        symbols = query.all()
        symbol_list = [s.symbol for s in symbols]
        
        return SymbolListResponse(
            symbols=symbol_list,
            total_count=len(symbol_list)
        )
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical/{symbol}", response_model=HistoricalDataResponse)
async def get_historical_data(
    symbol: str,
    timeframe: str = Query("1D", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1D, 1W, 1M, 3M, 6M, 1Y"),
    limit: int = Query(100, description="Number of records to return"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get historical market data"""
    try:
        data_service = DataService(db)
        
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1D', '1W', '1M', '3M', '6M', '1Y']
        if timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe. Valid options: {valid_timeframes}")
        
        # Get data
        if start_date and end_date:
            # Get data for specific date range
            data = db.query(HistoricalData).filter(
                HistoricalData.symbol == symbol.upper(),
                HistoricalData.timeframe == timeframe,
                HistoricalData.date >= start_date,
                HistoricalData.date <= end_date
            ).order_by(HistoricalData.date.desc()).all()
        else:
            # Get latest data
            data = db.query(HistoricalData).filter(
                HistoricalData.symbol == symbol.upper(),
                HistoricalData.timeframe == timeframe
            ).order_by(HistoricalData.date.desc()).limit(limit).all()
        
        # Format response
        formatted_data = []
        for row in data:
            formatted_data.append({
                "date": row.date.isoformat(),
                "timestamp": row.timestamp.isoformat(),
                "open": row.open_price,
                "high": row.high_price,
                "low": row.low_price,
                "close": row.close_price,
                "volume": row.volume,
                "adjusted_close": row.adjusted_close,
                "sma_20": row.sma_20,
                "sma_50": row.sma_50,
                "rsi_14": row.rsi_14,
                "macd": row.macd
            })
        
        return HistoricalDataResponse(
            symbol=symbol.upper(),
            timeframe=timeframe,
            data=formatted_data,
            total_records=len(formatted_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/{symbol}", response_model=RealTimePriceResponse)
async def get_real_time_price(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get real-time price for symbol"""
    try:
        data_service = DataService(db)
        price_data = data_service.get_real_time_price(symbol.upper())
        
        if not price_data:
            raise HTTPException(status_code=404, detail=f"No real-time data available for {symbol}")
        
        return RealTimePriceResponse(**price_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting real-time price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update/{symbol}", response_model=DataUpdateResponse)
async def update_symbol_data(
    symbol: str,
    timeframe: str = Query("1D", description="Timeframe to update"),
    days_back: int = Query(730, description="Days of historical data to fetch"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Update historical data for symbol"""
    try:
        data_service = DataService(db)
        
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1D', '1W', '1M', '3M', '6M', '1Y']
        if timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe. Valid options: {valid_timeframes}")
        
        # Update data
        result = data_service.update_historical_data(symbol.upper(), timeframe, days_back)
        
        return DataUpdateResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize", response_model=Dict)
async def initialize_market_data(
    symbols: Optional[List[str]] = Query(None, description="List of symbols to initialize"),
    timeframes: Optional[List[str]] = Query(None, description="List of timeframes"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Initialize market data for popular IDX symbols"""
    try:
        data_service = DataService(db)
        
        # Default symbols and timeframes
        if not symbols:
            symbols = data_service.get_popular_idx_symbols()
        
        if not timeframes:
            timeframes = ['1D', '1W', '1M']
        
        # Initialize data in background
        def initialize_data():
            return data_service.initialize_symbol_data(symbols, timeframes)
        
        if background_tasks:
            background_tasks.add_task(initialize_data)
            return {
                "status": "started",
                "message": f"Initializing data for {len(symbols)} symbols and {len(timeframes)} timeframes in background",
                "symbols": symbols,
                "timeframes": timeframes
            }
        else:
            # Run synchronously
            results = initialize_data()
            return {
                "status": "completed",
                "message": "Data initialization completed",
                "results": results
            }
        
    except Exception as e:
        logger.error(f"Error initializing market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{symbol}")
async def get_data_status(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get data status for symbol"""
    try:
        # Get latest data dates for different timeframes
        timeframes = ['1D', '1W', '1M']
        status = {}
        
        for tf in timeframes:
            latest_data = db.query(HistoricalData).filter(
                HistoricalData.symbol == symbol.upper(),
                HistoricalData.timeframe == tf
            ).order_by(HistoricalData.date.desc()).first()
            
            status[tf] = {
                "latest_date": latest_data.date.isoformat() if latest_data else None,
                "total_records": db.query(HistoricalData).filter(
                    HistoricalData.symbol == symbol.upper(),
                    HistoricalData.timeframe == tf
                ).count()
            }
        
        return {
            "symbol": symbol.upper(),
            "status": status,
            "last_checked": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting data status for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_symbols(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """Search symbols by name or symbol"""
    try:
        symbols = db.query(SymbolInfo).filter(
            (SymbolInfo.symbol.ilike(f"%{query}%")) |
            (SymbolInfo.name.ilike(f"%{query}%"))
        ).limit(limit).all()
        
        results = []
        for symbol in symbols:
            results.append({
                "symbol": symbol.symbol,
                "name": symbol.name,
                "sector": symbol.sector,
                "industry": symbol.industry,
                "market_cap": symbol.market_cap,
                "is_active": symbol.is_active
            })
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))
