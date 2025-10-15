"""
Risk Management Service
Advanced risk management untuk trading platform
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.trading import Portfolio, Position, Order
from app.models.market_data import MarketData
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskManagementService:
    """Service untuk risk management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_position_limits(self, portfolio_id: int, symbol: str, quantity: int) -> Dict:
        """Check position size limits"""
        try:
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == portfolio_id
            ).first()
            
            if not portfolio:
                return {"allowed": False, "reason": "Portfolio not found"}
            
            # Get current position
            current_position = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.symbol == symbol
            ).first()
            
            current_quantity = current_position.quantity if current_position else 0
            new_quantity = current_quantity + quantity
            
            # Check position size limit (10% of portfolio)
            max_position_value = portfolio.total_value * 0.1
            current_price = self._get_current_price(symbol)
            max_quantity = int(max_position_value / current_price) if current_price > 0 else 0
            
            if abs(new_quantity) > max_quantity:
                return {
                    "allowed": False,
                    "reason": f"Position size exceeds limit. Max: {max_quantity}, Requested: {new_quantity}"
                }
            
            return {"allowed": True}
            
        except Exception as e:
            logger.error(f"Error checking position limits: {e}")
            return {"allowed": False, "reason": "Risk check failed"}
    
    def check_daily_loss_limits(self, portfolio_id: int) -> Dict:
        """Check daily loss limits"""
        try:
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == portfolio_id
            ).first()
            
            if not portfolio:
                return {"allowed": False, "reason": "Portfolio not found"}
            
            # Get today's trades
            today = datetime.now().date()
            today_trades = self.db.query(Order).filter(
                Order.portfolio_id == portfolio_id,
                Order.created_at >= today,
                Order.status == "filled"
            ).all()
            
            # Calculate today's P&L
            today_pnl = sum([trade.realized_pnl or 0 for trade in today_trades])
            
            # Check daily loss limit (5% of portfolio)
            max_daily_loss = portfolio.total_value * 0.05
            
            if today_pnl <= -max_daily_loss:
                return {
                    "allowed": False,
                    "reason": f"Daily loss limit exceeded. Current: {today_pnl:.2f}, Limit: {-max_daily_loss:.2f}"
                }
            
            return {"allowed": True, "current_pnl": today_pnl}
            
        except Exception as e:
            logger.error(f"Error checking daily loss limits: {e}")
            return {"allowed": False, "reason": "Risk check failed"}
    
    def check_concentration_limits(self, portfolio_id: int, symbol: str) -> Dict:
        """Check portfolio concentration limits"""
        try:
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == portfolio_id
            ).first()
            
            if not portfolio:
                return {"allowed": False, "reason": "Portfolio not found"}
            
            # Get all positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            # Calculate total portfolio value
            total_value = sum([pos.quantity * pos.average_price for pos in positions])
            
            # Get current position value
            current_position = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.symbol == symbol
            ).first()
            
            if current_position:
                position_value = current_position.quantity * current_position.average_price
                concentration_ratio = position_value / total_value if total_value > 0 else 0
                
                # Check concentration limit (20% max)
                if concentration_ratio > 0.2:
                    return {
                        "allowed": False,
                        "reason": f"Position concentration too high. Current: {concentration_ratio:.2%}, Limit: 20%"
                    }
            
            return {"allowed": True}
            
        except Exception as e:
            logger.error(f"Error checking concentration limits: {e}")
            return {"allowed": False, "reason": "Risk check failed"}
    
    def check_volatility_limits(self, symbol: str) -> Dict:
        """Check volatility limits"""
        try:
            # Get recent price data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            price_data = self.db.query(MarketData).filter(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            ).order_by(MarketData.timestamp).all()
            
            if len(price_data) < 2:
                return {"allowed": True, "reason": "Insufficient data"}
            
            # Calculate volatility
            prices = [data.last_price for data in price_data if data.last_price]
            if len(prices) < 2:
                return {"allowed": True, "reason": "Insufficient price data"}
            
            import numpy as np
            returns = np.diff(np.log(prices))
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            
            # Check volatility limit (50% max)
            if volatility > 0.5:
                return {
                    "allowed": False,
                    "reason": f"Asset volatility too high. Current: {volatility:.2%}, Limit: 50%"
                }
            
            return {"allowed": True, "volatility": volatility}
            
        except Exception as e:
            logger.error(f"Error checking volatility limits: {e}")
            return {"allowed": True, "reason": "Risk check failed"}
    
    def calculate_portfolio_risk(self, portfolio_id: int) -> Dict:
        """Calculate overall portfolio risk metrics"""
        try:
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == portfolio_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Get all positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            if not positions:
                return {
                    "portfolio_id": portfolio_id,
                    "total_risk": 0,
                    "diversification_score": 1.0,
                    "concentration_risk": 0,
                    "recommendations": ["No positions found"]
                }
            
            # Calculate risk metrics
            total_value = sum([pos.quantity * pos.average_price for pos in positions])
            
            # Concentration risk (max position weight)
            position_weights = []
            for pos in positions:
                weight = (pos.quantity * pos.average_price) / total_value if total_value > 0 else 0
                position_weights.append(weight)
            
            max_concentration = max(position_weights) if position_weights else 0
            
            # Diversification score (1 - Herfindahl Index)
            hhi = sum([w**2 for w in position_weights])
            diversification_score = 1 - hhi
            
            # Risk recommendations
            recommendations = []
            if max_concentration > 0.2:
                recommendations.append("Reduce position concentration")
            if diversification_score < 0.3:
                recommendations.append("Improve portfolio diversification")
            if len(positions) < 5:
                recommendations.append("Consider adding more positions")
            
            return {
                "portfolio_id": portfolio_id,
                "total_risk": total_value,
                "diversification_score": round(diversification_score, 4),
                "concentration_risk": round(max_concentration, 4),
                "position_count": len(positions),
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return {"error": str(e)}
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            latest_data = self.db.query(MarketData).filter(
                MarketData.symbol == symbol
            ).order_by(MarketData.timestamp.desc()).first()
            
            return latest_data.last_price if latest_data else 100.0  # Default price
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return 100.0
