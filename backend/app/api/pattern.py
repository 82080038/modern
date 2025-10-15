"""
Pattern Recognition API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.database import get_db
from app.services.pattern_service import PatternRecognitionService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pattern", tags=["Pattern Recognition"])

# Pydantic schemas
class PatternDetectionRequest(BaseModel):
    symbol: str
    timeframes: Optional[List[str]] = None

class PatternResponse(BaseModel):
    symbol: str
    timeframes_analyzed: List[str]
    patterns_found: Dict
    total_patterns: int
    analysis_date: str

@router.post("/detect", response_model=PatternResponse)
async def detect_patterns(
    pattern_request: PatternDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect patterns across multiple timeframes"""
    try:
        pattern_service = PatternRecognitionService(db)
        result = pattern_service.detect_patterns(
            symbol=pattern_request.symbol,
            timeframes=pattern_request.timeframes
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return PatternResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detect/{symbol}")
async def detect_patterns_simple(
    symbol: str,
    timeframes: Optional[str] = Query(None, description="Comma-separated timeframes"),
    db: Session = Depends(get_db)
):
    """Detect patterns for a symbol (simple endpoint)"""
    try:
        # Parse timeframes
        if timeframes:
            timeframe_list = [tf.strip() for tf in timeframes.split(',')]
        else:
            timeframe_list = ['1D', '1W', '1M']
        
        pattern_service = PatternRecognitionService(db)
        result = pattern_service.detect_patterns(
            symbol=symbol,
            timeframes=timeframe_list
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support-resistance/{symbol}")
async def get_support_resistance_levels(
    symbol: str,
    timeframe: str = Query('1D', description="Timeframe for analysis"),
    db: Session = Depends(get_db)
):
    """Get support and resistance levels for a symbol"""
    try:
        pattern_service = PatternRecognitionService(db)
        result = pattern_service.get_support_resistance_levels(symbol, timeframe)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting support/resistance levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns/available")
async def get_available_patterns(db: Session = Depends(get_db)):
    """Get list of available patterns for detection"""
    try:
        pattern_service = PatternRecognitionService(db)
        
        patterns = []
        for pattern_type, pattern_info in pattern_service.patterns.items():
            patterns.append({
                "type": pattern_type,
                "name": pattern_info["name"],
                "description": pattern_info["description"],
                "timeframe_min": pattern_info["timeframe_min"],
                "confidence_threshold": pattern_info["confidence_threshold"]
            })
        
        return {
            "patterns": patterns,
            "total_count": len(patterns)
        }
        
    except Exception as e:
        logger.error(f"Error getting available patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{symbol}")
async def get_comprehensive_pattern_analysis(
    symbol: str,
    timeframes: Optional[str] = Query('1D,1W,1M', description="Comma-separated timeframes"),
    db: Session = Depends(get_db)
):
    """Get comprehensive pattern analysis for a symbol"""
    try:
        # Parse timeframes
        timeframe_list = [tf.strip() for tf in timeframes.split(',')]
        
        pattern_service = PatternRecognitionService(db)
        
        # Get pattern detection
        patterns_result = pattern_service.detect_patterns(symbol, timeframe_list)
        
        # Get support/resistance levels
        sr_result = pattern_service.get_support_resistance_levels(symbol, '1D')
        
        # Combine results
        analysis = {
            "symbol": symbol,
            "analysis_date": patterns_result.get("analysis_date"),
            "pattern_analysis": patterns_result,
            "support_resistance": sr_result,
            "summary": {
                "total_patterns": patterns_result.get("total_patterns", 0),
                "timeframes_analyzed": timeframe_list,
                "has_support_levels": len(sr_result.get("support_levels", [])) > 0,
                "has_resistance_levels": len(sr_result.get("resistance_levels", [])) > 0
            }
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting comprehensive pattern analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trend/{symbol}")
async def get_trend_analysis(
    symbol: str,
    timeframe: str = Query('1D', description="Timeframe for trend analysis"),
    db: Session = Depends(get_db)
):
    """Get trend analysis for a symbol"""
    try:
        pattern_service = PatternRecognitionService(db)
        
        # Get historical data
        from app.services.data_service import DataService
        data_service = DataService(db)
        
        historical_data = data_service.get_historical_candlestick_data(
            symbol, timeframe, 
            datetime.now() - timedelta(days=365), 
            datetime.now()
        )
        
        if not historical_data or len(historical_data) < 20:
            raise HTTPException(status_code=400, detail="Insufficient data for trend analysis")
        
        # Convert to DataFrame for analysis
        import pandas as pd
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Calculate trend indicators
        trend_analysis = {
            "symbol": symbol,
            "timeframe": timeframe,
            "analysis_date": datetime.now().isoformat(),
            "trend_direction": "neutral",
            "trend_strength": 0.0,
            "trend_duration": 0,
            "key_levels": [],
            "momentum": {
                "rsi": 0.0,
                "macd": 0.0,
                "trend_slope": 0.0
            }
        }
        
        # Simple trend analysis
        if len(df) >= 20:
            # Calculate moving averages
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            sma_50 = df['close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else sma_20
            current_price = df['close'].iloc[-1]
            
            # Determine trend direction
            if current_price > sma_20 > sma_50:
                trend_analysis["trend_direction"] = "uptrend"
                trend_analysis["trend_strength"] = 0.8
            elif current_price < sma_20 < sma_50:
                trend_analysis["trend_direction"] = "downtrend"
                trend_analysis["trend_strength"] = 0.8
            else:
                trend_analysis["trend_direction"] = "sideways"
                trend_analysis["trend_strength"] = 0.3
            
            # Calculate trend slope
            if len(df) >= 20:
                x = range(20)
                y = df['close'].tail(20).values
                slope, _, _, _, _ = linregress(x, y)
                trend_analysis["momentum"]["trend_slope"] = slope
            
            # Add key levels
            trend_analysis["key_levels"] = [
                {"type": "support", "price": sma_20, "strength": 0.7},
                {"type": "resistance", "price": sma_50, "strength": 0.5}
            ]
        
        return trend_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan")
async def scan_multiple_symbols(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    timeframes: str = Query('1D', description="Comma-separated timeframes"),
    pattern_types: Optional[str] = Query(None, description="Comma-separated pattern types"),
    db: Session = Depends(get_db)
):
    """Scan multiple symbols for patterns"""
    try:
        # Parse inputs
        symbol_list = [s.strip() for s in symbols.split(',')]
        timeframe_list = [tf.strip() for tf in timeframes.split(',')]
        pattern_type_list = [pt.strip() for pt in pattern_types.split(',')] if pattern_types else None
        
        pattern_service = PatternRecognitionService(db)
        
        scan_results = []
        
        for symbol in symbol_list:
            try:
                # Detect patterns
                patterns_result = pattern_service.detect_patterns(symbol, timeframe_list)
                
                # Filter by pattern types if specified
                if pattern_type_list and "patterns_found" in patterns_result:
                    filtered_patterns = {}
                    for tf, patterns in patterns_result["patterns_found"].items():
                        filtered_patterns[tf] = [
                            p for p in patterns 
                            if p.get("pattern_type") in pattern_type_list
                        ]
                    patterns_result["patterns_found"] = filtered_patterns
                
                scan_results.append({
                    "symbol": symbol,
                    "status": "success",
                    "patterns": patterns_result
                })
                
            except Exception as e:
                scan_results.append({
                    "symbol": symbol,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "scan_results": scan_results,
            "total_symbols": len(symbol_list),
            "successful_scans": len([r for r in scan_results if r["status"] == "success"]),
            "scan_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scanning multiple symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/confidence/{symbol}")
async def get_pattern_confidence_scores(
    symbol: str,
    timeframe: str = Query('1D', description="Timeframe for analysis"),
    db: Session = Depends(get_db)
):
    """Get confidence scores for all patterns for a symbol"""
    try:
        pattern_service = PatternRecognitionService(db)
        
        # Get pattern detection
        patterns_result = pattern_service.detect_patterns(symbol, [timeframe])
        
        if "error" in patterns_result:
            raise HTTPException(status_code=400, detail=patterns_result["error"])
        
        # Extract confidence scores
        confidence_scores = []
        
        if timeframe in patterns_result.get("patterns_found", {}):
            patterns = patterns_result["patterns_found"][timeframe]
            
            for pattern in patterns:
                confidence_scores.append({
                    "pattern_type": pattern.get("pattern_type"),
                    "name": pattern.get("name"),
                    "confidence": pattern.get("confidence", 0.0),
                    "description": pattern.get("description")
                })
        
        # Sort by confidence
        confidence_scores.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "confidence_scores": confidence_scores,
            "highest_confidence": confidence_scores[0] if confidence_scores else None,
            "analysis_date": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pattern confidence scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))
