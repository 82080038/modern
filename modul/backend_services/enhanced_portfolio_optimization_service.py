"""
Enhanced Portfolio Optimization Service
======================================

Service untuk portfolio optimization dengan implementasi algoritma terbukti
menggunakan Modern Portfolio Theory, Black-Litterman, dan advanced optimization.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy import stats
import quantlib as ql
from app.models.trading import Portfolio, Position
from app.models.market_data import MarketData
from app.services.enhanced_risk_management_service import EnhancedRiskManagementService

logger = logging.getLogger(__name__)

class EnhancedPortfolioOptimizationService:
    """
    Enhanced Portfolio Optimization Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = EnhancedRiskManagementService(db)
        
        # Optimization parameters
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.max_weight = 0.4       # 40% maximum weight per asset
        self.min_weight = 0.0       # 0% minimum weight per asset
        self.rebalance_threshold = 0.05  # 5% rebalancing threshold
        
    async def optimize_portfolio(
        self, 
        portfolio_id: int, 
        optimization_method: str = 'markowitz',
        risk_tolerance: float = 0.5,
        target_return: Optional[float] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize portfolio menggunakan advanced algorithms"""
        try:
            # Get current portfolio
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'error': 'Portfolio not found'}
            
            # Get portfolio positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            if not positions:
                return {'error': 'No positions found in portfolio'}
            
            # Get symbols
            symbols = [pos.symbol for pos in positions]
            
            # Get historical data
            historical_data = await self._get_historical_data(symbols, days=252)  # 1 year
            
            if historical_data.empty:
                return {'error': 'Insufficient historical data'}
            
            # Calculate returns and covariance matrix
            returns_data = await self._calculate_returns(historical_data)
            covariance_matrix = await self._calculate_covariance_matrix(returns_data)
            expected_returns = await self._calculate_expected_returns(returns_data)
            
            # Run optimization based on method
            if optimization_method == 'markowitz':
                optimization_result = await self._markowitz_optimization(
                    expected_returns, covariance_matrix, risk_tolerance, target_return
                )
            elif optimization_method == 'black_litterman':
                optimization_result = await self._black_litterman_optimization(
                    expected_returns, covariance_matrix, risk_tolerance, target_return
                )
            elif optimization_method == 'risk_parity':
                optimization_result = await self._risk_parity_optimization(
                    covariance_matrix, risk_tolerance
                )
            elif optimization_method == 'minimum_variance':
                optimization_result = await self._minimum_variance_optimization(
                    covariance_matrix, risk_tolerance
                )
            else:
                return {'error': f'Unknown optimization method: {optimization_method}'}
            
            # Apply constraints if provided
            if constraints:
                optimization_result = await self._apply_constraints(
                    optimization_result, constraints
                )
            
            # Calculate portfolio metrics
            portfolio_metrics = await self._calculate_portfolio_metrics(
                optimization_result, expected_returns, covariance_matrix
            )
            
            # Generate rebalancing recommendations
            rebalancing_recommendations = await self._generate_rebalancing_recommendations(
                portfolio_id, optimization_result, symbols
            )
            
            return {
                'success': True,
                'optimization_method': optimization_method,
                'optimal_weights': optimization_result['weights'],
                'expected_return': optimization_result['expected_return'],
                'expected_volatility': optimization_result['expected_volatility'],
                'sharpe_ratio': optimization_result['sharpe_ratio'],
                'portfolio_metrics': portfolio_metrics,
                'rebalancing_recommendations': rebalancing_recommendations,
                'optimization_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return {'error': str(e)}
    
    async def _get_historical_data(self, symbols: List[str], days: int) -> pd.DataFrame:
        """Get historical data untuk symbols"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            market_data = self.db.query(MarketData).filter(
                MarketData.symbol.in_(symbols),
                MarketData.timestamp >= start_date
            ).order_by(MarketData.timestamp).all()
            
            # Convert to DataFrame
            data = []
            for record in market_data:
                data.append({
                    'timestamp': record.timestamp,
                    'symbol': record.symbol,
                    'close': record.close_price
                })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    async def _calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns untuk each symbol"""
        try:
            returns_data = {}
            
            for symbol in data['symbol'].unique():
                symbol_data = data[data['symbol'] == symbol]['close']
                if len(symbol_data) > 1:
                    returns = symbol_data.pct_change().dropna()
                    returns_data[symbol] = returns
            
            return pd.DataFrame(returns_data)
            
        except Exception as e:
            logger.error(f"Error calculating returns: {e}")
            return pd.DataFrame()
    
    async def _calculate_covariance_matrix(self, returns_data: pd.DataFrame) -> np.ndarray:
        """Calculate covariance matrix"""
        try:
            if returns_data.empty:
                return np.array([])
            
            # Calculate covariance matrix
            covariance_matrix = returns_data.cov().values
            
            # Handle NaN values
            covariance_matrix = np.nan_to_num(covariance_matrix, nan=0.0)
            
            return covariance_matrix
            
        except Exception as e:
            logger.error(f"Error calculating covariance matrix: {e}")
            return np.array([])
    
    async def _calculate_expected_returns(self, returns_data: pd.DataFrame) -> np.ndarray:
        """Calculate expected returns"""
        try:
            if returns_data.empty:
                return np.array([])
            
            # Calculate mean returns
            expected_returns = returns_data.mean().values
            
            # Annualize returns
            expected_returns = expected_returns * 252
            
            return expected_returns
            
        except Exception as e:
            logger.error(f"Error calculating expected returns: {e}")
            return np.array([])
    
    async def _markowitz_optimization(
        self, 
        expected_returns: np.ndarray, 
        covariance_matrix: np.ndarray, 
        risk_tolerance: float,
        target_return: Optional[float]
    ) -> Dict[str, Any]:
        """Markowitz mean-variance optimization"""
        try:
            n_assets = len(expected_returns)
            
            # Objective function: minimize portfolio variance
            def objective(weights):
                return np.dot(weights.T, np.dot(covariance_matrix, weights))
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Weights sum to 1
            ]
            
            # Add target return constraint if specified
            if target_return is not None:
                constraints.append({
                    'type': 'eq', 
                    'fun': lambda w: np.dot(w, expected_returns) - target_return
                })
            
            # Bounds: 0 <= weight <= max_weight
            bounds = [(0, self.max_weight) for _ in range(n_assets)]
            
            # Initial guess: equal weights
            x0 = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective, x0, method='SLSQP', 
                bounds=bounds, constraints=constraints
            )
            
            if not result.success:
                return {'error': f'Optimization failed: {result.message}'}
            
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_variance = np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
            
            return {
                'weights': optimal_weights,
                'expected_return': portfolio_return,
                'expected_volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'method': 'markowitz'
            }
            
        except Exception as e:
            logger.error(f"Error in Markowitz optimization: {e}")
            return {'error': str(e)}
    
    async def _black_litterman_optimization(
        self, 
        expected_returns: np.ndarray, 
        covariance_matrix: np.ndarray, 
        risk_tolerance: float,
        target_return: Optional[float]
    ) -> Dict[str, Any]:
        """Black-Litterman optimization dengan views"""
        try:
            n_assets = len(expected_returns)
            
            # Black-Litterman parameters
            tau = 0.05  # Confidence level
            P = np.eye(n_assets)  # Pick matrix (identity for simplicity)
            Q = expected_returns  # Views (using historical returns as views)
            Omega = np.diag(np.diag(covariance_matrix)) * tau  # Uncertainty matrix
            
            # Calculate Black-Litterman expected returns
            M1 = np.linalg.inv(tau * covariance_matrix)
            M2 = np.dot(P.T, np.dot(np.linalg.inv(Omega), P))
            M3 = np.dot(P.T, np.dot(np.linalg.inv(Omega), Q))
            
            bl_expected_returns = np.dot(
                np.linalg.inv(M1 + M2),
                np.dot(M1, expected_returns) + M3
            )
            
            # Use Markowitz optimization with BL expected returns
            return await self._markowitz_optimization(
                bl_expected_returns, covariance_matrix, risk_tolerance, target_return
            )
            
        except Exception as e:
            logger.error(f"Error in Black-Litterman optimization: {e}")
            return {'error': str(e)}
    
    async def _risk_parity_optimization(
        self, 
        covariance_matrix: np.ndarray, 
        risk_tolerance: float
    ) -> Dict[str, Any]:
        """Risk parity optimization"""
        try:
            n_assets = covariance_matrix.shape[0]
            
            # Risk parity objective: minimize sum of squared risk contributions
            def objective(weights):
                portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
                risk_contributions = (weights * np.dot(covariance_matrix, weights)) / portfolio_variance
                return np.sum((risk_contributions - 1/n_assets) ** 2)
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Weights sum to 1
            ]
            
            # Bounds
            bounds = [(0, self.max_weight) for _ in range(n_assets)]
            
            # Initial guess
            x0 = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective, x0, method='SLSQP',
                bounds=bounds, constraints=constraints
            )
            
            if not result.success:
                return {'error': f'Risk parity optimization failed: {result.message}'}
            
            optimal_weights = result.x
            portfolio_variance = np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            return {
                'weights': optimal_weights,
                'expected_return': 0,  # Risk parity doesn't optimize for return
                'expected_volatility': portfolio_volatility,
                'sharpe_ratio': 0,
                'method': 'risk_parity'
            }
            
        except Exception as e:
            logger.error(f"Error in risk parity optimization: {e}")
            return {'error': str(e)}
    
    async def _minimum_variance_optimization(
        self, 
        covariance_matrix: np.ndarray, 
        risk_tolerance: float
    ) -> Dict[str, Any]:
        """Minimum variance optimization"""
        try:
            n_assets = covariance_matrix.shape[0]
            
            # Objective: minimize portfolio variance
            def objective(weights):
                return np.dot(weights.T, np.dot(covariance_matrix, weights))
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Weights sum to 1
            ]
            
            # Bounds
            bounds = [(0, self.max_weight) for _ in range(n_assets)]
            
            # Initial guess
            x0 = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective, x0, method='SLSQP',
                bounds=bounds, constraints=constraints
            )
            
            if not result.success:
                return {'error': f'Minimum variance optimization failed: {result.message}'}
            
            optimal_weights = result.x
            portfolio_variance = np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            return {
                'weights': optimal_weights,
                'expected_return': 0,  # Minimum variance doesn't optimize for return
                'expected_volatility': portfolio_volatility,
                'sharpe_ratio': 0,
                'method': 'minimum_variance'
            }
            
        except Exception as e:
            logger.error(f"Error in minimum variance optimization: {e}")
            return {'error': str(e)}
    
    async def _apply_constraints(
        self, 
        optimization_result: Dict[str, Any], 
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply additional constraints to optimization result"""
        try:
            weights = optimization_result['weights']
            
            # Apply sector constraints
            if 'sector_limits' in constraints:
                # This would require sector information
                pass
            
            # Apply individual asset constraints
            if 'asset_limits' in constraints:
                asset_limits = constraints['asset_limits']
                for i, limit in enumerate(asset_limits):
                    if i < len(weights):
                        weights[i] = min(weights[i], limit)
            
            # Normalize weights
            weights = weights / np.sum(weights)
            
            optimization_result['weights'] = weights
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error applying constraints: {e}")
            return optimization_result
    
    async def _calculate_portfolio_metrics(
        self, 
        optimization_result: Dict[str, Any], 
        expected_returns: np.ndarray, 
        covariance_matrix: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate comprehensive portfolio metrics"""
        try:
            weights = optimization_result['weights']
            
            # Basic metrics
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Risk metrics
            var_95 = self._calculate_var(weights, covariance_matrix, 0.95)
            var_99 = self._calculate_var(weights, covariance_matrix, 0.99)
            max_drawdown = self._calculate_max_drawdown(weights, covariance_matrix)
            
            # Diversification metrics
            diversification_ratio = self._calculate_diversification_ratio(weights, covariance_matrix)
            concentration_ratio = self._calculate_concentration_ratio(weights)
            
            # Risk-adjusted returns
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
            sortino_ratio = self._calculate_sortino_ratio(weights, expected_returns, covariance_matrix)
            
            return {
                'portfolio_return': portfolio_return,
                'portfolio_volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'var_95': var_95,
                'var_99': var_99,
                'max_drawdown': max_drawdown,
                'diversification_ratio': diversification_ratio,
                'concentration_ratio': concentration_ratio
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {}
    
    def _calculate_var(self, weights: np.ndarray, covariance_matrix: np.ndarray, confidence: float) -> float:
        """Calculate Value at Risk"""
        try:
            portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            z_score = stats.norm.ppf(1 - confidence)
            return z_score * portfolio_volatility
        except:
            return 0.0
    
    def _calculate_max_drawdown(self, weights: np.ndarray, covariance_matrix: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        try:
            portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            # Simplified max drawdown calculation
            return portfolio_volatility * 2.5  # Approximate
        except:
            return 0.0
    
    def _calculate_diversification_ratio(self, weights: np.ndarray, covariance_matrix: np.ndarray) -> float:
        """Calculate diversification ratio"""
        try:
            portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
            weighted_volatility = np.dot(weights, np.sqrt(np.diag(covariance_matrix)))
            return weighted_volatility / np.sqrt(portfolio_variance)
        except:
            return 1.0
    
    def _calculate_concentration_ratio(self, weights: np.ndarray) -> float:
        """Calculate concentration ratio (Herfindahl index)"""
        try:
            return np.sum(weights ** 2)
        except:
            return 1.0
    
    def _calculate_sortino_ratio(self, weights: np.ndarray, expected_returns: np.ndarray, covariance_matrix: np.ndarray) -> float:
        """Calculate Sortino ratio"""
        try:
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Simplified Sortino ratio (using volatility as downside deviation)
            return (portfolio_return - self.risk_free_rate) / portfolio_volatility
        except:
            return 0.0
    
    async def _generate_rebalancing_recommendations(
        self, 
        portfolio_id: int, 
        optimization_result: Dict[str, Any], 
        symbols: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate rebalancing recommendations"""
        try:
            recommendations = []
            optimal_weights = optimization_result['weights']
            
            # Get current positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            current_weights = {}
            total_value = 0
            
            # Calculate current weights
            for position in positions:
                # Get current market price
                latest_data = self.db.query(MarketData).filter(
                    MarketData.symbol == position.symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    position_value = position.quantity * latest_data.close_price
                    current_weights[position.symbol] = position_value
                    total_value += position_value
            
            # Normalize current weights
            if total_value > 0:
                for symbol in current_weights:
                    current_weights[symbol] /= total_value
            
            # Compare with optimal weights
            for i, symbol in enumerate(symbols):
                if i < len(optimal_weights):
                    optimal_weight = optimal_weights[i]
                    current_weight = current_weights.get(symbol, 0)
                    weight_diff = optimal_weight - current_weight
                    
                    if abs(weight_diff) > self.rebalancing_threshold:
                        action = 'buy' if weight_diff > 0 else 'sell'
                        amount = abs(weight_diff) * total_value
                        
                        recommendations.append({
                            'symbol': symbol,
                            'action': action,
                            'current_weight': current_weight,
                            'optimal_weight': optimal_weight,
                            'weight_difference': weight_diff,
                            'recommended_amount': amount,
                            'priority': 'high' if abs(weight_diff) > 0.1 else 'medium'
                        })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating rebalancing recommendations: {e}")
            return []
    
    async def get_portfolio_analysis(self, portfolio_id: int) -> Dict[str, Any]:
        """Get comprehensive portfolio analysis"""
        try:
            # Get portfolio
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'error': 'Portfolio not found'}
            
            # Get positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.quantity > 0
            ).all()
            
            if not positions:
                return {'error': 'No positions found'}
            
            # Calculate basic metrics
            total_value = 0
            position_values = {}
            
            for position in positions:
                latest_data = self.db.query(MarketData).filter(
                    MarketData.symbol == position.symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    position_value = position.quantity * latest_data.close_price
                    position_values[position.symbol] = {
                        'quantity': position.quantity,
                        'average_price': position.average_price,
                        'current_price': latest_data.close_price,
                        'market_value': position_value,
                        'unrealized_pnl': (latest_data.close_price - position.average_price) * position.quantity
                    }
                    total_value += position_value
            
            # Calculate weights
            weights = {}
            for symbol, data in position_values.items():
                weights[symbol] = data['market_value'] / total_value if total_value > 0 else 0
            
            # Calculate portfolio metrics
            portfolio_metrics = {
                'total_value': total_value,
                'position_count': len(positions),
                'weights': weights,
                'position_values': position_values,
                'analysis_timestamp': datetime.now()
            }
            
            return {
                'success': True,
                'portfolio_analysis': portfolio_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio analysis: {e}")
            return {'error': str(e)}
