"""
Indonesia Kulamagi Strategy Analyzer
Analisis database MySQL dan implementasi strategi Christian Kulamagi untuk pasar Indonesia
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndonesiaKulamagiAnalyzer:
    """
    Analyzer untuk strategi Kulamagi di pasar Indonesia
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
    
    def analyze_database_structure(self):
        """Analyze database structure and available data"""
        if not self.connection:
            logger.error("❌ No database connection")
            return None
        
        try:
            with self.connection.cursor() as cursor:
                # Get all tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                logger.info(f"📊 Found {len(tables)} tables in database:")
                
                database_info = {
                    'tables': [],
                    'total_tables': len(tables),
                    'analysis_date': datetime.now().isoformat()
                }
                
                for table in tables:
                    table_name = list(table.values())[0]
                    
                    # Get table structure
                    cursor.execute(f"DESCRIBE `{table_name}`")
                    columns = cursor.fetchall()
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                    row_count = cursor.fetchone()['count']
                    
                    # Get sample data
                    cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 3")
                    sample_data = cursor.fetchall()
                    
                    table_info = {
                        'name': table_name,
                        'columns': [col['Field'] for col in columns],
                        'row_count': row_count,
                        'sample_data': sample_data
                    }
                    
                    database_info['tables'].append(table_info)
                    
                    logger.info(f"  📋 Table: {table_name}")
                    logger.info(f"     Columns: {', '.join(table_info['columns'])}")
                    logger.info(f"     Rows: {row_count}")
                
                return database_info
                
        except Exception as e:
            logger.error(f"❌ Error analyzing database: {e}")
            return None
    
    def get_indonesia_market_data(self):
        """Get Indonesia market data (IDX Composite)"""
        try:
            # Yahoo Finance API for IDX Composite (^JKSE)
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EJKSE"
            params = {
                'period1': int((datetime.now() - timedelta(days=365)).timestamp()),
                'period2': int(datetime.now().timestamp()),
                'interval': '1d'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
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
                
                logger.info(f"✅ Retrieved {len(df)} days of IDX Composite data")
                return df
            else:
                logger.error("❌ Failed to retrieve IDX Composite data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting Indonesia market data: {e}")
            return None
    
    def get_indonesia_stock_data(self, symbol: str, days: int = 365):
        """Get Indonesia stock data from Yahoo Finance"""
        try:
            # Add .JK suffix for Indonesia stocks
            if not symbol.endswith('.JK'):
                symbol += '.JK'
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': int((datetime.now() - timedelta(days=days)).timestamp()),
                'period2': int(datetime.now().timestamp()),
                'interval': '1d'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
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
                
                logger.info(f"✅ Retrieved {len(df)} days of {symbol} data")
                return df
            else:
                logger.error(f"❌ Failed to retrieve {symbol} data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting {symbol} data: {e}")
            return None
    
    def calculate_emas(self, df: pd.DataFrame, periods: List[int] = [10, 20, 50]):
        """Calculate EMAs for given periods"""
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        return df
    
    def check_indonesia_market_condition(self, df: pd.DataFrame):
        """Check Indonesia market condition (IDX > EMA 10 > EMA 20)"""
        try:
            if len(df) < 20:
                return {
                    "market_favorable": False,
                    "reason": "Insufficient data",
                    "idx_price": None,
                    "ema_10": None,
                    "ema_20": None
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
                "date": df['date'].iloc[-1].strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking market condition: {e}")
            return {
                "market_favorable": False,
                "reason": f"Error: {str(e)}",
                "idx_price": None,
                "ema_10": None,
                "ema_20": None
            }
    
    def screen_indonesia_momentum_stocks(self, symbols: List[str], min_performance_1m: float = 0.15, 
                                       min_performance_3m: float = 0.25, min_performance_6m: float = 0.40):
        """Screen Indonesia stocks with momentum"""
        momentum_stocks = []
        
        logger.info(f"🔍 Screening {len(symbols)} Indonesia stocks for momentum...")
        
        for i, symbol in enumerate(symbols):
            try:
                # Add delay to avoid rate limiting
                if i > 0:
                    time.sleep(1)  # 1 second delay between requests
                
                # Get stock data
                df = self.get_indonesia_stock_data(symbol, days=180)
                
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
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        # Sort by total performance
        momentum_stocks.sort(key=lambda x: x['total_performance'], reverse=True)
        
        logger.info(f"🎯 Found {len(momentum_stocks)} momentum stocks")
        return momentum_stocks
    
    def analyze_breakout_setup_indonesia(self, symbol: str):
        """Analyze breakout setup for Indonesia stock"""
        try:
            df = self.get_indonesia_stock_data(symbol, days=90)
            
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
        """Find momentum leg (20-80% move in short period)"""
        if len(df) < 10:
            return None
        
        # Look for significant moves in last 20 days
        for i in range(10, len(df)):
            start_price = df['close'].iloc[i-10]
            end_price = df['close'].iloc[i]
            move_percent = (end_price / start_price - 1) * 100
            
            if 20 <= move_percent <= 80:  # 20-80% move for Indonesia market
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
        
        # Consolidation should be tight (less than 20% range for Indonesia)
        if range_percent > 20:
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
                current_volume > avg_volume * 1.3):  # Lower volume requirement for Indonesia
                
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
            return None
        
        # 2. Analyze database structure
        logger.info("\n📊 DATABASE ANALYSIS")
        logger.info("-" * 30)
        db_info = self.analyze_database_structure()
        if db_info:
            logger.info(f"Database: {self.database}")
            logger.info(f"Total tables: {db_info['total_tables']}")
            for table in db_info['tables']:
                logger.info(f"  📋 {table['name']}: {table['row_count']} rows")
        
        # 3. Get Indonesia market data
        logger.info("\n📈 INDONESIA MARKET DATA")
        logger.info("-" * 30)
        idx_data = self.get_indonesia_market_data()
        if idx_data is not None:
            logger.info(f"IDX Composite data: {len(idx_data)} days")
            logger.info(f"Date range: {idx_data['date'].min()} to {idx_data['date'].max()}")
        
        # 4. Check market condition
        logger.info("\n🎯 MARKET CONDITION CHECK")
        logger.info("-" * 30)
        if idx_data is not None:
            market_condition = self.check_indonesia_market_condition(idx_data)
            logger.info(f"Market Favorable: {market_condition['market_favorable']}")
            logger.info(f"Condition: {market_condition['condition']}")
            logger.info(f"IDX Price: {market_condition['idx_price']:.2f}")
            logger.info(f"EMA 10: {market_condition['ema_10']:.2f}")
            logger.info(f"EMA 20: {market_condition['ema_20']:.2f}")
        
        # 5. Screen momentum stocks
        logger.info("\n🔥 MOMENTUM STOCK SCREENING")
        logger.info("-" * 30)
        
        # Popular Indonesia stocks
        indonesia_symbols = [
            'BBCA', 'BBRI', 'BMRI', 'BBNI', 'TLKM',  # Banking
            'ASII', 'AUTO', 'INDF', 'UNVR', 'ICBP',  # Consumer
            'GOTO', 'TOWR', 'ADRO', 'ANTM', 'PGAS',  # Tech & Energy
            'CPIN', 'INCO', 'SMGR', 'UNTR', 'WIKA'   # Others
        ]
        
        momentum_stocks = self.screen_indonesia_momentum_stocks(indonesia_symbols)
        
        if momentum_stocks:
            logger.info(f"\n🎯 TOP MOMENTUM STOCKS:")
            for i, stock in enumerate(momentum_stocks[:5], 1):
                logger.info(f"  {i}. {stock['symbol']}: {stock['current_price']:.2f}")
                logger.info(f"     1M: {stock['performance_1m']:.1%}, 3M: {stock['performance_3m']:.1%}, 6M: {stock['performance_6m']:.1%}")
        
        # 6. Analyze breakout setups
        logger.info("\n📊 BREAKOUT SETUP ANALYSIS")
        logger.info("-" * 30)
        
        for stock in momentum_stocks[:3]:  # Analyze top 3
            logger.info(f"\nAnalyzing {stock['symbol']}...")
            setup = self.analyze_breakout_setup_indonesia(stock['symbol'])
            
            if setup['setup_found']:
                logger.info(f"  ✅ Breakout setup found!")
                logger.info(f"     Current Price: {setup['current_price']:.2f}")
                logger.info(f"     EMA 10: {setup['ema_10']:.2f}")
                logger.info(f"     EMA 20: {setup['ema_20']:.2f}")
                if setup['breakout']:
                    logger.info(f"     Breakout: {setup['breakout']['date']} at {setup['breakout']['price']:.2f}")
            else:
                logger.info(f"  ❌ No breakout setup: {setup['reason']}")
        
        # 7. Summary
        logger.info("\n📋 ANALYSIS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Database: {self.database} ({db_info['total_tables']} tables)")
        logger.info(f"Market Condition: {'Favorable' if market_condition['market_favorable'] else 'Not Favorable'}")
        logger.info(f"Momentum Stocks Found: {len(momentum_stocks)}")
        logger.info(f"Breakout Setups: {sum(1 for stock in momentum_stocks[:3] if self.analyze_breakout_setup_indonesia(stock['symbol'])['setup_found'])}")
        
        return {
            'database_info': db_info,
            'market_condition': market_condition,
            'momentum_stocks': momentum_stocks,
            'analysis_date': datetime.now().isoformat()
        }

def main():
    """Main function to run Indonesia Kulamagi analysis"""
    analyzer = IndonesiaKulamagiAnalyzer()
    result = analyzer.run_full_analysis()
    
    if result:
        logger.info("\n✅ Analysis completed successfully!")
        return result
    else:
        logger.error("\n❌ Analysis failed!")
        return None

if __name__ == "__main__":
    main()
