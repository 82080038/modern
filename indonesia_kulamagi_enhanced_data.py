"""
Indonesia Kulamagi Strategy - Enhanced Data Implementation
Data Enhancement: Tambahkan lebih banyak symbols dan data historis
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

class IndonesiaKulamagiEnhancedData:
    """
    Enhanced Data Implementation untuk strategi Christian Kulamagi
    """
    
    def __init__(self, host='localhost', user='root', password='', database='scalper'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        # Enhanced symbols list untuk pasar Indonesia
        self.symbols = {
            'banking': ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'BNGA.JK', 'BTPN.JK', 'BSIM.JK', 'BJTM.JK'],
            'telecom': ['TLKM.JK', 'ISAT.JK', 'EXCL.JK', 'FREN.JK'],
            'consumer': ['UNVR.JK', 'ICBP.JK', 'INDF.JK', 'GGRM.JK', 'SIDO.JK', 'MLBI.JK', 'ROTI.JK'],
            'automotive': ['ASII.JK', 'AUTO.JK', 'INCO.JK', 'ADRO.JK'],
            'infrastructure': ['PTPP.JK', 'ADHI.JK', 'WIKA.JK', 'JSMR.JK', 'SMGR.JK'],
            'mining': ['ANTM.JK', 'ADRO.JK', 'INCO.JK', 'PTBA.JK', 'PGAS.JK'],
            'technology': ['BUKA.JK', 'EMTK.JK', 'SCMA.JK', 'MNCN.JK'],
            'energy': ['PGAS.JK', 'PTBA.JK', 'ADRO.JK', 'ANTM.JK'],
            'property': ['BSDE.JK', 'LPKR.JK', 'ASRI.JK', 'CTRA.JK'],
            'healthcare': ['SIDO.JK', 'KLBF.JK', 'SCMA.JK', 'EMTK.JK']
        }
        
        # Market indices
        self.indices = {
            'IDX_COMPOSITE': '^JKSE',
            'IDX_LQ45': '^JKLQ45',
            'IDX_SECTORAL': {
                'banking': '^JKBANK',
                'telecom': '^JKTELECOM',
                'consumer': '^JKCONSUMER',
                'mining': '^JKMINING'
            }
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
    
    def get_all_symbols(self):
        """Get all available symbols from database"""
        try:
            if not self.connection:
                return []
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT symbol, COUNT(*) as record_count 
                    FROM historical_ohlcv_daily 
                    WHERE date >= '2020-01-01' 
                    GROUP BY symbol 
                    HAVING record_count >= 100
                    ORDER BY record_count DESC
                """)
                
                symbols = cursor.fetchall()
                logger.info(f"✅ Found {len(symbols)} symbols with sufficient data")
                
                return [s['symbol'] for s in symbols]
                
        except Exception as e:
            logger.error(f"❌ Error getting available symbols: {e}")
            return []
    
    def get_enhanced_symbols(self):
        """Get enhanced symbols list with sector classification"""
        all_symbols = self.get_all_symbols()
        enhanced_symbols = {}
        
        for sector, symbols in self.symbols.items():
            sector_symbols = [s for s in symbols if s in all_symbols]
            if sector_symbols:
                enhanced_symbols[sector] = sector_symbols
                logger.info(f"✅ {sector.upper()}: {len(sector_symbols)} symbols")
        
        return enhanced_symbols
    
    def get_historical_data_enhanced(self, symbol: str, start_date: str, end_date: str):
        """Get enhanced historical data with additional metrics"""
        try:
            if not self.connection:
                return None
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT date, open, high, low, close, volume, adj_close
                    FROM historical_ohlcv_daily 
                    WHERE symbol = %s 
                    AND date BETWEEN %s AND %s
                    ORDER BY date ASC
                """, (symbol, start_date, end_date))
                
                data = cursor.fetchall()
                
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    # Add additional metrics
                    df = self._add_technical_indicators(df)
                    df = self._add_volume_metrics(df)
                    df = self._add_volatility_metrics(df)
                    
                    return df
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return None
    
    def _add_technical_indicators(self, df: pd.DataFrame):
        """Add technical indicators to dataframe"""
        df = df.copy()
        
        # Moving averages
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential moving averages
        df['ema_5'] = df['close'].ewm(span=5).mean()
        df['ema_10'] = df['close'].ewm(span=10).mean()
        df['ema_20'] = df['close'].ewm(span=20).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'])
        
        # MACD
        macd_data = self._calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        
        # Bollinger Bands
        bb_data = self._calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_data['upper']
        df['bb_middle'] = bb_data['middle']
        df['bb_lower'] = bb_data['lower']
        df['bb_width'] = bb_data['width']
        df['bb_position'] = bb_data['position']
        
        return df
    
    def _add_volume_metrics(self, df: pd.DataFrame):
        """Add volume-based metrics"""
        df = df.copy()
        
        # Volume moving averages
        df['volume_sma_10'] = df['volume'].rolling(window=10).mean()
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        
        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']
        
        # Volume trend
        df['volume_trend'] = df['volume'].rolling(window=5).mean() / df['volume'].rolling(window=20).mean()
        
        # On Balance Volume
        df['obv'] = self._calculate_obv(df)
        
        return df
    
    def _add_volatility_metrics(self, df: pd.DataFrame):
        """Add volatility metrics"""
        df = df.copy()
        
        # Price volatility
        df['volatility_10'] = df['close'].rolling(window=10).std()
        df['volatility_20'] = df['close'].rolling(window=20).std()
        df['volatility_50'] = df['close'].rolling(window=50).std()
        
        # Average True Range
        df['atr'] = self._calculate_atr(df)
        
        # Price range
        df['price_range'] = (df['high'] - df['low']) / df['close']
        df['price_range_pct'] = df['price_range'] * 100
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        width = (upper - lower) / sma
        position = (prices - lower) / (upper - lower)
        
        return {
            'upper': upper,
            'middle': sma,
            'lower': lower,
            'width': width,
            'position': position
        }
    
    def _calculate_obv(self, df: pd.DataFrame):
        """Calculate On Balance Volume"""
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=df.index)
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14):
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def get_sector_performance(self, start_date: str, end_date: str):
        """Get sector performance analysis"""
        logger.info("📊 Analyzing sector performance...")
        
        sector_performance = {}
        
        for sector, symbols in self.get_enhanced_symbols().items():
            sector_data = []
            
            for symbol in symbols:
                df = self.get_historical_data_enhanced(symbol, start_date, end_date)
                if df is not None and len(df) > 50:
                    # Calculate performance metrics
                    start_price = df['close'].iloc[0]
                    end_price = df['close'].iloc[-1]
                    total_return = (end_price / start_price - 1) * 100
                    
                    # Calculate volatility
                    volatility = df['close'].pct_change().std() * np.sqrt(252) * 100
                    
                    # Calculate Sharpe ratio (simplified)
                    returns = df['close'].pct_change().dropna()
                    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
                    
                    sector_data.append({
                        'symbol': symbol,
                        'total_return': total_return,
                        'volatility': volatility,
                        'sharpe_ratio': sharpe_ratio,
                        'max_drawdown': self._calculate_max_drawdown(df['close'])
                    })
            
            if sector_data:
                sector_performance[sector] = {
                    'symbols': sector_data,
                    'avg_return': np.mean([s['total_return'] for s in sector_data]),
                    'avg_volatility': np.mean([s['volatility'] for s in sector_data]),
                    'avg_sharpe': np.mean([s['sharpe_ratio'] for s in sector_data]),
                    'best_performer': max(sector_data, key=lambda x: x['total_return']),
                    'worst_performer': min(sector_data, key=lambda x: x['total_return'])
                }
                
                logger.info(f"✅ {sector.upper()}: {len(sector_data)} symbols, "
                          f"Avg Return: {sector_performance[sector]['avg_return']:.2f}%, "
                          f"Avg Volatility: {sector_performance[sector]['avg_volatility']:.2f}%")
        
        return sector_performance
    
    def _calculate_max_drawdown(self, prices: pd.Series):
        """Calculate maximum drawdown"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min() * 100
    
    def get_market_rotation_analysis(self, start_date: str, end_date: str):
        """Analyze market rotation between sectors"""
        logger.info("🔄 Analyzing market rotation...")
        
        # Get sector performance
        sector_performance = self.get_sector_performance(start_date, end_date)
        
        # Analyze rotation patterns
        rotation_analysis = {}
        
        for sector, data in sector_performance.items():
            # Calculate relative strength
            avg_return = data['avg_return']
            avg_volatility = data['avg_volatility']
            
            # Risk-adjusted return
            risk_adjusted_return = avg_return / avg_volatility if avg_volatility > 0 else 0
            
            # Momentum score
            momentum_score = 0
            for symbol_data in data['symbols']:
                if symbol_data['total_return'] > 0:
                    momentum_score += 1
            
            momentum_score = momentum_score / len(data['symbols'])
            
            rotation_analysis[sector] = {
                'avg_return': avg_return,
                'avg_volatility': avg_volatility,
                'risk_adjusted_return': risk_adjusted_return,
                'momentum_score': momentum_score,
                'rotation_strength': risk_adjusted_return * momentum_score
            }
        
        # Sort by rotation strength
        sorted_sectors = sorted(rotation_analysis.items(), 
                              key=lambda x: x[1]['rotation_strength'], reverse=True)
        
        logger.info("📈 Market Rotation Analysis:")
        for i, (sector, data) in enumerate(sorted_sectors):
            logger.info(f"  {i+1}. {sector.upper()}: "
                       f"Return: {data['avg_return']:.2f}%, "
                       f"Volatility: {data['avg_volatility']:.2f}%, "
                       f"Rotation Strength: {data['rotation_strength']:.2f}")
        
        return rotation_analysis, sorted_sectors
    
    def run_enhanced_data_analysis(self, start_date: str = '2020-01-01', end_date: str = '2024-12-31'):
        """Run enhanced data analysis"""
        logger.info("🚀 Starting Enhanced Data Analysis")
        logger.info("=" * 80)
        
        if not self.connect_database():
            return None
        
        # Get enhanced symbols
        enhanced_symbols = self.get_enhanced_symbols()
        total_symbols = sum(len(symbols) for symbols in enhanced_symbols.values())
        logger.info(f"📊 Total symbols: {total_symbols} across {len(enhanced_symbols)} sectors")
        
        # Analyze sector performance
        sector_performance = self.get_sector_performance(start_date, end_date)
        
        # Analyze market rotation
        rotation_analysis, sorted_sectors = self.get_market_rotation_analysis(start_date, end_date)
        
        # Summary
        logger.info("\n📊 ENHANCED DATA ANALYSIS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Analysis Period: {start_date} to {end_date}")
        logger.info(f"Total Sectors: {len(enhanced_symbols)}")
        logger.info(f"Total Symbols: {total_symbols}")
        logger.info(f"Top Performing Sector: {sorted_sectors[0][0].upper()}")
        logger.info(f"Best Rotation Strength: {sorted_sectors[0][1]['rotation_strength']:.2f}")
        
        return {
            'enhanced_symbols': enhanced_symbols,
            'sector_performance': sector_performance,
            'rotation_analysis': rotation_analysis,
            'sorted_sectors': sorted_sectors,
            'analysis_period': f"{start_date} to {end_date}",
            'total_symbols': total_symbols,
            'total_sectors': len(enhanced_symbols)
        }

def main():
    """Main function to run enhanced data analysis"""
    analyzer = IndonesiaKulamagiEnhancedData()
    
    # Run enhanced data analysis
    result = analyzer.run_enhanced_data_analysis()
    
    if result:
        logger.info("\n✅ Enhanced data analysis completed successfully!")
        return result
    else:
        logger.error("\n❌ Enhanced data analysis failed!")
        return None

if __name__ == "__main__":
    main()
