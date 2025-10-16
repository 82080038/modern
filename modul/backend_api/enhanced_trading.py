"""
Enhanced Trading API Endpoints
=============================

Enhanced trading module dengan error handling, validation, dan risk controls
yang diperbaiki untuk mencapai akurasi >80%.

Author: AI Assistant
Date: 2025-01-16
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import get_db
from app.services.enhanced_trading_service import EnhancedTradingService
from app.models.trading import OrderType, OrderSide, TradingMode
from pydantic import BaseModel, validator
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/enhanced-trading", tags=["Enhanced Trading"])

# Enhanced Pydantic schemas with validation
class EnhancedCreateOrderRequest(BaseModel):
    symbol: str
    order_type: str
    side: str
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    trading_mode: str = "training"
    auto_trading: bool = False
    notes: Optional[str] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v) < 1 or len(v) > 10:
            raise ValueError('Symbol must be 1-10 characters')
        return v.upper()
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        if v > 10000:
            raise ValueError('Quantity cannot exceed 10,000')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('order_type')
    def validate_order_type(cls, v):
        valid_types = ["market", "limit", "stop_loss", "stop_limit", "trailing_stop"]
        if v not in valid_types:
            raise ValueError(f'Invalid order type. Must be one of: {valid_types}')
        return v
    
    @validator('side')
    def validate_side(cls, v):
        if v not in ["buy", "sell"]:
            raise ValueError('Side must be "buy" or "sell"')
        return v
    
    @validator('trading_mode')
    def validate_trading_mode(cls, v):
        if v not in ["training", "real_time"]:
            raise ValueError('Trading mode must be "training" or "real_time"')
        return v

class EnhancedOrderResponse(BaseModel):
    order_id: str
    symbol: str
    order_type: str
    side: str
    quantity: int
    price: Optional[float]
    status: str
    filled_quantity: int
    average_price: Optional[float]
    trading_mode: str
    auto_trading: bool
    created_at: str
    filled_at: Optional[str] = None
    risk_score: Optional[float] = None
    validation_status: str = "validated"

class RiskAssessmentResponse(BaseModel):
    order_id: str
    risk_score: float
    risk_level: str  # low, medium, high, critical
    warnings: List[str]
    recommendations: List[str]
    approved: bool

class EnhancedPortfolioSummaryResponse(BaseModel):
    trading_mode: str
    total_positions: int
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    position_count: int
    risk_metrics: Dict[str, Any]
    performance_score: float

@router.post("/orders", response_model=EnhancedOrderResponse)
async def create_enhanced_order(
    order_request: EnhancedCreateOrderRequest,
    db: Session = Depends(get_db)
):
    """Create new order with enhanced validation and risk controls"""
    try:
        # Initialize enhanced trading service
        trading_service = EnhancedTradingService(db)
        
        # Pre-order validation
        validation_result = await trading_service.validate_order(order_request)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=400, 
                detail=f"Order validation failed: {validation_result['errors']}"
            )
        
        # Risk assessment
        risk_assessment = await trading_service.assess_risk(order_request)
        if not risk_assessment['approved']:
            raise HTTPException(
                status_code=400,
                detail=f"Order rejected due to risk: {risk_assessment['reason']}"
            )
        
        # Create order with enhanced error handling
        result = await trading_service.create_enhanced_order(
            symbol=order_request.symbol,
            order_type=order_request.order_type,
            side=order_request.side,
            quantity=order_request.quantity,
            price=order_request.price,
            stop_price=order_request.stop_price,
            trading_mode=order_request.trading_mode,
            auto_trading=order_request.auto_trading,
            notes=order_request.notes,
            risk_score=risk_assessment['risk_score']
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Get created order details
        order = db.query(Order).filter(
            Order.order_id == result["order_id"]
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found after creation")
        
        return EnhancedOrderResponse(
            order_id=order.order_id,
            symbol=order.symbol,
            order_type=order.order_type.value,
            side=order.side.value,
            quantity=order.quantity,
            price=order.price,
            status=order.status.value,
            filled_quantity=order.filled_quantity,
            average_price=order.average_price,
            trading_mode=order.trading_mode.value,
            auto_trading=order.auto_trading,
            created_at=order.created_at.isoformat(),
            filled_at=order.filled_at.isoformat() if order.filled_at else None,
            risk_score=risk_assessment['risk_score'],
            validation_status="validated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating enhanced order: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/orders/{order_id}/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_order_risk(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Assess risk for a specific order"""
    try:
        trading_service = EnhancedTradingService(db)
        
        # Get order
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Perform risk assessment
        risk_assessment = await trading_service.assess_order_risk(order)
        
        return RiskAssessmentResponse(
            order_id=order_id,
            risk_score=risk_assessment['risk_score'],
            risk_level=risk_assessment['risk_level'],
            warnings=risk_assessment['warnings'],
            recommendations=risk_assessment['recommendations'],
            approved=risk_assessment['approved']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing order risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}", response_model=EnhancedOrderResponse)
async def get_enhanced_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Get order details with enhanced information"""
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get risk assessment for the order
        trading_service = EnhancedTradingService(db)
        risk_assessment = await trading_service.get_order_risk_score(order_id)
        
        return EnhancedOrderResponse(
            order_id=order.order_id,
            symbol=order.symbol,
            order_type=order.order_type.value,
            side=order.side.value,
            quantity=order.quantity,
            price=order.price,
            status=order.status.value,
            filled_quantity=order.filled_quantity,
            average_price=order.average_price,
            trading_mode=order.trading_mode.value,
            auto_trading=order.auto_trading,
            created_at=order.created_at.isoformat(),
            filled_at=order.filled_at.isoformat() if order.filled_at else None,
            risk_score=risk_assessment.get('risk_score'),
            validation_status="validated"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enhanced order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/enhanced", response_model=EnhancedPortfolioSummaryResponse)
async def get_enhanced_portfolio(
    trading_mode: str = Query("training", description="Trading mode: training or real_time"),
    db: Session = Depends(get_db)
):
    """Get enhanced portfolio summary with risk metrics"""
    try:
        # Validate trading mode
        if trading_mode not in ["training", "real_time"]:
            raise HTTPException(status_code=400, detail="Invalid trading mode")
        
        trading_mode_enum = TradingMode(trading_mode)
        trading_service = EnhancedTradingService(db)
        
        # Get enhanced portfolio summary
        portfolio = await trading_service.get_enhanced_portfolio_summary(trading_mode_enum)
        
        if "error" in portfolio:
            raise HTTPException(status_code=400, detail=portfolio["error"])
        
        return EnhancedPortfolioSummaryResponse(
            trading_mode=trading_mode,
            total_positions=portfolio.get("total_positions", 0),
            total_value=portfolio.get("total_value", 0.0),
            total_cost=portfolio.get("total_cost", 0.0),
            total_pnl=portfolio.get("total_pnl", 0.0),
            total_pnl_percent=portfolio.get("total_pnl_percent", 0.0),
            position_count=portfolio.get("position_count", 0),
            risk_metrics=portfolio.get("risk_metrics", {}),
            performance_score=portfolio.get("performance_score", 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enhanced portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/analytics")
async def get_trading_performance_analytics(
    trading_mode: str = Query("training", description="Trading mode"),
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get comprehensive trading performance analytics"""
    try:
        trading_service = EnhancedTradingService(db)
        
        analytics = await trading_service.get_performance_analytics(
            trading_mode=trading_mode,
            days=days
        )
        
        return {
            "trading_mode": trading_mode,
            "analysis_period_days": days,
            "analytics": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/{order_id}/cancel")
async def cancel_enhanced_order(
    order_id: str,
    reason: str = Body(..., description="Cancellation reason"),
    db: Session = Depends(get_db)
):
    """Cancel order with enhanced validation"""
    try:
        trading_service = EnhancedTradingService(db)
        
        result = await trading_service.cancel_enhanced_order(
            order_id=order_id,
            reason=reason
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "order_id": order_id,
            "status": "cancelled",
            "reason": reason,
            "cancelled_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling enhanced order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_enhanced_trading_health():
    """Get enhanced trading module health status"""
    try:
        return {
            "status": "healthy",
            "module": "enhanced_trading",
            "version": "2.0.0",
            "features": [
                "enhanced_validation",
                "risk_assessment",
                "error_handling",
                "performance_monitoring"
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
