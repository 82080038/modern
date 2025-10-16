"""
Order Management Service dengan Training Mode dan Real-Time Trading Mode
"""
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.trading import (
    Order, Trade, Position, Portfolio, TaxLot, TradingSession, Alert,
    OrderType, OrderStatus, OrderSide, TradingMode
)
from app.services.data_service import DataService
import logging

logger = logging.getLogger(__name__)

class OrderService:
    """Service untuk order management dan trading"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
    
    def create_order(self, 
                    symbol: str,
                    order_type: OrderType,
                    side: OrderSide,
                    quantity: int,
                    price: Optional[float] = None,
                    stop_price: Optional[float] = None,
                    limit_price: Optional[float] = None,
                    trading_mode: TradingMode = TradingMode.TRAINING,
                    auto_trading: bool = False,
                    notes: str = None) -> Dict:
        """Create new order"""
        try:
            # Generate unique order ID
            order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            
            # Validate order parameters
            validation_result = self._validate_order(symbol, order_type, side, quantity, price, stop_price, limit_price)
            if not validation_result["valid"]:
                return {"error": validation_result["message"]}
            
            # Create order
            order = Order(
                order_id=order_id,
                symbol=symbol.upper(),
                order_type=order_type,
                side=side,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                limit_price=limit_price,
                remaining_quantity=quantity,
                trading_mode=trading_mode,
                auto_trading=auto_trading,
                notes=notes
            )
            
            self.db.add(order)
            self.db.commit()
            
            # Auto-execute jika training mode atau auto-trading enabled
            if trading_mode == TradingMode.TRAINING or (trading_mode == TradingMode.REAL_TIME and auto_trading):
                execution_result = self._execute_order(order)
                return {
                    "order_id": order_id,
                    "status": "submitted",
                    "execution_result": execution_result
                }
            else:
                return {
                    "order_id": order_id,
                    "status": "pending",
                    "message": "Order created, waiting for manual execution"
                }
                
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _validate_order(self, symbol: str, order_type: OrderType, side: OrderSide, 
                       quantity: int, price: Optional[float], stop_price: Optional[float], 
                       limit_price: Optional[float]) -> Dict:
        """Validate order parameters"""
        try:
            # Basic validations
            if quantity <= 0:
                return {"valid": False, "message": "Quantity must be positive"}
            
            if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and not price:
                return {"valid": False, "message": "Price required for limit orders"}
            
            if order_type in [OrderType.STOP_LOSS, OrderType.STOP_LIMIT] and not stop_price:
                return {"valid": False, "message": "Stop price required for stop orders"}
            
            if order_type == OrderType.STOP_LIMIT and not limit_price:
                return {"valid": False, "message": "Limit price required for stop-limit orders"}
            
            # Check symbol exists
            # This would typically check against a symbols table
            # For now, we'll assume all symbols are valid
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Error validating order: {e}")
            return {"valid": False, "message": str(e)}
    
    def _execute_order(self, order: Order) -> Dict:
        """Execute order (simulation untuk training mode)"""
        try:
            # Get current market price
            market_data = self.data_service.get_real_time_price(order.symbol)
            if not market_data or not market_data.get('price'):
                return {"error": "Unable to get market price"}
            
            current_price = market_data['price']
            
            # Determine execution price based on order type
            execution_price = self._calculate_execution_price(order, current_price)
            if not execution_price:
                return {"error": "Order conditions not met"}
            
            # Create trade record
            trade_id = f"TRD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            trade_value = order.quantity * execution_price
            
            # Calculate fees (Indonesia format)
            commission_rate = 0.0015  # 0.15%
            tax_rate = 0.001  # 0.1%
            commission = trade_value * commission_rate
            tax = trade_value * tax_rate
            total_fees = commission + tax
            net_amount = trade_value - total_fees
            
            trade = Trade(
                trade_id=trade_id,
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=execution_price,
                trade_value=trade_value,
                trading_mode=order.trading_mode,
                commission=commission,
                tax=tax,
                total_fees=total_fees,
                net_amount=net_amount
            )
            
            self.db.add(trade)
            
            # Update order status
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.remaining_quantity = 0
            order.average_fill_price = execution_price
            order.filled_at = datetime.now()
            order.commission_amount = commission
            order.tax_amount = tax
            order.total_fees = total_fees
            
            # Update position
            self._update_position(order.symbol, order.side, order.quantity, execution_price, order.trading_mode)
            
            # Create tax lot
            self._create_tax_lot(order.symbol, trade_id, order.quantity, execution_price, order.side)
            
            self.db.commit()
            
            return {
                "trade_id": trade_id,
                "execution_price": execution_price,
                "trade_value": trade_value,
                "fees": total_fees,
                "net_amount": net_amount
            }
            
        except Exception as e:
            logger.error(f"Error executing order: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _calculate_execution_price(self, order: Order, current_price: float) -> Optional[float]:
        """Calculate execution price based on order type"""
        try:
            if order.order_type == OrderType.MARKET:
                return current_price
            
            elif order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and order.price >= current_price:
                    return current_price
                elif order.side == OrderSide.SELL and order.price <= current_price:
                    return current_price
                else:
                    return None  # Order conditions not met
            
            elif order.order_type == OrderType.STOP_LOSS:
                if order.side == OrderSide.SELL and current_price <= order.stop_price:
                    return current_price
                elif order.side == OrderSide.BUY and current_price >= order.stop_price:
                    return current_price
                else:
                    return None
            
            elif order.order_type == OrderType.STOP_LIMIT:
                if order.side == OrderSide.SELL and current_price <= order.stop_price:
                    return min(order.limit_price, current_price)
                elif order.side == OrderSide.BUY and current_price >= order.stop_price:
                    return max(order.limit_price, current_price)
                else:
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating execution price: {e}")
            return None
    
    def _update_position(self, symbol: str, side: OrderSide, quantity: int, 
                       price: float, trading_mode: TradingMode):
        """Update position after trade execution"""
        try:
            # Get or create position
            position = self.db.query(Position).filter(
                Position.symbol == symbol,
                Position.trading_mode == trading_mode
            ).first()
            
            if not position:
                position = Position(
                    symbol=symbol,
                    quantity=0,
                    trading_mode=trading_mode
                )
                self.db.add(position)
            
            # Update position
            if side == OrderSide.BUY:
                # Calculate new average price
                if position.quantity >= 0:  # Adding to long position
                    total_value = (position.quantity * (position.average_price or 0)) + (quantity * price)
                    position.quantity += quantity
                    position.average_price = total_value / position.quantity if position.quantity > 0 else 0
                else:  # Reducing short position
                    position.quantity += quantity
                    if position.quantity > 0:
                        position.average_price = price
            else:  # SELL
                if position.quantity > 0:  # Reducing long position
                    position.quantity -= quantity
                    if position.quantity <= 0:
                        position.average_price = 0
                else:  # Adding to short position
                    total_value = (abs(position.quantity) * (position.average_price or 0)) + (quantity * price)
                    position.quantity -= quantity
                    position.average_price = total_value / abs(position.quantity) if position.quantity < 0 else 0
            
            # Update position value and P&L
            position.market_price = price
            position.position_value = abs(position.quantity) * price
            
            # Calculate unrealized P&L
            if position.quantity > 0:  # Long position
                position.unrealized_pnl = (price - position.average_price) * position.quantity
            elif position.quantity < 0:  # Short position
                position.unrealized_pnl = (position.average_price - price) * abs(position.quantity)
            else:
                position.unrealized_pnl = 0
            
            position.total_pnl = position.realized_pnl + position.unrealized_pnl
            position.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating position: {e}")
            raise e
    
    def _create_tax_lot(self, symbol: str, trade_id: str, quantity: int, 
                       price: float, side: OrderSide):
        """Create tax lot untuk FIFO/LIFO tracking"""
        try:
            tax_lot = TaxLot(
                symbol=symbol,
                trade_id=trade_id,
                quantity=quantity if side == OrderSide.BUY else -quantity,
                cost_basis=price,
                acquisition_date=date.today(),
                is_fifo=True  # Default FIFO untuk Indonesia
            )
            
            self.db.add(tax_lot)
            
        except Exception as e:
            logger.error(f"Error creating tax lot: {e}")
            raise e
    
    def get_orders(self, symbol: str = None, status: OrderStatus = None, 
                  trading_mode: TradingMode = None, limit: int = 100) -> List[Dict]:
        """Get orders dengan filtering"""
        try:
            query = self.db.query(Order)
            
            if symbol:
                query = query.filter(Order.symbol == symbol.upper())
            if status:
                query = query.filter(Order.status == status)
            if trading_mode:
                query = query.filter(Order.trading_mode == trading_mode)
            
            orders = query.order_by(Order.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "order_id": order.order_id,
                    "symbol": order.symbol,
                    "order_type": order.order_type.value,
                    "side": order.side.value,
                    "quantity": order.quantity,
                    "price": order.price,
                    "status": order.status.value,
                    "filled_quantity": order.filled_quantity,
                    "remaining_quantity": order.remaining_quantity,
                    "average_fill_price": order.average_fill_price,
                    "trading_mode": order.trading_mode.value,
                    "auto_trading": order.auto_trading,
                    "created_at": order.created_at.isoformat(),
                    "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                    "total_fees": order.total_fees
                }
                for order in orders
            ]
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    def get_positions(self, trading_mode: TradingMode = None) -> List[Dict]:
        """Get current positions"""
        try:
            query = self.db.query(Position)
            
            if trading_mode:
                query = query.filter(Position.trading_mode == trading_mode)
            
            positions = query.all()
            
            return [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "average_price": pos.average_price,
                    "market_price": pos.market_price,
                    "position_value": pos.position_value,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "realized_pnl": pos.realized_pnl,
                    "total_pnl": pos.total_pnl,
                    "trading_mode": pos.trading_mode.value,
                    "updated_at": pos.updated_at.isoformat()
                }
                for pos in positions
            ]
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel pending order"""
        try:
            order = self.db.query(Order).filter(Order.order_id == order_id).first()
            
            if not order:
                return {"error": "Order not found"}
            
            if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
                return {"error": f"Cannot cancel order with status: {order.status.value}"}
            
            order.status = OrderStatus.CANCELLED
            order.cancelled_at = datetime.now()
            
            self.db.commit()
            
            return {
                "order_id": order_id,
                "status": "cancelled",
                "message": "Order cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_trading_session(self, trading_mode: TradingMode) -> Dict:
        """Get or create trading session"""
        try:
            session = self.db.query(TradingSession).filter(
                TradingSession.trading_mode == trading_mode,
                TradingSession.is_active == True
            ).first()
            
            if not session:
                # Create new session
                session_id = f"SES_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
                session = TradingSession(
                    session_id=session_id,
                    trading_mode=trading_mode,
                    session_name=f"{trading_mode.value.title()} Session"
                )
                self.db.add(session)
                self.db.commit()
            
            return {
                "session_id": session.session_id,
                "trading_mode": session.trading_mode.value,
                "auto_trading_enabled": session.auto_trading_enabled,
                "started_at": session.started_at.isoformat(),
                "total_orders": session.total_orders,
                "filled_orders": session.filled_orders,
                "total_pnl": session.total_pnl,
                "is_active": session.is_active
            }
            
        except Exception as e:
            logger.error(f"Error getting trading session: {e}")
            return {"error": str(e)}
    
    def set_auto_trading(self, trading_mode: TradingMode, enabled: bool) -> Dict:
        """Enable/disable auto trading untuk real-time mode"""
        try:
            if trading_mode != TradingMode.REAL_TIME:
                return {"error": "Auto trading only available for real-time mode"}
            
            session = self.db.query(TradingSession).filter(
                TradingSession.trading_mode == trading_mode,
                TradingSession.is_active == True
            ).first()
            
            if session:
                session.auto_trading_enabled = enabled
                self.db.commit()
            
            return {
                "trading_mode": trading_mode.value,
                "auto_trading_enabled": enabled,
                "message": f"Auto trading {'enabled' if enabled else 'disabled'}"
            }
            
        except Exception as e:
            logger.error(f"Error setting auto trading: {e}")
            return {"error": str(e)}
