"""
Trading API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.database import get_db
from app.services.trading_service import TradingService
from app.models.trading import OrderType, OrderSide, TradingMode
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trading", tags=["Trading"])

# Pydantic schemas
class CreateOrderRequest(BaseModel):
    symbol: str
    order_type: str  # market, limit, stop_loss, stop_limit, trailing_stop
    side: str  # buy, sell
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    trading_mode: str = "training"  # training, real_time
    auto_trading: bool = False
    notes: Optional[str] = None

class OrderResponse(BaseModel):
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

class PortfolioSummaryResponse(BaseModel):
    trading_mode: str
    total_positions: int
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    positions: List[Dict]

class RiskMetricsResponse(BaseModel):
    portfolio_value: float
    total_pnl: float
    var_1d: float
    current_drawdown: float
    position_count: int
    trading_mode: str

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_request: CreateOrderRequest,
    db: Session = Depends(get_db)
):
    """Create new order"""
    try:
        # Validate order type
        valid_order_types = ["market", "limit", "stop_loss", "stop_limit", "trailing_stop"]
        if order_request.order_type not in valid_order_types:
            raise HTTPException(status_code=400, detail=f"Invalid order type. Valid options: {valid_order_types}")
        
        # Validate side
        valid_sides = ["buy", "sell"]
        if order_request.side not in valid_sides:
            raise HTTPException(status_code=400, detail=f"Invalid side. Valid options: {valid_sides}")
        
        # Validate trading mode
        valid_modes = ["training", "real_time"]
        if order_request.trading_mode not in valid_modes:
            raise HTTPException(status_code=400, detail=f"Invalid trading mode. Valid options: {valid_modes}")
        
        # Convert to enums
        order_type = OrderType(order_request.order_type)
        side = OrderSide(order_request.side)
        trading_mode = TradingMode(order_request.trading_mode)
        
        # Create trading service
        trading_service = TradingService(db)
        
        # Create order
        result = trading_service.create_order(
            symbol=order_request.symbol,
            order_type=order_type,
            side=side,
            quantity=order_request.quantity,
            price=order_request.price,
            stop_price=order_request.stop_price,
            trading_mode=trading_mode,
            auto_trading=order_request.auto_trading,
            notes=order_request.notes
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Get created order details
        order = db.query(Order).filter(
            Order.order_id == result["order_id"]
        ).first()
        
        if not order:
            raise HTTPException(status_code=500, detail="Order created but not found")
        
        return OrderResponse(
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
            filled_at=order.filled_at.isoformat() if order.filled_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders", response_model=List[OrderResponse])
async def get_order_history(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    trading_mode: Optional[str] = Query(None, description="Filter by trading mode"),
    limit: int = Query(50, description="Maximum number of orders to return"),
    db: Session = Depends(get_db)
):
    """Get order history"""
    try:
        trading_service = TradingService(db)
        
        # Convert trading mode if provided
        trading_mode_enum = None
        if trading_mode:
            if trading_mode not in ["training", "real_time"]:
                raise HTTPException(status_code=400, detail="Invalid trading mode")
            trading_mode_enum = TradingMode(trading_mode)
        
        orders = trading_service.get_order_history(
            symbol=symbol,
            trading_mode=trading_mode_enum,
            limit=limit
        )
        
        return orders
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Cancel order"""
    try:
        trading_service = TradingService(db)
        result = trading_service.cancel_order(order_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    trading_mode: str = Query("training", description="Trading mode: training or real_time"),
    db: Session = Depends(get_db)
):
    """Get portfolio summary"""
    try:
        # Validate trading mode
        if trading_mode not in ["training", "real_time"]:
            raise HTTPException(status_code=400, detail="Invalid trading mode")
        
        trading_mode_enum = TradingMode(trading_mode)
        trading_service = TradingService(db)
        
        portfolio = trading_service.get_portfolio_summary(trading_mode_enum)
        
        if "error" in portfolio:
            raise HTTPException(status_code=400, detail=portfolio["error"])
        
        return PortfolioSummaryResponse(**portfolio)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk", response_model=RiskMetricsResponse)
async def get_risk_metrics(
    trading_mode: str = Query("training", description="Trading mode: training or real_time"),
    db: Session = Depends(get_db)
):
    """Get risk metrics"""
    try:
        # Validate trading mode
        if trading_mode not in ["training", "real_time"]:
            raise HTTPException(status_code=400, detail="Invalid trading mode")
        
        trading_mode_enum = TradingMode(trading_mode)
        trading_service = TradingService(db)
        
        risk_metrics = trading_service.get_risk_metrics(trading_mode_enum)
        
        if "error" in risk_metrics:
            raise HTTPException(status_code=400, detail=risk_metrics["error"])
        
        return RiskMetricsResponse(**risk_metrics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mode/switch")
async def switch_trading_mode(
    new_mode: str = Body(..., description="New trading mode: training or real_time"),
    db: Session = Depends(get_db)
):
    """Switch trading mode"""
    try:
        # Validate trading mode
        if new_mode not in ["training", "real_time"]:
            raise HTTPException(status_code=400, detail="Invalid trading mode")
        
        trading_mode_enum = TradingMode(new_mode)
        trading_service = TradingService(db)
        
        result = trading_service.switch_trading_mode(trading_mode_enum)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching trading mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_positions(
    trading_mode: str = Query("training", description="Trading mode: training or real_time"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    db: Session = Depends(get_db)
):
    """Get current positions"""
    try:
        # Validate trading mode
        if trading_mode not in ["training", "real_time"]:
            raise HTTPException(status_code=400, detail="Invalid trading mode")
        
        trading_mode_enum = TradingMode(trading_mode)
        trading_service = TradingService(db)
        
        portfolio = trading_service.get_portfolio_summary(trading_mode_enum)
        
        if "error" in portfolio:
            raise HTTPException(status_code=400, detail=portfolio["error"])
        
        positions = portfolio.get("positions", [])
        
        # Filter by symbol if provided
        if symbol:
            positions = [p for p in positions if p["symbol"] == symbol.upper()]
        
        return {
            "trading_mode": trading_mode,
            "positions": positions,
            "total_count": len(positions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trade_history(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    trading_mode: Optional[str] = Query(None, description="Filter by trading mode"),
    limit: int = Query(50, description="Maximum number of trades to return"),
    db: Session = Depends(get_db)
):
    """Get trade history"""
    try:
        from app.models.trading import Trade
        
        query = db.query(Trade)
        
        if symbol:
            query = query.filter(Trade.symbol == symbol.upper())
        
        if trading_mode:
            if trading_mode not in ["training", "real_time"]:
                raise HTTPException(status_code=400, detail="Invalid trading mode")
            from app.models.trading import TradingMode
            trading_mode_enum = TradingMode(trading_mode)
            query = query.filter(Trade.trading_mode == trading_mode_enum)
        
        trades = query.order_by(Trade.executed_at.desc()).limit(limit).all()
        
        trade_list = []
        for trade in trades:
            trade_list.append({
                "trade_id": trade.trade_id,
                "order_id": trade.order_id,
                "symbol": trade.symbol,
                "side": trade.side.value,
                "quantity": trade.quantity,
                "price": trade.price,
                "commission": trade.commission,
                "tax": trade.tax,
                "realized_pnl": trade.realized_pnl,
                "trading_mode": trade.trading_mode.value,
                "executed_at": trade.executed_at.isoformat()
            })
        
        return {
            "trades": trade_list,
            "total_count": len(trade_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_trading_status(db: Session = Depends(get_db)):
    """Get current trading status"""
    try:
        from app.models.trading import Order, Position, Trade
        
        # Get current mode (from most recent order)
        latest_order = db.query(Order).order_by(Order.created_at.desc()).first()
        current_mode = latest_order.trading_mode.value if latest_order else "training"
        
        # Get statistics
        total_orders = db.query(Order).count()
        active_orders = db.query(Order).filter(Order.status.in_(["pending", "submitted"])).count()
        total_positions = db.query(Position).filter(Position.quantity > 0).count()
        total_trades = db.query(Trade).count()
        
        return {
            "current_mode": current_mode,
            "total_orders": total_orders,
            "active_orders": active_orders,
            "total_positions": total_positions,
            "total_trades": total_trades,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error getting trading status: {e}")
        raise HTTPException(status_code=500, detail=str(e))