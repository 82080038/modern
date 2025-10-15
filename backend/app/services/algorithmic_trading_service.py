"""
Algorithmic Trading Engine Service
Real-time strategy execution dan risk management
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.trading import Strategy, StrategyRule, Order, Position, Portfolio
from app.models.market_data import MarketData
from app.services.strategy_builder_service import StrategyBuilderService
from app.services.risk_management_service import RiskManagementService
import logging

logger = logging.getLogger(__name__)

class AlgorithmicTradingEngine:
    """Algorithmic Trading Engine untuk real-time strategy execution"""
    
    def __init__(self, db: Session):
        self.db = db
        self.strategy_service = StrategyBuilderService(db)
        self.risk_service = RiskManagementService(db)
        self.running_strategies = {}
        self.market_data_cache = {}
    
    async def start_strategy(self, strategy_id: int, portfolio_id: int) -> Dict:
        """Start algorithmic trading strategy"""
        try:
            # Check if strategy is already running
            if strategy_id in self.running_strategies:
                return {"error": "Strategy is already running"}
            
            # Get strategy
            strategy_data = self.strategy_service.get_strategy(strategy_id)
            if "error" in strategy_data:
                return {"error": strategy_data["error"]}
            
            # Validate portfolio
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == portfolio_id
            ).first()
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Start strategy execution
            strategy_task = asyncio.create_task(
                self._execute_strategy(strategy_id, portfolio_id, strategy_data)
            )
            
            self.running_strategies[strategy_id] = {
                "task": strategy_task,
                "portfolio_id": portfolio_id,
                "started_at": datetime.now(),
                "status": "running"
            }
            
            return {
                "success": True,
                "message": f"Strategy {strategy_data['name']} started successfully",
                "strategy_id": strategy_id,
                "portfolio_id": portfolio_id
            }
            
        except Exception as e:
            logger.error(f"Error starting strategy: {e}")
            return {"error": str(e)}
    
    async def stop_strategy(self, strategy_id: int) -> Dict:
        """Stop algorithmic trading strategy"""
        try:
            if strategy_id not in self.running_strategies:
                return {"error": "Strategy is not running"}
            
            # Cancel strategy task
            strategy_info = self.running_strategies[strategy_id]
            strategy_info["task"].cancel()
            
            # Update status
            strategy_info["status"] = "stopped"
            strategy_info["stopped_at"] = datetime.now()
            
            # Remove from running strategies
            del self.running_strategies[strategy_id]
            
            return {
                "success": True,
                "message": "Strategy stopped successfully",
                "strategy_id": strategy_id
            }
            
        except Exception as e:
            logger.error(f"Error stopping strategy: {e}")
            return {"error": str(e)}
    
    async def get_running_strategies(self) -> Dict:
        """Get all running strategies"""
        try:
            running_strategies = []
            for strategy_id, info in self.running_strategies.items():
                running_strategies.append({
                    "strategy_id": strategy_id,
                    "portfolio_id": info["portfolio_id"],
                    "status": info["status"],
                    "started_at": info["started_at"].isoformat(),
                    "uptime": (datetime.now() - info["started_at"]).total_seconds()
                })
            
            return {
                "running_strategies": running_strategies,
                "total": len(running_strategies)
            }
            
        except Exception as e:
            logger.error(f"Error getting running strategies: {e}")
            return {"error": str(e)}
    
    async def _execute_strategy(self, strategy_id: int, portfolio_id: int, strategy_data: Dict):
        """Execute strategy in real-time"""
        try:
            logger.info(f"Starting strategy execution: {strategy_data['name']}")
            
            while True:
                try:
                    # Get current market data
                    market_data = await self._get_market_data(strategy_data.get("symbols", []))
                    
                    # Evaluate strategy rules
                    signals = await self._evaluate_strategy_rules(
                        strategy_id, strategy_data["rules"], market_data
                    )
                    
                    # Execute trades based on signals
                    for signal in signals:
                        await self._execute_trade_signal(
                            strategy_id, portfolio_id, signal
                        )
                    
                    # Wait for next evaluation cycle
                    await asyncio.sleep(60)  # Evaluate every minute
                    
                except asyncio.CancelledError:
                    logger.info(f"Strategy {strategy_id} execution cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in strategy execution: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Error in strategy execution loop: {e}")
    
    async def _get_market_data(self, symbols: List[str]) -> Dict:
        """Get current market data for symbols"""
        try:
            market_data = {}
            
            for symbol in symbols:
                # Get latest market data
                latest_data = self.db.query(MarketData).filter(
                    MarketData.symbol == symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    market_data[symbol] = {
                        "price": latest_data.last_price,
                        "change": latest_data.change,
                        "change_percent": latest_data.change_percent,
                        "volume": latest_data.volume,
                        "timestamp": latest_data.timestamp
                    }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {}
    
    async def _evaluate_strategy_rules(self, strategy_id: int, rules: List[Dict], market_data: Dict) -> List[Dict]:
        """Evaluate strategy rules and generate signals"""
        try:
            signals = []
            
            for rule in rules:
                try:
                    # Evaluate rule condition
                    condition_met = await self._evaluate_condition(
                        rule["condition"], market_data
                    )
                    
                    if condition_met:
                        signal = {
                            "strategy_id": strategy_id,
                            "action": rule["action"],
                            "symbol": self._extract_symbol_from_condition(rule["condition"]),
                            "parameters": rule.get("parameters", {}),
                            "timestamp": datetime.now(),
                            "rule_type": rule["type"]
                        }
                        signals.append(signal)
                        
                except Exception as e:
                    logger.error(f"Error evaluating rule: {e}")
                    continue
            
            return signals
            
        except Exception as e:
            logger.error(f"Error evaluating strategy rules: {e}")
            return []
    
    async def _evaluate_condition(self, condition: str, market_data: Dict) -> bool:
        """Evaluate trading condition (simplified)"""
        try:
            # This is a simplified condition evaluator
            # In a real implementation, you would parse the condition string
            # and evaluate it against market data
            
            # For now, return random evaluation for demo
            import random
            return random.random() > 0.7  # 30% chance of signal
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _extract_symbol_from_condition(self, condition: str) -> str:
        """Extract symbol from condition string"""
        try:
            # Simplified symbol extraction
            # In a real implementation, you would parse the condition
            return "AAPL"  # Default symbol for demo
            
        except Exception as e:
            logger.error(f"Error extracting symbol: {e}")
            return "AAPL"
    
    async def _execute_trade_signal(self, strategy_id: int, portfolio_id: int, signal: Dict):
        """Execute trade signal"""
        try:
            # Check risk management
            risk_check = await self._check_risk_limits(portfolio_id, signal)
            if not risk_check["allowed"]:
                logger.warning(f"Trade blocked by risk management: {risk_check['reason']}")
                return
            
            # Create order
            order = Order(
                portfolio_id=portfolio_id,
                symbol=signal["symbol"],
                order_type="market",
                side=signal["action"],
                quantity=signal.get("parameters", {}).get("quantity", 100),
                price=0,  # Market order
                status="pending",
                strategy_id=strategy_id,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            
            # Simulate order execution
            await self._simulate_order_execution(order)
            
            logger.info(f"Trade executed: {signal['action']} {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error executing trade signal: {e}")
    
    async def _check_risk_limits(self, portfolio_id: int, signal: Dict) -> Dict:
        """Check risk management limits"""
        try:
            # Get portfolio
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == portfolio_id
            ).first()
            
            if not portfolio:
                return {"allowed": False, "reason": "Portfolio not found"}
            
            # Check position limits
            current_positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.symbol == signal["symbol"]
            ).all()
            
            total_quantity = sum([pos.quantity for pos in current_positions])
            max_position_size = portfolio.total_value * 0.1  # 10% max position
            
            if total_quantity >= max_position_size:
                return {
                    "allowed": False,
                    "reason": "Position size limit exceeded"
                }
            
            # Check daily loss limit
            today_trades = self.db.query(Order).filter(
                Order.portfolio_id == portfolio_id,
                Order.created_at >= datetime.now().date(),
                Order.status == "filled"
            ).all()
            
            today_pnl = sum([trade.realized_pnl or 0 for trade in today_trades])
            max_daily_loss = portfolio.total_value * 0.05  # 5% max daily loss
            
            if today_pnl <= -max_daily_loss:
                return {
                    "allowed": False,
                    "reason": "Daily loss limit exceeded"
                }
            
            return {"allowed": True}
            
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return {"allowed": False, "reason": "Risk check failed"}
    
    async def _simulate_order_execution(self, order: Order):
        """Simulate order execution (for demo)"""
        try:
            # Simulate execution delay
            await asyncio.sleep(1)
            
            # Update order status
            order.status = "filled"
            order.filled_at = datetime.now()
            order.filled_price = order.price or 100.0  # Mock price
            
            # Update position
            await self._update_position(order)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error simulating order execution: {e}")
    
    async def _update_position(self, order: Order):
        """Update portfolio position"""
        try:
            # Get existing position
            position = self.db.query(Position).filter(
                Position.portfolio_id == order.portfolio_id,
                Position.symbol == order.symbol
            ).first()
            
            if position:
                # Update existing position
                if order.side == "buy":
                    new_quantity = position.quantity + order.quantity
                    new_avg_price = (
                        (position.quantity * position.average_price) + 
                        (order.quantity * order.filled_price)
                    ) / new_quantity
                    
                    position.quantity = new_quantity
                    position.average_price = new_avg_price
                else:  # sell
                    position.quantity = max(0, position.quantity - order.quantity)
            else:
                # Create new position
                if order.side == "buy":
                    position = Position(
                        portfolio_id=order.portfolio_id,
                        symbol=order.symbol,
                        quantity=order.quantity,
                        average_price=order.filled_price,
                        created_at=datetime.now()
                    )
                    self.db.add(position)
            
        except Exception as e:
            logger.error(f"Error updating position: {e}")
    
    async def get_strategy_performance(self, strategy_id: int) -> Dict:
        """Get strategy performance metrics"""
        try:
            if strategy_id not in self.running_strategies:
                return {"error": "Strategy is not running"}
            
            strategy_info = self.running_strategies[strategy_id]
            portfolio_id = strategy_info["portfolio_id"]
            
            # Get strategy trades
            trades = self.db.query(Order).filter(
                Order.strategy_id == strategy_id,
                Order.status == "filled"
            ).all()
            
            if not trades:
                return {
                    "strategy_id": strategy_id,
                    "total_trades": 0,
                    "total_pnl": 0,
                    "win_rate": 0,
                    "uptime": (datetime.now() - strategy_info["started_at"]).total_seconds()
                }
            
            # Calculate metrics
            total_pnl = sum([trade.realized_pnl or 0 for trade in trades])
            winning_trades = len([t for t in trades if (t.realized_pnl or 0) > 0])
            win_rate = (winning_trades / len(trades)) * 100 if trades else 0
            
            return {
                "strategy_id": strategy_id,
                "total_trades": len(trades),
                "total_pnl": total_pnl,
                "win_rate": win_rate,
                "uptime": (datetime.now() - strategy_info["started_at"]).total_seconds(),
                "status": strategy_info["status"]
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy performance: {e}")
            return {"error": str(e)}
