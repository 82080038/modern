"""
Strategy Builder Service
Visual strategy builder untuk trading algorithms
"""
import json
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.trading import Strategy, StrategyRule, StrategyBacktest
from app.models.market_data import HistoricalData
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StrategyBuilderService:
    """Service untuk Strategy Builder"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_strategy(self, strategy_data: Dict) -> Dict:
        """Create new trading strategy"""
        try:
            # Validate strategy data
            validation_result = self._validate_strategy_data(strategy_data)
            if not validation_result["valid"]:
                return {"error": validation_result["message"]}
            
            # Create strategy
            strategy = Strategy(
                name=strategy_data["name"],
                description=strategy_data.get("description", ""),
                strategy_type=strategy_data.get("strategy_type", "custom"),
                is_active=True,
                created_at=datetime.now()
            )
            
            self.db.add(strategy)
            self.db.flush()  # Get strategy ID
            
            # Create strategy rules
            rules = strategy_data.get("rules", [])
            for rule_data in rules:
                rule = StrategyRule(
                    strategy_id=strategy.id,
                    rule_type=rule_data["type"],
                    condition=rule_data["condition"],
                    action=rule_data["action"],
                    parameters=json.dumps(rule_data.get("parameters", {})),
                    order=rule_data.get("order", 0)
                )
                self.db.add(rule)
            
            self.db.commit()
            
            return {
                "success": True,
                "strategy_id": strategy.id,
                "message": "Strategy created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating strategy: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def update_strategy(self, strategy_id: int, strategy_data: Dict) -> Dict:
        """Update existing strategy"""
        try:
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return {"error": "Strategy not found"}
            
            # Update strategy fields
            strategy.name = strategy_data.get("name", strategy.name)
            strategy.description = strategy_data.get("description", strategy.description)
            strategy.strategy_type = strategy_data.get("strategy_type", strategy.strategy_type)
            strategy.updated_at = datetime.now()
            
            # Update rules
            if "rules" in strategy_data:
                # Delete existing rules
                self.db.query(StrategyRule).filter(
                    StrategyRule.strategy_id == strategy_id
                ).delete()
                
                # Add new rules
                for rule_data in strategy_data["rules"]:
                    rule = StrategyRule(
                        strategy_id=strategy_id,
                        rule_type=rule_data["type"],
                        condition=rule_data["condition"],
                        action=rule_data["action"],
                        parameters=json.dumps(rule_data.get("parameters", {})),
                        order=rule_data.get("order", 0)
                    )
                    self.db.add(rule)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Strategy updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating strategy: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_strategy(self, strategy_id: int) -> Dict:
        """Get strategy dengan rules"""
        try:
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return {"error": "Strategy not found"}
            
            # Get strategy rules
            rules = self.db.query(StrategyRule).filter(
                StrategyRule.strategy_id == strategy_id
            ).order_by(StrategyRule.order).all()
            
            rules_data = []
            for rule in rules:
                rules_data.append({
                    "id": rule.id,
                    "type": rule.rule_type,
                    "condition": rule.condition,
                    "action": rule.action,
                    "parameters": json.loads(rule.parameters) if rule.parameters else {},
                    "order": rule.order
                })
            
            return {
                "id": strategy.id,
                "name": strategy.name,
                "description": strategy.description,
                "strategy_type": strategy.strategy_type,
                "is_active": strategy.is_active,
                "created_at": strategy.created_at.isoformat(),
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
                "rules": rules_data
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy: {e}")
            return {"error": str(e)}
    
    def list_strategies(self, strategy_type: Optional[str] = None) -> Dict:
        """List all strategies"""
        try:
            query = self.db.query(Strategy)
            if strategy_type:
                query = query.filter(Strategy.strategy_type == strategy_type)
            
            strategies = query.order_by(Strategy.created_at.desc()).all()
            
            strategies_data = []
            for strategy in strategies:
                # Get rule count
                rule_count = self.db.query(StrategyRule).filter(
                    StrategyRule.strategy_id == strategy.id
                ).count()
                
                strategies_data.append({
                    "id": strategy.id,
                    "name": strategy.name,
                    "description": strategy.description,
                    "strategy_type": strategy.strategy_type,
                    "is_active": strategy.is_active,
                    "rule_count": rule_count,
                    "created_at": strategy.created_at.isoformat(),
                    "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None
                })
            
            return {
                "strategies": strategies_data,
                "total": len(strategies_data)
            }
            
        except Exception as e:
            logger.error(f"Error listing strategies: {e}")
            return {"error": str(e)}
    
    def delete_strategy(self, strategy_id: int) -> Dict:
        """Delete strategy"""
        try:
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return {"error": "Strategy not found"}
            
            # Delete strategy rules first
            self.db.query(StrategyRule).filter(
                StrategyRule.strategy_id == strategy_id
            ).delete()
            
            # Delete strategy
            self.db.delete(strategy)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Strategy deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting strategy: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def backtest_strategy(self, strategy_id: int, backtest_params: Dict) -> Dict:
        """Backtest strategy"""
        try:
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return {"error": "Strategy not found"}
            
            # Get strategy rules
            rules = self.db.query(StrategyRule).filter(
                StrategyRule.strategy_id == strategy_id
            ).order_by(StrategyRule.order).all()
            
            if not rules:
                return {"error": "No rules found for strategy"}
            
            # Run backtest simulation
            backtest_result = self._run_backtest_simulation(
                strategy, rules, backtest_params
            )
            
            # Save backtest result
            backtest = StrategyBacktest(
                strategy_id=strategy_id,
                start_date=backtest_params["start_date"],
                end_date=backtest_params["end_date"],
                initial_capital=backtest_params.get("initial_capital", 100000),
                final_capital=backtest_result["final_capital"],
                total_return=backtest_result["total_return"],
                sharpe_ratio=backtest_result["sharpe_ratio"],
                max_drawdown=backtest_result["max_drawdown"],
                win_rate=backtest_result["win_rate"],
                total_trades=backtest_result["total_trades"],
                backtest_data=json.dumps(backtest_result["trades"]),
                created_at=datetime.now()
            )
            
            self.db.add(backtest)
            self.db.commit()
            
            return {
                "success": True,
                "backtest_id": backtest.id,
                "results": backtest_result
            }
            
        except Exception as e:
            logger.error(f"Error backtesting strategy: {e}")
            return {"error": str(e)}
    
    def get_strategy_templates(self) -> Dict:
        """Get predefined strategy templates"""
        try:
            templates = [
                {
                    "id": "moving_average_crossover",
                    "name": "Moving Average Crossover",
                    "description": "Buy when short MA crosses above long MA, sell when it crosses below",
                    "strategy_type": "trend_following",
                    "rules": [
                        {
                            "type": "indicator",
                            "condition": "short_ma > long_ma",
                            "action": "buy",
                            "parameters": {
                                "short_period": 20,
                                "long_period": 50
                            }
                        },
                        {
                            "type": "indicator",
                            "condition": "short_ma < long_ma",
                            "action": "sell",
                            "parameters": {
                                "short_period": 20,
                                "long_period": 50
                            }
                        }
                    ]
                },
                {
                    "id": "rsi_oversold",
                    "name": "RSI Oversold Strategy",
                    "description": "Buy when RSI is oversold, sell when RSI is overbought",
                    "strategy_type": "mean_reversion",
                    "rules": [
                        {
                            "type": "indicator",
                            "condition": "rsi < 30",
                            "action": "buy",
                            "parameters": {
                                "rsi_period": 14,
                                "oversold_level": 30
                            }
                        },
                        {
                            "type": "indicator",
                            "condition": "rsi > 70",
                            "action": "sell",
                            "parameters": {
                                "rsi_period": 14,
                                "overbought_level": 70
                            }
                        }
                    ]
                },
                {
                    "id": "bollinger_bands",
                    "name": "Bollinger Bands Strategy",
                    "description": "Buy when price touches lower band, sell when price touches upper band",
                    "strategy_type": "mean_reversion",
                    "rules": [
                        {
                            "type": "indicator",
                            "condition": "price <= lower_band",
                            "action": "buy",
                            "parameters": {
                                "period": 20,
                                "std_dev": 2
                            }
                        },
                        {
                            "type": "indicator",
                            "condition": "price >= upper_band",
                            "action": "sell",
                            "parameters": {
                                "period": 20,
                                "std_dev": 2
                            }
                        }
                    ]
                },
                {
                    "id": "macd_crossover",
                    "name": "MACD Crossover Strategy",
                    "description": "Buy when MACD line crosses above signal line, sell when it crosses below",
                    "strategy_type": "trend_following",
                    "rules": [
                        {
                            "type": "indicator",
                            "condition": "macd_line > macd_signal",
                            "action": "buy",
                            "parameters": {
                                "fast_period": 12,
                                "slow_period": 26,
                                "signal_period": 9
                            }
                        },
                        {
                            "type": "indicator",
                            "condition": "macd_line < macd_signal",
                            "action": "sell",
                            "parameters": {
                                "fast_period": 12,
                                "slow_period": 26,
                                "signal_period": 9
                            }
                        }
                    ]
                }
            ]
            
            return {
                "templates": templates,
                "total": len(templates)
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy templates: {e}")
            return {"error": str(e)}
    
    def _validate_strategy_data(self, strategy_data: Dict) -> Dict:
        """Validate strategy data"""
        try:
            required_fields = ["name", "rules"]
            for field in required_fields:
                if field not in strategy_data:
                    return {
                        "valid": False,
                        "message": f"Missing required field: {field}"
                    }
            
            # Validate rules
            rules = strategy_data.get("rules", [])
            if not rules:
                return {
                    "valid": False,
                    "message": "Strategy must have at least one rule"
                }
            
            for i, rule in enumerate(rules):
                if not all(key in rule for key in ["type", "condition", "action"]):
                    return {
                        "valid": False,
                        "message": f"Rule {i+1} is missing required fields"
                    }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Error validating strategy data: {e}")
            return {"valid": False, "message": str(e)}
    
    def _run_backtest_simulation(self, strategy: Strategy, rules: List, params: Dict) -> Dict:
        """Run backtest simulation (simplified)"""
        try:
            # This is a simplified backtest simulation
            # In a real implementation, you would:
            # 1. Get historical data
            # 2. Apply strategy rules
            # 3. Calculate returns
            # 4. Calculate metrics
            
            # Mock results for now
            return {
                "final_capital": 120000,
                "total_return": 0.20,
                "sharpe_ratio": 1.5,
                "max_drawdown": 0.05,
                "win_rate": 0.65,
                "total_trades": 45,
                "trades": [
                    {
                        "date": "2024-01-01",
                        "action": "buy",
                        "price": 100,
                        "quantity": 100
                    },
                    {
                        "date": "2024-01-15",
                        "action": "sell",
                        "price": 105,
                        "quantity": 100
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error running backtest simulation: {e}")
            return {"error": str(e)}
