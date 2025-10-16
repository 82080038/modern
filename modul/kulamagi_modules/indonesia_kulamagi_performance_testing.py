"""
Indonesia Kulamagi Strategy - Performance Testing
Performance Testing: Testing dengan data yang lebih lengkap
"""
import pymysql
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndonesiaKulamagiPerformanceTesting:
    """
    Performance Testing untuk strategi Christian Kulamagi di pasar Indonesia
    """
    
    def __init__(self, host='localhost', user='root', password='', database='scalper'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        # Performance testing parameters
        self.test_periods = [
            {'start': '2020-01-01', 'end': '2020-12-31', 'name': '2020'},
            {'start': '2021-01-01', 'end': '2021-12-31', 'name': '2021'},
            {'start': '2022-01-01', 'end': '2022-12-31', 'name': '2022'},
            {'start': '2023-01-01', 'end': '2023-12-31', 'name': '2023'},
            {'start': '2024-01-01', 'end': '2024-12-31', 'name': '2024'}
        ]
        
        # Enhanced symbols for comprehensive testing
        self.test_symbols = [
            'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'BNGA.JK', 'BTPN.JK', 'BSIM.JK', 'BJTM.JK',  # Banking
            'TLKM.JK', 'ISAT.JK', 'EXCL.JK', 'FREN.JK',  # Telecom
            'UNVR.JK', 'ICBP.JK', 'INDF.JK', 'GGRM.JK', 'SIDO.JK', 'MLBI.JK', 'ROTI.JK',  # Consumer
            'ASII.JK', 'AUTO.JK', 'INCO.JK', 'ADRO.JK',  # Automotive
            'PTPP.JK', 'ADHI.JK', 'WIKA.JK', 'JSMR.JK', 'SMGR.JK',  # Infrastructure
            'ANTM.JK', 'ADRO.JK', 'INCO.JK', 'PTBA.JK', 'PGAS.JK',  # Mining
            'BUKA.JK', 'EMTK.JK', 'SCMA.JK', 'MNCN.JK',  # Technology
            'PGAS.JK', 'PTBA.JK', 'ADRO.JK', 'ANTM.JK'  # Energy
        ]
        
        # Performance metrics
        self.metrics = {
            'total_return': 0,
            'annualized_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'calmar_ratio': 0,
            'sortino_ratio': 0,
            'var_95': 0,
            'cvar_95': 0
        }
        
    def connect_database(self):
        """Connect to MySQL database"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"✅ Connected to MySQL database: {self.database}")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str):
        """Get historical data with proper data type handling"""
        try:
            if not self.connection:
                return None
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT date, open, high, low, close, volume 
                    FROM historical_ohlcv_daily 
                    WHERE symbol = %s 
                    AND date BETWEEN %s AND %s
                    ORDER BY date ASC
                """, (symbol, start_date, end_date))
                
                data = cursor.fetchall()
                
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    # Convert to float to avoid decimal issues
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    return df
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return None
    
    def calculate_emas(self, df: pd.DataFrame, periods: List[int] = [10, 20, 50]):
        """Calculate EMAs with proper handling"""
        df = df.copy()
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        return df
    
    def run_strategy_simulation(self, start_date: str, end_date: str, symbols: List[str]):
        """Run strategy simulation for given period"""
        logger.info(f"🚀 Running strategy simulation: {start_date} to {end_date}")
        
        # Initialize portfolio
        initial_capital = 1000000  # 1M IDR
        portfolio_value = initial_capital
        positions = []
        trades = []
        equity_curve = []
        
        # Load data for all symbols
        symbols_data = {}
        for symbol in symbols:
            df = self.get_historical_data(symbol, start_date, end_date)
            if df is not None and len(df) > 50:
                symbols_data[symbol] = df
                logger.info(f"✅ Loaded {len(df)} records for {symbol}")
        
        if not symbols_data:
            logger.error("❌ No data available for simulation")
            return None
        
        # Get date range
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        date_range = pd.date_range(start, end, freq='D')
        
        # Simulation loop
        for i, current_date in enumerate(date_range):
            date_str = current_date.strftime('%Y-%m-%d')
            
            if i % 30 == 0:  # Log every 30 days
                logger.info(f"📅 Processing {date_str}...")
            
            # Check market condition (simplified)
            market_favorable = self._check_market_condition_simple(symbols_data, date_str)
            
            if market_favorable:
                # Screen momentum stocks
                momentum_stocks = self._screen_momentum_stocks(symbols_data, date_str)
                
                # Analyze breakout setups
                for stock in momentum_stocks[:3]:  # Top 3
                    if stock['symbol'] in symbols_data:
                        setup = self._analyze_breakout_setup(
                            stock['symbol'], symbols_data[stock['symbol']], date_str)
                        
                        if setup['setup_found']:
                            # Execute trade
                            entry_price = setup['current_price']
                            stop_loss = setup['consolidation']['low']
                            
                            # Calculate position size
                            risk_per_share = entry_price - stop_loss
                            if risk_per_share > 0:
                                risk_amount = portfolio_value * 0.008  # 0.8% risk
                                shares = int(risk_amount / risk_per_share)
                                
                                # Max position size
                                max_shares = int(portfolio_value * 0.08 / entry_price)
                                shares = min(shares, max_shares)
                                
                                if shares > 0:
                                    # Execute buy
                                    trade_value = entry_price * shares
                                    commission = trade_value * 0.001
                                    
                                    if trade_value + commission <= portfolio_value:
                                        portfolio_value -= (trade_value + commission)
                                        positions.append({
                                            'symbol': stock['symbol'],
                                            'shares': shares,
                                            'entry_price': entry_price,
                                            'entry_date': date_str,
                                            'stop_loss': stop_loss
                                        })
                                        
                                        trades.append({
                                            'symbol': stock['symbol'],
                                            'side': 'buy',
                                            'shares': shares,
                                            'price': entry_price,
                                            'date': date_str,
                                            'value': trade_value
                                        })
                                        
                                        logger.info(f"✅ Bought {shares} shares of {stock['symbol']} at {entry_price:.2f}")
            
            # Update portfolio value
            total_value = portfolio_value
            for pos in positions:
                if pos['symbol'] in symbols_data:
                    df = symbols_data[pos['symbol']]
                    df_filtered = df[df['date'] <= date_str]
                    if len(df_filtered) > 0:
                        current_price = df_filtered['close'].iloc[-1]
                        total_value += pos['shares'] * current_price
            
            equity_curve.append({
                'date': date_str,
                'portfolio_value': total_value,
                'cash': portfolio_value,
                'positions_value': total_value - portfolio_value
            })
        
        # Calculate final metrics
        final_value = equity_curve[-1]['portfolio_value']
        total_return = (final_value / initial_capital - 1) * 100
        
        # Calculate additional metrics
        returns = [eq['portfolio_value'] for eq in equity_curve]
        daily_returns = [returns[i] / returns[i-1] - 1 for i in range(1, len(returns))]
        
        metrics = self._calculate_performance_metrics(
            initial_capital, final_value, daily_returns, trades)
        
        return {
            'period': f"{start_date} to {end_date}",
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'trades': trades,
            'positions': positions,
            'equity_curve': equity_curve,
            'metrics': metrics
        }
    
    def _check_market_condition_simple(self, symbols_data: Dict, date: str):
        """Simple market condition check"""
        favorable_count = 0
        total_count = 0
        
        for symbol, df in symbols_data.items():
            if df is None or len(df) < 20:
                continue
            
            df_filtered = df[df['date'] <= date]
            if len(df_filtered) < 20:
                continue
            
            df_filtered = self.calculate_emas(df_filtered, [20])
            current_price = df_filtered['close'].iloc[-1]
            ema_20 = df_filtered['ema_20'].iloc[-1]
            
            if current_price > ema_20:
                favorable_count += 1
            total_count += 1
        
        return favorable_count / total_count >= 0.4 if total_count > 0 else False
    
    def _screen_momentum_stocks(self, symbols_data: Dict, date: str):
        """Screen momentum stocks"""
        momentum_stocks = []
        
        for symbol, df in symbols_data.items():
            if df is None or len(df) < 30:
                continue
            
            df_filtered = df[df['date'] <= date]
            if len(df_filtered) < 30:
                continue
            
            current_price = df_filtered['close'].iloc[-1]
            
            # Calculate performance
            performance_1m = 0
            performance_3m = 0
            performance_6m = 0
            
            if len(df_filtered) >= 30:
                price_1m_ago = df_filtered['close'].iloc[-30]
                performance_1m = (current_price / price_1m_ago - 1) if price_1m_ago > 0 else 0
            
            if len(df_filtered) >= 90:
                price_3m_ago = df_filtered['close'].iloc[-90]
                performance_3m = (current_price / price_3m_ago - 1) if price_3m_ago > 0 else 0
            
            if len(df_filtered) >= 180:
                price_6m_ago = df_filtered['close'].iloc[-180]
                performance_6m = (current_price / price_6m_ago - 1) if price_6m_ago > 0 else 0
            
            # Check momentum criteria
            if (performance_1m >= 0.03 and performance_3m >= 0.08 and performance_6m >= 0.12):
                momentum_stocks.append({
                    'symbol': symbol,
                    'current_price': current_price,
                    'performance_1m': performance_1m,
                    'performance_3m': performance_3m,
                    'performance_6m': performance_6m,
                    'total_performance': performance_1m + performance_3m + performance_6m
                })
        
        return sorted(momentum_stocks, key=lambda x: x['total_performance'], reverse=True)
    
    def _analyze_breakout_setup(self, symbol: str, df: pd.DataFrame, date: str):
        """Analyze breakout setup"""
        try:
            df_filtered = df[df['date'] <= date]
            if len(df_filtered) < 50:
                return {"setup_found": False, "reason": "Insufficient data"}
            
            # Find momentum leg
            recent_30_days = df_filtered.tail(30)
            momentum_leg = self._find_momentum_leg(recent_30_days)
            
            if not momentum_leg:
                return {"setup_found": False, "reason": "No momentum leg found"}
            
            # Find consolidation
            consolidation = self._find_consolidation_phase(df_filtered, momentum_leg)
            
            if not consolidation:
                return {"setup_found": False, "reason": "No consolidation found"}
            
            # Check breakout
            breakout = self._check_breakout(df_filtered, consolidation)
            
            return {
                "setup_found": breakout is not None,
                "symbol": symbol,
                "momentum_leg": momentum_leg,
                "consolidation": consolidation,
                "breakout": breakout,
                "current_price": df_filtered['close'].iloc[-1]
            }
            
        except Exception as e:
            return {"setup_found": False, "reason": f"Error: {str(e)}"}
    
    def _find_momentum_leg(self, df: pd.DataFrame):
        """Find momentum leg"""
        if len(df) < 10:
            return None
        
        for i in range(10, len(df)):
            start_price = df['close'].iloc[i-10]
            end_price = df['close'].iloc[i]
            move_percent = (end_price / start_price - 1) * 100
            
            if 8 <= move_percent <= 40:
                return {
                    "start_date": df['date'].iloc[i-10].strftime('%Y-%m-%d'),
                    "end_date": df['date'].iloc[i].strftime('%Y-%m-%d'),
                    "start_price": start_price,
                    "end_price": end_price,
                    "move_percent": move_percent
                }
        
        return None
    
    def _find_consolidation_phase(self, df: pd.DataFrame, momentum_leg: Dict):
        """Find consolidation phase"""
        momentum_end_date = momentum_leg['end_date']
        momentum_end_idx = df[df['date'] == momentum_end_date].index[0]
        
        consolidation_data = df.iloc[momentum_end_idx:momentum_end_idx+30]
        
        if len(consolidation_data) < 10:
            return None
        
        high_price = consolidation_data['high'].max()
        low_price = consolidation_data['low'].min()
        range_percent = (high_price - low_price) / low_price * 100
        
        if range_percent > 25:
            return None
        
        volume_trend = consolidation_data['volume'].iloc[-5:].mean() / consolidation_data['volume'].iloc[:5].mean()
        
        if volume_trend > 0.85:
            return None
        
        return {
            "start_date": consolidation_data['date'].iloc[0].strftime('%Y-%m-%d'),
            "end_date": consolidation_data['date'].iloc[-1].strftime('%Y-%m-%d'),
            "high": high_price,
            "low": low_price,
            "range_percent": range_percent,
            "volume_trend": volume_trend
        }
    
    def _check_breakout(self, df: pd.DataFrame, consolidation: Dict):
        """Check for breakout"""
        consolidation_end_date = consolidation['end_date']
        consolidation_end_idx = df[df['date'] == consolidation_end_date].index[0]
        
        breakout_data = df.iloc[consolidation_end_idx:consolidation_end_idx+5]
        
        if len(breakout_data) < 2:
            return None
        
        for i in range(1, len(breakout_data)):
            current_price = breakout_data['close'].iloc[i]
            current_volume = breakout_data['volume'].iloc[i]
            avg_volume = breakout_data['volume'].iloc[:i].mean()
            
            if (current_price > consolidation['high'] and 
                current_volume > avg_volume * 1.1):
                
                return {
                    "date": breakout_data['date'].iloc[i].strftime('%Y-%m-%d'),
                    "price": current_price,
                    "volume": current_volume,
                    "volume_ratio": current_volume / avg_volume,
                    "breakout_level": consolidation['high']
                }
        
        return None
    
    def _calculate_performance_metrics(self, initial_capital: float, final_value: float, 
                                     daily_returns: List[float], trades: List[Dict]):
        """Calculate comprehensive performance metrics"""
        total_return = (final_value / initial_capital - 1) * 100
        annualized_return = ((final_value / initial_capital) ** (252 / len(daily_returns)) - 1) * 100
        volatility = np.std(daily_returns) * np.sqrt(252) * 100
        sharpe_ratio = (annualized_return / 100) / (volatility / 100) if volatility > 0 else 0
        
        # Max drawdown
        peak = initial_capital
        max_dd = 0
        for ret in daily_returns:
            peak = max(peak, peak * (1 + ret))
            drawdown = (peak - peak * (1 + ret)) / peak
            max_dd = max(max_dd, drawdown)
        max_drawdown = max_dd * 100
        
        # Win rate
        buy_trades = [t for t in trades if t['side'] == 'buy']
        win_rate = 0  # Simplified for now
        
        # Calmar ratio
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        # Sortino ratio
        negative_returns = [r for r in daily_returns if r < 0]
        downside_std = np.std(negative_returns) * np.sqrt(252) * 100 if negative_returns else 0
        sortino_ratio = (annualized_return / 100) / (downside_std / 100) if downside_std > 0 else 0
        
        # VaR 95%
        var_95 = np.percentile(daily_returns, 5) * 100
        
        # CVaR 95%
        cvar_95 = np.mean([r for r in daily_returns if r <= np.percentile(daily_returns, 5)]) * 100
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'var_95': var_95,
            'cvar_95': cvar_95
        }
    
    def run_comprehensive_performance_test(self):
        """Run comprehensive performance testing"""
        logger.info("🚀 Starting Comprehensive Performance Testing")
        logger.info("=" * 80)
        
        if not self.connect_database():
            return None
        
        results = []
        
        for period in self.test_periods:
            logger.info(f"\n📅 Testing Period: {period['name']}")
            logger.info(f"📊 Symbols: {len(self.test_symbols)}")
            
            result = self.run_strategy_simulation(
                period['start'], period['end'], self.test_symbols)
            
            if result:
                results.append(result)
                logger.info(f"✅ {period['name']}: {result['total_return']:.2f}% return, "
                          f"{len(result['trades'])} trades")
            else:
                logger.error(f"❌ {period['name']}: Failed")
        
        # Calculate overall performance
        if results:
            overall_metrics = self._calculate_overall_metrics(results)
            
            logger.info("\n📊 COMPREHENSIVE PERFORMANCE TEST SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Test Periods: {len(results)}")
            logger.info(f"Average Return: {overall_metrics['avg_return']:.2f}%")
            logger.info(f"Average Volatility: {overall_metrics['avg_volatility']:.2f}%")
            logger.info(f"Average Sharpe: {overall_metrics['avg_sharpe']:.2f}")
            logger.info(f"Average Max DD: {overall_metrics['avg_max_dd']:.2f}%")
            logger.info(f"Best Year: {overall_metrics['best_year']}")
            logger.info(f"Worst Year: {overall_metrics['worst_year']}")
            
            return {
                'results': results,
                'overall_metrics': overall_metrics,
                'test_periods': len(results)
            }
        
        return None
    
    def _calculate_overall_metrics(self, results: List[Dict]):
        """Calculate overall performance metrics"""
        returns = [r['total_return'] for r in results]
        volatilities = [r['metrics']['volatility'] for r in results]
        sharpes = [r['metrics']['sharpe_ratio'] for r in results]
        max_dds = [r['metrics']['max_drawdown'] for r in results]
        
        return {
            'avg_return': np.mean(returns),
            'avg_volatility': np.mean(volatilities),
            'avg_sharpe': np.mean(sharpes),
            'avg_max_dd': np.mean(max_dds),
            'best_year': max(results, key=lambda x: x['total_return'])['period'],
            'worst_year': min(results, key=lambda x: x['total_return'])['period'],
            'total_trades': sum(len(r['trades']) for r in results)
        }

def main():
    """Main function to run performance testing"""
    tester = IndonesiaKulamagiPerformanceTesting()
    
    # Run comprehensive performance test
    result = tester.run_comprehensive_performance_test()
    
    if result:
        logger.info("\n✅ Performance testing completed successfully!")
        return result
    else:
        logger.error("\n❌ Performance testing failed!")
        return None

if __name__ == "__main__":
    main()
