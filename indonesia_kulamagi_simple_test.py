"""
Indonesia Kulamagi Strategy - Simple Testing
Testing sederhana untuk memvalidasi strategi Christian Kulamagi
"""
import pymysql
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndonesiaKulamagiSimpleTest:
    """
    Simple Testing untuk strategi Christian Kulamagi
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
    
    def get_available_symbols(self):
        """Get available symbols from database"""
        try:
            if not self.connection:
                return []
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT symbol, COUNT(*) as record_count 
                    FROM historical_ohlcv_daily 
                    WHERE date >= '2024-01-01' 
                    GROUP BY symbol 
                    HAVING record_count >= 50
                    ORDER BY record_count DESC 
                    LIMIT 10
                """)
                
                symbols = cursor.fetchall()
                logger.info(f"✅ Found {len(symbols)} symbols with sufficient data")
                
                return [s['symbol'] for s in symbols]
                
        except Exception as e:
            logger.error(f"❌ Error getting available symbols: {e}")
            return []
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str):
        """Get historical data"""
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
        df = df.copy()  # Avoid SettingWithCopyWarning
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        return df
    
    def test_market_condition(self, symbols_data: Dict[str, pd.DataFrame], test_date: str):
        """Test market condition using available symbols"""
        logger.info(f"🔍 Testing market condition for {test_date}")
        
        favorable_count = 0
        total_count = 0
        results = []
        
        for symbol, df in symbols_data.items():
            if df is None or len(df) < 20:
                continue
            
            try:
                # Filter data up to test date
                df_filtered = df[df['date'] <= test_date]
                if len(df_filtered) < 20:
                    continue
                
                # Calculate EMAs
                df_filtered = self.calculate_emas(df_filtered, [10, 20])
                
                current_price = df_filtered['close'].iloc[-1]
                ema_10 = df_filtered['ema_10'].iloc[-1]
                ema_20 = df_filtered['ema_20'].iloc[-1]
                
                # Check Kulamagi condition: Price > EMA 10 > EMA 20
                condition_met = current_price > ema_10 > ema_20
                
                if condition_met:
                    favorable_count += 1
                
                total_count += 1
                
                results.append({
                    'symbol': symbol,
                    'price': current_price,
                    'ema_10': ema_10,
                    'ema_20': ema_20,
                    'condition_met': condition_met
                })
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        favorable_ratio = favorable_count / total_count if total_count > 0 else 0
        market_favorable = favorable_ratio >= 0.5  # 50% threshold
        
        logger.info(f"📊 Market Condition Results:")
        logger.info(f"  Favorable: {favorable_count}/{total_count} ({favorable_ratio:.1%})")
        logger.info(f"  Market Favorable: {market_favorable}")
        
        return {
            'market_favorable': market_favorable,
            'favorable_ratio': favorable_ratio,
            'favorable_count': favorable_count,
            'total_count': total_count,
            'results': results
        }
    
    def test_momentum_screening(self, symbols_data: Dict[str, pd.DataFrame], test_date: str):
        """Test momentum screening"""
        logger.info(f"🚀 Testing momentum screening for {test_date}")
        
        momentum_stocks = []
        
        for symbol, df in symbols_data.items():
            if df is None or len(df) < 30:
                continue
            
            try:
                # Filter data up to test date
                df_filtered = df[df['date'] <= test_date]
                if len(df_filtered) < 30:
                    continue
                
                current_price = df_filtered['close'].iloc[-1]
                
                # Calculate performance periods
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
                
                # Check momentum criteria (relaxed for testing)
                if (performance_1m >= 0.05 and  # 5% for 1 month
                    performance_3m >= 0.10 and  # 10% for 3 months
                    performance_6m >= 0.15):   # 15% for 6 months
                    
                    momentum_stocks.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'performance_1m': performance_1m,
                        'performance_3m': performance_3m,
                        'performance_6m': performance_6m,
                        'total_performance': performance_1m + performance_3m + performance_6m
                    })
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        # Sort by total performance
        momentum_stocks.sort(key=lambda x: x['total_performance'], reverse=True)
        
        logger.info(f"📈 Momentum Screening Results:")
        logger.info(f"  Found {len(momentum_stocks)} momentum stocks")
        
        if momentum_stocks:
            logger.info("  Top 5 momentum stocks:")
            for i, stock in enumerate(momentum_stocks[:5]):
                logger.info(f"    {i+1}. {stock['symbol']}: {stock['total_performance']:.1%} total performance")
        
        return momentum_stocks
    
    def test_breakout_analysis(self, symbol: str, df: pd.DataFrame, test_date: str):
        """Test breakout analysis for a specific symbol"""
        logger.info(f"🔍 Testing breakout analysis for {symbol} on {test_date}")
        
        try:
            # Filter data up to test date
            df_filtered = df[df['date'] <= test_date]
            
            if len(df_filtered) < 50:
                return {"setup_found": False, "reason": "Insufficient data"}
            
            # Calculate EMAs
            df_filtered = self.calculate_emas(df_filtered, [10, 20])
            
            # Find momentum leg in last 30 days
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
            
            result = {
                "setup_found": breakout is not None,
                "symbol": symbol,
                "momentum_leg": momentum_leg,
                "consolidation": consolidation,
                "breakout": breakout,
                "current_price": df_filtered['close'].iloc[-1],
                "ema_10": df_filtered['ema_10'].iloc[-1],
                "ema_20": df_filtered['ema_20'].iloc[-1],
                "date": test_date
            }
            
            if result["setup_found"]:
                logger.info(f"✅ Breakout setup found for {symbol}")
                logger.info(f"  Momentum: {momentum_leg['move_percent']:.1f}% move")
                logger.info(f"  Consolidation: {consolidation['range_percent']:.1f}% range")
                logger.info(f"  Breakout: {breakout['price']:.2f} (volume: {breakout['volume_ratio']:.1f}x)")
            else:
                logger.info(f"❌ No breakout setup for {symbol}: {result.get('reason', 'Unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing breakout setup for {symbol}: {e}")
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
            
            if 10 <= move_percent <= 50:
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
        
        # Check if price is consolidating
        high_price = consolidation_data['high'].max()
        low_price = consolidation_data['low'].min()
        range_percent = (high_price - low_price) / low_price * 100
        
        # Consolidation should be tight
        if range_percent > 30:
            return None
        
        # Volume should be declining
        volume_trend = consolidation_data['volume'].iloc[-5:].mean() / consolidation_data['volume'].iloc[:5].mean()
        
        if volume_trend > 0.9:
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
                current_volume > avg_volume * 1.1):
                
                return {
                    "date": breakout_data['date'].iloc[i].strftime('%Y-%m-%d'),
                    "price": current_price,
                    "volume": current_volume,
                    "volume_ratio": current_volume / avg_volume,
                    "breakout_level": consolidation['high']
                }
        
        return None
    
    def run_simple_test(self, test_date: str = '2024-12-01'):
        """Run simple test for the strategy"""
        logger.info("🚀 Starting Simple Test for Indonesia Kulamagi Strategy")
        logger.info("=" * 70)
        
        if not self.connect_database():
            return None
        
        # Get available symbols
        symbols = self.get_available_symbols()
        if not symbols:
            logger.error("❌ No symbols available for testing")
            return None
        
        logger.info(f"📊 Testing {len(symbols)} symbols: {', '.join(symbols)}")
        
        # Load symbol data
        symbols_data = {}
        for symbol in symbols:
            df = self.get_historical_data(symbol, '2024-01-01', test_date)
            if df is not None and len(df) > 50:
                symbols_data[symbol] = df
                logger.info(f"✅ Loaded {len(df)} records for {symbol}")
        
        if not symbols_data:
            logger.error("❌ No data available for testing")
            return None
        
        logger.info(f"\n📅 Testing date: {test_date}")
        logger.info(f"📊 Testing {len(symbols_data)} symbols with sufficient data")
        
        # Test 1: Market Condition
        logger.info("\n" + "="*50)
        logger.info("TEST 1: MARKET CONDITION")
        logger.info("="*50)
        market_condition = self.test_market_condition(symbols_data, test_date)
        
        # Test 2: Momentum Screening
        logger.info("\n" + "="*50)
        logger.info("TEST 2: MOMENTUM SCREENING")
        logger.info("="*50)
        momentum_stocks = self.test_momentum_screening(symbols_data, test_date)
        
        # Test 3: Breakout Analysis
        logger.info("\n" + "="*50)
        logger.info("TEST 3: BREAKOUT ANALYSIS")
        logger.info("="*50)
        breakout_setups = []
        
        for stock in momentum_stocks[:3]:  # Test top 3 momentum stocks
            if stock['symbol'] in symbols_data:
                setup = self.test_breakout_analysis(
                    stock['symbol'], symbols_data[stock['symbol']], test_date)
                breakout_setups.append(setup)
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("TESTING SUMMARY")
        logger.info("="*70)
        logger.info(f"Market Favorable: {market_condition['market_favorable']}")
        logger.info(f"Momentum Stocks Found: {len(momentum_stocks)}")
        logger.info(f"Breakout Setups Found: {sum(1 for s in breakout_setups if s['setup_found'])}")
        
        if market_condition['market_favorable'] and momentum_stocks:
            logger.info("✅ Strategy conditions met - trading opportunities available")
        else:
            logger.info("❌ Strategy conditions not met - no trading opportunities")
        
        return {
            'test_date': test_date,
            'market_condition': market_condition,
            'momentum_stocks': momentum_stocks,
            'breakout_setups': breakout_setups,
            'strategy_ready': market_condition['market_favorable'] and len(momentum_stocks) > 0
        }

def main():
    """Main function to run simple test"""
    tester = IndonesiaKulamagiSimpleTest()
    
    # Test with different dates
    test_dates = ['2024-06-01', '2024-09-01', '2024-12-01']
    
    for test_date in test_dates:
        logger.info(f"\n{'='*80}")
        logger.info(f"TESTING DATE: {test_date}")
        logger.info(f"{'='*80}")
        
        result = tester.run_simple_test(test_date)
        
        if result:
            logger.info(f"✅ Test completed for {test_date}")
        else:
            logger.error(f"❌ Test failed for {test_date}")

if __name__ == "__main__":
    main()
