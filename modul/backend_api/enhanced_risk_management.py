"""
Enhanced Risk Management API Endpoints
======================================

Enhanced risk management module dengan real-time risk calculation,
position limits, dan automated stop-loss untuk mencapai akurasi >80%.

Author: AI Assistant
Date: 2025-01-16
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.services.enhanced_risk_management_service import EnhancedRiskManagementService
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/enhanced-risk-management", tags=["Enhanced Risk Management"])

# Enhanced Pydantic schemas
class RiskAssessmentRequest(BaseModel):
    portfolio_id: str
    symbols: List[str]
    weights: List[float]
    confidence_level: float = 0.95
    time_horizon: int = 1  # days
    
    @validator('weights')
    def validate_weights(cls, v):
        if abs(sum(v) - 1.0) > 0.01:
            raise ValueError('Weights must sum to 1.0')
        return v
    
    @validator('confidence_level')
    def validate_confidence_level(cls, v):
        if not 0.5 <= v <= 0.99:
            raise ValueError('Confidence level must be between 0.5 and 0.99')
        return v

class RiskMetricsResponse(BaseModel):
    portfolio_id: str
    var_95: float
    var_99: float
    expected_shortfall: float
    sharpe_ratio: float
    max_drawdown: float
    concentration_risk: float
    risk_score: float
    risk_level: str  # low, medium, high, critical
    calculated_at: datetime

class PositionLimitRequest(BaseModel):
    symbol: str
    max_position_size: float
    max_daily_loss: float
    stop_loss_percentage: float
    take_profit_percentage: float

class StopLossRequest(BaseModel):
    symbol: str
    current_price: float
    stop_loss_price: float
    quantity: int
    order_type: str = "stop_loss"

class RiskAlertResponse(BaseModel):
    alert_id: str
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    symbol: Optional[str] = None
    portfolio_id: Optional[str] = None
    triggered_at: datetime
    resolved: bool = False

@router.post("/assess", response_model=RiskMetricsResponse)
async def assess_portfolio_risk(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db)
):
    """Assess portfolio risk dengan enhanced calculation"""
    try:
        # Initialize enhanced risk management service
        risk_service = EnhancedRiskManagementService(db)
        
        # Perform risk assessment
        risk_result = await risk_service.assess_portfolio_risk(
            portfolio_id=request.portfolio_id,
            symbols=request.symbols,
            weights=request.weights,
            confidence_level=request.confidence_level,
            time_horizon=request.time_horizon
        )
        
        if "error" in risk_result:
            raise HTTPException(status_code=400, detail=risk_result["error"])
        
        return RiskMetricsResponse(
            portfolio_id=risk_result["portfolio_id"],
            var_95=risk_result["var_95"],
            var_99=risk_result["var_99"],
            expected_shortfall=risk_result["expected_shortfall"],
            sharpe_ratio=risk_result["sharpe_ratio"],
            max_drawdown=risk_result["max_drawdown"],
            concentration_risk=risk_result["concentration_risk"],
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            calculated_at=risk_result["calculated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing portfolio risk: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/position-limits")
async def set_position_limits(
    request: PositionLimitRequest,
    db: Session = Depends(get_db)
):
    """Set position limits dengan enhanced validation"""
    try:
        risk_service = EnhancedRiskManagementService(db)
        
        # Set position limits
        result = await risk_service.set_position_limits(
            symbol=request.symbol,
            max_position_size=request.max_position_size,
            max_daily_loss=request.max_daily_loss,
            stop_loss_percentage=request.stop_loss_percentage,
            take_profit_percentage=request.take_profit_percentage
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "symbol": request.symbol,
            "limits_set": True,
            "limits": result["limits"],
            "set_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting position limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-loss")
async def set_stop_loss(
    request: StopLossRequest,
    db: Session = Depends(get_db)
):
    """Set automated stop-loss dengan enhanced logic"""
    try:
        risk_service = EnhancedRiskManagementService(db)
        
        # Set stop loss
        result = await risk_service.set_stop_loss(
            symbol=request.symbol,
            current_price=request.current_price,
            stop_loss_price=request.stop_loss_price,
            quantity=request.quantity,
            order_type=request.order_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "symbol": request.symbol,
            "stop_loss_set": True,
            "stop_loss_price": request.stop_loss_price,
            "order_id": result.get("order_id"),
            "set_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting stop loss: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts", response_model=List[RiskAlertResponse])
async def get_risk_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    limit: int = Query(50, description="Maximum number of alerts"),
    db: Session = Depends(get_db)
):
    """Get risk alerts dengan enhanced filtering"""
    try:
        risk_service = EnhancedRiskManagementService(db)
        
        # Get risk alerts
        alerts_result = await risk_service.get_risk_alerts(
            severity=severity,
            resolved=resolved,
            limit=limit
        )
        
        if "error" in alerts_result:
            raise HTTPException(status_code=400, detail=alerts_result["error"])
        
        return [
            RiskAlertResponse(
                alert_id=alert["alert_id"],
                alert_type=alert["alert_type"],
                severity=alert["severity"],
                message=alert["message"],
                symbol=alert.get("symbol"),
                portfolio_id=alert.get("portfolio_id"),
                triggered_at=alert["triggered_at"],
                resolved=alert["resolved"]
            )
            for alert in alerts_result["alerts"]
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_risk_dashboard(
    portfolio_id: Optional[str] = Query(None, description="Portfolio ID"),
    db: Session = Depends(get_db)
):
    """Get risk dashboard dengan enhanced metrics"""
    try:
        risk_service = EnhancedRiskManagementService(db)
        
        # Get risk dashboard
        dashboard_result = await risk_service.get_risk_dashboard(portfolio_id)
        
        if "error" in dashboard_result:
            raise HTTPException(status_code=400, detail=dashboard_result["error"])
        
        return {
            "portfolio_id": portfolio_id,
            "dashboard": dashboard_result["dashboard"],
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/resolve")
async def resolve_risk_alert(
    alert_id: str,
    resolution_notes: str = Body(..., description="Resolution notes"),
    db: Session = Depends(get_db)
):
    """Resolve risk alert"""
    try:
        risk_service = EnhancedRiskManagementService(db)
        
        # Resolve alert
        result = await risk_service.resolve_risk_alert(
            alert_id=alert_id,
            resolution_notes=resolution_notes
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "alert_id": alert_id,
            "resolved": True,
            "resolved_at": datetime.now().isoformat(),
            "resolution_notes": resolution_notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving risk alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_enhanced_risk_management_health():
    """Get enhanced risk management module health status"""
    try:
        return {
            "status": "healthy",
            "module": "enhanced_risk_management",
            "version": "2.0.0",
            "features": [
                "real_time_risk_calculation",
                "position_limits",
                "automated_stop_loss",
                "risk_alerts",
                "portfolio_monitoring"
            ],
            "risk_models": [
                "var_calculation",
                "expected_shortfall",
                "sharpe_ratio",
                "max_drawdown",
                "concentration_risk"
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
