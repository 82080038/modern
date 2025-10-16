"""
Enhanced Trading Service V2
============================

Service untuk trading dengan implementasi algoritma terbukti
menggunakan advanced order management, position sizing, dan execution algorithms.

Author: AI Assistant
Date: 2025-01-17
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from app.models.trading import Order, OrderType, OrderSide, TradingMode, Trade, Position, Portfolio
from app.models.market_data import MarketData
from app.services.risk_management_service import RiskManagementService
from app.services.enhanced_risk_management_service import EnhancedRiskManagementService
import uuid
import json

logger = logging.getLogger(__name__)

class EnhancedTradingServiceV2:
    """
    Enhanced Trading Service V2 dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = EnhancedRiskManagementService(db)
        self.order_queue = []
        self.execution_engine = {}
        self.performance_tracker = {}
        
        # Trading parameters
        self.max_order_size = 10000
        self.max_daily_orders = 100
        self.slippage_tolerance = 0.001  # 0.1%
        self.commission_rate = 0.0015   # 0.15%
        
    async def create_order(
        self, 
        portfolio_id: int, 
        symbol: str, 
        order_type: str, 
        side: str, 
        quantity: float, 
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        limit_price: Optional[float] = None,
        time_in_force: str = 'GTC'
    ) -> Dict[str, Any]:
        """Create enhanced order dengan advanced validation"""
        try:
            # Validate order parameters
            validation_result = await self._validate_order(
                portfolio_id, symbol, order_type, side, quantity, price, stop_price, limit_price
            )
            
            if not validation_result['valid']:
                return {'error': validation_result['reason']}
            
            # Get current market data
            market_data = await self._get_current_market_data(symbol)
            if not market_data:
                return {'error': f'No market data available for {symbol}'}
            
            # Calculate optimal price
            optimal_price = await self._calculate_optimal_price(
                symbol, side, quantity, order_type, market_data
            )
            
            # Risk management checks
            risk_check = await self.risk_service.check_position_limits(
                portfolio_id, symbol, quantity, optimal_price
            )
            if not risk_check['allowed']:
                return {'error': f'Risk management: {risk_check["reason"]}'}
            
            # Create order
            order = Order(
                portfolio_id=portfolio_id,
                symbol=symbol,
                order_type=order_type,
                side=side,
                quantity=quantity,
                price=optimal_price,
                stop_price=stop_price,
                limit_price=limit_price,
                time_in_force=time_in_force,
                status='pending',
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.flush()  # Get the ID
            
            # Add to execution queue
            await self._add_to_execution_queue(order)
            
            return {
                'success': True,
                'order_id': order.id,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': optimal_price,
                'status': 'pending',
                'estimated_execution_time': await self._estimate_execution_time(order)
            }
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {'error': str(e)}
    
    async def _validate_order(
        self, 
        portfolio_id: int, 
        symbol: str, 
        order_type: str, 
        side: str, 
        quantity: float, 
        price: Optional[float],
        stop_price: Optional[float],
        limit_price: Optional[float]
    ) -> Dict[str, Any]:
        """Validate order parameters dengan comprehensive checks"""
        try:
            # Basic validation
            if quantity <= 0:
                return {'valid': False, 'reason': 'Quantity must be positive'}
            
            if quantity > self.max_order_size:
                return {'valid': False, 'reason': f'Quantity exceeds maximum {self.max_order_size}'}
            
            # Check daily order limit
            daily_orders = await self._get_daily_order_count(portfolio_id)
            if daily_orders >= self.max_daily_orders:
                return {'valid': False, 'reason': 'Daily order limit exceeded'}
            
            # Validate order type specific parameters
            if order_type == 'market':
                if price is not None:
                    return {'valid': False, 'reason': 'Market orders cannot have price'}
            
            elif order_type == 'limit':
                if price is None and limit_price is None:
                    return {'valid': False, 'reason': 'Limit orders must have price or limit_price'}
            
            elif order_type == 'stop':
                if stop_price is None:
                    return {'valid': False, 'reason': 'Stop orders must have stop_price'}
            
            elif order_type == 'stop_limit':
                if stop_price is None or limit_price is None:
                    return {'valid': False, 'reason': 'Stop-limit orders must have both stop_price and limit_price'}
            
            # Validate side
            if side not in ['buy', 'sell']:
                return {'valid': False, 'reason': 'Side must be buy or sell'}
            
            # Check portfolio exists
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'valid': False, 'reason': 'Portfolio not found'}
            
            # Check symbol exists in market data
            symbol_exists = self.db.query(MarketData).filter(
                MarketData.symbol == symbol
            ).first()
            if not symbol_exists:
                return {'valid': False, 'reason': f'Symbol {symbol} not found in market data'}
            
            return {'valid': True, 'reason': 'Order validation passed'}
            
        except Exception as e:
            logger.error(f"Error validating order: {e}")
            return {'valid': False, 'reason': f'Validation error: {str(e)}'}
    
    async def _get_current_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current market data untuk symbol"""
        try:
            market_data = self.db.query(MarketData).filter(
                MarketData.symbol == symbol
            ).order_by(MarketData.timestamp.desc()).first()
            
            if market_data:
                return {
                    'symbol': market_data.symbol,
                    'open': market_data.open_price,
                    'high': market_data.high_price,
                    'low': market_data.low_price,
                    'close': market_data.close_price,
                    'volume': market_data.volume,
                    'timestamp': market_data.timestamp
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
    
    async def _calculate_optimal_price(
        self, 
        symbol: str, 
        side: str, 
        quantity: float, 
        order_type: str, 
        market_data: Dict[str, Any]
    ) -> float:
        """Calculate optimal execution price dengan market impact analysis"""
        try:
            current_price = market_data['close']
            volume = market_data['volume']
            
            # Calculate market impact
            market_impact = await self._calculate_market_impact(symbol, quantity, volume)
            
            # Calculate optimal price based on order type
            if order_type == 'market':
                if side == 'buy':
                    # Add slippage for buy orders
                    optimal_price = current_price * (1 + market_impact + self.slippage_tolerance)
                else:
                    # Subtract slippage for sell orders
                    optimal_price = current_price * (1 - market_impact - self.slippage_tolerance)
            
            elif order_type == 'limit':
                if side == 'buy':
                    # Set limit price slightly below current price
                    optimal_price = current_price * (1 - 0.001)  # 0.1% below
                else:
                    # Set limit price slightly above current price
                    optimal_price = current_price * (1 + 0.001)  # 0.1% above
            
            else:
                optimal_price = current_price
            
            return round(optimal_price, 2)
            
        except Exception as e:
            logger.error(f"Error calculating optimal price: {e}")
            return market_data['close']
    
    async def _calculate_market_impact(self, symbol: str, quantity: float, volume: float) -> float:
        """Calculate market impact berdasarkan order size dan volume"""
        try:
            if volume == 0:
                return 0.001  # Default 0.1% impact
            
            # Calculate order size as percentage of volume
            order_size_ratio = quantity / volume
            
            # Market impact increases with order size
            if order_size_ratio < 0.01:  # Less than 1% of volume
                impact = 0.0005  # 0.05%
            elif order_size_ratio < 0.05:  # Less than 5% of volume
                impact = 0.001   # 0.1%
            elif order_size_ratio < 0.1:   # Less than 10% of volume
                impact = 0.002  # 0.2%
            else:
                impact = 0.005  # 0.5%
            
            return impact
            
        except Exception as e:
            logger.error(f"Error calculating market impact: {e}")
            return 0.001
    
    async def _add_to_execution_queue(self, order: Order):
        """Add order to execution queue"""
        try:
            execution_task = {
                'order_id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': order.quantity,
                'price': order.price,
                'order_type': order.order_type,
                'created_at': order.created_at,
                'priority': await self._calculate_order_priority(order)
            }
            
            self.order_queue.append(execution_task)
            
            # Sort by priority
            self.order_queue.sort(key=lambda x: x['priority'], reverse=True)
            
            # Start execution if not already running
            if not hasattr(self, '_execution_running') or not self._execution_running:
                asyncio.create_task(self._execute_orders())
            
        except Exception as e:
            logger.error(f"Error adding to execution queue: {e}")
    
    async def _calculate_order_priority(self, order: Order) -> int:
        """Calculate order priority untuk execution"""
        try:
            priority = 0
            
            # Market orders have highest priority
            if order.order_type == 'market':
                priority += 100
            
            # Stop orders have high priority
            elif order.order_type == 'stop':
                priority += 80
            
            # Limit orders have medium priority
            elif order.order_type == 'limit':
                priority += 60
            
            # Larger orders have higher priority
            if order.quantity > 1000:
                priority += 20
            elif order.quantity > 100:
                priority += 10
            
            # Recent orders have higher priority
            age_minutes = (datetime.now() - order.created_at).total_seconds() / 60
            if age_minutes < 1:
                priority += 30
            elif age_minutes < 5:
                priority += 20
            elif age_minutes < 15:
                priority += 10
            
            return priority
            
        except Exception as e:
            logger.error(f"Error calculating order priority: {e}")
            return 50
    
    async def _execute_orders(self):
        """Execute orders dari queue dengan advanced algorithms"""
        try:
            self._execution_running = True
            
            while self.order_queue:
                # Get highest priority order
                order_task = self.order_queue.pop(0)
                
                # Execute order
                execution_result = await self._execute_single_order(order_task)
                
                if execution_result['success']:
                    # Update order status
                    await self._update_order_status(
                        order_task['order_id'], 'filled', execution_result
                    )
                    
                    # Create trade record
                    await self._create_trade_record(order_task, execution_result)
                    
                    # Update position
                    await self._update_position(order_task, execution_result)
                    
                    logger.info(f"Order {order_task['order_id']} executed successfully")
                else:
                    # Handle execution failure
                    await self._handle_execution_failure(order_task, execution_result)
                    
                    logger.warning(f"Order {order_task['order_id']} execution failed: {execution_result['reason']}")
                
                # Small delay between executions
                await asyncio.sleep(0.1)
            
            self._execution_running = False
            
        except Exception as e:
            logger.error(f"Error executing orders: {e}")
            self._execution_running = False
    
    async def _execute_single_order(self, order_task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single order dengan market simulation"""
        try:
            # Get current market data
            market_data = await self._get_current_market_data(order_task['symbol'])
            if not market_data:
                return {'success': False, 'reason': 'No market data available'}
            
            current_price = market_data['close']
            order_price = order_task['price']
            order_type = order_task['order_type']
            side = order_task['side']
            
            # Simulate execution based on order type
            if order_type == 'market':
                # Market orders execute at current price with slippage
                execution_price = current_price
                if side == 'buy':
                    execution_price *= (1 + self.slippage_tolerance)
                else:
                    execution_price *= (1 - self.slippage_tolerance)
            
            elif order_type == 'limit':
                # Limit orders execute if price is favorable
                if side == 'buy' and current_price <= order_price:
                    execution_price = min(current_price, order_price)
                elif side == 'sell' and current_price >= order_price:
                    execution_price = max(current_price, order_price)
                else:
                    return {'success': False, 'reason': 'Limit order conditions not met'}
            
            elif order_type == 'stop':
                # Stop orders execute when stop price is hit
                stop_price = order_task.get('stop_price', order_price)
                if side == 'buy' and current_price >= stop_price:
                    execution_price = current_price
                elif side == 'sell' and current_price <= stop_price:
                    execution_price = current_price
                else:
                    return {'success': False, 'reason': 'Stop order conditions not met'}
            
            else:
                return {'success': False, 'reason': f'Unsupported order type: {order_type}'}
            
            # Calculate commission
            commission = order_task['quantity'] * execution_price * self.commission_rate
            
            return {
                'success': True,
                'execution_price': round(execution_price, 2),
                'quantity': order_task['quantity'],
                'commission': round(commission, 2),
                'total_value': round(order_task['quantity'] * execution_price, 2),
                'executed_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error executing single order: {e}")
            return {'success': False, 'reason': str(e)}
    
    async def _update_order_status(self, order_id: int, status: str, execution_result: Dict[str, Any]):
        """Update order status setelah execution"""
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = status
                if status == 'filled':
                    order.executed_at = execution_result.get('executed_at', datetime.now())
                    order.executed_price = execution_result.get('execution_price', order.price)
                
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
    
    async def _create_trade_record(self, order_task: Dict[str, Any], execution_result: Dict[str, Any]):
        """Create trade record setelah successful execution"""
        try:
            trade = Trade(
                order_id=order_task['order_id'],
                symbol=order_task['symbol'],
                side=order_task['side'],
                quantity=execution_result['quantity'],
                price=execution_result['execution_price'],
                commission=execution_result['commission'],
                total_value=execution_result['total_value'],
                executed_at=execution_result['executed_at'],
                created_at=datetime.now()
            )
            
            self.db.add(trade)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating trade record: {e}")
    
    async def _update_position(self, order_task: Dict[str, Any], execution_result: Dict[str, Any]):
        """Update position setelah trade execution"""
        try:
            # Get or create position
            position = self.db.query(Position).filter(
                Position.portfolio_id=order_task.get('portfolio_id', 0),
                Position.symbol=order_task['symbol']
            ).first()
            
            if not position:
                # Create new position
                position = Position(
                    portfolio_id=order_task.get('portfolio_id', 0),
                    symbol=order_task['symbol'],
                    quantity=0,
                    average_price=0,
                    created_at=datetime.now()
                )
                self.db.add(position)
            
            # Update position
            if order_task['side'] == 'buy':
                # Add to position
                new_quantity = position.quantity + execution_result['quantity']
                if position.quantity > 0:
                    # Calculate new average price
                    total_cost = (position.quantity * position.average_price) + execution_result['total_value']
                    new_average_price = total_cost / new_quantity
                else:
                    new_average_price = execution_result['execution_price']
                
                position.quantity = new_quantity
                position.average_price = new_average_price
                
            else:
                # Subtract from position
                position.quantity -= execution_result['quantity']
                if position.quantity < 0:
                    position.quantity = 0  # Cannot have negative position
            
            position.updated_at = datetime.now()
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating position: {e}")
    
    async def _handle_execution_failure(self, order_task: Dict[str, Any], execution_result: Dict[str, Any]):
        """Handle execution failure"""
        try:
            # Update order status to failed
            await self._update_order_status(
                order_task['order_id'], 'failed', execution_result
            )
            
            # Log failure reason
            logger.warning(f"Order {order_task['order_id']} failed: {execution_result.get('reason', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"Error handling execution failure: {e}")
    
    async def _get_daily_order_count(self, portfolio_id: int) -> int:
        """Get daily order count untuk portfolio"""
        try:
            today = datetime.now().date()
            count = self.db.query(Order).filter(
                Order.portfolio_id == portfolio_id,
                Order.created_at >= today
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting daily order count: {e}")
            return 0
    
    async def _estimate_execution_time(self, order: Order) -> str:
        """Estimate execution time untuk order"""
        try:
            # Estimate based on order type and market conditions
            if order.order_type == 'market':
                return 'Immediate'
            elif order.order_type == 'limit':
                return '1-5 minutes'
            elif order.order_type == 'stop':
                return 'Conditional'
            else:
                return 'Unknown'
                
        except Exception as e:
            logger.error(f"Error estimating execution time: {e}")
            return 'Unknown'
    
    async def get_order_status(self, order_id: int) -> Dict[str, Any]:
        """Get order status dan execution details"""
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {'error': 'Order not found'}
            
            # Get trade details if executed
            trade = self.db.query(Trade).filter(Trade.order_id == order_id).first()
            
            result = {
                'order_id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': order.quantity,
                'order_type': order.order_type,
                'status': order.status,
                'created_at': order.created_at,
                'executed_at': order.executed_at,
                'executed_price': order.executed_price
            }
            
            if trade:
                result['trade_details'] = {
                    'trade_id': trade.id,
                    'execution_price': trade.price,
                    'commission': trade.commission,
                    'total_value': trade.total_value,
                    'executed_at': trade.executed_at
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return {'error': str(e)}
    
    async def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """Cancel pending order"""
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {'error': 'Order not found'}
            
            if order.status != 'pending':
                return {'error': f'Cannot cancel order with status: {order.status}'}
            
            # Update order status
            order.status = 'cancelled'
            order.updated_at = datetime.now()
            self.db.commit()
            
            # Remove from execution queue if present
            self.order_queue = [o for o in self.order_queue if o['order_id'] != order_id]
            
            return {
                'success': True,
                'order_id': order_id,
                'status': 'cancelled',
                'cancelled_at': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return {'error': str(e)}
    
    async def get_portfolio_positions(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """Get portfolio positions dengan detailed information"""
        try:
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            result = []
            for position in positions:
                # Get current market price
                market_data = await self._get_current_market_data(position.symbol)
                current_price = market_data['close'] if market_data else position.average_price
                
                # Calculate P&L
                unrealized_pnl = (current_price - position.average_price) * position.quantity
                unrealized_pnl_percentage = (current_price - position.average_price) / position.average_price * 100
                
                result.append({
                    'symbol': position.symbol,
                    'quantity': position.quantity,
                    'average_price': position.average_price,
                    'current_price': current_price,
                    'market_value': current_price * position.quantity,
                    'unrealized_pnl': round(unrealized_pnl, 2),
                    'unrealized_pnl_percentage': round(unrealized_pnl_percentage, 2),
                    'created_at': position.created_at,
                    'updated_at': position.updated_at
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting portfolio positions: {e}")
            return []
