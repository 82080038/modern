"""
Indonesia Kulamagi Strategy - Market Analysis
Market Analysis: Implementasi analisis sektor dan rotasi
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

class IndonesiaKulamagiMarketAnalysis:
    """
    Market Analysis untuk strategi Christian Kulamagi di pasar Indonesia
    """
    
    def __init__(self, host='localhost', user='root', password='', database='scalper'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        # Sektor dan rotasi pasar Indonesia
        self.sectors = {
            'banking': {
                'symbols': ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 'BNGA.JK', 'BTPN.JK', 'BSIM.JK', 'BJTM.JK'],
                'weight': 0.25,  # 25% weight in IDX
                'volatility': 0.20,
                'correlation': 0.7
            },
            'telecom': {
                'symbols': ['TLKM.JK', 'ISAT.JK', 'EXCL.JK', 'FREN.JK'],
                'weight': 0.15,
                'volatility': 0.25,
                'correlation': 0.6
            },
            'consumer': {
                'symbols': ['UNVR.JK', 'ICBP.JK', 'INDF.JK', 'GGRM.JK', 'SIDO.JK', 'MLBI.JK', 'ROTI.JK'],
                'weight': 0.20,
                'volatility': 0.18,
                'correlation': 0.5
            },
            'automotive': {
                'symbols': ['ASII.JK', 'AUTO.JK', 'INCO.JK', 'ADRO.JK'],
                'weight': 0.10,
                'volatility': 0.30,
                'correlation': 0.8
            },
            'infrastructure': {
                'symbols': ['PTPP.JK', 'ADHI.JK', 'WIKA.JK', 'JSMR.JK', 'SMGR.JK'],
                'weight': 0.12,
                'volatility': 0.35,
                'correlation': 0.6
            },
            'mining': {
                'symbols': ['ANTM.JK', 'ADRO.JK', 'INCO.JK', 'PTBA.JK', 'PGAS.JK'],
                'weight': 0.08,
                'volatility': 0.40,
                'correlation': 0.9
            },
            'technology': {
                'symbols': ['BUKA.JK', 'EMTK.JK', 'SCMA.JK', 'MNCN.JK'],
                'weight': 0.05,
                'volatility': 0.45,
                'correlation': 0.4
            },
            'energy': {
                'symbols': ['PGAS.JK', 'PTBA.JK', 'ADRO.JK', 'ANTM.JK'],
                'weight': 0.05,
                'volatility': 0.35,
                'correlation': 0.8
            }
        }
        
        # Market rotation patterns
        self.rotation_patterns = {
            'bull_market': ['technology', 'consumer', 'banking'],
            'bear_market': ['mining', 'energy', 'infrastructure'],
            'recovery': ['banking', 'consumer', 'telecom'],
            'growth': ['technology', 'consumer', 'automotive'],
            'value': ['banking', 'infrastructure', 'energy']
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
    
    def analyze_sector_performance(self, start_date: str, end_date: str):
        """Analyze sector performance and rotation"""
        logger.info("📊 Analyzing sector performance and rotation...")
        
        sector_analysis = {}
        
        for sector_name, sector_info in self.sectors.items():
            logger.info(f"🔍 Analyzing {sector_name.upper()} sector...")
            
            sector_data = []
            sector_returns = []
            
            for symbol in sector_info['symbols']:
                df = self.get_historical_data(symbol, start_date, end_date)
                if df is not None and len(df) > 50:
                    # Calculate performance metrics
                    start_price = df['close'].iloc[0]
                    end_price = df['close'].iloc[-1]
                    total_return = (end_price / start_price - 1) * 100
                    
                    # Calculate volatility
                    returns = df['close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252) * 100
                    
                    # Calculate Sharpe ratio
                    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
                    
                    # Calculate max drawdown
                    peak = df['close'].expanding().max()
                    drawdown = (df['close'] - peak) / peak
                    max_drawdown = drawdown.min() * 100
                    
                    sector_data.append({
                        'symbol': symbol,
                        'total_return': total_return,
                        'volatility': volatility,
                        'sharpe_ratio': sharpe_ratio,
                        'max_drawdown': max_drawdown,
                        'start_price': start_price,
                        'end_price': end_price
                    })
                    
                    sector_returns.append(total_return)
            
            if sector_data:
                # Calculate sector metrics
                avg_return = np.mean(sector_returns)
                avg_volatility = np.mean([s['volatility'] for s in sector_data])
                avg_sharpe = np.mean([s['sharpe_ratio'] for s in sector_data])
                avg_drawdown = np.mean([s['max_drawdown'] for s in sector_data])
                
                # Calculate sector momentum
                momentum_score = self._calculate_sector_momentum(sector_data)
                
                # Calculate relative strength
                relative_strength = self._calculate_relative_strength(sector_data, sector_returns)
                
                sector_analysis[sector_name] = {
                    'symbols': sector_data,
                    'avg_return': avg_return,
                    'avg_volatility': avg_volatility,
                    'avg_sharpe': avg_sharpe,
                    'avg_drawdown': avg_drawdown,
                    'momentum_score': momentum_score,
                    'relative_strength': relative_strength,
                    'sector_weight': sector_info['weight'],
                    'expected_volatility': sector_info['volatility'],
                    'correlation': sector_info['correlation']
                }
                
                logger.info(f"✅ {sector_name.upper()}: {len(sector_data)} symbols, "
                          f"Return: {avg_return:.2f}%, Volatility: {avg_volatility:.2f}%, "
                          f"Momentum: {momentum_score:.2f}")
        
        return sector_analysis
    
    def _calculate_sector_momentum(self, sector_data: List[Dict]):
        """Calculate sector momentum score"""
        if not sector_data:
            return 0
        
        # Weighted momentum based on performance and volatility
        momentum_scores = []
        for data in sector_data:
            # Positive momentum for positive returns
            return_momentum = max(0, data['total_return'] / 100)
            
            # Volatility adjustment (lower volatility = higher momentum score)
            volatility_adj = 1 / (1 + data['volatility'] / 100)
            
            # Combined momentum score
            momentum_score = return_momentum * volatility_adj
            momentum_scores.append(momentum_score)
        
        return np.mean(momentum_scores)
    
    def _calculate_relative_strength(self, sector_data: List[Dict], sector_returns: List[float]):
        """Calculate relative strength of sector"""
        if not sector_returns:
            return 0
        
        # Compare to market average (simplified)
        market_avg = np.mean(sector_returns)
        sector_avg = np.mean(sector_returns)
        
        # Relative strength ratio
        relative_strength = sector_avg / market_avg if market_avg != 0 else 1
        
        return relative_strength
    
    def analyze_market_rotation(self, sector_analysis: Dict):
        """Analyze market rotation patterns"""
        logger.info("🔄 Analyzing market rotation patterns...")
        
        # Sort sectors by performance
        sorted_sectors = sorted(sector_analysis.items(), 
                              key=lambda x: x[1]['avg_return'], reverse=True)
        
        # Identify rotation patterns
        rotation_analysis = {}
        
        # Bull market indicators
        bull_sectors = [s for s in sorted_sectors if s[1]['avg_return'] > 0]
        bear_sectors = [s for s in sorted_sectors if s[1]['avg_return'] < 0]
        
        # Growth vs Value analysis
        growth_sectors = ['technology', 'consumer', 'automotive']
        value_sectors = ['banking', 'infrastructure', 'energy']
        
        growth_performance = np.mean([sector_analysis[s]['avg_return'] 
                                    for s in growth_sectors if s in sector_analysis])
        value_performance = np.mean([sector_analysis[s]['avg_return'] 
                                   for s in value_sectors if s in sector_analysis])
        
        # Sector rotation score
        rotation_score = self._calculate_rotation_score(sector_analysis)
        
        rotation_analysis = {
            'sorted_sectors': sorted_sectors,
            'bull_sectors': bull_sectors,
            'bear_sectors': bear_sectors,
            'growth_performance': growth_performance,
            'value_performance': value_performance,
            'rotation_score': rotation_score,
            'market_phase': self._identify_market_phase(sector_analysis)
        }
        
        logger.info("📈 Market Rotation Analysis:")
        logger.info(f"  Bull Sectors: {len(bull_sectors)}")
        logger.info(f"  Bear Sectors: {len(bear_sectors)}")
        logger.info(f"  Growth Performance: {growth_performance:.2f}%")
        logger.info(f"  Value Performance: {value_performance:.2f}%")
        logger.info(f"  Rotation Score: {rotation_score:.2f}")
        logger.info(f"  Market Phase: {rotation_analysis['market_phase']}")
        
        return rotation_analysis
    
    def _calculate_rotation_score(self, sector_analysis: Dict):
        """Calculate overall rotation score"""
        if not sector_analysis:
            return 0
        
        # Calculate dispersion of returns
        returns = [data['avg_return'] for data in sector_analysis.values()]
        return_std = np.std(returns)
        
        # Calculate momentum dispersion
        momentums = [data['momentum_score'] for data in sector_analysis.values()]
        momentum_std = np.std(momentums)
        
        # Rotation score (higher = more rotation)
        rotation_score = (return_std + momentum_std) / 2
        
        return rotation_score
    
    def _identify_market_phase(self, sector_analysis: Dict):
        """Identify current market phase"""
        if not sector_analysis:
            return "Unknown"
        
        # Calculate overall market performance
        avg_return = np.mean([data['avg_return'] for data in sector_analysis.values()])
        avg_volatility = np.mean([data['avg_volatility'] for data in sector_analysis.values()])
        
        # Identify phase based on performance and volatility
        if avg_return > 5 and avg_volatility < 20:
            return "Bull Market"
        elif avg_return < -5 and avg_volatility > 25:
            return "Bear Market"
        elif avg_return > 0 and avg_volatility < 25:
            return "Recovery"
        elif avg_return > 2 and avg_volatility > 20:
            return "Growth"
        else:
            return "Consolidation"
    
    def get_sector_rotation_signals(self, sector_analysis: Dict, rotation_analysis: Dict):
        """Get sector rotation trading signals"""
        logger.info("📡 Generating sector rotation signals...")
        
        signals = []
        
        for sector_name, sector_data in sector_analysis.items():
            # Calculate signal strength
            signal_strength = self._calculate_signal_strength(sector_data, rotation_analysis)
            
            # Determine signal type
            if signal_strength > 0.7:
                signal_type = "STRONG_BUY"
            elif signal_strength > 0.4:
                signal_type = "BUY"
            elif signal_strength < -0.7:
                signal_type = "STRONG_SELL"
            elif signal_strength < -0.4:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            signals.append({
                'sector': sector_name,
                'signal_type': signal_type,
                'signal_strength': signal_strength,
                'avg_return': sector_data['avg_return'],
                'momentum_score': sector_data['momentum_score'],
                'relative_strength': sector_data['relative_strength']
            })
        
        # Sort by signal strength
        signals.sort(key=lambda x: x['signal_strength'], reverse=True)
        
        logger.info("🎯 Sector Rotation Signals:")
        for signal in signals[:5]:  # Top 5 signals
            logger.info(f"  {signal['sector'].upper()}: {signal['signal_type']} "
                       f"(Strength: {signal['signal_strength']:.2f})")
        
        return signals
    
    def _calculate_signal_strength(self, sector_data: Dict, rotation_analysis: Dict):
        """Calculate signal strength for sector"""
        # Base signal from performance
        performance_signal = sector_data['avg_return'] / 100
        
        # Momentum signal
        momentum_signal = sector_data['momentum_score']
        
        # Relative strength signal
        relative_signal = (sector_data['relative_strength'] - 1) * 0.5
        
        # Market phase adjustment
        market_phase = rotation_analysis.get('market_phase', 'Unknown')
        phase_multiplier = self._get_phase_multiplier(market_phase, sector_data)
        
        # Combined signal strength
        signal_strength = (performance_signal + momentum_signal + relative_signal) * phase_multiplier
        
        return signal_strength
    
    def _get_phase_multiplier(self, market_phase: str, sector_data: Dict):
        """Get phase multiplier for sector"""
        phase_multipliers = {
            'Bull Market': 1.2,
            'Bear Market': 0.8,
            'Recovery': 1.1,
            'Growth': 1.0,
            'Consolidation': 0.9
        }
        
        return phase_multipliers.get(market_phase, 1.0)
    
    def run_market_analysis(self, start_date: str = '2024-01-01', end_date: str = '2024-12-31'):
        """Run comprehensive market analysis"""
        logger.info("🚀 Starting Market Analysis for Indonesian Market")
        logger.info("=" * 80)
        
        if not self.connect_database():
            return None
        
        # Analyze sector performance
        sector_analysis = self.analyze_sector_performance(start_date, end_date)
        
        # Analyze market rotation
        rotation_analysis = self.analyze_market_rotation(sector_analysis)
        
        # Get sector rotation signals
        rotation_signals = self.get_sector_rotation_signals(sector_analysis, rotation_analysis)
        
        # Summary
        logger.info("\n📊 MARKET ANALYSIS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Analysis Period: {start_date} to {end_date}")
        logger.info(f"Sectors Analyzed: {len(sector_analysis)}")
        logger.info(f"Market Phase: {rotation_analysis['market_phase']}")
        logger.info(f"Rotation Score: {rotation_analysis['rotation_score']:.2f}")
        logger.info(f"Strong Signals: {len([s for s in rotation_signals if s['signal_strength'] > 0.7])}")
        
        return {
            'sector_analysis': sector_analysis,
            'rotation_analysis': rotation_analysis,
            'rotation_signals': rotation_signals,
            'analysis_period': f"{start_date} to {end_date}",
            'total_sectors': len(sector_analysis)
        }

def main():
    """Main function to run market analysis"""
    analyzer = IndonesiaKulamagiMarketAnalysis()
    
    # Run market analysis
    result = analyzer.run_market_analysis()
    
    if result:
        logger.info("\n✅ Market analysis completed successfully!")
        return result
    else:
        logger.error("\n❌ Market analysis failed!")
        return None

if __name__ == "__main__":
    main()
