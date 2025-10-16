"""
Backtesting Service untuk Strategy Testing
"""
from sqlalchemy.orm import Session
from app.models.backtesting import (
    Backtest, BacktestTrade, BacktestMetrics, StrategyOptimization, MonteCarloSimulation,
    StrategyType, BacktestStatus
)
from app.models.trading import Strategy
from app.services.data_service import DataService
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import logging
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class BacktestingService:
    """Service untuk backtesting operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
    
    def create_backtest(self,
                       strategy_name: str,
                       strategy_type: StrategyType,
                       symbol: str,
                       timeframe: str,
                       start_date: date,
                       end_date: date,
                       initial_capital: float,
                       strategy_params: Dict = None,
                       commission_rate: float = 0.001,
                       slippage_rate: float = 0.0005) -> Dict:
        """Create new backtest"""
        try:
            # Generate unique backtest ID
            backtest_id = f"BT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create backtest record
            backtest = Backtest(
                backtest_id=backtest_id,
                strategy_name=strategy_name,
                strategy_type=strategy_type,
                strategy_params=strategy_params or {},
                symbol=symbol.upper(),
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                commission_rate=commission_rate,
                slippage_rate=slippage_rate
            )
            
            self.db.add(backtest)
            self.db.commit()
            
            return {
                "backtest_id": backtest_id,
                "status": "created",
                "message": "Backtest created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating backtest: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def run_backtest(self, backtest_id: str) -> Dict:
        """Run backtest execution"""
        try:
            # Get backtest record
            backtest = self.db.query(Backtest).filter(Backtest.backtest_id == backtest_id).first()
            if not backtest:
                return {"error": "Backtest not found"}
            
            # Update status
            backtest.status = BacktestStatus.RUNNING
            backtest.started_at = datetime.now()
            self.db.commit()
            
            # Load historical data
            historical_data = self._load_historical_data(
                backtest.symbol,
                backtest.timeframe,
                backtest.start_date,
                backtest.end_date
            )
            
            if not historical_data:
                backtest.status = BacktestStatus.FAILED
                self.db.commit()
                return {"error": "No historical data available"}
            
            # Run strategy simulation
            results = self._run_strategy_simulation(backtest, historical_data)
            
            # Update backtest with results
            self._update_backtest_results(backtest, results)
            
            # Create detailed metrics
            self._create_backtest_metrics(backtest, results)
            
            # Create trade records
            self._create_trade_records(backtest, results)
            
            backtest.status = BacktestStatus.COMPLETED
            backtest.completed_at = datetime.now()
            self.db.commit()
            
            return {
                "backtest_id": backtest_id,
                "status": "completed",
                "results": self._format_backtest_results(backtest, results)
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            backtest.status = BacktestStatus.FAILED
            self.db.commit()
            return {"error": str(e)}
    
    def _load_historical_data(self, symbol: str, timeframe: str, start_date: date, end_date: date) -> List[Dict]:
        """Load historical data for backtesting"""
        try:
            # This would integrate with the data service
            # For now, return mock data
            logger.info(f"Loading historical data for {symbol} {timeframe} from {start_date} to {end_date}")
            
            # Mock data generation
            data = []
            current_date = start_date
            price = 1000.0
            
            while current_date <= end_date:
                # Generate realistic price movement
                change = np.random.normal(0, 0.02)  # 2% daily volatility
                price *= (1 + change)
                
                # Generate OHLCV data
                open_price = price
                high_price = price * (1 + abs(np.random.normal(0, 0.01)))
                low_price = price * (1 - abs(np.random.normal(0, 0.01)))
                close_price = price * (1 + np.random.normal(0, 0.005))
                volume = np.random.randint(100000, 1000000)
                
                data.append({
                    'timestamp': datetime.combine(current_date, datetime.min.time()),
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })
                
                current_date += timedelta(days=1)
            
            return data
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return []
    
    def _run_strategy_simulation(self, backtest: Backtest, data: List[Dict]) -> Dict:
        """Run strategy simulation"""
        try:
            # Initialize simulation state
            capital = backtest.initial_capital
            position = 0
            trades = []
            equity_curve = []
            
            # Strategy parameters
            strategy_type = backtest.strategy_type
            params = backtest.strategy_params or {}
            
            # Run simulation
            for i, bar in enumerate(data):
                # Calculate technical indicators
                indicators = self._calculate_indicators(data[:i+1], strategy_type, params)
                
                # Generate signals
                signal = self._generate_signal(bar, indicators, position, strategy_type, params)
                
                # Execute trades
                if signal['action'] == 'buy' and position == 0:
                    # Buy signal
                    shares = int(capital / bar['close'])
                    if shares > 0:
                        position = shares
                        capital -= shares * bar['close']
                        
                        # Apply commission and slippage
                        commission = shares * bar['close'] * backtest.commission_rate
                        slippage = shares * bar['close'] * backtest.slippage_rate
                        capital -= commission + slippage
                        
                        trades.append({
                            'timestamp': bar['timestamp'],
                            'action': 'buy',
                            'price': bar['close'],
                            'shares': shares,
                            'commission': commission,
                            'slippage': slippage
                        })
                
                elif signal['action'] == 'sell' and position > 0:
                    # Sell signal
                    capital += position * bar['close']
                    
                    # Apply commission and slippage
                    commission = position * bar['close'] * backtest.commission_rate
                    slippage = position * bar['close'] * backtest.slippage_rate
                    capital -= commission + slippage
                    
                    trades.append({
                        'timestamp': bar['timestamp'],
                        'action': 'sell',
                        'price': bar['close'],
                        'shares': position,
                        'commission': commission,
                        'slippage': slippage
                    })
                    
                    position = 0
                
                # Calculate current equity
                current_equity = capital + (position * bar['close'])
                equity_curve.append({
                    'date': bar['timestamp'].date(),
                    'equity': current_equity
                })
            
            # Close any remaining position
            if position > 0:
                final_price = data[-1]['close']
                capital += position * final_price
                commission = position * final_price * backtest.commission_rate
                slippage = position * final_price * backtest.slippage_rate
                capital -= commission + slippage
                
                trades.append({
                    'timestamp': data[-1]['timestamp'],
                    'action': 'sell',
                    'price': final_price,
                    'shares': position,
                    'commission': commission,
                    'slippage': slippage
                })
            
            # Calculate performance metrics
            metrics = self._calculate_performance_metrics(
                backtest.initial_capital,
                capital,
                equity_curve,
                trades
            )
            
            return {
                'final_capital': capital,
                'total_trades': len(trades),
                'trades': trades,
                'equity_curve': equity_curve,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error running strategy simulation: {e}")
            return {}
    
    def _calculate_indicators(self, data: List[Dict], strategy_type: StrategyType, params: Dict) -> Dict:
        """Calculate technical indicators"""
        if len(data) < 20:  # Need minimum data for indicators
            return {}
        
        prices = [bar['close'] for bar in data]
        
        indicators = {}
        
        if strategy_type == StrategyType.MOVING_AVERAGE:
            period = params.get('period', 20)
            indicators['sma'] = self._calculate_sma(prices, period)
            indicators['sma_prev'] = self._calculate_sma(prices[:-1], period) if len(prices) > period else None
            
        elif strategy_type == StrategyType.RSI:
            period = params.get('period', 14)
            indicators['rsi'] = self._calculate_rsi(prices, period)
            
        elif strategy_type == StrategyType.MACD:
            fast = params.get('fast', 12)
            slow = params.get('slow', 26)
            signal = params.get('signal', 9)
            macd_data = self._calculate_macd(prices, fast, slow, signal)
            indicators.update(macd_data)
            
        elif strategy_type == StrategyType.BOLLINGER_BANDS:
            period = params.get('period', 20)
            std_dev = params.get('std_dev', 2)
            bb_data = self._calculate_bollinger_bands(prices, period, std_dev)
            indicators.update(bb_data)
        
        return indicators
    
    def _generate_signal(self, bar: Dict, indicators: Dict, position: int, strategy_type: StrategyType, params: Dict) -> Dict:
        """Generate trading signal"""
        signal = {'action': 'hold', 'strength': 0}
        
        if strategy_type == StrategyType.MOVING_AVERAGE:
            if 'sma' in indicators and 'sma_prev' in indicators:
                if bar['close'] > indicators['sma'] and bar['close'] <= indicators['sma_prev']:
                    signal = {'action': 'buy', 'strength': 1}
                elif bar['close'] < indicators['sma'] and bar['close'] >= indicators['sma_prev']:
                    signal = {'action': 'sell', 'strength': 1}
        
        elif strategy_type == StrategyType.RSI:
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:  # Oversold
                    signal = {'action': 'buy', 'strength': 1}
                elif rsi > 70:  # Overbought
                    signal = {'action': 'sell', 'strength': 1}
        
        elif strategy_type == StrategyType.MACD:
            if 'macd' in indicators and 'signal' in indicators:
                macd = indicators['macd']
                signal_line = indicators['signal']
                if macd > signal_line and indicators.get('macd_prev', 0) <= indicators.get('signal_prev', 0):
                    signal = {'action': 'buy', 'strength': 1}
                elif macd < signal_line and indicators.get('macd_prev', 0) >= indicators.get('signal_prev', 0):
                    signal = {'action': 'sell', 'strength': 1}
        
        elif strategy_type == StrategyType.BOLLINGER_BANDS:
            if 'upper' in indicators and 'lower' in indicators:
                if bar['close'] < indicators['lower']:
                    signal = {'action': 'buy', 'strength': 1}
                elif bar['close'] > indicators['upper']:
                    signal = {'action': 'sell', 'strength': 1}
        
        return signal
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return 0
        return sum(prices[-period:]) / period
    
    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        if len(gains) < period:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float], fast: int, slow: int, signal: int) -> Dict:
        """Calculate MACD"""
        if len(prices) < slow:
            return {}
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(prices, fast)
        slow_ema = self._calculate_ema(prices, slow)
        
        macd = fast_ema - slow_ema
        
        return {
            'macd': macd,
            'signal': macd,  # Simplified
            'macd_prev': macd,  # Simplified
            'signal_prev': macd  # Simplified
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int, std_dev: float) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {}
        
        sma = self._calculate_sma(prices, period)
        recent_prices = prices[-period:]
        variance = sum((x - sma) ** 2 for x in recent_prices) / period
        std = variance ** 0.5
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def _calculate_performance_metrics(self, initial_capital: float, final_capital: float, 
                                     equity_curve: List[Dict], trades: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        try:
            # Basic metrics
            total_return = (final_capital - initial_capital) / initial_capital
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(equity_curve)):
                prev_equity = equity_curve[i-1]['equity']
                curr_equity = equity_curve[i]['equity']
                daily_return = (curr_equity - prev_equity) / prev_equity
                daily_returns.append(daily_return)
            
            # Sharpe ratio
            if daily_returns:
                avg_return = np.mean(daily_returns)
                std_return = np.std(daily_returns)
                sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Sortino ratio
            negative_returns = [r for r in daily_returns if r < 0]
            if negative_returns:
                downside_std = np.std(negative_returns)
                sortino_ratio = (avg_return / downside_std) * np.sqrt(252) if downside_std > 0 else 0
            else:
                sortino_ratio = 0
            
            # Maximum drawdown
            peak = initial_capital
            max_drawdown = 0
            for point in equity_curve:
                if point['equity'] > peak:
                    peak = point['equity']
                drawdown = (peak - point['equity']) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            # Win rate
            winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
            total_trades = len(trades)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Profit factor
            gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
            gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            return {
                'total_return': total_return,
                'annualized_return': total_return * (252 / len(equity_curve)) if equity_curve else 0,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': total_trades - winning_trades
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def _update_backtest_results(self, backtest: Backtest, results: Dict):
        """Update backtest with results"""
        try:
            backtest.final_capital = results.get('final_capital', backtest.initial_capital)
            backtest.total_trades = results.get('total_trades', 0)
            backtest.equity_curve = results.get('equity_curve', [])
            backtest.trade_log = results.get('trades', [])
            
            metrics = results.get('metrics', {})
            backtest.total_return = metrics.get('total_return', 0)
            backtest.annualized_return = metrics.get('annualized_return', 0)
            backtest.sharpe_ratio = metrics.get('sharpe_ratio', 0)
            backtest.sortino_ratio = metrics.get('sortino_ratio', 0)
            backtest.max_drawdown = metrics.get('max_drawdown', 0)
            backtest.win_rate = metrics.get('win_rate', 0)
            backtest.profit_factor = metrics.get('profit_factor', 0)
            backtest.winning_trades = metrics.get('winning_trades', 0)
            backtest.losing_trades = metrics.get('losing_trades', 0)
            
        except Exception as e:
            logger.error(f"Error updating backtest results: {e}")
    
    def _create_backtest_metrics(self, backtest: Backtest, results: Dict):
        """Create detailed backtest metrics"""
        try:
            equity_curve = results.get('equity_curve', [])
            
            for point in equity_curve:
                metric = BacktestMetrics(
                    backtest_id=backtest.backtest_id,
                    date=point['date'],
                    equity=point['equity']
                )
                self.db.add(metric)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating backtest metrics: {e}")
    
    def _create_trade_records(self, backtest: Backtest, results: Dict):
        """Create trade records"""
        try:
            trades = results.get('trades', [])
            
            for trade in trades:
                trade_record = BacktestTrade(
                    trade_id=f"TR_{uuid.uuid4().hex[:8]}",
                    backtest_id=backtest.backtest_id,
                    symbol=backtest.symbol,
                    side=trade['action'],
                    quantity=trade['shares'],
                    entry_price=trade['price'],
                    entry_time=trade['timestamp'],
                    commission=trade['commission'],
                    slippage=trade['slippage']
                )
                self.db.add(trade_record)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating trade records: {e}")
    
    def _format_backtest_results(self, backtest: Backtest, results: Dict) -> Dict:
        """Format backtest results for API response"""
        return {
            'backtest_id': backtest.backtest_id,
            'strategy_name': backtest.strategy_name,
            'symbol': backtest.symbol,
            'timeframe': backtest.timeframe,
            'start_date': backtest.start_date.isoformat(),
            'end_date': backtest.end_date.isoformat(),
            'initial_capital': backtest.initial_capital,
            'final_capital': backtest.final_capital,
            'total_return': backtest.total_return,
            'annualized_return': backtest.annualized_return,
            'sharpe_ratio': backtest.sharpe_ratio,
            'sortino_ratio': backtest.sortino_ratio,
            'max_drawdown': backtest.max_drawdown,
            'win_rate': backtest.win_rate,
            'profit_factor': backtest.profit_factor,
            'total_trades': backtest.total_trades,
            'winning_trades': backtest.winning_trades,
            'losing_trades': backtest.losing_trades,
            'status': backtest.status.value,
            'created_at': backtest.created_at.isoformat(),
            'completed_at': backtest.completed_at.isoformat() if backtest.completed_at else None
        }
    
    def get_backtest_results(self, backtest_id: str) -> Dict:
        """Get backtest results"""
        try:
            backtest = self.db.query(Backtest).filter(Backtest.backtest_id == backtest_id).first()
            if not backtest:
                return {"error": "Backtest not found"}
            
            return self._format_backtest_results(backtest, {})
            
        except Exception as e:
            logger.error(f"Error getting backtest results: {e}")
            return {"error": str(e)}
    
    def list_backtests(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List backtests"""
        try:
            backtests = self.db.query(Backtest).order_by(Backtest.created_at.desc()).offset(offset).limit(limit).all()
            
            results = []
            for backtest in backtests:
                results.append(self._format_backtest_results(backtest, {}))
            
            return results
            
        except Exception as e:
            logger.error(f"Error listing backtests: {e}")
            return []
    
    def run_monte_carlo_simulation(self, backtest_id: str, num_simulations: int = 1000) -> Dict:
        """Run Monte Carlo simulation"""
        try:
            # Get backtest results
            backtest = self.db.query(Backtest).filter(Backtest.backtest_id == backtest_id).first()
            if not backtest:
                return {"error": "Backtest not found"}
            
            # Generate simulation ID
            simulation_id = f"MC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Run Monte Carlo simulation
            simulation_results = self._run_monte_carlo(backtest, num_simulations)
            
            # Save simulation results
            simulation = MonteCarloSimulation(
                simulation_id=simulation_id,
                backtest_id=backtest_id,
                num_simulations=num_simulations,
                simulation_length=365,  # 1 year
                confidence_levels=simulation_results.get('confidence_levels', {}),
                worst_case_scenario=simulation_results.get('worst_case', 0),
                best_case_scenario=simulation_results.get('best_case', 0),
                expected_value=simulation_results.get('expected_value', 0),
                var_95=simulation_results.get('var_95', 0),
                var_99=simulation_results.get('var_99', 0),
                cvar_95=simulation_results.get('cvar_95', 0),
                cvar_99=simulation_results.get('cvar_99', 0),
                simulation_paths=simulation_results.get('paths', []),
                distribution_stats=simulation_results.get('stats', {})
            )
            
            self.db.add(simulation)
            self.db.commit()
            
            return {
                "simulation_id": simulation_id,
                "results": simulation_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error running Monte Carlo simulation: {e}")
            return {"error": str(e)}
    
    def _run_monte_carlo(self, backtest: Backtest, num_simulations: int) -> Dict:
        """Run Monte Carlo simulation"""
        try:
            # Get daily returns from backtest
            daily_returns = []
            if backtest.equity_curve:
                for i in range(1, len(backtest.equity_curve)):
                    prev_equity = backtest.equity_curve[i-1]['equity']
                    curr_equity = backtest.equity_curve[i]['equity']
                    daily_return = (curr_equity - prev_equity) / prev_equity
                    daily_returns.append(daily_return)
            
            if not daily_returns:
                return {"error": "No daily returns data available"}
            
            # Calculate statistics
            mean_return = np.mean(daily_returns)
            std_return = np.std(daily_returns)
            
            # Run simulations
            simulation_paths = []
            final_values = []
            
            for _ in range(num_simulations):
                # Generate random path
                random_returns = np.random.normal(mean_return, std_return, 252)  # 1 year
                path = [backtest.initial_capital]
                
                for ret in random_returns:
                    new_value = path[-1] * (1 + ret)
                    path.append(new_value)
                
                simulation_paths.append(path)
                final_values.append(path[-1])
            
            # Calculate statistics
            final_values = np.array(final_values)
            
            return {
                'confidence_levels': {
                    '95': np.percentile(final_values, 5),
                    '99': np.percentile(final_values, 1)
                },
                'worst_case': np.min(final_values),
                'best_case': np.max(final_values),
                'expected_value': np.mean(final_values),
                'var_95': np.percentile(final_values, 5),
                'var_99': np.percentile(final_values, 1),
                'cvar_95': np.mean(final_values[final_values <= np.percentile(final_values, 5)]),
                'cvar_99': np.mean(final_values[final_values <= np.percentile(final_values, 1)]),
                'paths': simulation_paths[:100],  # Sample of paths
                'stats': {
                    'mean': np.mean(final_values),
                    'std': np.std(final_values),
                    'skewness': self._calculate_skewness(final_values),
                    'kurtosis': self._calculate_kurtosis(final_values)
                }
            }
            
        except Exception as e:
            logger.error(f"Error running Monte Carlo simulation: {e}")
            return {}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 4) - 3
