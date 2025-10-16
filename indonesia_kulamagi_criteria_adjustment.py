"""
Indonesia Kulamagi Strategy - Criteria Adjustment
Criteria Adjustment: Sesuaikan kriteria untuk pasar Indonesia
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

class IndonesiaKulamagiCriteriaAdjustment:
    """
    Criteria Adjustment untuk strategi Christian Kulamagi di pasar Indonesia
    """
    
    def __init__(self, host='localhost', user='root', password='', database='scalper'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        # Adjusted criteria untuk pasar Indonesia
        self.criteria = {
            # Market Condition - lebih fleksibel untuk pasar Indonesia
            'market_condition': {
                'favorable_threshold': 0.4,  # 40% instead of 60%
                'use_sector_rotation': True,
                'include_volume_analysis': True,
                'min_symbols_above_ema': 3  # Minimum 3 symbols above EMA 20
            },
            
            # Momentum Screening - disesuaikan untuk volatilitas pasar Indonesia
            'momentum_screening': {
                '1_month_min': 0.03,  # 3% instead of 5%
                '3_month_min': 0.08,  # 8% instead of 10%
                '6_month_min': 0.12,  # 12% instead of 15%
                'total_performance_min': 0.20,  # 20% total performance
                'use_relative_strength': True,  # Compare to market
                'use_sector_relative': True  # Compare to sector
            },
            
            # Breakout Analysis - disesuaikan untuk karakteristik pasar Indonesia
            'breakout_analysis': {
                'momentum_leg_min': 0.08,  # 8% instead of 10%
                'momentum_leg_max': 0.40,  # 40% instead of 50%
                'consolidation_range_max': 0.25,  # 25% instead of 30%
                'volume_decline_min': 0.85,  # 15% volume decline
                'breakout_volume_min': 1.1,  # 10% volume increase
                'breakout_confirmation_days': 3  # 3 days confirmation
            },
            
            # Risk Management - disesuaikan untuk volatilitas tinggi
            'risk_management': {
                'risk_per_trade': 0.008,  # 0.8% instead of 1%
                'max_position_size': 0.08,  # 8% instead of 10%
                'max_daily_loss': 0.02,  # 2% daily loss limit
                'max_portfolio_risk': 0.15,  # 15% total portfolio risk
                'stop_loss_atr_multiplier': 2.0,  # 2x ATR for stop loss
                'take_profit_ratio': 2.0  # 2:1 risk reward ratio
            },
            
            # Position Sizing - lebih konservatif
            'position_sizing': {
                'base_risk': 0.008,  # 0.8% base risk
                'volatility_adjustment': True,
                'correlation_adjustment': True,
                'sector_concentration_limit': 0.20,  # 20% max per sector
                'max_positions': 8  # Maximum 8 positions
            }
        }
        
        # Indonesian market characteristics
        self.market_characteristics = {
            'avg_volatility': 0.25,  # 25% average volatility
            'sector_rotation_frequency': 0.3,  # 30% sector rotation
            'liquidity_threshold': 1000000,  # 1M IDR minimum volume
            'market_hours': '09:00-16:00',
            'trading_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'holiday_impact': 0.15  # 15% impact during holidays
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
    
    def check_market_condition_adjusted(self, symbols_data: Dict[str, pd.DataFrame], date: str):
        """Check market condition with adjusted criteria for Indonesia"""
        logger.info(f"🔍 Checking market condition for {date} (Indonesian Market)")
        
        favorable_count = 0
        total_count = 0
        results = []
        
        for symbol, df in symbols_data.items():
            if df is None or len(df) < 20:
                continue
            
            try:
                # Filter data up to the date
                df_filtered = df[df['date'] <= date]
                if len(df_filtered) < 20:
                    continue
                
                # Calculate EMAs
                df_filtered = self.calculate_emas(df_filtered, [10, 20])
                
                current_price = df_filtered['close'].iloc[-1]
                ema_10 = df_filtered['ema_10'].iloc[-1]
                ema_20 = df_filtered['ema_20'].iloc[-1]
                
                # Adjusted condition for Indonesian market
                # More flexible: Price > EMA 10 OR Price > EMA 20
                condition_met = (current_price > ema_10) or (current_price > ema_20)
                
                if condition_met:
                    favorable_count += 1
                
                total_count += 1
                
                results.append({
                    'symbol': symbol,
                    'price': current_price,
                    'ema_10': ema_10,
                    'ema_20': ema_20,
                    'condition_met': condition_met,
                    'price_vs_ema10': (current_price / ema_10 - 1) * 100,
                    'price_vs_ema20': (current_price / ema_20 - 1) * 100
                })
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        # Adjusted threshold for Indonesian market
        favorable_ratio = favorable_count / total_count if total_count > 0 else 0
        market_favorable = favorable_ratio >= self.criteria['market_condition']['favorable_threshold']
        
        logger.info(f"📊 Market Condition Results (Indonesian Market):")
        logger.info(f"  Favorable: {favorable_count}/{total_count} ({favorable_ratio:.1%})")
        logger.info(f"  Threshold: {self.criteria['market_condition']['favorable_threshold']:.1%}")
        logger.info(f"  Market Favorable: {market_favorable}")
        
        return {
            'market_favorable': market_favorable,
            'favorable_ratio': favorable_ratio,
            'favorable_count': favorable_count,
            'total_count': total_count,
            'results': results
        }
    
    def screen_momentum_stocks_adjusted(self, symbols_data: Dict[str, pd.DataFrame], date: str):
        """Screen momentum stocks with adjusted criteria for Indonesia"""
        logger.info(f"🚀 Screening momentum stocks for {date} (Indonesian Market)")
        
        momentum_stocks = []
        
        for symbol, df in symbols_data.items():
            if df is None or len(df) < 30:
                continue
            
            try:
                # Filter data up to the date
                df_filtered = df[df['date'] <= date]
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
                
                # Adjusted momentum criteria for Indonesian market
                momentum_criteria = self.criteria['momentum_screening']
                
                if (performance_1m >= momentum_criteria['1_month_min'] and
                    performance_3m >= momentum_criteria['3_month_min'] and
                    performance_6m >= momentum_criteria['6_month_min']):
                    
                    total_performance = performance_1m + performance_3m + performance_6m
                    
                    # Additional check for total performance
                    if total_performance >= momentum_criteria['total_performance_min']:
                        momentum_stocks.append({
                            'symbol': symbol,
                            'current_price': current_price,
                            'performance_1m': performance_1m,
                            'performance_3m': performance_3m,
                            'performance_6m': performance_6m,
                            'total_performance': total_performance,
                            'momentum_score': self._calculate_momentum_score(performance_1m, performance_3m, performance_6m)
                        })
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                continue
        
        # Sort by momentum score
        momentum_stocks.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        logger.info(f"📈 Momentum Screening Results (Indonesian Market):")
        logger.info(f"  Found {len(momentum_stocks)} momentum stocks")
        logger.info(f"  Criteria: 1M≥{self.criteria['momentum_screening']['1_month_min']:.1%}, "
                   f"3M≥{self.criteria['momentum_screening']['3_month_min']:.1%}, "
                   f"6M≥{self.criteria['momentum_screening']['6_month_min']:.1%}")
        
        if momentum_stocks:
            logger.info("  Top 5 momentum stocks:")
            for i, stock in enumerate(momentum_stocks[:5]):
                logger.info(f"    {i+1}. {stock['symbol']}: {stock['total_performance']:.1%} total, "
                           f"score: {stock['momentum_score']:.2f}")
        
        return momentum_stocks
    
    def _calculate_momentum_score(self, perf_1m: float, perf_3m: float, perf_6m: float):
        """Calculate momentum score with weighted factors"""
        # Weighted momentum score
        weights = {'1m': 0.4, '3m': 0.4, '6m': 0.2}
        score = (perf_1m * weights['1m'] + 
                perf_3m * weights['3m'] + 
                perf_6m * weights['6m'])
        return score
    
    def analyze_breakout_setup_adjusted(self, symbol: str, df: pd.DataFrame, date: str):
        """Analyze breakout setup with adjusted criteria for Indonesia"""
        logger.info(f"🔍 Analyzing breakout setup for {symbol} on {date} (Indonesian Market)")
        
        try:
            # Filter data up to the date
            df_filtered = df[df['date'] <= date]
            
            if len(df_filtered) < 50:
                return {"setup_found": False, "reason": "Insufficient data"}
            
            # Calculate EMAs
            df_filtered = self.calculate_emas(df_filtered, [10, 20])
            
            # Find momentum leg with adjusted criteria
            recent_30_days = df_filtered.tail(30)
            momentum_leg = self._find_momentum_leg_adjusted(recent_30_days)
            
            if not momentum_leg:
                return {"setup_found": False, "reason": "No momentum leg found"}
            
            # Find consolidation phase with adjusted criteria
            consolidation = self._find_consolidation_phase_adjusted(df_filtered, momentum_leg)
            
            if not consolidation:
                return {"setup_found": False, "reason": "No consolidation found"}
            
            # Check for breakout with adjusted criteria
            breakout = self._check_breakout_adjusted(df_filtered, consolidation)
            
            result = {
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
            
            if result["setup_found"]:
                logger.info(f"✅ Breakout setup found for {symbol} (Indonesian Market)")
                logger.info(f"  Momentum: {momentum_leg['move_percent']:.1f}% move")
                logger.info(f"  Consolidation: {consolidation['range_percent']:.1f}% range")
                logger.info(f"  Breakout: {breakout['price']:.2f} (volume: {breakout['volume_ratio']:.1f}x)")
            else:
                logger.info(f"❌ No breakout setup for {symbol}: {result.get('reason', 'Unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing breakout setup for {symbol}: {e}")
            return {"setup_found": False, "reason": f"Error: {str(e)}"}
    
    def _find_momentum_leg_adjusted(self, df: pd.DataFrame):
        """Find momentum leg with adjusted criteria for Indonesia"""
        if len(df) < 10:
            return None
        
        criteria = self.criteria['breakout_analysis']
        
        # Look for significant moves in last 20 days
        for i in range(10, len(df)):
            start_price = df['close'].iloc[i-10]
            end_price = df['close'].iloc[i]
            move_percent = (end_price / start_price - 1) * 100
            
            if (criteria['momentum_leg_min'] * 100 <= move_percent <= criteria['momentum_leg_max'] * 100):
                return {
                    "start_date": df['date'].iloc[i-10].strftime('%Y-%m-%d'),
                    "end_date": df['date'].iloc[i].strftime('%Y-%m-%d'),
                    "start_price": start_price,
                    "end_price": end_price,
                    "move_percent": move_percent
                }
        
        return None
    
    def _find_consolidation_phase_adjusted(self, df: pd.DataFrame, momentum_leg: Dict):
        """Find consolidation phase with adjusted criteria for Indonesia"""
        momentum_end_date = momentum_leg['end_date']
        momentum_end_idx = df[df['date'] == momentum_end_date].index[0]
        
        # Look for consolidation in next 20-30 days
        consolidation_data = df.iloc[momentum_end_idx:momentum_end_idx+30]
        
        if len(consolidation_data) < 10:
            return None
        
        criteria = self.criteria['breakout_analysis']
        
        # Check if price is consolidating
        high_price = consolidation_data['high'].max()
        low_price = consolidation_data['low'].min()
        range_percent = (high_price - low_price) / low_price * 100
        
        # Adjusted consolidation criteria
        if range_percent > criteria['consolidation_range_max'] * 100:
            return None
        
        # Volume should be declining
        volume_trend = consolidation_data['volume'].iloc[-5:].mean() / consolidation_data['volume'].iloc[:5].mean()
        
        if volume_trend > criteria['volume_decline_min']:
            return None
        
        return {
            "start_date": consolidation_data['date'].iloc[0].strftime('%Y-%m-%d'),
            "end_date": consolidation_data['date'].iloc[-1].strftime('%Y-%m-%d'),
            "high": high_price,
            "low": low_price,
            "range_percent": range_percent,
            "volume_trend": volume_trend
        }
    
    def _check_breakout_adjusted(self, df: pd.DataFrame, consolidation: Dict):
        """Check for breakout with adjusted criteria for Indonesia"""
        consolidation_end_date = consolidation['end_date']
        consolidation_end_idx = df[df['date'] == consolidation_end_date].index[0]
        
        criteria = self.criteria['breakout_analysis']
        
        # Check next few days for breakout
        breakout_data = df.iloc[consolidation_end_idx:consolidation_end_idx+criteria['breakout_confirmation_days']]
        
        if len(breakout_data) < 2:
            return None
        
        # Look for price breaking above consolidation high with volume
        for i in range(1, len(breakout_data)):
            current_price = breakout_data['close'].iloc[i]
            current_volume = breakout_data['volume'].iloc[i]
            avg_volume = breakout_data['volume'].iloc[:i].mean()
            
            # Adjusted breakout criteria
            if (current_price > consolidation['high'] and 
                current_volume > avg_volume * criteria['breakout_volume_min']):
                
                return {
                    "date": breakout_data['date'].iloc[i].strftime('%Y-%m-%d'),
                    "price": current_price,
                    "volume": current_volume,
                    "volume_ratio": current_volume / avg_volume,
                    "breakout_level": consolidation['high']
                }
        
        return None
    
    def calculate_position_size_adjusted(self, symbol: str, entry_price: float, stop_loss: float, portfolio_value: float):
        """Calculate position size with adjusted criteria for Indonesia"""
        criteria = self.criteria['position_sizing']
        
        # Risk per share
        risk_per_share = entry_price - stop_loss
        if risk_per_share <= 0:
            return 0
        
        # Base risk amount
        risk_amount = portfolio_value * criteria['base_risk']
        
        # Calculate shares
        shares = int(risk_amount / risk_per_share)
        
        # Apply position size limits
        max_shares = int(portfolio_value * criteria['max_position_size'] / entry_price)
        shares = min(shares, max_shares)
        
        # Apply maximum positions limit
        if shares > 0:
            position_value = shares * entry_price
            logger.info(f"📊 Position sizing for {symbol}:")
            logger.info(f"  Entry: {entry_price:.2f}, Stop: {stop_loss:.2f}")
            logger.info(f"  Risk per share: {risk_per_share:.2f}")
            logger.info(f"  Shares: {shares}, Value: {position_value:,.0f} IDR")
            logger.info(f"  Risk: {(risk_per_share * shares / portfolio_value * 100):.2f}%")
        
        return shares
    
    def run_criteria_adjustment_test(self, test_date: str = '2024-12-01'):
        """Run test with adjusted criteria for Indonesian market"""
        logger.info("🚀 Starting Criteria Adjustment Test for Indonesian Market")
        logger.info("=" * 80)
        
        if not self.connect_database():
            return None
        
        # Get available symbols
        symbols = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'TLKM.JK', 
                  'ASII.JK', 'AUTO.JK', 'INDF.JK', 'UNVR.JK', 'ICBP.JK']
        
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
        logger.info(f"📊 Testing {len(symbols_data)} symbols with adjusted criteria")
        
        # Test 1: Adjusted Market Condition
        logger.info("\n" + "="*60)
        logger.info("TEST 1: ADJUSTED MARKET CONDITION (Indonesian Market)")
        logger.info("="*60)
        market_condition = self.check_market_condition_adjusted(symbols_data, test_date)
        
        # Test 2: Adjusted Momentum Screening
        logger.info("\n" + "="*60)
        logger.info("TEST 2: ADJUSTED MOMENTUM SCREENING (Indonesian Market)")
        logger.info("="*60)
        momentum_stocks = self.screen_momentum_stocks_adjusted(symbols_data, test_date)
        
        # Test 3: Adjusted Breakout Analysis
        logger.info("\n" + "="*60)
        logger.info("TEST 3: ADJUSTED BREAKOUT ANALYSIS (Indonesian Market)")
        logger.info("="*60)
        breakout_setups = []
        
        for stock in momentum_stocks[:3]:  # Test top 3 momentum stocks
            if stock['symbol'] in symbols_data:
                setup = self.analyze_breakout_setup_adjusted(
                    stock['symbol'], symbols_data[stock['symbol']], test_date)
                breakout_setups.append(setup)
        
        # Test 4: Position Sizing
        logger.info("\n" + "="*60)
        logger.info("TEST 4: ADJUSTED POSITION SIZING (Indonesian Market)")
        logger.info("="*60)
        
        portfolio_value = 1000000  # 1M IDR
        position_sizes = []
        
        for stock in momentum_stocks[:3]:
            if stock['symbol'] in symbols_data:
                df = symbols_data[stock['symbol']]
                current_price = df['close'].iloc[-1]
                stop_loss = current_price * 0.95  # 5% stop loss
                
                shares = self.calculate_position_size_adjusted(
                    stock['symbol'], current_price, stop_loss, portfolio_value)
                
                if shares > 0:
                    position_sizes.append({
                        'symbol': stock['symbol'],
                        'shares': shares,
                        'entry_price': current_price,
                        'stop_loss': stop_loss,
                        'position_value': shares * current_price
                    })
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("CRITERIA ADJUSTMENT TEST SUMMARY")
        logger.info("="*80)
        logger.info(f"Market Favorable: {market_condition['market_favorable']}")
        logger.info(f"Momentum Stocks Found: {len(momentum_stocks)}")
        logger.info(f"Breakout Setups Found: {sum(1 for s in breakout_setups if s['setup_found'])}")
        logger.info(f"Position Sizes Calculated: {len(position_sizes)}")
        
        if market_condition['market_favorable'] and momentum_stocks:
            logger.info("✅ Adjusted strategy conditions met - trading opportunities available")
        else:
            logger.info("❌ Adjusted strategy conditions not met - no trading opportunities")
        
        return {
            'test_date': test_date,
            'market_condition': market_condition,
            'momentum_stocks': momentum_stocks,
            'breakout_setups': breakout_setups,
            'position_sizes': position_sizes,
            'strategy_ready': market_condition['market_favorable'] and len(momentum_stocks) > 0,
            'criteria_used': self.criteria
        }

def main():
    """Main function to run criteria adjustment test"""
    tester = IndonesiaKulamagiCriteriaAdjustment()
    
    # Test with adjusted criteria
    result = tester.run_criteria_adjustment_test()
    
    if result:
        logger.info("\n✅ Criteria adjustment test completed successfully!")
        logger.info(f"📊 Results: {result['strategy_ready']}")
        return result
    else:
        logger.error("\n❌ Criteria adjustment test failed!")
        return None

if __name__ == "__main__":
    main()
