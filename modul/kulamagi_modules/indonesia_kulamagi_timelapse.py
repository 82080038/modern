"""
Indonesia Kulamagi Strategy - Time Lapse Testing
Testing strategi Christian Kulamagi menggunakan data historis untuk validasi
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

class IndonesiaKulamagiTimeLapse:
    """
    Time Lapse Testing untuk strategi Christian Kulamagi di pasar Indonesia
    Menggunakan data historis untuk validasi strategi
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
        """Get historical data for time lapse testing"""
        try:
            if not self.connection:
                return None
            
            with self.connection.cursor() as cursor:
                # Try different table structures
                tables_to_try = [
                    'historical_ohlcv_daily',
                    'historical_data', 
                    'market_data',
                    'comprehensive_market_data'
                ]
                
                for table in tables_to_try:
                    try:
                        cursor.execute(f"""
                            SELECT * FROM `{table}` 
                            WHERE symbol = %s 
                            AND date BETWEEN %s AND %s
                            ORDER BY date ASC
                        """, (symbol, start_date, end_date))
                        
                        data = cursor.fetchall()
                        
                        if data:
                            logger.info(f"✅ Found {len(data)} records for {symbol} in {table}")
                            return self._format_historical_data(data, table)
                    except Exception as e:
                        logger.debug(f"Table {table} not suitable: {e}")
                        continue
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return None
    
    def _format_historical_data(self, data: List[Dict], table: str) -> pd.DataFrame:
        """Format historical data to DataFrame"""
        try:
            df_data = []
            
            for row in data:
                # Handle different column names
                date_col = None
                for col in ['date', 'datetime', 'timestamp']:
                    if col in row and row[col]:
                        date_col = col
                        break
                
                if not date_col:
                    continue
                
                # Map price columns
                price_mapping = {
                    'open': ['open', 'open_price'],
                    'high': ['high', 'high_price'],
                    'low': ['low', 'low_price'],
                    'close': ['close', 'close_price', 'adj_close'],
                    'volume': ['volume']
                }
                
                row_data = {'date': row[date_col]}
                
                for price_type, possible_cols in price_mapping.items():
                    for col in possible_cols:
                        if col in row and row[col] is not None:
                            row_data[price_type] = row[col]
                            break
                
                if len(row_data) >= 5:  # date + 4 price columns
                    df_data.append(row_data)
            
            if df_data:
                df = pd.DataFrame(df_data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error formatting historical data: {e}")
            return None
    
    def calculate_emas(self, df: pd.DataFrame, periods: List[int] = [10, 20, 50]):
        """Calculate EMAs for given periods"""
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        return df
    
    def check_market_condition_at_date(self, df: pd.DataFrame, date: str):
        """Check market condition at specific date"""
        try:
            # Filter data up to the specified date
            date_obj = pd.to_datetime(date)
            df_filtered = df[df['date'] <= date_obj]
            
            if len(df_filtered) < 20:
                return {
                    "market_favorable": False,
                    "reason": "Insufficient data",
                    "idx_price": None,
                    "ema_10": None,
                    "ema_20": None
                }
            
            # Calculate EMAs
            df_filtered = self.calculate_emas(df_filtered, [10, 20])
            
            # Get latest values
            current_price = df_filtered['close'].iloc[-1]
            ema_10 = df_filtered['ema_10'].iloc[-1]
            ema_20 = df_filtered['ema_20'].iloc[-1]
            
            # Check Kulamagi condition: IDX > EMA 10 > EMA 20
            market_favorable = (current_price > ema_10 > ema_20)
            
            return {
                "market_favorable": market_favorable,
                "idx_price": current_price,
                "ema_10": ema_10,
                "ema_20": ema_20,
                "date": date
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking market condition at {date}: {e}")
            return {
                "market_favorable": False,
                "reason": f"Error: {str(e)}",
                "idx_price": None,
                "ema_10": None,
                "ema_20": None
            }
    
    def screen_momentum_stocks_at_date(self, symbols: List[str], date: str):
        """Screen momentum stocks at specific date"""
        momentum_stocks = []
        
        for symbol in symbols:
            try:
                # Get historical data up to the date
                df = self.get_historical_data(symbol, 
                    (pd.to_datetime(date) - timedelta(days=180)).strftime('%Y-%m-%d'), 
                    date)
                
                if df is None or len(df) < 30:
                    continue
                
                # Calculate performance
                current_price = df['close'].iloc[-1]
                
                # 1 month performance
                if len(df) >= 30:
                    price_1m_ago = df['close'].iloc[-30]
                    performance_1m = (current_price / price_1m_ago - 1) if price_1m_ago > 0 else 0
                else:
                    performance_1m = 0
                
                # 3 months performance
                if len(df) >= 90:
                    price_3m_ago = df['close'].iloc[-90]
                    performance_3m = (current_price / price_3m_ago - 1) if price_3m_ago > 0 else 0
                else:
                    performance_3m = 0
                
                # 6 months performance
                if len(df) >= 180:
                    price_6m_ago = df['close'].iloc[-180]
                    performance_6m = (current_price / price_6m_ago - 1) if price_6m_ago > 0 else 0
                else:
                    performance_6m = 0
                
                # Check if meets momentum criteria
                if (performance_1m >= 0.10 and 
                    performance_3m >= 0.20 and 
                    performance_6m >= 0.30):
                    
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
    
    def analyze_breakout_setup_at_date(self, symbol: str, date: str):
        """Analyze breakout setup at specific date"""
        try:
            # Get historical data up to the date
            df = self.get_historical_data(symbol, 
                (pd.to_datetime(date) - timedelta(days=90)).strftime('%Y-%m-%d'), 
                date)
            
            if df is None or len(df) < 50:
                return {"setup_found": False, "reason": "Insufficient data"}
            
            # Calculate EMAs
            df = self.calculate_emas(df, [10, 20])
            
            # Find momentum leg (recent strong move)
            recent_30_days = df.tail(30)
            momentum_leg = self._find_momentum_leg(recent_30_days)
            
            if not momentum_leg:
                return {"setup_found": False, "reason": "No momentum leg found"}
            
            # Find consolidation phase
            consolidation = self._find_consolidation_phase(df, momentum_leg)
            
            if not consolidation:
                return {"setup_found": False, "reason": "No consolidation found"}
            
            # Check for breakout
            breakout = self._check_breakout(df, consolidation)
            
            return {
                "setup_found": breakout is not None,
                "symbol": symbol,
                "momentum_leg": momentum_leg,
                "consolidation": consolidation,
                "breakout": breakout,
                "current_price": df['close'].iloc[-1],
                "ema_10": df['ema_10'].iloc[-1],
                "ema_20": df['ema_20'].iloc[-1],
                "date": date
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing breakout setup for {symbol} at {date}: {e}")
            return {"setup_found": False, "reason": f"Error: {str(e)}"}
    
    def _find_momentum_leg(self, df: pd.DataFrame):
        """Find momentum leg (15-60% move in short period)"""
        if len(df) < 10:
            return None
        
        # Look for significant moves in last 20 days
        for i in range(10, len(df)):
            start_price = df['close'].iloc[i-10]
            end_price = df['close'].iloc[i]
            move_percent = (end_price / start_price - 1) * 100
            
            if 15 <= move_percent <= 60:
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
        
        # Consolidation should be tight
        if range_percent > 25:
            return None
        
        # Volume should be declining
        volume_trend = consolidation_data['volume'].iloc[-5:].mean() / consolidation_data['volume'].iloc[:5].mean()
        
        if volume_trend > 0.8:  # Volume not declining enough
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
                current_volume > avg_volume * 1.2):
                
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
                logger.info(f"✅ Bought {quantity} shares of {symbol} at {price:.2f} on {date}")
                return True
        else:  # sell
            for i, pos in enumerate(self.positions):
                if pos['symbol'] == symbol and pos['side'] == 'buy':
                    if pos['quantity'] >= quantity:
                        sell_value = price * quantity
                        self.portfolio_value += (sell_value - commission)
                        
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
                            'date': date
                        })
                        logger.info(f"✅ Sold {quantity} shares of {symbol} at {price:.2f} on {date}")
                        return True
        
        return False
    
    def update_positions(self, date: str):
        """Update current prices of positions"""
        for pos in self.positions:
            # Get current price for the symbol
            df = self.get_historical_data(pos['symbol'], date, date)
            if df is not None and len(df) > 0:
                pos['current_price'] = df['close'].iloc[-1]
    
    def calculate_portfolio_value(self, date: str):
        """Calculate total portfolio value"""
        self.update_positions(date)
        
        total_value = self.portfolio_value
        
        for pos in self.positions:
            if pos['side'] == 'buy':
                total_value += pos['quantity'] * pos['current_price']
        
        return total_value
    
    def run_time_lapse_test(self, start_date: str, end_date: str, symbols: List[str] = None):
        """Run time lapse test for the strategy"""
        logger.info("🚀 Starting Time Lapse Test for Indonesia Kulamagi Strategy")
        logger.info("=" * 70)
        
        if not self.connect_database():
            return None
        
        if symbols is None:
            symbols = ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'TLKM', 'ASII', 'AUTO', 'INDF', 'UNVR', 'ICBP']
        
        self.start_date = start_date
        self.end_date = end_date
        
        # Get date range
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        date_range = pd.date_range(start, end, freq='D')
        
        logger.info(f"📅 Testing period: {start_date} to {end_date}")
        logger.info(f"📊 Testing {len(symbols)} symbols")
        logger.info(f"💰 Initial capital: {self.initial_capital:,.0f} IDR")
        
        # Get IDX data for market condition
        idx_data = self.get_historical_data('^JKSE', start_date, end_date)
        if idx_data is None:
            logger.warning("⚠️ No IDX data available, using alternative market filter")
        
        # Time lapse simulation
        for i, current_date in enumerate(date_range):
            date_str = current_date.strftime('%Y-%m-%d')
            
            if i % 30 == 0:  # Log every 30 days
                logger.info(f"📅 Processing {date_str}...")
            
            # Check market condition
            if idx_data is not None:
                market_condition = self.check_market_condition_at_date(idx_data, date_str)
            else:
                market_condition = {"market_favorable": True}  # Assume favorable if no IDX data
            
            # Only trade if market is favorable
            if market_condition.get("market_favorable", False):
                # Screen momentum stocks
                momentum_stocks = self.screen_momentum_stocks_at_date(symbols, date_str)
                
                # Analyze breakout setups for top momentum stocks
                for stock in momentum_stocks[:3]:  # Top 3 momentum stocks
                    setup = self.analyze_breakout_setup_at_date(stock['symbol'], date_str)
                    
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
            portfolio_value = self.calculate_portfolio_value(date_str)
            self.equity_curve.append({
                'date': date_str,
                'portfolio_value': portfolio_value,
                'cash': self.portfolio_value,
                'positions_value': portfolio_value - self.portfolio_value
            })
        
        # Calculate final results
        final_value = self.calculate_portfolio_value(end_date)
        total_return = (final_value / self.initial_capital - 1) * 100
        
        logger.info("\n📊 TIME LAPSE TEST RESULTS")
        logger.info("=" * 70)
        logger.info(f"Initial Capital: {self.initial_capital:,.0f} IDR")
        logger.info(f"Final Value: {final_value:,.0f} IDR")
        logger.info(f"Total Return: {total_return:.2f}%")
        logger.info(f"Total Trades: {len(self.trades)}")
        logger.info(f"Active Positions: {len(self.positions)}")
        
        # Calculate win rate
        if self.trades:
            buy_trades = [t for t in self.trades if t['side'] == 'buy']
            sell_trades = [t for t in self.trades if t['side'] == 'sell']
            
            if sell_trades:
                profitable_trades = 0
                for sell_trade in sell_trades:
                    # Find corresponding buy trade
                    buy_trade = next((t for t in buy_trades if t['symbol'] == sell_trade['symbol']), None)
                    if buy_trade and sell_trade['price'] > buy_trade['price']:
                        profitable_trades += 1
                
                win_rate = (profitable_trades / len(sell_trades)) * 100
                logger.info(f"Win Rate: {win_rate:.1f}%")
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': len(self.trades),
            'active_positions': len(self.positions),
            'equity_curve': self.equity_curve,
            'trades': self.trades
        }

def main():
    """Main function to run time lapse test"""
    tester = IndonesiaKulamagiTimeLapse()
    
    # Test with historical data
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    
    result = tester.run_time_lapse_test(start_date, end_date)
    
    if result:
        logger.info("\n✅ Time lapse test completed successfully!")
        return result
    else:
        logger.error("\n❌ Time lapse test failed!")
        return None

if __name__ == "__main__":
    main()
