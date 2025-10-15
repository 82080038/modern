"""
Risk Management API Endpoints
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
router = APIRouter(prefix="/risk", tags=["Risk Management"])

# Pydantic schemas
class RiskAnalysisResponse(BaseModel):
    analysis_date: str
    portfolio_value: float
    var_1d: float
    var_score: int
    stress_score: int
    scenario_score: int
    correlation_score: int
    concentration_score: int
    liquidity_score: int
    monte_carlo_score: int
    risk_score: int
    risk_level: str

class RiskMetricsResponse(BaseModel):
    timestamp: str
    portfolio_var: float
    portfolio_cvar: float
    max_drawdown: float
    correlation_risk: float
    concentration_risk: float
    leverage_ratio: float
    risk_level: str

class MonteCarloResponse(BaseModel):
    simulation_id: str
    symbol: str
    simulation_date: str
    scenarios: int
    confidence_level: float
    var_1d: float
    var_5d: float
    var_30d: float
    expected_shortfall: float
    worst_case_scenario: float
    best_case_scenario: float

@router.get("/analysis")
async def get_risk_analysis(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get risk analysis data"""
    try:
        query_parts = ["SELECT * FROM risk_analysis WHERE 1=1"]
        params = {}
        
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
            raise HTTPException(status_code=404, detail="No risk analysis data found")
        
        analyses = []
        for row in rows:
            analyses.append({
                "analysis_date": row.analysis_date.isoformat(),
                "portfolio_value": float(row.portfolio_value) if row.portfolio_value else None,
                "var_1d": float(row.var_1d) if row.var_1d else None,
                "var_score": row.var_score,
                "stress_score": row.stress_score,
                "scenario_score": row.scenario_score,
                "correlation_score": row.correlation_score,
                "concentration_score": row.concentration_score,
                "liquidity_score": row.liquidity_score,
                "monte_carlo_score": row.monte_carlo_score,
                "risk_score": row.risk_score,
                "risk_level": row.risk_level
            })
        
        return {
            "total_analyses": len(analyses),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "analyses": analyses
        }
        
    except Exception as e:
        logger.error(f"Error getting risk analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_risk_metrics(
    start_date: Optional[date] = Query(None, description="Start date for metrics"),
    end_date: Optional[date] = Query(None, description="End date for metrics"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get risk metrics data"""
    try:
        query_parts = ["SELECT * FROM risk_metrics WHERE 1=1"]
        params = {}
        
        if start_date:
            query_parts.append("AND DATE(timestamp) >= :start_date")
            params["start_date"] = start_date
        if end_date:
            query_parts.append("AND DATE(timestamp) <= :end_date")
            params["end_date"] = end_date
        
        query_parts.append("ORDER BY timestamp DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No risk metrics data found")
        
        metrics = []
        for row in rows:
            metrics.append({
                "timestamp": row.timestamp.isoformat(),
                "portfolio_var": float(row.portfolio_var) if row.portfolio_var else None,
                "portfolio_cvar": float(row.portfolio_cvar) if row.portfolio_cvar else None,
                "max_drawdown": float(row.max_drawdown) if row.max_drawdown else None,
                "correlation_risk": float(row.correlation_risk) if row.correlation_risk else None,
                "concentration_risk": float(row.concentration_risk) if row.concentration_risk else None,
                "leverage_ratio": float(row.leverage_ratio) if row.leverage_ratio else None,
                "risk_level": row.risk_level
            })
        
        return {
            "total_metrics": len(metrics),
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monte-carlo")
async def get_monte_carlo_simulations(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    start_date: Optional[date] = Query(None, description="Start date for simulations"),
    end_date: Optional[date] = Query(None, description="End date for simulations"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get Monte Carlo simulation results"""
    try:
        query_parts = ["SELECT * FROM monte_carlo_simulations WHERE 1=1"]
        params = {}
        
        if symbol:
            query_parts.append("AND symbol = :symbol")
            params["symbol"] = symbol
        if start_date:
            query_parts.append("AND DATE(simulation_date) >= :start_date")
            params["start_date"] = start_date
        if end_date:
            query_parts.append("AND DATE(simulation_date) <= :end_date")
            params["end_date"] = end_date
        
        query_parts.append("ORDER BY simulation_date DESC LIMIT :limit")
        params["limit"] = limit
        
        query_sql = " ".join(query_parts)
        result = db.execute(text(query_sql), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No Monte Carlo simulation data found")
        
        simulations = []
        for row in rows:
            simulations.append({
                "simulation_id": row.simulation_id,
                "symbol": row.symbol,
                "simulation_date": row.simulation_date.isoformat(),
                "scenarios": row.scenarios,
                "confidence_level": float(row.confidence_level) if row.confidence_level else None,
                "var_1d": float(row.var_1d) if row.var_1d else None,
                "var_5d": float(row.var_5d) if row.var_5d else None,
                "var_30d": float(row.var_30d) if row.var_30d else None,
                "expected_shortfall": float(row.expected_shortfall) if row.expected_shortfall else None,
                "worst_case_scenario": float(row.worst_case_scenario) if row.worst_case_scenario else None,
                "best_case_scenario": float(row.best_case_scenario) if row.best_case_scenario else None
            })
        
        return {
            "total_simulations": len(simulations),
            "filters": {
                "symbol": symbol,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "simulations": simulations
        }
        
    except Exception as e:
        logger.error(f"Error getting Monte Carlo simulations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_risk_dashboard(
    db: Session = Depends(get_db)
):
    """Get risk management dashboard summary"""
    try:
        # Get latest risk analysis
        latest_analysis_query = """
            SELECT * FROM risk_analysis 
            ORDER BY analysis_date DESC 
            LIMIT 1
        """
        analysis_result = db.execute(text(latest_analysis_query))
        latest_analysis = analysis_result.fetchone()
        
        # Get latest risk metrics
        latest_metrics_query = """
            SELECT * FROM risk_metrics 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        metrics_result = db.execute(text(latest_metrics_query))
        latest_metrics = metrics_result.fetchone()
        
        # Get risk level distribution
        risk_distribution_query = """
            SELECT risk_level, COUNT(*) as count
            FROM risk_metrics 
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY risk_level
        """
        distribution_result = db.execute(text(risk_distribution_query))
        risk_distribution = distribution_result.fetchall()
        
        # Get portfolio risk summary
        portfolio_risk_query = """
            SELECT 
                AVG(portfolio_var) as avg_var,
                AVG(portfolio_cvar) as avg_cvar,
                AVG(max_drawdown) as avg_max_drawdown,
                AVG(correlation_risk) as avg_correlation_risk,
                AVG(concentration_risk) as avg_concentration_risk
            FROM risk_metrics 
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """
        portfolio_result = db.execute(text(portfolio_risk_query))
        portfolio_risk = portfolio_result.fetchone()
        
        return {
            "latest_analysis": {
                "analysis_date": latest_analysis.analysis_date.isoformat() if latest_analysis else None,
                "portfolio_value": float(latest_analysis.portfolio_value) if latest_analysis and latest_analysis.portfolio_value else None,
                "var_1d": float(latest_analysis.var_1d) if latest_analysis and latest_analysis.var_1d else None,
                "risk_score": latest_analysis.risk_score if latest_analysis else None,
                "risk_level": latest_analysis.risk_level if latest_analysis else None
            } if latest_analysis else None,
            "latest_metrics": {
                "timestamp": latest_metrics.timestamp.isoformat() if latest_metrics else None,
                "portfolio_var": float(latest_metrics.portfolio_var) if latest_metrics and latest_metrics.portfolio_var else None,
                "portfolio_cvar": float(latest_metrics.portfolio_cvar) if latest_metrics and latest_metrics.portfolio_cvar else None,
                "max_drawdown": float(latest_metrics.max_drawdown) if latest_metrics and latest_metrics.max_drawdown else None,
                "risk_level": latest_metrics.risk_level if latest_metrics else None
            } if latest_metrics else None,
            "risk_distribution": [
                {
                    "risk_level": r.risk_level,
                    "count": r.count
                } for r in risk_distribution
            ],
            "portfolio_risk_summary": {
                "avg_var": float(portfolio_risk.avg_var) if portfolio_risk and portfolio_risk.avg_var else None,
                "avg_cvar": float(portfolio_risk.avg_cvar) if portfolio_risk and portfolio_risk.avg_cvar else None,
                "avg_max_drawdown": float(portfolio_risk.avg_max_drawdown) if portfolio_risk and portfolio_risk.avg_max_drawdown else None,
                "avg_correlation_risk": float(portfolio_risk.avg_correlation_risk) if portfolio_risk and portfolio_risk.avg_correlation_risk else None,
                "avg_concentration_risk": float(portfolio_risk.avg_concentration_risk) if portfolio_risk and portfolio_risk.avg_concentration_risk else None
            } if portfolio_risk else None
        }
        
    except Exception as e:
        logger.error(f"Error getting risk dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-risk")
async def calculate_portfolio_risk(
    symbols: List[str],
    weights: List[float],
    confidence_level: float = 0.95,
    time_horizon: int = 1,
    db: Session = Depends(get_db)
):
    """Calculate portfolio risk metrics (placeholder for future implementation)"""
    try:
        # This is a placeholder - in a real implementation, this would:
        # 1. Get historical data for the symbols
        # 2. Calculate portfolio returns
        # 3. Calculate VaR, CVaR, and other risk metrics
        # 4. Run Monte Carlo simulations
        # 5. Return comprehensive risk analysis
        
        return {
            "message": "Portfolio risk calculation initiated",
            "symbols": symbols,
            "weights": weights,
            "confidence_level": confidence_level,
            "time_horizon": time_horizon,
            "status": "PENDING",
            "note": "This is a placeholder endpoint. Full risk calculation implementation would be added here."
        }
        
    except Exception as e:
        logger.error(f"Error calculating portfolio risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))
