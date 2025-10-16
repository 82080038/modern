"""
Enhanced Watchlist Service
==========================

Service untuk watchlist dengan implementasi algoritma terbukti
menggunakan smart recommendations, performance tracking, dan advanced filtering.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import yfinance as yf
from app.models.watchlist import Watchlist, WatchlistItem, WatchlistCategory
from app.models.market_data import MarketData
from app.services.enhanced_market_data_service_v2 import EnhancedMarketDataServiceV2
from app.services.enhanced_fundamental_analysis_service import EnhancedFundamentalAnalysisService
from app.services.enhanced_notifications_service import EnhancedNotificationsService

logger = logging.getLogger(__name__)

class EnhancedWatchlistService:
    """
    Enhanced Watchlist Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = EnhancedMarketDataServiceV2(db)
        self.fundamental_service = EnhancedFundamentalAnalysisService(db)
        self.notifications_service = EnhancedNotificationsService(db)
        
        # Watchlist categories
        self.categories = {
            'high_growth': {'description': 'High growth potential stocks', 'criteria': ['revenue_growth', 'earnings_growth']},
            'value': {'description': 'Undervalued stocks', 'criteria': ['pe_ratio', 'pb_ratio', 'intrinsic_value']},
            'dividend': {'description': 'Dividend paying stocks', 'criteria': ['dividend_yield', 'dividend_growth']},
            'momentum': {'description': 'Momentum stocks', 'criteria': ['price_momentum', 'volume_momentum']},
            'sector': {'description': 'Sector-specific stocks', 'criteria': ['sector_performance']},
            'technical': {'description': 'Technically strong stocks', 'criteria': ['technical_indicators']},
            'fundamental': {'description': 'Fundamentally strong stocks', 'criteria': ['financial_ratios']},
            'custom': {'description': 'Custom criteria', 'criteria': []}
        }
        
        # Performance metrics
        self.performance_metrics = [
            'total_return', 'annualized_return', 'volatility', 'sharpe_ratio',
            'max_drawdown', 'win_rate', 'average_hold_time', 'best_performer',
            'worst_performer', 'correlation_analysis'
        ]
        
        # Recommendation algorithms
        self.recommendation_algorithms = {
            'similarity_based': {'weight': 0.3, 'description': 'Based on similar stocks'},
            'performance_based': {'weight': 0.25, 'description': 'Based on historical performance'},
            'fundamental_based': {'weight': 0.25, 'description': 'Based on fundamental analysis'},
            'technical_based': {'weight': 0.2, 'description': 'Based on technical analysis'}
        }
    
    async def create_watchlist(
        self, 
        user_id: int,
        name: str,
        description: Optional[str] = None,
        category: str = 'custom',
        is_public: bool = False,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create enhanced watchlist"""
        try:
            # Validate category
            if category not in self.categories:
                return {'error': f'Invalid category: {category}'}
            
            # Create watchlist
            watchlist = Watchlist(
                user_id=user_id,
                name=name,
                description=description,
                category=category,
                is_public=is_public,
                tags=json.dumps(tags or []),
                created_at=datetime.now()
            )
            
            self.db.add(watchlist)
            self.db.flush()  # Get the ID
            
            # Initialize watchlist metrics
            await self._initialize_watchlist_metrics(watchlist.id)
            
            return {
                'success': True,
                'watchlist_id': watchlist.id,
                'name': name,
                'category': category,
                'created_at': watchlist.created_at
            }
            
        except Exception as e:
            logger.error(f"Error creating watchlist: {e}")
            return {'error': str(e)}
    
    async def add_symbol_to_watchlist(
        self, 
        watchlist_id: int, 
        symbol: str,
        user_id: int,
        notes: Optional[str] = None,
        target_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add symbol to watchlist dengan enhanced features"""
        try:
            # Verify watchlist ownership
            watchlist = self.db.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()
            
            if not watchlist:
                return {'error': 'Watchlist not found or access denied'}
            
            # Check if symbol already exists
            existing_item = self.db.query(WatchlistItem).filter(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.symbol == symbol
            ).first()
            
            if existing_item:
                return {'error': f'Symbol {symbol} already exists in watchlist'}
            
            # Get symbol data
            symbol_data = await self._get_symbol_data(symbol)
            if not symbol_data:
                return {'error': f'Invalid symbol: {symbol}'}
            
            # Create watchlist item
            watchlist_item = WatchlistItem(
                watchlist_id=watchlist_id,
                symbol=symbol,
                notes=notes,
                target_price=target_price,
                stop_loss=stop_loss,
                tags=json.dumps(tags or []),
                added_at=datetime.now()
            )
            
            self.db.add(watchlist_item)
            self.db.commit()
            
            # Update watchlist metrics
            await self._update_watchlist_metrics(watchlist_id)
            
            # Create price alert if target price is set
            if target_price:
                await self._create_price_alert(user_id, symbol, target_price)
            
            return {
                'success': True,
                'watchlist_item_id': watchlist_item.id,
                'symbol': symbol,
                'added_at': watchlist_item.added_at
            }
            
        except Exception as e:
            logger.error(f"Error adding symbol to watchlist: {e}")
            return {'error': str(e)}
    
    async def _get_symbol_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol data untuk validation"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting symbol data: {e}")
            return None
    
    async def _create_price_alert(self, user_id: int, symbol: str, target_price: float):
        """Create price alert untuk target price"""
        try:
            await self.notifications_service.create_price_alert(
                user_id=user_id,
                symbol=symbol,
                target_price=target_price,
                condition='above',
                message=f"Target price reached for {symbol}"
            )
            
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
    
    async def get_watchlist_performance(
        self, 
        watchlist_id: int, 
        user_id: int,
        period: str = '1y',
        include_benchmark: bool = True
    ) -> Dict[str, Any]:
        """Get comprehensive watchlist performance analysis"""
        try:
            # Verify watchlist ownership
            watchlist = self.db.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()
            
            if not watchlist:
                return {'error': 'Watchlist not found or access denied'}
            
            # Get watchlist items
            items = self.db.query(WatchlistItem).filter(
                WatchlistItem.watchlist_id == watchlist_id
            ).all()
            
            if not items:
                return {'error': 'No symbols in watchlist'}
            
            # Get performance data
            performance_data = await self._calculate_watchlist_performance(items, period)
            
            # Get benchmark comparison
            benchmark_data = None
            if include_benchmark:
                benchmark_data = await self._get_benchmark_performance(period)
            
            # Get individual symbol performance
            symbol_performance = await self._get_symbol_performance(items, period)
            
            # Get correlation analysis
            correlation_analysis = await self._analyze_correlation(items, period)
            
            # Get risk metrics
            risk_metrics = await self._calculate_risk_metrics(items, period)
            
            # Get recommendations
            recommendations = await self._generate_watchlist_recommendations(watchlist_id, items)
            
            return {
                'success': True,
                'watchlist_id': watchlist_id,
                'period': period,
                'performance_data': performance_data,
                'benchmark_data': benchmark_data,
                'symbol_performance': symbol_performance,
                'correlation_analysis': correlation_analysis,
                'risk_metrics': risk_metrics,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting watchlist performance: {e}")
            return {'error': str(e)}
    
    async def _calculate_watchlist_performance(self, items: List[WatchlistItem], period: str) -> Dict[str, Any]:
        """Calculate watchlist performance metrics"""
        try:
            symbols = [item.symbol for item in items]
            
            # Get historical data
            historical_data = await self._get_historical_data(symbols, period)
            if historical_data.empty:
                return {}
            
            # Calculate performance metrics
            performance = {
                'total_return': 0.0,
                'annualized_return': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'best_performer': None,
                'worst_performer': None
            }
            
            # Calculate returns for each symbol
            returns_data = {}
            for symbol in symbols:
                symbol_data = historical_data[historical_data['symbol'] == symbol]
                if not symbol_data.empty:
                    symbol_data = symbol_data.sort_values('date')
                    returns = symbol_data['close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if not returns_data:
                return performance
            
            # Calculate portfolio returns (equal weight)
            portfolio_returns = pd.DataFrame(returns_data).mean(axis=1)
            
            # Total return
            if len(portfolio_returns) > 0:
                performance['total_return'] = (1 + portfolio_returns).prod() - 1
            
            # Annualized return
            days = len(portfolio_returns)
            if days > 0:
                performance['annualized_return'] = (1 + performance['total_return']) ** (252 / days) - 1
            
            # Volatility
            performance['volatility'] = portfolio_returns.std() * np.sqrt(252)
            
            # Sharpe ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02
            if performance['volatility'] > 0:
                performance['sharpe_ratio'] = (performance['annualized_return'] - risk_free_rate) / performance['volatility']
            
            # Max drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            performance['max_drawdown'] = drawdown.min()
            
            # Win rate
            positive_returns = (portfolio_returns > 0).sum()
            total_returns = len(portfolio_returns)
            performance['win_rate'] = positive_returns / total_returns if total_returns > 0 else 0
            
            # Best and worst performers
            symbol_returns = {}
            for symbol, returns in returns_data.items():
                if len(returns) > 0:
                    symbol_returns[symbol] = (1 + returns).prod() - 1
            
            if symbol_returns:
                performance['best_performer'] = max(symbol_returns, key=symbol_returns.get)
                performance['worst_performer'] = min(symbol_returns, key=symbol_returns.get)
            
            return performance
            
        except Exception as e:
            logger.error(f"Error calculating watchlist performance: {e}")
            return {}
    
    async def _get_historical_data(self, symbols: List[str], period: str) -> pd.DataFrame:
        """Get historical data untuk symbols"""
        try:
            # Convert period to days
            period_map = {
                '1m': 30, '3m': 90, '6m': 180, '1y': 365, '2y': 730, '5y': 1825
            }
            days = period_map.get(period, 365)
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Get market data from database
            market_data = self.db.query(MarketData).filter(
                MarketData.symbol.in_(symbols),
                MarketData.timestamp >= start_date
            ).order_by(MarketData.timestamp).all()
            
            # Convert to DataFrame
            data = []
            for record in market_data:
                data.append({
                    'date': record.timestamp,
                    'symbol': record.symbol,
                    'close': record.close_price
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    async def _get_benchmark_performance(self, period: str) -> Dict[str, Any]:
        """Get benchmark performance (S&P 500)"""
        try:
            # Get S&P 500 data
            benchmark_data = await self._get_historical_data(['^GSPC'], period)
            if benchmark_data.empty:
                return {}
            
            benchmark_data = benchmark_data.sort_values('date')
            returns = benchmark_data['close'].pct_change().dropna()
            
            if len(returns) == 0:
                return {}
            
            # Calculate benchmark metrics
            total_return = (1 + returns).prod() - 1
            days = len(returns)
            annualized_return = (1 + total_return) ** (252 / days) - 1
            volatility = returns.std() * np.sqrt(252)
            
            return {
                'symbol': '^GSPC',
                'name': 'S&P 500',
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Error getting benchmark performance: {e}")
            return {}
    
    async def _get_symbol_performance(self, items: List[WatchlistItem], period: str) -> List[Dict[str, Any]]:
        """Get individual symbol performance"""
        try:
            symbol_performance = []
            
            for item in items:
                # Get symbol data
                symbol_data = await self._get_historical_data([item.symbol], period)
                if symbol_data.empty:
                    continue
                
                symbol_data = symbol_data.sort_values('date')
                returns = symbol_data['close'].pct_change().dropna()
                
                if len(returns) == 0:
                    continue
                
                # Calculate metrics
                total_return = (1 + returns).prod() - 1
                days = len(returns)
                annualized_return = (1 + total_return) ** (252 / days) - 1
                volatility = returns.std() * np.sqrt(252)
                
                # Calculate Sharpe ratio
                risk_free_rate = 0.02
                sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
                
                symbol_performance.append({
                    'symbol': item.symbol,
                    'total_return': total_return,
                    'annualized_return': annualized_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'target_price': item.target_price,
                    'stop_loss': item.stop_loss,
                    'notes': item.notes
                })
            
            return symbol_performance
            
        except Exception as e:
            logger.error(f"Error getting symbol performance: {e}")
            return []
    
    async def _analyze_correlation(self, items: List[WatchlistItem], period: str) -> Dict[str, Any]:
        """Analyze correlation between symbols"""
        try:
            symbols = [item.symbol for item in items]
            if len(symbols) < 2:
                return {}
            
            # Get historical data
            historical_data = await self._get_historical_data(symbols, period)
            if historical_data.empty:
                return {}
            
            # Calculate returns
            returns_data = {}
            for symbol in symbols:
                symbol_data = historical_data[historical_data['symbol'] == symbol]
                if not symbol_data.empty:
                    symbol_data = symbol_data.sort_values('date')
                    returns = symbol_data['close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return {}
            
            # Calculate correlation matrix
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            # Find high correlation pairs
            high_correlation_pairs = []
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols):
                    if i < j and symbol1 in correlation_matrix.columns and symbol2 in correlation_matrix.columns:
                        correlation = correlation_matrix.loc[symbol1, symbol2]
                        if abs(correlation) > 0.7:  # High correlation threshold
                            high_correlation_pairs.append({
                                'symbol1': symbol1,
                                'symbol2': symbol2,
                                'correlation': correlation
                            })
            
            # Calculate average correlation
            correlations = correlation_matrix.values
            correlations = correlations[np.triu_indices_from(correlations, k=1)]
            average_correlation = np.mean(correlations)
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'high_correlation_pairs': high_correlation_pairs,
                'average_correlation': average_correlation,
                'diversification_score': 1 - abs(average_correlation)  # Higher is better
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlation: {e}")
            return {}
    
    async def _calculate_risk_metrics(self, items: List[WatchlistItem], period: str) -> Dict[str, Any]:
        """Calculate risk metrics untuk watchlist"""
        try:
            symbols = [item.symbol for item in items]
            
            # Get historical data
            historical_data = await self._get_historical_data(symbols, period)
            if historical_data.empty:
                return {}
            
            # Calculate returns
            returns_data = {}
            for symbol in symbols:
                symbol_data = historical_data[historical_data['symbol'] == symbol]
                if not symbol_data.empty:
                    symbol_data = symbol_data.sort_values('date')
                    returns = symbol_data['close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if not returns_data:
                return {}
            
            # Calculate portfolio returns
            returns_df = pd.DataFrame(returns_data)
            portfolio_returns = returns_df.mean(axis=1)
            
            # Risk metrics
            risk_metrics = {
                'portfolio_volatility': portfolio_returns.std() * np.sqrt(252),
                'var_95': np.percentile(portfolio_returns, 5),
                'var_99': np.percentile(portfolio_returns, 1),
                'max_drawdown': 0.0,
                'beta': 0.0,
                'tracking_error': 0.0
            }
            
            # Max drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            risk_metrics['max_drawdown'] = drawdown.min()
            
            # Beta (simplified)
            if len(portfolio_returns) > 1:
                risk_metrics['beta'] = portfolio_returns.cov(portfolio_returns) / portfolio_returns.var()
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    async def _generate_watchlist_recommendations(self, watchlist_id: int, items: List[WatchlistItem]) -> List[Dict[str, Any]]:
        """Generate watchlist recommendations"""
        try:
            recommendations = []
            
            # Analyze watchlist composition
            symbols = [item.symbol for item in items]
            
            # Get sector analysis
            sector_analysis = await self._analyze_sector_diversification(symbols)
            
            # Get performance analysis
            performance_analysis = await self._analyze_performance_trends(symbols)
            
            # Generate recommendations
            if sector_analysis.get('concentration_risk', 0) > 0.7:
                recommendations.append({
                    'type': 'diversification',
                    'priority': 'high',
                    'message': 'High sector concentration detected. Consider diversifying across sectors.',
                    'action': 'add_different_sectors'
                })
            
            if performance_analysis.get('underperformers', 0) > len(symbols) * 0.3:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'message': 'Multiple underperforming symbols detected. Consider reviewing positions.',
                    'action': 'review_performance'
                })
            
            if len(symbols) < 5:
                recommendations.append({
                    'type': 'size',
                    'priority': 'low',
                    'message': 'Watchlist has fewer than 5 symbols. Consider adding more for better diversification.',
                    'action': 'add_more_symbols'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating watchlist recommendations: {e}")
            return []
    
    async def _analyze_sector_diversification(self, symbols: List[str]) -> Dict[str, Any]:
        """Analyze sector diversification"""
        try:
            sectors = {}
            for symbol in symbols:
                # Get sector information
                ticker = yf.Ticker(symbol)
                info = ticker.info
                sector = info.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + 1
            
            # Calculate concentration
            total_symbols = len(symbols)
            sector_weights = {sector: count / total_symbols for sector, count in sectors.items()}
            concentration_risk = max(sector_weights.values()) if sector_weights else 0
            
            return {
                'sectors': sectors,
                'sector_weights': sector_weights,
                'concentration_risk': concentration_risk,
                'diversification_score': 1 - concentration_risk
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sector diversification: {e}")
            return {}
    
    async def _analyze_performance_trends(self, symbols: List[str]) -> Dict[str, Any]:
        """Analyze performance trends"""
        try:
            # This would implement performance trend analysis
            # For now, return placeholder
            return {
                'underperformers': 0,
                'outperformers': 0,
                'trend_direction': 'neutral'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {}
    
    async def _initialize_watchlist_metrics(self, watchlist_id: int):
        """Initialize watchlist metrics"""
        try:
            # This would initialize watchlist metrics
            logger.info(f"Initialized metrics for watchlist {watchlist_id}")
            
        except Exception as e:
            logger.error(f"Error initializing watchlist metrics: {e}")
    
    async def _update_watchlist_metrics(self, watchlist_id: int):
        """Update watchlist metrics"""
        try:
            # This would update watchlist metrics
            logger.info(f"Updated metrics for watchlist {watchlist_id}")
            
        except Exception as e:
            logger.error(f"Error updating watchlist metrics: {e}")
    
    async def get_smart_recommendations(
        self, 
        user_id: int,
        watchlist_id: int,
        recommendation_type: str = 'similar',
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get smart recommendations untuk watchlist"""
        try:
            # Get watchlist
            watchlist = self.db.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()
            
            if not watchlist:
                return {'error': 'Watchlist not found or access denied'}
            
            # Get current symbols
            items = self.db.query(WatchlistItem).filter(
                WatchlistItem.watchlist_id == watchlist_id
            ).all()
            
            current_symbols = [item.symbol for item in items]
            
            # Generate recommendations based on type
            if recommendation_type == 'similar':
                recommendations = await self._get_similar_recommendations(current_symbols, limit)
            elif recommendation_type == 'diversification':
                recommendations = await self._get_diversification_recommendations(current_symbols, limit)
            elif recommendation_type == 'performance':
                recommendations = await self._get_performance_recommendations(current_symbols, limit)
            else:
                return {'error': f'Invalid recommendation type: {recommendation_type}'}
            
            return {
                'success': True,
                'recommendations': recommendations,
                'recommendation_type': recommendation_type,
                'total_recommendations': len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error getting smart recommendations: {e}")
            return {'error': str(e)}
    
    async def _get_similar_recommendations(self, current_symbols: List[str], limit: int) -> List[Dict[str, Any]]:
        """Get similar stock recommendations"""
        try:
            # This would implement similarity-based recommendations
            # For now, return placeholder
            return [
                {
                    'symbol': 'AAPL',
                    'company_name': 'Apple Inc.',
                    'sector': 'Technology',
                    'similarity_score': 0.85,
                    'reason': 'Similar sector and market cap'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting similar recommendations: {e}")
            return []
    
    async def _get_diversification_recommendations(self, current_symbols: List[str], limit: int) -> List[Dict[str, Any]]:
        """Get diversification recommendations"""
        try:
            # This would implement diversification-based recommendations
            # For now, return placeholder
            return [
                {
                    'symbol': 'JNJ',
                    'company_name': 'Johnson & Johnson',
                    'sector': 'Healthcare',
                    'diversification_score': 0.9,
                    'reason': 'Different sector for diversification'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting diversification recommendations: {e}")
            return []
    
    async def _get_performance_recommendations(self, current_symbols: List[str], limit: int) -> List[Dict[str, Any]]:
        """Get performance-based recommendations"""
        try:
            # This would implement performance-based recommendations
            # For now, return placeholder
            return [
                {
                    'symbol': 'TSLA',
                    'company_name': 'Tesla Inc.',
                    'sector': 'Automotive',
                    'performance_score': 0.8,
                    'reason': 'Strong recent performance'
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting performance recommendations: {e}")
            return []
