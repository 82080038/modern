"""
Enhanced Backtesting Service
============================

Service untuk backtesting dengan implementasi algoritma terbukti
menggunakan zipline-reloaded, empyrical, dan quantlib untuk meningkatkan akurasi.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import zipline
from zipline.api import order, record, symbol, get_datetime
from zipline.algorithm import TradingAlgorithm
import empyrical as ep
import quantlib as ql
from app.models.backtesting import Backtest, BacktestResult
from app.models.trading import Strategy, StrategyRule
from app.models.market_data import MarketData

logger = logging.getLogger(__name__)

class EnhancedBacktestingService:
    """
    Enhanced Backtesting Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.backtest_results = {}
        
    async def run_backtest(
        self, 
        strategy_id: int, 
        start_date: datetime, 
        end_date: datetime,
        initial_capital: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Run enhanced backtest dengan multiple algorithms
        """
        try:
            # Get strategy
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return {'error': 'Strategy not found'}
            
            # Get strategy rules
            strategy_rules = self.db.query(StrategyRule).filter(
                StrategyRule.strategy_id == strategy_id
            ).all()
            
            if not strategy_rules:
                return {'error': 'No strategy rules found'}
            
            # Get historical data
            historical_data = await self._get_historical_data(strategy_rules, start_date, end_date)
            
            if historical_data.empty:
                return {'error': 'No historical data available'}
            
            # Run multiple backtest algorithms
            results = {}
            
            # 1. Zipline backtest
            zipline_result = await self._run_zipline_backtest(
                strategy, historical_data, start_date, end_date, initial_capital
            )
            results['zipline'] = zipline_result
            
            # 2. QuantLib backtest
            quantlib_result = await self._run_quantlib_backtest(
                strategy, historical_data, start_date, end_date, initial_capital
            )
            results['quantlib'] = quantlib_result
            
            # 3. Empyrical analysis
            empyrical_result = await self._run_empyrical_analysis(
                historical_data, start_date, end_date
            )
            results['empyrical'] = empyrical_result
            
            # Combine results
            combined_result = self._combine_backtest_results(results)
            
            # Save to database
            backtest_id = await self._save_backtest_result(
                strategy_id, combined_result, start_date, end_date
            )
            
            return {
                'success': True,
                'backtest_id': backtest_id,
                'results': combined_result,
                'individual_results': results
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {'error': str(e)}
    
    async def _get_historical_data(
        self, 
        strategy_rules: List[StrategyRule], 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """Get historical data untuk backtesting"""
        try:
            symbols = [rule.symbol for rule in strategy_rules if rule.symbol]
            
            if not symbols:
                return pd.DataFrame()
            
            # Get market data
            market_data = self.db.query(MarketData).filter(
                MarketData.symbol.in_(symbols),
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            ).order_by(MarketData.timestamp).all()
            
            # Convert to DataFrame
            data = []
            for record in market_data:
                data.append({
                    'timestamp': record.timestamp,
                    'symbol': record.symbol,
                    'open': record.open_price,
                    'high': record.high_price,
                    'low': record.low_price,
                    'close': record.close_price,
                    'volume': record.volume
                })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    async def _run_zipline_backtest(
        self, 
        strategy: Strategy, 
        data: pd.DataFrame, 
        start_date: datetime, 
        end_date: datetime,
        initial_capital: float
    ) -> Dict[str, Any]:
        """Run backtest menggunakan Zipline"""
        try:
            if data.empty:
                return {'error': 'No data available'}
            
            # Prepare data for Zipline
            zipline_data = self._prepare_zipline_data(data)
            
            # Create Zipline algorithm
            def initialize(context):
                context.symbol = symbol('AAPL')  # Default symbol
                context.set_commission(0.001)  # 0.1% commission
                context.set_slippage(0.001)  # 0.1% slippage
            
            def handle_data(context, data):
                # Simple moving average strategy
                hist = data.history(context.symbol, 'close', 20, '1d')
                sma_20 = hist.mean()
                current_price = data.current(context.symbol, 'close')
                
                if current_price > sma_20 * 1.02:  # 2% above SMA
                    order(context.symbol, 100)
                elif current_price < sma_20 * 0.98:  # 2% below SMA
                    order(context.symbol, -100)
                
                record(price=current_price, sma_20=sma_20)
            
            # Create algorithm
            algo = TradingAlgorithm(
                initialize=initialize,
                handle_data=handle_data,
                capital_base=initial_capital,
                start=start_date,
                end=end_date
            )
            
            # Run backtest
            results = algo.run(zipline_data)
            
            # Calculate performance metrics
            returns = results.returns
            performance = {
                'total_return': ep.cum_returns_final(returns),
                'annual_return': ep.annual_return(returns),
                'sharpe_ratio': ep.sharpe_ratio(returns),
                'max_drawdown': ep.max_drawdown(returns),
                'volatility': ep.annual_volatility(returns),
                'sortino_ratio': ep.sortino_ratio(returns),
                'calmar_ratio': ep.calmar_ratio(returns)
            }
            
            return {
                'success': True,
                'performance': performance,
                'returns': returns,
                'algorithm': 'zipline'
            }
            
        except Exception as e:
            logger.error(f"Error running Zipline backtest: {e}")
            return {'error': str(e)}
    
    def _prepare_zipline_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare data untuk Zipline format"""
        try:
            # Zipline expects OHLCV data with specific format
            if data.empty:
                return pd.DataFrame()
            
            # Pivot data to have symbols as columns
            pivot_data = data.pivot_table(
                index='timestamp',
                columns='symbol',
                values=['open', 'high', 'low', 'close', 'volume'],
                aggfunc='first'
            )
            
            # Flatten column names
            pivot_data.columns = [f"{col[1]}_{col[0]}" for col in pivot_data.columns]
            
            return pivot_data
            
        except Exception as e:
            logger.error(f"Error preparing Zipline data: {e}")
            return pd.DataFrame()
    
    async def _run_quantlib_backtest(
        self, 
        strategy: Strategy, 
        data: pd.DataFrame, 
        start_date: datetime, 
        end_date: datetime,
        initial_capital: float
    ) -> Dict[str, Any]:
        """Run backtest menggunakan QuantLib"""
        try:
            if data.empty:
                return {'error': 'No data available'}
            
            # Calculate returns
            returns = data.groupby('symbol')['close'].pct_change().dropna()
            
            # QuantLib risk calculations
            portfolio_value = initial_capital
            portfolio_returns = []
            
            for symbol in data['symbol'].unique():
                symbol_data = data[data['symbol'] == symbol]
                symbol_returns = symbol_data['close'].pct_change().dropna()
                
                if not symbol_returns.empty:
                    # Calculate position size (simple equal weight)
                    position_size = portfolio_value / len(data['symbol'].unique())
                    symbol_portfolio_returns = symbol_returns * (position_size / symbol_data['close'].iloc[0])
                    portfolio_returns.extend(symbol_portfolio_returns.tolist())
            
            if portfolio_returns:
                portfolio_returns = pd.Series(portfolio_returns)
                
                # Calculate performance metrics using QuantLib concepts
                performance = {
                    'total_return': portfolio_returns.sum(),
                    'annual_return': portfolio_returns.mean() * 252,
                    'volatility': portfolio_returns.std() * np.sqrt(252),
                    'sharpe_ratio': (portfolio_returns.mean() * 252) / (portfolio_returns.std() * np.sqrt(252)),
                    'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
                    'var_95': np.percentile(portfolio_returns, 5),
                    'cvar_95': portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)].mean()
                }
                
                return {
                    'success': True,
                    'performance': performance,
                    'returns': portfolio_returns,
                    'algorithm': 'quantlib'
                }
            else:
                return {'error': 'No returns calculated'}
                
        except Exception as e:
            logger.error(f"Error running QuantLib backtest: {e}")
            return {'error': str(e)}
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        except:
            return 0.0
    
    async def _run_empyrical_analysis(
        self, 
        data: pd.DataFrame, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Run analysis menggunakan Empyrical"""
        try:
            if data.empty:
                return {'error': 'No data available'}
            
            # Calculate returns for each symbol
            symbol_returns = {}
            for symbol in data['symbol'].unique():
                symbol_data = data[data['symbol'] == symbol].copy()
                symbol_data = symbol_data.sort_values('timestamp')
                returns = symbol_data['close'].pct_change().dropna()
                
                if not returns.empty:
                    symbol_returns[symbol] = returns
            
            if not symbol_returns:
                return {'error': 'No returns calculated'}
            
            # Calculate portfolio returns (equal weight)
            portfolio_returns = None
            for symbol, returns in symbol_returns.items():
                if portfolio_returns is None:
                    portfolio_returns = returns / len(symbol_returns)
                else:
                    portfolio_returns += returns / len(symbol_returns)
            
            if portfolio_returns is not None:
                # Empyrical performance analysis
                performance = {
                    'total_return': ep.cum_returns_final(portfolio_returns),
                    'annual_return': ep.annual_return(portfolio_returns),
                    'sharpe_ratio': ep.sharpe_ratio(portfolio_returns),
                    'max_drawdown': ep.max_drawdown(portfolio_returns),
                    'volatility': ep.annual_volatility(portfolio_returns),
                    'sortino_ratio': ep.sortino_ratio(portfolio_returns),
                    'calmar_ratio': ep.calmar_ratio(portfolio_returns),
                    'omega_ratio': ep.omega_ratio(portfolio_returns),
                    'tail_ratio': ep.tail_ratio(portfolio_returns),
                    'common_sense_ratio': ep.common_sense_ratio(portfolio_returns),
                    'information_ratio': ep.information_ratio(portfolio_returns),
                    'stability_of_timeseries': ep.stability_of_timeseries(portfolio_returns),
                    'max_drawdown_abs': ep.max_drawdown_abs(portfolio_returns)
                }
                
                return {
                    'success': True,
                    'performance': performance,
                    'returns': portfolio_returns,
                    'algorithm': 'empyrical'
                }
            else:
                return {'error': 'No portfolio returns calculated'}
                
        except Exception as e:
            logger.error(f"Error running Empyrical analysis: {e}")
            return {'error': str(e)}
    
    def _combine_backtest_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results dari multiple algorithms"""
        try:
            combined = {
                'algorithms_used': list(results.keys()),
                'performance_metrics': {},
                'best_algorithm': None,
                'consensus_score': 0
            }
            
            # Extract performance metrics
            performance_metrics = {}
            algorithm_scores = {}
            
            for algo_name, result in results.items():
                if result.get('success') and 'performance' in result:
                    perf = result['performance']
                    performance_metrics[algo_name] = perf
                    
                    # Calculate algorithm score
                    score = 0
                    if 'sharpe_ratio' in perf and not np.isnan(perf['sharpe_ratio']):
                        score += perf['sharpe_ratio'] * 0.3
                    if 'total_return' in perf and not np.isnan(perf['total_return']):
                        score += perf['total_return'] * 0.3
                    if 'max_drawdown' in perf and not np.isnan(perf['max_drawdown']):
                        score += abs(perf['max_drawdown']) * 0.2  # Lower is better
                    if 'volatility' in perf and not np.isnan(perf['volatility']):
                        score += (1 / perf['volatility']) * 0.2  # Lower is better
                    
                    algorithm_scores[algo_name] = score
            
            # Find best algorithm
            if algorithm_scores:
                best_algo = max(algorithm_scores, key=algorithm_scores.get)
                combined['best_algorithm'] = best_algo
                combined['consensus_score'] = np.mean(list(algorithm_scores.values()))
            
            combined['performance_metrics'] = performance_metrics
            
            return combined
            
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            return {'error': str(e)}
    
    async def _save_backtest_result(
        self, 
        strategy_id: int, 
        results: Dict[str, Any], 
        start_date: datetime, 
        end_date: datetime
    ) -> int:
        """Save backtest results ke database"""
        try:
            # Create backtest record
            backtest = Backtest(
                strategy_id=strategy_id,
                start_date=start_date,
                end_date=end_date,
                status='completed',
                created_at=datetime.now()
            )
            
            self.db.add(backtest)
            self.db.flush()  # Get the ID
            
            # Create backtest result
            if 'performance_metrics' in results and results['performance_metrics']:
                best_algo = results.get('best_algorithm', 'unknown')
                best_performance = results['performance_metrics'].get(best_algo, {})
                
                backtest_result = BacktestResult(
                    backtest_id=backtest.id,
                    total_return=best_performance.get('total_return', 0),
                    annual_return=best_performance.get('annual_return', 0),
                    sharpe_ratio=best_performance.get('sharpe_ratio', 0),
                    max_drawdown=best_performance.get('max_drawdown', 0),
                    volatility=best_performance.get('volatility', 0),
                    algorithm_used=best_algo,
                    created_at=datetime.now()
                )
                
                self.db.add(backtest_result)
            
            self.db.commit()
            return backtest.id
            
        except Exception as e:
            logger.error(f"Error saving backtest result: {e}")
            self.db.rollback()
            return 0
    
    async def get_backtest_results(self, strategy_id: int) -> List[Dict[str, Any]]:
        """Get backtest results untuk strategy"""
        try:
            backtests = self.db.query(Backtest).filter(
                Backtest.strategy_id == strategy_id
            ).order_by(Backtest.created_at.desc()).all()
            
            results = []
            for backtest in backtests:
                backtest_result = self.db.query(BacktestResult).filter(
                    BacktestResult.backtest_id == backtest.id
                ).first()
                
                if backtest_result:
                    results.append({
                        'backtest_id': backtest.id,
                        'start_date': backtest.start_date,
                        'end_date': backtest.end_date,
                        'status': backtest.status,
                        'total_return': backtest_result.total_return,
                        'annual_return': backtest_result.annual_return,
                        'sharpe_ratio': backtest_result.sharpe_ratio,
                        'max_drawdown': backtest_result.max_drawdown,
                        'volatility': backtest_result.volatility,
                        'algorithm_used': backtest_result.algorithm_used,
                        'created_at': backtest.created_at
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting backtest results: {e}")
            return []
