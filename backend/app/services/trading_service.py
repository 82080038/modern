"""
Trading Service untuk Order Management dan Portfolio Operations
"""
from sqlalchemy.orm import Session
from app.models.trading import (
    Order, Position, Trade, Portfolio, TaxLot, TradingSession, RiskMetrics,
    OrderType, OrderSide, OrderStatus, TradingMode
)
from app.services.data_service import DataService
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import logging
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class TradingService:
    """Service untuk trading operations"""
    
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
                    trading_mode: TradingMode = TradingMode.TRAINING,
                    auto_trading: bool = False,
                    notes: str = None) -> Dict:
        """Create new order"""
        try:
            # Generate unique order ID
            order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Validate order parameters
            if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and not price:
                return {"error": "Price required for limit orders"}
            
            if order_type in [OrderType.STOP_LOSS, OrderType.STOP_LIMIT] and not stop_price:
                return {"error": "Stop price required for stop orders"}
            
            # Create order
            order = Order(
                order_id=order_id,
                symbol=symbol.upper(),
                order_type=order_type,
                side=side,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                trading_mode=trading_mode,
                auto_trading=auto_trading,
                notes=notes,
                remaining_quantity=quantity
            )
            
            self.db.add(order)
            self.db.commit()
            
            # Auto-execute if in training mode or auto-trading enabled
            if trading_mode == TradingMode.TRAINING or auto_trading:
                execution_result = self._execute_order(order)
                return {
                    "order_id": order_id,
                    "status": "created_and_executed",
                    "execution_result": execution_result
                }
            
            return {
                "order_id": order_id,
                "status": "created",
                "message": "Order created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _execute_order(self, order: Order) -> Dict:
        """Execute order (simulation)"""
        try:
            # Get current price
            price_data = self.data_service.get_real_time_price(order.symbol)
            if not price_data:
                return {"error": "Unable to get current price"}
            
            current_price = price_data.get('price', 0)
            if not current_price:
                return {"error": "Invalid current price"}
            
            # Calculate execution price based on order type
            if order.order_type == OrderType.MARKET:
                execution_price = current_price
            elif order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and current_price <= order.price:
                    execution_price = min(current_price, order.price)
                elif order.side == OrderSide.SELL and current_price >= order.price:
                    execution_price = max(current_price, order.price)
                else:
                    return {"error": "Limit order conditions not met"}
            else:
                # For stop orders, use current price
                execution_price = current_price
            
            # Calculate commission (Indonesian format)
            commission_rate = 0.0015  # 0.15%
            commission = execution_price * order.quantity * commission_rate
            
            # Calculate tax (Indonesian format)
            tax_rate = 0.001  # 0.1% for stock transactions
            tax = execution_price * order.quantity * tax_rate
            
            # Create trade record
            trade_id = f"TRD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            trade = Trade(
                trade_id=trade_id,
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=execution_price,
                commission=commission,
                tax=tax,
                trading_mode=order.trading_mode,
                executed_at=datetime.now()
            )
            
            self.db.add(trade)
            
            # Update order status
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.average_price = execution_price
            order.remaining_quantity = 0
            order.filled_at = datetime.now()
            
            # Update position
            self._update_position(order, execution_price, commission, tax)
            
            self.db.commit()
            
            return {
                "trade_id": trade_id,
                "execution_price": execution_price,
                "commission": commission,
                "tax": tax,
                "total_cost": execution_price * order.quantity + commission + tax
            }
            
        except Exception as e:
            logger.error(f"Error executing order: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _update_position(self, order: Order, execution_price: float, commission: float, tax: float):
        """Update position after trade execution"""
        try:
            # Get or create position
            position = self.db.query(Position).filter(
                Position.symbol == order.symbol,
                Position.trading_mode == order.trading_mode
            ).first()
            
            if not position:
                # Create new position
                position = Position(
                    symbol=order.symbol,
                    quantity=0,
                    average_price=0.0,
                    current_price=execution_price,
                    trading_mode=order.trading_mode,
                    first_buy_date=date.today() if order.side == OrderSide.BUY else None
                )
                self.db.add(position)
            
            # Update position based on trade side
            if order.side == OrderSide.BUY:
                # Add to position
                total_cost = execution_price * order.quantity + commission + tax
                new_quantity = position.quantity + order.quantity
                new_average_price = ((position.average_price * position.quantity) + total_cost) / new_quantity
                
                position.quantity = new_quantity
                position.average_price = new_average_price
                position.current_price = execution_price
                position.last_trade_date = date.today()
                
                # Create tax lot for FIFO/LIFO tracking
                self._create_tax_lot(position.id, order.quantity, execution_price, date.today())
                
            else:  # SELL
                # Reduce position
                if position.quantity < order.quantity:
                    return {"error": "Insufficient position for sell order"}
                
                # Calculate realized P&L using FIFO
                realized_pnl = self._calculate_realized_pnl(position.id, order.quantity, execution_price)
                
                position.quantity -= order.quantity
                position.current_price = execution_price
                position.realized_pnl += realized_pnl
                position.last_trade_date = date.today()
            
            # Update P&L
            position.unrealized_pnl = (position.current_price - position.average_price) * position.quantity
            position.total_pnl = position.realized_pnl + position.unrealized_pnl
            
        except Exception as e:
            logger.error(f"Error updating position: {e}")
            raise e
    
    def _create_tax_lot(self, position_id: int, quantity: int, price: float, purchase_date: date):
        """Create tax lot for FIFO/LIFO tracking"""
        try:
            tax_lot = TaxLot(
                symbol="",  # Will be set by position
                position_id=position_id,
                quantity=quantity,
                cost_basis=price,
                purchase_date=purchase_date,
                remaining_quantity=quantity
            )
            self.db.add(tax_lot)
        except Exception as e:
            logger.error(f"Error creating tax lot: {e}")
    
    def _calculate_realized_pnl(self, position_id: int, sell_quantity: int, sell_price: float) -> float:
        """Calculate realized P&L using FIFO method (Indonesia standard)"""
        try:
            # Get tax lots in FIFO order
            tax_lots = self.db.query(TaxLot).filter(
                TaxLot.position_id == position_id,
                TaxLot.remaining_quantity > 0
            ).order_by(TaxLot.purchase_date.asc()).all()
            
            total_realized_pnl = 0.0
            remaining_sell = sell_quantity
            
            for lot in tax_lots:
                if remaining_sell <= 0:
                    break
                
                sell_from_lot = min(remaining_sell, lot.remaining_quantity)
                cost_basis = lot.cost_basis * sell_from_lot
                proceeds = sell_price * sell_from_lot
                lot_pnl = proceeds - cost_basis
                
                total_realized_pnl += lot_pnl
                lot.remaining_quantity -= sell_from_lot
                lot.sold_quantity += sell_from_lot
                lot.capital_gain += lot_pnl
                
                # Calculate Indonesian tax liability (0.1% of proceeds)
                lot.tax_liability = proceeds * 0.001
                
                remaining_sell -= sell_from_lot
            
            return total_realized_pnl
            
        except Exception as e:
            logger.error(f"Error calculating realized P&L: {e}")
            return 0.0
    
    def get_portfolio_summary(self, trading_mode: TradingMode = TradingMode.TRAINING) -> Dict:
        """Get portfolio summary"""
        try:
            # Get all positions
            positions = self.db.query(Position).filter(
                Position.trading_mode == trading_mode,
                Position.quantity > 0
            ).all()
            
            total_value = 0.0
            total_cost = 0.0
            total_pnl = 0.0
            position_count = len(positions)
            
            position_details = []
            
            for pos in positions:
                # Update current price
                price_data = self.data_service.get_real_time_price(pos.symbol)
                if price_data:
                    pos.current_price = price_data.get('price', pos.current_price)
                    pos.unrealized_pnl = (pos.current_price - pos.average_price) * pos.quantity
                    pos.total_pnl = pos.realized_pnl + pos.unrealized_pnl
                
                position_value = pos.current_price * pos.quantity
                cost_basis = pos.average_price * pos.quantity
                
                total_value += position_value
                total_cost += cost_basis
                total_pnl += pos.total_pnl
                
                position_details.append({
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "average_price": pos.average_price,
                    "current_price": pos.current_price,
                    "position_value": position_value,
                    "cost_basis": cost_basis,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "realized_pnl": pos.realized_pnl,
                    "total_pnl": pos.total_pnl,
                    "pnl_percent": (pos.total_pnl / cost_basis * 100) if cost_basis > 0 else 0
                })
            
            return {
                "trading_mode": trading_mode.value,
                "total_positions": position_count,
                "total_value": total_value,
                "total_cost": total_cost,
                "total_pnl": total_pnl,
                "total_pnl_percent": (total_pnl / total_cost * 100) if total_cost > 0 else 0,
                "positions": position_details
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {"error": str(e)}
    
    def get_order_history(self, 
                         symbol: Optional[str] = None,
                         trading_mode: Optional[TradingMode] = None,
                         limit: int = 50) -> List[Dict]:
        """Get order history"""
        try:
            query = self.db.query(Order)
            
            if symbol:
                query = query.filter(Order.symbol == symbol.upper())
            
            if trading_mode:
                query = query.filter(Order.trading_mode == trading_mode)
            
            orders = query.order_by(Order.created_at.desc()).limit(limit).all()
            
            order_list = []
            for order in orders:
                order_list.append({
                    "order_id": order.order_id,
                    "symbol": order.symbol,
                    "order_type": order.order_type.value,
                    "side": order.side.value,
                    "quantity": order.quantity,
                    "price": order.price,
                    "status": order.status.value,
                    "filled_quantity": order.filled_quantity,
                    "average_price": order.average_price,
                    "trading_mode": order.trading_mode.value,
                    "auto_trading": order.auto_trading,
                    "created_at": order.created_at.isoformat(),
                    "filled_at": order.filled_at.isoformat() if order.filled_at else None
                })
            
            return order_list
            
        except Exception as e:
            logger.error(f"Error getting order history: {e}")
            return []
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel order"""
        try:
            order = self.db.query(Order).filter(Order.order_id == order_id).first()
            
            if not order:
                return {"error": "Order not found"}
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
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
    
    def switch_trading_mode(self, new_mode: TradingMode) -> Dict:
        """Switch trading mode"""
        try:
            # Update all active orders
            active_orders = self.db.query(Order).filter(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.SUBMITTED])
            ).all()
            
            for order in active_orders:
                order.trading_mode = new_mode
                if new_mode == TradingMode.TRAINING:
                    order.auto_trading = True
                else:
                    order.auto_trading = False
            
            self.db.commit()
            
            return {
                "new_mode": new_mode.value,
                "updated_orders": len(active_orders),
                "message": f"Switched to {new_mode.value} mode"
            }
            
        except Exception as e:
            logger.error(f"Error switching trading mode: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_risk_metrics(self, trading_mode: TradingMode = TradingMode.TRAINING) -> Dict:
        """Calculate risk metrics"""
        try:
            portfolio = self.get_portfolio_summary(trading_mode)
            
            if "error" in portfolio:
                return portfolio
            
            # Calculate VaR (simplified)
            positions = portfolio.get("positions", [])
            if not positions:
                return {"error": "No positions to calculate risk metrics"}
            
            # Simple VaR calculation (1-day, 95% confidence)
            returns = []
            for pos in positions:
                if pos["cost_basis"] > 0:
                    return_pct = pos["total_pnl"] / pos["cost_basis"]
                    returns.append(return_pct)
            
            if returns:
                var_1d = np.percentile(returns, 5) * portfolio["total_value"]  # 5th percentile
            else:
                var_1d = 0.0
            
            # Calculate current drawdown
            # This would need historical portfolio values
            current_drawdown = 0.0  # Placeholder
            
            return {
                "portfolio_value": portfolio["total_value"],
                "total_pnl": portfolio["total_pnl"],
                "var_1d": var_1d,
                "current_drawdown": current_drawdown,
                "position_count": portfolio["total_positions"],
                "trading_mode": trading_mode.value
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {"error": str(e)}
