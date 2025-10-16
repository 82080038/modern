"""
Portfolio Heat Map Service
Visualisasi risk exposure dan performance per sector/asset
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.trading import Portfolio, Position, Trade
from app.models.market_data import HistoricalData
from app.models.fundamental import CompanyProfile
import logging

logger = logging.getLogger(__name__)

class PortfolioHeatMapService:
    """Service untuk Portfolio Heat Map visualization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_sector_exposure(self, portfolio_id: int) -> Dict:
        """Calculate sector exposure untuk portfolio"""
        try:
            # Get portfolio positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            if not positions:
                return {"error": "No positions found for portfolio"}
            
            # Get company profiles untuk sector information
            symbols = [pos.symbol for pos in positions]
            companies = self.db.query(CompanyProfile).filter(
                CompanyProfile.symbol.in_(symbols)
            ).all()
            
            # Create sector mapping
            sector_mapping = {comp.symbol: comp.sector for comp in companies}
            
            # Calculate sector exposure
            sector_exposure = {}
            total_value = 0
            
            for position in positions:
                sector = sector_mapping.get(position.symbol, "Unknown")
                position_value = position.quantity * position.average_price
                total_value += position_value
                
                if sector not in sector_exposure:
                    sector_exposure[sector] = {
                        "value": 0,
                        "percentage": 0,
                        "positions": [],
                        "count": 0
                    }
                
                sector_exposure[sector]["value"] += position_value
                sector_exposure[sector]["positions"].append({
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "value": position_value
                })
                sector_exposure[sector]["count"] += 1
            
            # Calculate percentages
            for sector in sector_exposure:
                sector_exposure[sector]["percentage"] = (
                    sector_exposure[sector]["value"] / total_value * 100
                ) if total_value > 0 else 0
            
            return {
                "portfolio_id": portfolio_id,
                "total_value": total_value,
                "sector_exposure": sector_exposure,
                "diversification_score": self._calculate_diversification_score(sector_exposure)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sector exposure: {e}")
            return {"error": str(e)}
    
    def calculate_risk_heatmap(self, portfolio_id: int) -> Dict:
        """Calculate risk heatmap untuk portfolio"""
        try:
            # Get portfolio positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            if not positions:
                return {"error": "No positions found for portfolio"}
            
            # Calculate risk metrics per position
            risk_data = []
            symbols = [pos.symbol for pos in positions]
            
            # Get historical data untuk volatility calculation
            end_date = datetime.now()
            start_date = end_date - timedelta(days=252)  # 1 year
            
            for position in positions:
                # Get historical data
                historical_data = self.db.query(HistoricalData).filter(
                    HistoricalData.symbol == position.symbol,
                    HistoricalData.date >= start_date,
                    HistoricalData.date <= end_date
                ).order_by(HistoricalData.date).all()
                
                if not historical_data:
                    continue
                
                # Calculate volatility
                prices = [data.close_price for data in historical_data if data.close_price]
                if len(prices) < 2:
                    continue
                
                returns = np.diff(np.log(prices))
                volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
                
                # Calculate position metrics
                position_value = position.quantity * position.average_price
                portfolio_value = sum([p.quantity * p.average_price for p in positions])
                weight = position_value / portfolio_value if portfolio_value > 0 else 0
                
                # Calculate VaR (simplified)
                var_95 = np.percentile(returns, 5) * position_value
                
                risk_data.append({
                    "symbol": position.symbol,
                    "weight": weight,
                    "volatility": volatility,
                    "value": position_value,
                    "var_95": var_95,
                    "risk_score": volatility * weight  # Risk contribution
                })
            
            # Sort by risk score
            risk_data.sort(key=lambda x: x["risk_score"], reverse=True)
            
            return {
                "portfolio_id": portfolio_id,
                "risk_data": risk_data,
                "total_risk": sum([item["risk_score"] for item in risk_data]),
                "max_risk_position": risk_data[0] if risk_data else None,
                "risk_distribution": self._calculate_risk_distribution(risk_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk heatmap: {e}")
            return {"error": str(e)}
    
    def calculate_performance_heatmap(self, portfolio_id: int, days: int = 30) -> Dict:
        """Calculate performance heatmap untuk portfolio"""
        try:
            # Get portfolio positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            if not positions:
                return {"error": "No positions found for portfolio"}
            
            # Get performance data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            performance_data = []
            
            for position in positions:
                # Get recent trades untuk P&L calculation
                trades = self.db.query(Trade).filter(
                    Trade.symbol == position.symbol,
                    Trade.created_at >= start_date,
                    Trade.created_at <= end_date
                ).all()
                
                # Calculate P&L
                total_pnl = sum([trade.realized_pnl or 0 for trade in trades])
                
                # Get current price (simplified)
                current_price = position.average_price  # This should be real-time price
                position_value = position.quantity * current_price
                
                # Calculate performance metrics
                if position.average_price > 0:
                    price_change = (current_price - position.average_price) / position.average_price
                else:
                    price_change = 0
                
                # Calculate portfolio weight
                portfolio_value = sum([p.quantity * p.average_price for p in positions])
                weight = position_value / portfolio_value if portfolio_value > 0 else 0
                
                # Calculate contribution to portfolio performance
                contribution = price_change * weight
                
                performance_data.append({
                    "symbol": position.symbol,
                    "weight": weight,
                    "price_change": price_change,
                    "pnl": total_pnl,
                    "value": position_value,
                    "contribution": contribution,
                    "performance_score": contribution * 100  # Percentage contribution
                })
            
            # Sort by performance score
            performance_data.sort(key=lambda x: x["performance_score"], reverse=True)
            
            return {
                "portfolio_id": portfolio_id,
                "period_days": days,
                "performance_data": performance_data,
                "total_contribution": sum([item["contribution"] for item in performance_data]),
                "best_performer": performance_data[0] if performance_data else None,
                "worst_performer": performance_data[-1] if performance_data else None,
                "performance_distribution": self._calculate_performance_distribution(performance_data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance heatmap: {e}")
            return {"error": str(e)}
    
    def calculate_correlation_heatmap(self, portfolio_id: int, days: int = 90) -> Dict:
        """Calculate correlation heatmap untuk portfolio positions"""
        try:
            # Get portfolio positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            if not positions:
                return {"error": "No positions found for portfolio"}
            
            symbols = [pos.symbol for pos in positions]
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get price data for all symbols
            price_data = {}
            for symbol in symbols:
                historical_data = self.db.query(HistoricalData).filter(
                    HistoricalData.symbol == symbol,
                    HistoricalData.date >= start_date,
                    HistoricalData.date <= end_date
                ).order_by(HistoricalData.date).all()
                
                if historical_data:
                    prices = [data.close_price for data in historical_data if data.close_price]
                    if len(prices) > 1:
                        # Calculate returns
                        returns = np.diff(np.log(prices))
                        price_data[symbol] = returns
            
            if len(price_data) < 2:
                return {"error": "Insufficient data for correlation analysis"}
            
            # Calculate correlation matrix
            correlation_matrix = {}
            for symbol1 in symbols:
                if symbol1 not in price_data:
                    continue
                    
                correlation_matrix[symbol1] = {}
                for symbol2 in symbols:
                    if symbol2 not in price_data:
                        continue
                    
                    if symbol1 == symbol2:
                        correlation_matrix[symbol1][symbol2] = 1.0
                    else:
                        # Calculate correlation
                        min_length = min(len(price_data[symbol1]), len(price_data[symbol2]))
                        if min_length > 1:
                            corr = np.corrcoef(
                                price_data[symbol1][:min_length],
                                price_data[symbol2][:min_length]
                            )[0, 1]
                            correlation_matrix[symbol1][symbol2] = round(corr, 4)
                        else:
                            correlation_matrix[symbol1][symbol2] = 0.0
            
            return {
                "portfolio_id": portfolio_id,
                "period_days": days,
                "correlation_matrix": correlation_matrix,
                "high_correlation_pairs": self._find_high_correlation_pairs(correlation_matrix),
                "diversification_analysis": self._analyze_diversification(correlation_matrix)
            }
            
        except Exception as e:
            logger.error(f"Error calculating correlation heatmap: {e}")
            return {"error": str(e)}
    
    def get_comprehensive_heatmap(self, portfolio_id: int) -> Dict:
        """Get comprehensive heatmap data untuk portfolio"""
        try:
            # Get all heatmap data
            sector_exposure = self.calculate_sector_exposure(portfolio_id)
            risk_heatmap = self.calculate_risk_heatmap(portfolio_id)
            performance_heatmap = self.calculate_performance_heatmap(portfolio_id)
            correlation_heatmap = self.calculate_correlation_heatmap(portfolio_id)
            
            return {
                "portfolio_id": portfolio_id,
                "sector_exposure": sector_exposure,
                "risk_heatmap": risk_heatmap,
                "performance_heatmap": performance_heatmap,
                "correlation_heatmap": correlation_heatmap,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive heatmap: {e}")
            return {"error": str(e)}
    
    def _calculate_diversification_score(self, sector_exposure: Dict) -> float:
        """Calculate diversification score (0-1, higher is better)"""
        try:
            if not sector_exposure:
                return 0.0
            
            # Calculate Herfindahl-Hirschman Index
            percentages = [sector["percentage"] for sector in sector_exposure.values()]
            hhi = sum([p**2 for p in percentages]) / 10000  # Normalize to 0-1
            
            # Convert to diversification score (1 - HHI)
            diversification_score = 1 - hhi
            return round(diversification_score, 4)
            
        except Exception as e:
            logger.error(f"Error calculating diversification score: {e}")
            return 0.0
    
    def _calculate_risk_distribution(self, risk_data: List[Dict]) -> Dict:
        """Calculate risk distribution statistics"""
        try:
            if not risk_data:
                return {"error": "No risk data available"}
            
            risk_scores = [item["risk_score"] for item in risk_data]
            
            return {
                "mean_risk": round(np.mean(risk_scores), 4),
                "std_risk": round(np.std(risk_scores), 4),
                "max_risk": round(np.max(risk_scores), 4),
                "min_risk": round(np.min(risk_scores), 4),
                "risk_concentration": round(np.max(risk_scores) / np.sum(risk_scores), 4)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk distribution: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_distribution(self, performance_data: List[Dict]) -> Dict:
        """Calculate performance distribution statistics"""
        try:
            if not performance_data:
                return {"error": "No performance data available"}
            
            contributions = [item["contribution"] for item in performance_data]
            
            return {
                "mean_contribution": round(np.mean(contributions), 4),
                "std_contribution": round(np.std(contributions), 4),
                "max_contribution": round(np.max(contributions), 4),
                "min_contribution": round(np.min(contributions), 4),
                "positive_contributors": len([c for c in contributions if c > 0]),
                "negative_contributors": len([c for c in contributions if c < 0])
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance distribution: {e}")
            return {"error": str(e)}
    
    def _find_high_correlation_pairs(self, correlation_matrix: Dict) -> List[Dict]:
        """Find pairs with high correlation (>0.7)"""
        try:
            high_correlation_pairs = []
            
            for symbol1, correlations in correlation_matrix.items():
                for symbol2, corr in correlations.items():
                    if symbol1 != symbol2 and corr > 0.7:
                        high_correlation_pairs.append({
                            "symbol1": symbol1,
                            "symbol2": symbol2,
                            "correlation": corr
                        })
            
            # Sort by correlation
            high_correlation_pairs.sort(key=lambda x: x["correlation"], reverse=True)
            return high_correlation_pairs
            
        except Exception as e:
            logger.error(f"Error finding high correlation pairs: {e}")
            return []
    
    def _analyze_diversification(self, correlation_matrix: Dict) -> Dict:
        """Analyze portfolio diversification"""
        try:
            if not correlation_matrix:
                return {"error": "No correlation data available"}
            
            # Calculate average correlation
            correlations = []
            for symbol1, correlations_dict in correlation_matrix.items():
                for symbol2, corr in correlations_dict.items():
                    if symbol1 != symbol2:
                        correlations.append(corr)
            
            if not correlations:
                return {"error": "No correlation data available"}
            
            avg_correlation = np.mean(correlations)
            max_correlation = np.max(correlations)
            
            # Diversification assessment
            if avg_correlation < 0.3:
                diversification_level = "Excellent"
            elif avg_correlation < 0.5:
                diversification_level = "Good"
            elif avg_correlation < 0.7:
                diversification_level = "Fair"
            else:
                diversification_level = "Poor"
            
            return {
                "average_correlation": round(avg_correlation, 4),
                "max_correlation": round(max_correlation, 4),
                "diversification_level": diversification_level,
                "recommendation": self._get_diversification_recommendation(avg_correlation)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing diversification: {e}")
            return {"error": str(e)}
    
    def _get_diversification_recommendation(self, avg_correlation: float) -> str:
        """Get diversification recommendation"""
        if avg_correlation < 0.3:
            return "Portfolio is well diversified. Consider adding more positions if desired."
        elif avg_correlation < 0.5:
            return "Portfolio has good diversification. Monitor for over-concentration."
        elif avg_correlation < 0.7:
            return "Portfolio shows moderate diversification. Consider reducing correlation."
        else:
            return "Portfolio is poorly diversified. Consider adding uncorrelated assets."
