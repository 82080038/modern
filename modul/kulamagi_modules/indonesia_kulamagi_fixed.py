"""
Indonesia Kulamagi Strategy - Fixed Version
Implementasi strategi Christian Kulamagi untuk pasar Indonesia dengan data dari database MySQL
"""
import pymysql
import pandas as pd
import numpy as np
import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndonesiaKulamagiStrategy:
    """
    Strategi Christian Kulamagi untuk pasar Indonesia
    Menggunakan data dari database MySQL dan Yahoo Finance sebagai backup
    """
    
    def __init__(self, host='localhost', user='root', password='', database='scalper'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
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
    
    def get_database_market_data(self, symbol: str = '^JKSE', days: int = 365):
        """Get market data from database"""
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
                        # Check if table exists and has data
                        cursor.execute(f"SELECT COUNT(*) as count FROM `{table}` WHERE symbol = %s", (symbol,))
                        count = cursor.fetchone()['count']
                        
                        if count > 0:
                            # Get data
                            cursor.execute(f"""
                                SELECT * FROM `{table}` 
                                WHERE symbol = %s 
                                ORDER BY date DESC 
                                LIMIT %s
                            """, (symbol, days))
                            
                            data = cursor.fetchall()
                            
                            if data:
                                logger.info(f"✅ Found {len(data)} records for {symbol} in {table}")
                                return self._format_database_data(data, table)
                    except Exception as e:
                        logger.debug(f"Table {table} not suitable: {e}")
                        continue
                
                logger.warning(f"❌ No data found for {symbol} in database")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting database market data: {e}")
            return None
    
    def _format_database_data(self, data: List[Dict], table: str) -> pd.DataFrame:
        """Format database data to DataFrame"""
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
            logger.error(f"❌ Error formatting database data: {e}")
            return None
    
    def get_yahoo_finance_data(self, symbol: str, days: int = 365):
        """Get data from Yahoo Finance as backup"""
        try:
            # Add .JK suffix for Indonesia stocks if not present
            if not symbol.endswith('.JK') and not symbol.startswith('^'):
                symbol += '.JK'
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': int((datetime.now() - timedelta(days=days)).timestamp()),
                'period2': int(datetime.now().timestamp()),
                'interval': '1d'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    timestamps = result['timestamp']
                    quotes = result['indicators']['quote'][0]
                    
                    df = pd.DataFrame({
                        'date': [datetime.fromtimestamp(ts) for ts in timestamps],
                        'open': quotes['open'],
                        'high': quotes['high'],
                        'low': quotes['low'],
                        'close': quotes['close'],
                        'volume': quotes['volume']
                    })
                    
                    # Remove NaN values
                    df = df.dropna()
                    
                    if len(df) > 0:
                        logger.info(f"✅ Retrieved {len(df)} days of {symbol} data from Yahoo Finance")
                        return df
            
            logger.warning(f"❌ Failed to get {symbol} data from Yahoo Finance")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting Yahoo Finance data for {symbol}: {e}")
            return None
    
    def get_market_data(self, symbol: str, days: int = 365):
        """Get market data from database first, then Yahoo Finance"""
        # Try database first
        df = self.get_database_market_data(symbol, days)
        
        if df is not None and len(df) > 0:
            return df
        
        # Fallback to Yahoo Finance
        logger.info(f"🔄 Database data not available, trying Yahoo Finance for {symbol}")
        return self.get_yahoo_finance_data(symbol, days)
    
    def calculate_emas(self, df: pd.DataFrame, periods: List[int] = [10, 20, 50]):
        """Calculate EMAs for given periods"""
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        return df
    
    def check_indonesia_market_condition(self):
        """Check Indonesia market condition (IDX > EMA 10 > EMA 20)"""
        try:
            # Get IDX Composite data
            df = self.get_market_data('^JKSE', days=100)
            
            if df is None or len(df) < 20:
                return {
                    "market_favorable": False,
                    "reason": "Insufficient IDX data",
                    "idx_price": None,
                    "ema_10": None,
                    "ema_20": None,
                    "data_source": "None"
                }
            
            # Calculate EMAs
            df = self.calculate_emas(df, [10, 20])
            
            # Get latest values
            current_price = df['close'].iloc[-1]
            ema_10 = df['ema_10'].iloc[-1]
            ema_20 = df['ema_20'].iloc[-1]
            
            # Check Kulamagi condition: IDX > EMA 10 > EMA 20
            market_favorable = (current_price > ema_10 > ema_20)
            
            return {
                "market_favorable": market_favorable,
                "idx_price": current_price,
                "ema_10": ema_10,
                "ema_20": ema_20,
                "condition": f"IDX: {current_price:.2f} > EMA10: {ema_10:.2f} > EMA20: {ema_20:.2f}" if market_favorable else "Market not favorable",
                "date": df['date'].iloc[-1].strftime('%Y-%m-%d'),
                "data_source": "Database" if 'database' in str(type(df)) else "Yahoo Finance"
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking market condition: {e}")
            return {
                "market_favorable": False,
                "reason": f"Error: {str(e)}",
                "idx_price": None,
                "ema_10": None,
                "ema_20": None,
                "data_source": "Error"
            }
    
    def screen_indonesia_momentum_stocks(self, symbols: List[str] = None, 
                                       min_performance_1m: float = 0.10, 
                                       min_performance_3m: float = 0.20, 
                                       min_performance_6m: float = 0.30):
        """Screen Indonesia stocks with momentum"""
        if symbols is None:
            # Popular Indonesia stocks
            symbols = [
                'BBCA', 'BBRI', 'BMRI', 'BBNI', 'TLKM',  # Banking
                'ASII', 'AUTO', 'INDF', 'UNVR', 'ICBP',  # Consumer
                'GOTO', 'TOWR', 'ADRO', 'ANTM', 'PGAS',  # Tech & Energy
                'CPIN', 'INCO', 'SMGR', 'UNTR', 'WIKA'   # Others
            ]
        
        momentum_stocks = []
        
        logger.info(f"🔍 Screening {len(symbols)} Indonesia stocks for momentum...")
        
        for i, symbol in enumerate(symbols):
            try:
                # Add delay to avoid rate limiting
                if i > 0:
                    time.sleep(0.5)  # 0.5 second delay between requests
                
                # Get stock data
                df = self.get_market_data(symbol, days=180)
                
                if df is None or len(df) < 30:
                    logger.debug(f"❌ Insufficient data for {symbol}")
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
                if (performance_1m >= min_performance_1m and 
                    performance_3m >= min_performance_3m and 
                    performance_6m >= min_performance_6m):
                    
                    momentum_stocks.append({
                        "symbol": symbol,
                        "current_price": current_price,
                        "performance_1m": performance_1m,
                        "performance_3m": performance_3m,
                        "performance_6m": performance_6m,
                        "total_performance": performance_1m + performance_3m + performance_6m,
                        "date": df['date'].iloc[-1].strftime('%Y-%m-%d')
                    })
                    
                    logger.info(f"  ✅ {symbol}: 1M={performance_1m:.1%}, 3M={performance_3m:.1%}, 6M={performance_6m:.1%}")
                else:
                    logger.debug(f"  ❌ {symbol}: 1M={performance_1m:.1%}, 3M={performance_3m:.1%}, 6M={performance_6m:.1%} (below criteria)")
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        # Sort by total performance
        momentum_stocks.sort(key=lambda x: x['total_performance'], reverse=True)
        
        logger.info(f"🎯 Found {len(momentum_stocks)} momentum stocks")
        return momentum_stocks
    
    def analyze_breakout_setup(self, symbol: str):
        """Analyze breakout setup for Indonesia stock"""
        try:
            df = self.get_market_data(symbol, days=90)
            
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
                "date": df['date'].iloc[-1].strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing breakout setup for {symbol}: {e}")
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
            
            if 15 <= move_percent <= 60:  # 15-60% move for Indonesia market
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
        
        # Consolidation should be tight (less than 25% range for Indonesia)
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
                current_volume > avg_volume * 1.2):  # Lower volume requirement for Indonesia
                
                return {
                    "date": breakout_data['date'].iloc[i].strftime('%Y-%m-%d'),
                    "price": current_price,
                    "volume": current_volume,
                    "volume_ratio": current_volume / avg_volume,
                    "breakout_level": consolidation['high']
                }
        
        return None
    
    def run_full_analysis(self):
        """Run complete Indonesia Kulamagi analysis"""
        logger.info("🚀 Starting Indonesia Kulamagi Strategy Analysis")
        logger.info("=" * 60)
        
        # 1. Connect to database
        if not self.connect_database():
            logger.warning("⚠️ Database connection failed, using Yahoo Finance only")
        
        # 2. Check market condition
        logger.info("\n🎯 MARKET CONDITION CHECK")
        logger.info("-" * 30)
        market_condition = self.check_indonesia_market_condition()
        logger.info(f"Market Favorable: {market_condition['market_favorable']}")
        logger.info(f"Condition: {market_condition['condition']}")
        logger.info(f"IDX Price: {market_condition['idx_price']:.2f}")
        logger.info(f"EMA 10: {market_condition['ema_10']:.2f}")
        logger.info(f"EMA 20: {market_condition['ema_20']:.2f}")
        logger.info(f"Data Source: {market_condition['data_source']}")
        
        # 3. Screen momentum stocks
        logger.info("\n🔥 MOMENTUM STOCK SCREENING")
        logger.info("-" * 30)
        
        momentum_stocks = self.screen_indonesia_momentum_stocks()
        
        if momentum_stocks:
            logger.info(f"\n🎯 TOP MOMENTUM STOCKS:")
            for i, stock in enumerate(momentum_stocks[:5], 1):
                logger.info(f"  {i}. {stock['symbol']}: {stock['current_price']:.2f}")
                logger.info(f"     1M: {stock['performance_1m']:.1%}, 3M: {stock['performance_3m']:.1%}, 6M: {stock['performance_6m']:.1%}")
        else:
            logger.info("❌ No momentum stocks found")
        
        # 4. Analyze breakout setups
        logger.info("\n📊 BREAKOUT SETUP ANALYSIS")
        logger.info("-" * 30)
        
        breakout_count = 0
        for stock in momentum_stocks[:3]:  # Analyze top 3
            logger.info(f"\nAnalyzing {stock['symbol']}...")
            setup = self.analyze_breakout_setup(stock['symbol'])
            
            if setup['setup_found']:
                logger.info(f"  ✅ Breakout setup found!")
                logger.info(f"     Current Price: {setup['current_price']:.2f}")
                logger.info(f"     EMA 10: {setup['ema_10']:.2f}")
                logger.info(f"     EMA 20: {setup['ema_20']:.2f}")
                if setup['breakout']:
                    logger.info(f"     Breakout: {setup['breakout']['date']} at {setup['breakout']['price']:.2f}")
                breakout_count += 1
            else:
                logger.info(f"  ❌ No breakout setup: {setup['reason']}")
        
        # 5. Summary
        logger.info("\n📋 ANALYSIS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Database: {self.database} (Connected: {self.connection is not None})")
        logger.info(f"Market Condition: {'Favorable' if market_condition['market_favorable'] else 'Not Favorable'}")
        logger.info(f"Momentum Stocks Found: {len(momentum_stocks)}")
        logger.info(f"Breakout Setups: {breakout_count}")
        
        # 6. Trading Recommendations
        logger.info("\n💡 TRADING RECOMMENDATIONS")
        logger.info("-" * 30)
        
        if market_condition['market_favorable'] and momentum_stocks:
            logger.info("✅ Market conditions are favorable for Kulamagi strategy")
            logger.info("✅ Momentum stocks found - consider position sizing 0.25%-1% per trade")
            logger.info("✅ Use trailing stop based on EMA 10/20 for exits")
        elif not market_condition['market_favorable']:
            logger.info("❌ Market not favorable - wait for IDX > EMA 10 > EMA 20")
        elif not momentum_stocks:
            logger.info("❌ No momentum stocks found - adjust screening criteria")
        
        return {
            'market_condition': market_condition,
            'momentum_stocks': momentum_stocks,
            'breakout_setups': breakout_count,
            'analysis_date': datetime.now().isoformat(),
            'recommendations': {
                'market_favorable': market_condition['market_favorable'],
                'has_momentum_stocks': len(momentum_stocks) > 0,
                'trading_ready': market_condition['market_favorable'] and len(momentum_stocks) > 0
            }
        }

def main():
    """Main function to run Indonesia Kulamagi analysis"""
    analyzer = IndonesiaKulamagiStrategy()
    result = analyzer.run_full_analysis()
    
    if result:
        logger.info("\n✅ Analysis completed successfully!")
        return result
    else:
        logger.error("\n❌ Analysis failed!")
        return None

if __name__ == "__main__":
    main()
