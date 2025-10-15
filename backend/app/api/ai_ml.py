"""
AI/ML Models API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from sqlalchemy import text
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-ml", tags=["AI/ML Models"])

# Pydantic schemas
class AIPatternResponse(BaseModel):
    symbol: str
    analysis_date: str
    pattern_strength: float
    gap_accuracy: float
    order_book_efficiency: float
    pattern_effectiveness: float
    mean_reversion_effectiveness: float
    overall_effectiveness: float
    pattern_classification: dict
    pattern_signals: dict

class AISignalResponse(BaseModel):
    symbol: str
    signal_date: str
    signal_type: str
    confidence_score: float
    gap_signal_weight: float
    order_book_signal_weight: float
    pattern_signal_weight: float
    mean_reversion_signal_weight: float
    buy_signals_count: int
    sell_signals_count: int
    hold_signals_count: int
    signal_reasoning: str

class MLPredictionResponse(BaseModel):
    symbol: str
    prediction_date: str
    predicted_price: float
    confidence: float
    model_name: str
    features_used: List[str]
    prediction_horizon: str

@router.get("/pattern-analysis/{symbol}")
async def get_ai_pattern_analysis(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get AI pattern analysis for a symbol"""
    try:
        query_parts = ["SELECT * FROM ai_pattern_analysis WHERE symbol = :symbol"]
        params = {"symbol": symbol}
        
        if start_date:
            query_parts.append("AND analysis_date >= :start_date")
            params["start_date"] = start_date
        if end_date:
            query_parts.append("AND analysis_date <= :end_date")
            params["end_date"] = end_date
        
        query_parts.append("ORDER BY analysis_date DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No AI pattern analysis found for symbol")
        
        analyses = []
        for row in rows:
            analyses.append({
                "symbol": row.symbol,
                "analysis_date": row.analysis_date.isoformat(),
                "pattern_strength": float(row.pattern_strength) if row.pattern_strength else None,
                "gap_accuracy": float(row.gap_accuracy) if row.gap_accuracy else None,
                "order_book_efficiency": float(row.order_book_efficiency) if row.order_book_efficiency else None,
                "pattern_effectiveness": float(row.pattern_effectiveness) if row.pattern_effectiveness else None,
                "mean_reversion_effectiveness": float(row.mean_reversion_effectiveness) if row.mean_reversion_effectiveness else None,
                "overall_effectiveness": float(row.overall_effectiveness) if row.overall_effectiveness else None,
                "pattern_classification": row.pattern_classification,
                "pattern_signals": row.pattern_signals
            })
        
        return {
            "symbol": symbol,
            "total_analyses": len(analyses),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "analyses": analyses
        }
        
    except Exception as e:
        logger.error(f"Error getting AI pattern analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/{symbol}")
async def get_ai_signals(
    symbol: str,
    signal_type: Optional[str] = Query(None, description="Signal type filter (BUY, SELL, HOLD)"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get AI trading signals for a symbol"""
    try:
        query_parts = ["SELECT * FROM ai_signals WHERE symbol = :symbol"]
        params = {"symbol": symbol}
        
        if signal_type:
            query_parts.append("AND signal_type = :signal_type")
            params["signal_type"] = signal_type
        if min_confidence is not None:
            query_parts.append("AND confidence_score >= :min_confidence")
            params["min_confidence"] = min_confidence
        
        query_parts.append("ORDER BY signal_date DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No AI signals found for symbol")
        
        signals = []
        for row in rows:
            signals.append({
                "symbol": row.symbol,
                "signal_date": row.signal_date.isoformat(),
                "signal_type": row.signal_type,
                "confidence_score": float(row.confidence_score) if row.confidence_score else None,
                "gap_signal_weight": float(row.gap_signal_weight) if row.gap_signal_weight else None,
                "order_book_signal_weight": float(row.order_book_signal_weight) if row.order_book_signal_weight else None,
                "pattern_signal_weight": float(row.pattern_signal_weight) if row.pattern_signal_weight else None,
                "mean_reversion_signal_weight": float(row.mean_reversion_signal_weight) if row.mean_reversion_signal_weight else None,
                "buy_signals_count": row.buy_signals_count,
                "sell_signals_count": row.sell_signals_count,
                "hold_signals_count": row.hold_signals_count,
                "signal_reasoning": row.signal_reasoning
            })
        
        return {
            "symbol": symbol,
            "total_signals": len(signals),
            "filters": {
                "signal_type": signal_type,
                "min_confidence": min_confidence
            },
            "signals": signals
        }
        
    except Exception as e:
        logger.error(f"Error getting AI signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/{symbol}")
async def get_ml_predictions(
    symbol: str,
    model_name: Optional[str] = Query(None, description="Model name filter"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get ML predictions for a symbol"""
    try:
        query_parts = ["SELECT * FROM ml_predictions WHERE symbol = :symbol"]
        params = {"symbol": symbol}
        
        if model_name:
            query_parts.append("AND model_name = :model_name")
            params["model_name"] = model_name
        if min_confidence is not None:
            query_parts.append("AND confidence >= :min_confidence")
            params["min_confidence"] = min_confidence
        
        query_parts.append("ORDER BY prediction_date DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No ML predictions found for symbol")
        
        predictions = []
        for row in rows:
            predictions.append({
                "symbol": row.symbol,
                "prediction_date": row.prediction_date.isoformat(),
                "predicted_price": float(row.predicted_price) if row.predicted_price else None,
                "confidence": float(row.confidence) if row.confidence else None,
                "model_name": row.model_name,
                "features_used": row.features_used,
                "prediction_horizon": row.prediction_horizon
            })
        
        return {
            "symbol": symbol,
            "total_predictions": len(predictions),
            "filters": {
                "model_name": model_name,
                "min_confidence": min_confidence
            },
            "predictions": predictions
        }
        
    except Exception as e:
        logger.error(f"Error getting ML predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/{symbol}")
async def get_ai_performance(
    symbol: str,
    module_name: Optional[str] = Query(None, description="Module name filter"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get AI performance metrics for a symbol"""
    try:
        query_parts = ["SELECT * FROM ai_performance WHERE symbol = :symbol"]
        params = {"symbol": symbol}
        
        if module_name:
            query_parts.append("AND module_name = :module_name")
            params["module_name"] = module_name
        
        query_parts.append("ORDER BY analysis_date DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No AI performance data found for symbol")
        
        performances = []
        for row in rows:
            performances.append({
                "symbol": row.symbol,
                "analysis_date": row.analysis_date.isoformat(),
                "module_name": row.module_name,
                "effectiveness_score": float(row.effectiveness_score) if row.effectiveness_score else None,
                "accuracy_score": float(row.accuracy_score) if row.accuracy_score else None,
                "precision_score": float(row.precision_score) if row.precision_score else None,
                "recall_score": float(row.recall_score) if row.recall_score else None,
                "f1_score": float(row.f1_score) if row.f1_score else None,
                "processing_time_ms": row.processing_time_ms,
                "memory_usage_mb": float(row.memory_usage_mb) if row.memory_usage_mb else None
            })
        
        return {
            "symbol": symbol,
            "total_performances": len(performances),
            "filters": {
                "module_name": module_name
            },
            "performances": performances
        }
        
    except Exception as e:
        logger.error(f"Error getting AI performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_ai_dashboard(
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get AI/ML dashboard summary"""
    try:
        # Get latest signals
        signals_query = """
            SELECT symbol, signal_type, confidence_score, signal_date
            FROM ai_signals 
            ORDER BY signal_date DESC 
            LIMIT :limit
        """
        signals_result = db.execute(text(signals_query), {"limit": limit})
        signals = signals_result.fetchall()
        
        # Get latest predictions
        predictions_query = """
            SELECT symbol, predicted_price, confidence, model_name, prediction_date
            FROM ml_predictions 
            ORDER BY prediction_date DESC 
            LIMIT :limit
        """
        predictions_result = db.execute(text(predictions_query), {"limit": limit})
        predictions = predictions_result.fetchall()
        
        # Get performance summary
        performance_query = """
            SELECT module_name, AVG(effectiveness_score) as avg_effectiveness,
                   AVG(accuracy_score) as avg_accuracy, AVG(f1_score) as avg_f1
            FROM ai_performance 
            GROUP BY module_name
        """
        performance_result = db.execute(text(performance_query))
        performance = performance_result.fetchall()
        
        return {
            "latest_signals": [
                {
                    "symbol": s.symbol,
                    "signal_type": s.signal_type,
                    "confidence_score": float(s.confidence_score) if s.confidence_score else None,
                    "signal_date": s.signal_date.isoformat()
                } for s in signals
            ],
            "latest_predictions": [
                {
                    "symbol": p.symbol,
                    "predicted_price": float(p.predicted_price) if p.predicted_price else None,
                    "confidence": float(p.confidence) if p.confidence else None,
                    "model_name": p.model_name if hasattr(p, 'model_name') else "ML Model",
                    "prediction_date": p.prediction_date.isoformat()
                } for p in predictions
            ],
            "performance_summary": [
                {
                    "module_name": p.module_name,
                    "avg_effectiveness": float(p.avg_effectiveness) if p.avg_effectiveness else None,
                    "avg_accuracy": float(p.avg_accuracy) if p.avg_accuracy else None,
                    "avg_f1": float(p.avg_f1) if p.avg_f1 else None
                } for p in performance
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting AI dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
