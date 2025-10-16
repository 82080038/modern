"""
Enhanced Risk Management Service
=================================

Service untuk risk management dengan implementasi algoritma terbukti
menggunakan QuantLib, VaR calculations, dan advanced risk metrics.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import quantlib as ql
from scipy import stats
from app.models.trading import Portfolio, Position, Order
from app.models.market_data import MarketData

logger = logging.getLogger(__name__)

class EnhancedRiskManagementService:
    """
    Enhanced Risk Management Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_limits = {
            'max_position_size': 0.1,  # 10% max position
            'max_daily_loss': 0.02,    # 2% daily loss limit
            'max_portfolio_risk': 0.15, # 15% max portfolio risk
            'var_confidence': 0.95,    # 95% VaR confidence
            'max_correlation': 0.7     # 70% max correlation
        }
    
    async def check_position_limits(self, portfolio_id: int, symbol: str, quantity: float, price: float) -> Dict[str, Any]:
        """Check position size limits dengan enhanced algorithms"""
        try:
            # Get portfolio
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'allowed': False, 'reason': 'Portfolio not found'}
            
            # Get current positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            
            # Calculate current portfolio value
            portfolio_value = await self._calculate_portfolio_value(portfolio_id)
            
            # Calculate new position value
            new_position_value = quantity * price
            new_position_percentage = new_position_value / portfolio_value if portfolio_value > 0 else 0
            
            # Check position size limit
            if new_position_percentage > self.risk_limits['max_position_size']:
                return {
                    'allowed': False,
                    'reason': f'Position size {new_position_percentage:.2%} exceeds limit {self.risk_limits["max_position_size"]:.2%}'
                }
            
            # Check concentration risk
            concentration_check = await self._check_concentration_risk(
                portfolio_id, symbol, new_position_value, portfolio_value
            )
            if not concentration_check['allowed']:
                return concentration_check
            
            # Check correlation risk
            correlation_check = await self._check_correlation_risk(
                portfolio_id, symbol, new_position_value
            )
            if not correlation_check['allowed']:
                return correlation_check
            
            return {'allowed': True, 'reason': 'Position limits satisfied'}
            
        except Exception as e:
            logger.error(f"Error checking position limits: {e}")
            return {'allowed': False, 'reason': f'Error: {str(e)}'}
    
    async def _calculate_portfolio_value(self, portfolio_id: int) -> float:
        """Calculate current portfolio value"""
        try:
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            
            total_value = 0
            for position in positions:
                # Get current market price
                latest_data = self.db.query(MarketData).filter(
                    MarketData.symbol == position.symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    current_price = latest_data.close_price
                    position_value = position.quantity * current_price
                    total_value += position_value
            
            return total_value
            
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            return 0.0
    
    async def _check_concentration_risk(
        self, 
        portfolio_id: int, 
        symbol: str, 
        new_position_value: float, 
        portfolio_value: float
    ) -> Dict[str, Any]:
        """Check concentration risk untuk single asset"""
        try:
            # Get current position for this symbol
            current_position = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id,
                Position.symbol == symbol
            ).first()
            
            if current_position:
                # Get current market price
                latest_data = self.db.query(MarketData).filter(
                    MarketData.symbol == symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    current_price = latest_data.close_price
                    current_position_value = current_position.quantity * current_price
                    total_position_value = current_position_value + new_position_value
                    concentration_ratio = total_position_value / portfolio_value
                    
                    if concentration_ratio > self.risk_limits['max_position_size']:
                        return {
                            'allowed': False,
                            'reason': f'Concentration risk: {concentration_ratio:.2%} exceeds limit'
                        }
            
            return {'allowed': True, 'reason': 'Concentration risk acceptable'}
            
        except Exception as e:
            logger.error(f"Error checking concentration risk: {e}")
            return {'allowed': False, 'reason': f'Error: {str(e)}'}
    
    async def _check_correlation_risk(
        self, 
        portfolio_id: int, 
        symbol: str, 
        new_position_value: float
    ) -> Dict[str, Any]:
        """Check correlation risk dengan existing positions"""
        try:
            # Get existing positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            
            if not positions:
                return {'allowed': True, 'reason': 'No existing positions'}
            
            # Get historical data for correlation analysis
            symbols = [pos.symbol for pos in positions] + [symbol]
            historical_data = await self._get_historical_data_for_correlation(symbols)
            
            if historical_data.empty:
                return {'allowed': True, 'reason': 'Insufficient data for correlation analysis'}
            
            # Calculate correlations
            correlations = await self._calculate_correlations(historical_data, symbol)
            
            # Check if any correlation exceeds limit
            max_correlation = max(correlations.values()) if correlations else 0
            
            if max_correlation > self.risk_limits['max_correlation']:
                return {
                    'allowed': False,
                    'reason': f'High correlation risk: {max_correlation:.2%} exceeds limit'
                }
            
            return {'allowed': True, 'reason': 'Correlation risk acceptable'}
            
        except Exception as e:
            logger.error(f"Error checking correlation risk: {e}")
            return {'allowed': False, 'reason': f'Error: {str(e)}'}
    
    async def _get_historical_data_for_correlation(self, symbols: List[str]) -> pd.DataFrame:
        """Get historical data untuk correlation analysis"""
        try:
            # Get 30 days of historical data
            start_date = datetime.now() - timedelta(days=30)
            
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
                # Pivot to get symbols as columns
                pivot_df = df.pivot(index='timestamp', columns='symbol', values='close')
                return pivot_df
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting historical data for correlation: {e}")
            return pd.DataFrame()
    
    async def _calculate_correlations(self, data: pd.DataFrame, new_symbol: str) -> Dict[str, float]:
        """Calculate correlations dengan new symbol"""
        try:
            correlations = {}
            
            if new_symbol not in data.columns:
                return correlations
            
            for symbol in data.columns:
                if symbol != new_symbol and not data[symbol].isna().all():
                    # Calculate correlation
                    correlation = data[new_symbol].corr(data[symbol])
                    if not np.isnan(correlation):
                        correlations[symbol] = abs(correlation)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            return {}
    
    async def check_daily_loss_limits(self, portfolio_id: int) -> Dict[str, Any]:
        """Check daily loss limits dengan VaR calculations"""
        try:
            # Get portfolio
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'allowed': False, 'reason': 'Portfolio not found'}
            
            # Calculate daily P&L
            daily_pnl = await self._calculate_daily_pnl(portfolio_id)
            
            # Calculate portfolio value
            portfolio_value = await self._calculate_portfolio_value(portfolio_id)
            
            if portfolio_value > 0:
                daily_loss_percentage = abs(daily_pnl) / portfolio_value if daily_pnl < 0 else 0
                
                if daily_loss_percentage > self.risk_limits['max_daily_loss']:
                    return {
                        'allowed': False,
                        'reason': f'Daily loss {daily_loss_percentage:.2%} exceeds limit {self.risk_limits["max_daily_loss"]:.2%}'
                    }
            
            return {'allowed': True, 'reason': 'Daily loss limits satisfied'}
            
        except Exception as e:
            logger.error(f"Error checking daily loss limits: {e}")
            return {'allowed': False, 'reason': f'Error: {str(e)}'}
    
    async def _calculate_daily_pnl(self, portfolio_id: int) -> float:
        """Calculate daily P&L untuk portfolio"""
        try:
            # Get positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            
            total_pnl = 0
            for position in positions:
                # Get current and previous day prices
                current_data = self.db.query(MarketData).filter(
                    MarketData.symbol == position.symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if current_data:
                    # Get previous day price
                    yesterday = current_data.timestamp - timedelta(days=1)
                    prev_data = self.db.query(MarketData).filter(
                        MarketData.symbol == position.symbol,
                        MarketData.timestamp <= yesterday
                    ).order_by(MarketData.timestamp.desc()).first()
                    
                    if prev_data:
                        current_price = current_data.close_price
                        prev_price = prev_data.close_price
                        position_pnl = position.quantity * (current_price - prev_price)
                        total_pnl += position_pnl
            
            return total_pnl
            
        except Exception as e:
            logger.error(f"Error calculating daily P&L: {e}")
            return 0.0
    
    async def calculate_portfolio_var(self, portfolio_id: int, confidence_level: float = 0.95) -> Dict[str, Any]:
        """Calculate Value at Risk (VaR) untuk portfolio"""
        try:
            # Get historical returns
            returns = await self._get_portfolio_returns(portfolio_id)
            
            if returns.empty:
                return {'error': 'Insufficient data for VaR calculation'}
            
            # Calculate VaR using different methods
            var_results = {}
            
            # 1. Historical VaR
            var_results['historical'] = self._calculate_historical_var(returns, confidence_level)
            
            # 2. Parametric VaR (assuming normal distribution)
            var_results['parametric'] = self._calculate_parametric_var(returns, confidence_level)
            
            # 3. Monte Carlo VaR
            var_results['monte_carlo'] = self._calculate_monte_carlo_var(returns, confidence_level)
            
            # 4. Expected Shortfall (CVaR)
            var_results['expected_shortfall'] = self._calculate_expected_shortfall(returns, confidence_level)
            
            return {
                'success': True,
                'var_results': var_results,
                'confidence_level': confidence_level,
                'portfolio_id': portfolio_id
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio VaR: {e}")
            return {'error': str(e)}
    
    async def _get_portfolio_returns(self, portfolio_id: int, days: int = 30) -> pd.Series:
        """Get portfolio returns untuk VaR calculation"""
        try:
            # Get positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            
            if not positions:
                return pd.Series()
            
            # Get historical data for all positions
            symbols = [pos.symbol for pos in positions]
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
            if df.empty:
                return pd.Series()
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Calculate returns for each symbol
            symbol_returns = {}
            for symbol in symbols:
                symbol_data = df[df['symbol'] == symbol]['close']
                if len(symbol_data) > 1:
                    returns = symbol_data.pct_change().dropna()
                    symbol_returns[symbol] = returns
            
            if not symbol_returns:
                return pd.Series()
            
            # Calculate portfolio returns (equal weight)
            portfolio_returns = None
            for symbol, returns in symbol_returns.items():
                if portfolio_returns is None:
                    portfolio_returns = returns / len(symbol_returns)
                else:
                    portfolio_returns += returns / len(symbol_returns)
            
            return portfolio_returns if portfolio_returns is not None else pd.Series()
            
        except Exception as e:
            logger.error(f"Error getting portfolio returns: {e}")
            return pd.Series()
    
    def _calculate_historical_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Historical VaR"""
        try:
            if returns.empty:
                return 0.0
            
            # Sort returns
            sorted_returns = returns.sort_values()
            
            # Calculate VaR
            var_index = int((1 - confidence_level) * len(sorted_returns))
            var = sorted_returns.iloc[var_index] if var_index < len(sorted_returns) else sorted_returns.min()
            
            return abs(var)
            
        except Exception as e:
            logger.error(f"Error calculating historical VaR: {e}")
            return 0.0
    
    def _calculate_parametric_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Parametric VaR (assuming normal distribution)"""
        try:
            if returns.empty:
                return 0.0
            
            mean = returns.mean()
            std = returns.std()
            
            # Z-score for confidence level
            z_score = stats.norm.ppf(1 - confidence_level)
            
            var = mean + z_score * std
            return abs(var)
            
        except Exception as e:
            logger.error(f"Error calculating parametric VaR: {e}")
            return 0.0
    
    def _calculate_monte_carlo_var(self, returns: pd.Series, confidence_level: float, simulations: int = 10000) -> float:
        """Calculate Monte Carlo VaR"""
        try:
            if returns.empty:
                return 0.0
            
            mean = returns.mean()
            std = returns.std()
            
            # Generate random returns
            np.random.seed(42)
            random_returns = np.random.normal(mean, std, simulations)
            
            # Calculate VaR
            var_index = int((1 - confidence_level) * simulations)
            var = np.sort(random_returns)[var_index]
            
            return abs(var)
            
        except Exception as e:
            logger.error(f"Error calculating Monte Carlo VaR: {e}")
            return 0.0
    
    def _calculate_expected_shortfall(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Expected Shortfall (CVaR)"""
        try:
            if returns.empty:
                return 0.0
            
            # Calculate VaR first
            var = self._calculate_historical_var(returns, confidence_level)
            
            # Calculate expected shortfall
            tail_returns = returns[returns <= -var]
            if len(tail_returns) > 0:
                expected_shortfall = abs(tail_returns.mean())
            else:
                expected_shortfall = abs(var)
            
            return expected_shortfall
            
        except Exception as e:
            logger.error(f"Error calculating expected shortfall: {e}")
            return 0.0
    
    async def get_risk_metrics(self, portfolio_id: int) -> Dict[str, Any]:
        """Get comprehensive risk metrics untuk portfolio"""
        try:
            # Calculate various risk metrics
            portfolio_value = await self._calculate_portfolio_value(portfolio_id)
            daily_pnl = await self._calculate_daily_pnl(portfolio_id)
            
            # VaR calculation
            var_result = await self.calculate_portfolio_var(portfolio_id)
            
            # Position analysis
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            
            position_metrics = {
                'total_positions': len(positions),
                'largest_position': 0,
                'concentration_risk': 0
            }
            
            if positions and portfolio_value > 0:
                position_values = []
                for position in positions:
                    latest_data = self.db.query(MarketData).filter(
                        MarketData.symbol == position.symbol
                    ).order_by(MarketData.timestamp.desc()).first()
                    
                    if latest_data:
                        position_value = position.quantity * latest_data.close_price
                        position_values.append(position_value)
                
                if position_values:
                    position_metrics['largest_position'] = max(position_values) / portfolio_value
                    position_metrics['concentration_risk'] = max(position_values) / portfolio_value
            
            return {
                'success': True,
                'portfolio_value': portfolio_value,
                'daily_pnl': daily_pnl,
                'daily_pnl_percentage': daily_pnl / portfolio_value if portfolio_value > 0 else 0,
                'var_results': var_result.get('var_results', {}),
                'position_metrics': position_metrics,
                'risk_limits': self.risk_limits,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting risk metrics: {e}")
            return {'error': str(e)}
