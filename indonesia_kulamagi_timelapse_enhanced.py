"""
Indonesia Kulamagi Strategy - Enhanced Time Lapse Testing
Enhanced testing dengan data yang tersedia dan validasi strategi yang lebih detail
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

class IndonesiaKulamagiTimeLapseEnhanced:
    """
    Enhanced Time Lapse Testing untuk strategi Christian Kulamagi
    """
    
    def __init__(self, host='localhost', user='root', password='', database='scalper'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        # Strategy parameters
        self.risk_per_trade = 0.01  # 1% risk per trade
        self.max_position_size = 0.1  # 10% max position
        self.initial_capital = 1000000  # 1M IDR
        
        # Time lapse parameters
        self.start_date = None
        self.end_date = None
        self.current_date = None
        self.portfolio_value = self.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0
        self.peak_value = self.initial_capital
        
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
    
    def get_available_symbols(self):
        """Get available symbols from database"""
        try:
            if not self.connection:
                return []
            
            with self.connection.cursor() as cursor:
                # Get symbols from historical_ohlcv_daily
                cursor.execute("""
                    SELECT DISTINCT symbol, COUNT(*) as record_count 
                    FROM historical_ohlcv_daily 
                    WHERE date >= '2024-01-01' 
                    GROUP BY symbol 
                    HAVING record_count >= 100
                    ORDER BY record_count DESC 
                    LIMIT 20
                """)
                
                symbols = cursor.fetchall()
                logger.info(f"✅ Found {len(symbols)} symbols with sufficient data")
                
                return [s['symbol'] for s in symbols]
                
        except Exception as e:
            logger.error(f"❌ Error getting available symbols: {e}")
            return []
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str):
        """Get historical data for time lapse testing"""
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
                    return df
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return None
    
    def calculate_emas(self, df: pd.DataFrame, periods: List[int] = [10, 20, 50]):
        """Calculate EMAs for given periods"""
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        return df
    
    def check_market_condition_simple(self, symbols_data: Dict[str, pd.DataFrame], date: str):
        """Simple market condition check using available symbols"""
        try:
            # Use a simple market condition based on available symbols
            # If most symbols are above their EMA 20, market is favorable
            favorable_count = 0
            total_count = 0
            
            for symbol, df in symbols_data.items():
                if df is not None and len(df) >= 20:
                    df_filtered = df[df['date'] <= date]
                    if len(df_filtered) >= 20:
                        df_filtered = self.calculate_emas(df_filtered, [20])
                        current_price = df_filtered['close'].iloc[-1]
                        ema_20 = df_filtered['ema_20'].iloc[-1]
                        
                        if current_price > ema_20:
                            favorable_count += 1
                        total_count += 1
            
            if total_count > 0:
                favorable_ratio = favorable_count / total_count
                return {
                    "market_favorable": favorable_ratio >= 0.6,  # 60% of symbols above EMA 20
                    "favorable_ratio": favorable_ratio,
                    "favorable_count": favorable_count,
                    "total_count": total_count
                }
            
            return {"market_favorable": False, "reason": "No data available"}
            
        except Exception as e:
            logger.error(f"❌ Error checking market condition: {e}")
            return {"market_favorable": False, "reason": f"Error: {str(e)}"}
    
    def screen_momentum_stocks_at_date(self, symbols_data: Dict[str, pd.DataFrame], date: str):
        """Screen momentum stocks at specific date"""
        momentum_stocks = []
        
        for symbol, df in symbols_data.items():
            if df is None or len(df) < 30:
                continue
            
            try:
                # Filter data up to the date
                df_filtered = df[df['date'] <= date]
                if len(df_filtered) < 30:
                    continue
                
                # Calculate performance
                current_price = df_filtered['close'].iloc[-1]
                
                # 1 month performance
                if len(df_filtered) >= 30:
                    price_1m_ago = df_filtered['close'].iloc[-30]
                    performance_1m = (current_price / price_1m_ago - 1) if price_1m_ago > 0 else 0
                else:
                    performance_1m = 0
                
                # 3 months performance
                if len(df_filtered) >= 90:
                    price_3m_ago = df_filtered['close'].iloc[-90]
                    performance_3m = (current_price / price_3m_ago - 1) if price_3m_ago > 0 else 0
                else:
                    performance_3m = 0
                
                # 6 months performance
                if len(df_filtered) >= 180:
                    price_6m_ago = df_filtered['close'].iloc[-180]
                    performance_6m = (current_price / price_6m_ago - 1) if price_6m_ago > 0 else 0
                else:
                    performance_6m = 0
                
                # Check if meets momentum criteria (relaxed for testing)
                if (performance_1m >= 0.05 and  # 5% for 1 month
                    performance_3m >= 0.10 and  # 10% for 3 months
                    performance_6m >= 0.15):    # 15% for 6 months
                    
                    momentum_stocks.append({
                        "symbol": symbol,
                        "current_price": current_price,
                        "performance_1m": performance_1m,
                        "performance_3m": performance_3m,
                        "performance_6m": performance_6m,
                        "total_performance": performance_1m + performance_3m + performance_6m,
                        "date": date
                    })
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol} at {date}: {e}")
                continue
        
        # Sort by total performance
        momentum_stocks.sort(key=lambda x: x['total_performance'], reverse=True)
        return momentum_stocks
    
    def analyze_breakout_setup_at_date(self, symbol: str, df: pd.DataFrame, date: str):
        """Analyze breakout setup at specific date"""
        try:
            # Filter data up to the date
            df_filtered = df[df['date'] <= date]
            
            if len(df_filtered) < 50:
                return {"setup_found": False, "reason": "Insufficient data"}
            
            # Calculate EMAs
            df_filtered = self.calculate_emas(df_filtered, [10, 20])
            
            # Find momentum leg (recent strong move)
            recent_30_days = df_filtered.tail(30)
            momentum_leg = self._find_momentum_leg(recent_30_days)
            
            if not momentum_leg:
                return {"setup_found": False, "reason": "No momentum leg found"}
            
            # Find consolidation phase
            consolidation = self._find_consolidation_phase(df_filtered, momentum_leg)
            
            if not consolidation:
                return {"setup_found": False, "reason": "No consolidation found"}
            
            # Check for breakout
            breakout = self._check_breakout(df_filtered, consolidation)
            
            return {
                "setup_found": breakout is not None,
                "symbol": symbol,
                "momentum_leg": momentum_leg,
                "consolidation": consolidation,
                "breakout": breakout,
                "current_price": df_filtered['close'].iloc[-1],
                "ema_10": df_filtered['ema_10'].iloc[-1],
                "ema_20": df_filtered['ema_20'].iloc[-1],
                "date": date
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing breakout setup for {symbol} at {date}: {e}")
            return {"setup_found": False, "reason": f"Error: {str(e)}"}
    
    def _find_momentum_leg(self, df: pd.DataFrame):
        """Find momentum leg (10-50% move in short period)"""
        if len(df) < 10:
            return None
        
        # Look for significant moves in last 20 days
        for i in range(10, len(df)):
            start_price = df['close'].iloc[i-10]
            end_price = df['close'].iloc[i]
            move_percent = (end_price / start_price - 1) * 100
            
            if 10 <= move_percent <= 50:  # Relaxed criteria for testing
                return {
                    "start_date": df['date'].iloc[i-10].strftime('%Y-%m-%d'),
                    "end_date": df['date'].iloc[i].strftime('%Y-%m-%d'),
                    "start_price": start_price,
                    "end_price": end_price,
                    "move_percent": move_percent
                }
        
        return None
    
    def _find_consolidation_phase(self, df: pd.DataFrame, momentum_leg: Dict):
        """Find consolidation phase after momentum leg"""
        momentum_end_date = momentum_leg['end_date']
        momentum_end_idx = df[df['date'] == momentum_end_date].index[0]
        
        # Look for consolidation in next 20-30 days
        consolidation_data = df.iloc[momentum_end_idx:momentum_end_idx+30]
        
        if len(consolidation_data) < 10:
            return None
        
        # Check if price is consolidating (tight range, declining volume)
        high_price = consolidation_data['high'].max()
        low_price = consolidation_data['low'].min()
        range_percent = (high_price - low_price) / low_price * 100
        
        # Consolidation should be tight (relaxed for testing)
        if range_percent > 30:
            return None
        
        # Volume should be declining
        volume_trend = consolidation_data['volume'].iloc[-5:].mean() / consolidation_data['volume'].iloc[:5].mean()
        
        if volume_trend > 0.9:  # Volume not declining enough
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
        """Check for breakout from consolidation"""
        consolidation_end_date = consolidation['end_date']
        consolidation_end_idx = df[df['date'] == consolidation_end_date].index[0]
        
        # Check next 5 days for breakout
        breakout_data = df.iloc[consolidation_end_idx:consolidation_end_idx+5]
        
        if len(breakout_data) < 2:
            return None
        
        # Look for price breaking above consolidation high with volume
        for i in range(1, len(breakout_data)):
            current_price = breakout_data['close'].iloc[i]
            current_volume = breakout_data['volume'].iloc[i]
            avg_volume = breakout_data['volume'].iloc[:i].mean()
            
            # Breakout: price above consolidation high + volume spike
            if (current_price > consolidation['high'] and 
                current_volume > avg_volume * 1.1):  # Relaxed volume requirement
                
                return {
                    "date": breakout_data['date'].iloc[i].strftime('%Y-%m-%d'),
                    "price": current_price,
                    "volume": current_volume,
                    "volume_ratio": current_volume / avg_volume,
                    "breakout_level": consolidation['high']
                }
        
        return None
    
    def execute_trade(self, symbol: str, side: str, price: float, quantity: int, date: str):
        """Execute a trade"""
        trade_value = price * quantity
        commission = trade_value * 0.001  # 0.1% commission
        
        if side == 'buy':
            if trade_value + commission <= self.portfolio_value:
                self.portfolio_value -= (trade_value + commission)
                self.positions.append({
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'entry_price': price,
                    'entry_date': date,
                    'current_price': price
                })
                self.trades.append({
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'value': trade_value,
                    'commission': commission,
                    'date': date
                })
                self.total_trades += 1
                logger.info(f"✅ Bought {quantity} shares of {symbol} at {price:.2f} on {date}")
                return True
        else:  # sell
            for i, pos in enumerate(self.positions):
                if pos['symbol'] == symbol and pos['side'] == 'buy':
                    if pos['quantity'] >= quantity:
                        sell_value = price * quantity
                        self.portfolio_value += (sell_value - commission)
                        
                        # Calculate P&L
                        pnl = (price - pos['entry_price']) * quantity - commission
                        if pnl > 0:
                            self.winning_trades += 1
                        else:
                            self.losing_trades += 1
                        
                        # Update position
                        self.positions[i]['quantity'] -= quantity
                        if self.positions[i]['quantity'] == 0:
                            self.positions.pop(i)
                        
                        self.trades.append({
                            'symbol': symbol,
                            'side': side,
                            'quantity': quantity,
                            'price': price,
                            'value': sell_value,
                            'commission': commission,
                            'date': date,
                            'pnl': pnl
                        })
                        logger.info(f"✅ Sold {quantity} shares of {symbol} at {price:.2f} on {date} (P&L: {pnl:.2f})")
                        return True
        
        return False
    
    def update_positions(self, symbols_data: Dict[str, pd.DataFrame], date: str):
        """Update current prices of positions"""
        for pos in self.positions:
            if pos['symbol'] in symbols_data:
                df = symbols_data[pos['symbol']]
                if df is not None:
                    df_filtered = df[df['date'] <= date]
                    if len(df_filtered) > 0:
                        pos['current_price'] = df_filtered['close'].iloc[-1]
    
    def calculate_portfolio_value(self, symbols_data: Dict[str, pd.DataFrame], date: str):
        """Calculate total portfolio value"""
        self.update_positions(symbols_data, date)
        
        total_value = self.portfolio_value
        
        for pos in self.positions:
            if pos['side'] == 'buy':
                total_value += pos['quantity'] * pos['current_price']
        
        # Update peak value and calculate drawdown
        if total_value > self.peak_value:
            self.peak_value = total_value
        
        current_drawdown = (self.peak_value - total_value) / self.peak_value
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
        
        return total_value
    
    def run_enhanced_time_lapse_test(self, start_date: str, end_date: str):
        """Run enhanced time lapse test for the strategy"""
        logger.info("🚀 Starting Enhanced Time Lapse Test for Indonesia Kulamagi Strategy")
        logger.info("=" * 80)
        
        if not self.connect_database():
            return None
        
        # Get available symbols
        symbols = self.get_available_symbols()
        if not symbols:
            logger.error("❌ No symbols available for testing")
            return None
        
        logger.info(f"📊 Testing {len(symbols)} symbols: {', '.join(symbols[:10])}")
        
        # Load all symbol data
        symbols_data = {}
        for symbol in symbols:
            df = self.get_historical_data(symbol, start_date, end_date)
            if df is not None and len(df) > 50:
                symbols_data[symbol] = df
                logger.info(f"✅ Loaded {len(df)} records for {symbol}")
        
        if not symbols_data:
            logger.error("❌ No data available for testing")
            return None
        
        self.start_date = start_date
        self.end_date = end_date
        
        # Get date range
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        date_range = pd.date_range(start, end, freq='D')
        
        logger.info(f"📅 Testing period: {start_date} to {end_date}")
        logger.info(f"💰 Initial capital: {self.initial_capital:,.0f} IDR")
        logger.info(f"📊 Processing {len(date_range)} days...")
        
        # Time lapse simulation
        for i, current_date in enumerate(date_range):
            date_str = current_date.strftime('%Y-%m-%d')
            
            if i % 30 == 0:  # Log every 30 days
                logger.info(f"📅 Processing {date_str}...")
            
            # Check market condition
            market_condition = self.check_market_condition_simple(symbols_data, date_str)
            
            # Only trade if market is favorable
            if market_condition.get("market_favorable", False):
                # Screen momentum stocks
                momentum_stocks = self.screen_momentum_stocks_at_date(symbols_data, date_str)
                
                if momentum_stocks:
                    logger.info(f"  🔥 Found {len(momentum_stocks)} momentum stocks on {date_str}")
                    
                    # Analyze breakout setups for top momentum stocks
                    for stock in momentum_stocks[:3]:  # Top 3 momentum stocks
                        if stock['symbol'] in symbols_data:
                            setup = self.analyze_breakout_setup_at_date(
                                stock['symbol'], symbols_data[stock['symbol']], date_str)
                            
                            if setup['setup_found']:
                                # Calculate position size
                                entry_price = setup['current_price']
                                stop_loss = setup['consolidation']['low']
                                
                                # Risk-based position sizing
                                risk_per_share = entry_price - stop_loss
                                if risk_per_share > 0:
                                    risk_amount = self.portfolio_value * self.risk_per_trade
                                    shares = int(risk_amount / risk_per_share)
                                    
                                    # Max position size check
                                    max_shares = int(self.portfolio_value * self.max_position_size / entry_price)
                                    shares = min(shares, max_shares)
                                    
                                    if shares > 0:
                                        self.execute_trade(stock['symbol'], 'buy', entry_price, shares, date_str)
            
            # Update portfolio value
            portfolio_value = self.calculate_portfolio_value(symbols_data, date_str)
            self.equity_curve.append({
                'date': date_str,
                'portfolio_value': portfolio_value,
                'cash': self.portfolio_value,
                'positions_value': portfolio_value - self.portfolio_value
            })
            
            # Calculate daily return
            if i > 0:
                prev_value = self.equity_curve[-2]['portfolio_value']
                daily_return = (portfolio_value - prev_value) / prev_value
                self.daily_returns.append(daily_return)
        
        # Calculate final results
        final_value = self.calculate_portfolio_value(symbols_data, end_date)
        total_return = (final_value / self.initial_capital - 1) * 100
        
        # Calculate additional metrics
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        avg_daily_return = np.mean(self.daily_returns) if self.daily_returns else 0
        volatility = np.std(self.daily_returns) if self.daily_returns else 0
        sharpe_ratio = (avg_daily_return / volatility) if volatility > 0 else 0
        
        logger.info("\n📊 ENHANCED TIME LAPSE TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Initial Capital: {self.initial_capital:,.0f} IDR")
        logger.info(f"Final Value: {final_value:,.0f} IDR")
        logger.info(f"Total Return: {total_return:.2f}%")
        logger.info(f"Total Trades: {self.total_trades}")
        logger.info(f"Winning Trades: {self.winning_trades}")
        logger.info(f"Losing Trades: {self.losing_trades}")
        logger.info(f"Win Rate: {win_rate:.1f}%")
        logger.info(f"Max Drawdown: {self.max_drawdown:.2f}%")
        logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        logger.info(f"Active Positions: {len(self.positions)}")
        
        # Show top performing trades
        if self.trades:
            profitable_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
            if profitable_trades:
                logger.info(f"\n🎯 Top Profitable Trades:")
                for trade in sorted(profitable_trades, key=lambda x: x.get('pnl', 0), reverse=True)[:5]:
                    logger.info(f"  {trade['symbol']}: {trade['pnl']:,.0f} IDR on {trade['date']}")
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'active_positions': len(self.positions),
            'equity_curve': self.equity_curve,
            'trades': self.trades
        }

def main():
    """Main function to run enhanced time lapse test"""
    tester = IndonesiaKulamagiTimeLapseEnhanced()
    
    # Test with historical data
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    
    result = tester.run_enhanced_time_lapse_test(start_date, end_date)
    
    if result:
        logger.info("\n✅ Enhanced time lapse test completed successfully!")
        logger.info(f"📊 Final Results: {result['total_return']:.2f}% return, {result['win_rate']:.1f}% win rate")
        return result
    else:
        logger.error("\n❌ Enhanced time lapse test failed!")
        return None

if __name__ == "__main__":
    main()
