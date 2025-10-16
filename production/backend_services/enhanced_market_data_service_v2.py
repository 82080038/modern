"""
Enhanced Market Data Service V2
===============================

Service untuk market data dengan implementasi algoritma terbukti
menggunakan multiple data sources, real-time processing, dan advanced analytics.

Author: AI Assistant
Date: 2025-01-17
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import json
from app.models.market_data import MarketData, HistoricalData, SymbolInfo
from app.services.cache_service import CacheService
import aiohttp
import websockets
import redis

logger = logging.getLogger(__name__)

class EnhancedMarketDataServiceV2:
    """
    Enhanced Market Data Service V2 dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = CacheService(db)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # Data sources configuration
        self.data_sources = {
            'yahoo_finance': {
                'enabled': True,
                'priority': 1,
                'rate_limit': 2000,  # requests per hour
                'timeout': 30
            },
            'alpha_vantage': {
                'enabled': True,
                'priority': 2,
                'rate_limit': 500,   # requests per day
                'timeout': 30,
                'api_key': 'YOUR_ALPHA_VANTAGE_API_KEY'
            },
            'polygon': {
                'enabled': False,
                'priority': 3,
                'rate_limit': 1000,  # requests per minute
                'timeout': 30,
                'api_key': 'YOUR_POLYGON_API_KEY'
            }
        }
        
        # Real-time data configuration
        self.real_time_symbols = set()
        self.websocket_connections = {}
        self.data_quality_threshold = 0.95  # 95% data quality required
        
    async def get_enhanced_market_data(
        self, 
        symbol: str, 
        timeframe: str = '1d',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_indicators: bool = True,
        include_volume: bool = True,
        include_sentiment: bool = False
    ) -> Dict[str, Any]:
        """Get enhanced market data dengan multiple sources dan quality validation"""
        try:
            # Set default dates
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Check cache first
            cache_key = f"market_data_{symbol}_{timeframe}_{start_date}_{end_date}"
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Returning cached data for {symbol}")
                return cached_data
            
            # Try multiple data sources
            data_result = None
            best_quality = 0
            
            for source_name, source_config in self.data_sources.items():
                if not source_config['enabled']:
                    continue
                
                try:
                    source_data = await self._get_data_from_source(
                        source_name, symbol, timeframe, start_date, end_date, source_config
                    )
                    
                    if source_data:
                        # Assess data quality
                        quality_score = await self._assess_data_quality(source_data)
                        
                        if quality_score > best_quality and quality_score >= self.data_quality_threshold:
                            data_result = source_data
                            data_result['source'] = source_name
                            data_result['quality_score'] = quality_score
                            best_quality = quality_score
                            
                            logger.info(f"Data from {source_name} quality: {quality_score:.2f}")
                            
                except Exception as e:
                    logger.warning(f"Data source {source_name} failed: {e}")
                    continue
            
            if not data_result:
                return {'error': 'All data sources failed or insufficient quality'}
            
            # Enhance data dengan indicators
            if include_indicators:
                data_result = await self._add_technical_indicators(data_result)
            
            # Add volume analysis
            if include_volume:
                data_result = await self._add_volume_analysis(data_result)
            
            # Add sentiment data
            if include_sentiment:
                data_result = await self._add_sentiment_data(symbol, data_result)
            
            # Add market microstructure data
            data_result = await self._add_microstructure_data(data_result)
            
            # Cache the result
            await self._cache_data(cache_key, data_result, ttl=300)  # 5 minutes
            
            return data_result
            
        except Exception as e:
            logger.error(f"Error getting enhanced market data: {e}")
            return {'error': str(e)}
    
    async def _get_data_from_source(
        self, 
        source_name: str, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime,
        source_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get data dari specific source"""
        try:
            if source_name == 'yahoo_finance':
                return await self._get_yahoo_finance_data(symbol, timeframe, start_date, end_date)
            elif source_name == 'alpha_vantage':
                return await self._get_alpha_vantage_data(symbol, timeframe, start_date, end_date)
            elif source_name == 'polygon':
                return await self._get_polygon_data(symbol, timeframe, start_date, end_date)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting data from {source_name}: {e}")
            return None
    
    async def _get_yahoo_finance_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get data dari Yahoo Finance"""
        try:
            # Convert timeframe to Yahoo Finance format
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '1d': '1d', '1w': '1wk', '1M': '1mo'
            }
            interval = interval_map.get(timeframe, '1d')
            
            # Download data
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=True,
                prepost=True
            )
            
            if data.empty:
                return None
            
            # Convert to standard format
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'data': data.to_dict('records'),
                'columns': list(data.columns),
                'index': data.index.tolist(),
                'metadata': {
                    'source': 'yahoo_finance',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'data_points': len(data)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance data: {e}")
            return None
    
    async def _get_alpha_vantage_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get data dari Alpha Vantage"""
        try:
            api_key = self.data_sources['alpha_vantage']['api_key']
            if not api_key or api_key == 'YOUR_ALPHA_VANTAGE_API_KEY':
                return None
            
            # Convert timeframe to Alpha Vantage format
            function_map = {
                '1m': 'TIME_SERIES_INTRADAY',
                '5m': 'TIME_SERIES_INTRADAY',
                '15m': 'TIME_SERIES_INTRADAY',
                '30m': 'TIME_SERIES_INTRADAY',
                '1h': 'TIME_SERIES_INTRADAY',
                '1d': 'TIME_SERIES_DAILY',
                '1w': 'TIME_SERIES_WEEKLY',
                '1M': 'TIME_SERIES_MONTHLY'
            }
            
            function = function_map.get(timeframe, 'TIME_SERIES_DAILY')
            
            # Build URL
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': api_key,
                'outputsize': 'full'
            }
            
            if function == 'TIME_SERIES_INTRADAY':
                params['interval'] = timeframe
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process Alpha Vantage response
                        time_series_key = None
                        for key in data.keys():
                            if 'Time Series' in key:
                                time_series_key = key
                                break
                        
                        if time_series_key and time_series_key in data:
                            time_series = data[time_series_key]
                            
                            # Convert to DataFrame
                            df_data = []
                            for timestamp, values in time_series.items():
                                df_data.append({
                                    'timestamp': pd.to_datetime(timestamp),
                                    'open': float(values['1. open']),
                                    'high': float(values['2. high']),
                                    'low': float(values['3. low']),
                                    'close': float(values['4. close']),
                                    'volume': int(values['5. volume'])
                                })
                            
                            df = pd.DataFrame(df_data)
                            df = df.sort_values('timestamp')
                            
                            # Filter by date range
                            df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
                            
                            if df.empty:
                                return None
                            
                            result = {
                                'symbol': symbol,
                                'timeframe': timeframe,
                                'data': df.to_dict('records'),
                                'columns': list(df.columns),
                                'index': df['timestamp'].tolist(),
                                'metadata': {
                                    'source': 'alpha_vantage',
                                    'symbol': symbol,
                                    'timeframe': timeframe,
                                    'start_date': start_date.isoformat(),
                                    'end_date': end_date.isoformat(),
                                    'data_points': len(df)
                                }
                            }
                            
                            return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Alpha Vantage data: {e}")
            return None
    
    async def _get_polygon_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get data dari Polygon.io"""
        try:
            api_key = self.data_sources['polygon']['api_key']
            if not api_key or api_key == 'YOUR_POLYGON_API_KEY':
                return None
            
            # Convert timeframe to Polygon format
            timespan_map = {
                '1m': 'minute', '5m': 'minute', '15m': 'minute', '30m': 'minute',
                '1h': 'hour', '1d': 'day', '1w': 'week', '1M': 'month'
            }
            
            multiplier_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 1, '1d': 1, '1w': 1, '1M': 1
            }
            
            timespan = timespan_map.get(timeframe, 'day')
            multiplier = multiplier_map.get(timeframe, 1)
            
            # Build URL
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {'apikey': api_key}
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'results' in data and data['results']:
                            results = data['results']
                            
                            # Convert to DataFrame
                            df_data = []
                            for item in results:
                                df_data.append({
                                    'timestamp': pd.to_datetime(item['t'], unit='ms'),
                                    'open': item['o'],
                                    'high': item['h'],
                                    'low': item['l'],
                                    'close': item['c'],
                                    'volume': item['v']
                                })
                            
                            df = pd.DataFrame(df_data)
                            df = df.sort_values('timestamp')
                            
                            result = {
                                'symbol': symbol,
                                'timeframe': timeframe,
                                'data': df.to_dict('records'),
                                'columns': list(df.columns),
                                'index': df['timestamp'].tolist(),
                                'metadata': {
                                    'source': 'polygon',
                                    'symbol': symbol,
                                    'timeframe': timeframe,
                                    'start_date': start_date.isoformat(),
                                    'end_date': end_date.isoformat(),
                                    'data_points': len(df)
                                }
                            }
                            
                            return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Polygon data: {e}")
            return None
    
    async def _assess_data_quality(self, data: Dict[str, Any]) -> float:
        """Assess data quality score"""
        try:
            if 'data' not in data or not data['data']:
                return 0.0
            
            df = pd.DataFrame(data['data'])
            
            # Check for missing values
            missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
            completeness_score = 1 - missing_ratio
            
            # Check for data consistency
            if 'close' in df.columns:
                # Check for negative prices
                negative_prices = (df['close'] <= 0).sum()
                consistency_score = 1 - (negative_prices / len(df))
            else:
                consistency_score = 0.5
            
            # Check for data gaps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                time_diff = df['timestamp'].diff().dt.total_seconds()
                expected_interval = time_diff.median()
                
                # Check for gaps larger than 2x expected interval
                large_gaps = (time_diff > expected_interval * 2).sum()
                gap_score = 1 - (large_gaps / len(df))
            else:
                gap_score = 0.5
            
            # Overall quality score
            quality_score = (completeness_score * 0.4 + consistency_score * 0.3 + gap_score * 0.3)
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            return 0.0
    
    async def _add_technical_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add technical indicators to market data"""
        try:
            if 'data' not in data or not data['data']:
                return data
            
            df = pd.DataFrame(data['data'])
            
            # Ensure we have required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                return data
            
            # Calculate technical indicators
            indicators = {}
            
            # Moving averages
            indicators['sma_5'] = df['close'].rolling(5).mean()
            indicators['sma_10'] = df['close'].rolling(10).mean()
            indicators['sma_20'] = df['close'].rolling(20).mean()
            indicators['sma_50'] = df['close'].rolling(50).mean()
            indicators['sma_200'] = df['close'].rolling(200).mean()
            
            # Exponential moving averages
            indicators['ema_12'] = df['close'].ewm(span=12).mean()
            indicators['ema_26'] = df['close'].ewm(span=26).mean()
            
            # RSI
            indicators['rsi'] = self._calculate_rsi(df['close'])
            
            # MACD
            macd_line, signal_line, histogram = self._calculate_macd(df['close'])
            indicators['macd'] = macd_line
            indicators['macd_signal'] = signal_line
            indicators['macd_histogram'] = histogram
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['close'])
            indicators['bb_upper'] = bb_upper
            indicators['bb_middle'] = bb_middle
            indicators['bb_lower'] = bb_lower
            
            # Stochastic Oscillator
            stoch_k, stoch_d = self._calculate_stochastic(df['high'], df['low'], df['close'])
            indicators['stoch_k'] = stoch_k
            indicators['stoch_d'] = stoch_d
            
            # Williams %R
            indicators['williams_r'] = self._calculate_williams_r(df['high'], df['low'], df['close'])
            
            # Average True Range
            indicators['atr'] = self._calculate_atr(df['high'], df['low'], df['close'])
            
            # Volume indicators
            indicators['volume_sma'] = df['volume'].rolling(20).mean()
            indicators['volume_ratio'] = df['volume'] / indicators['volume_sma']
            
            # Add indicators to data
            for indicator_name, indicator_values in indicators.items():
                df[indicator_name] = indicator_values
            
            # Update data
            data['data'] = df.to_dict('records')
            data['indicators'] = list(indicators.keys())
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series(index=prices.index, dtype=float)
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram
        except:
            return pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float)
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window=period).mean()
            std_dev = prices.rolling(window=period).std()
            upper_band = sma + (std_dev * std)
            lower_band = sma - (std_dev * std)
            return upper_band, sma, lower_band
        except:
            return pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float)
    
    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            return k_percent, d_percent
        except:
            return pd.Series(index=close.index, dtype=float), pd.Series(index=close.index, dtype=float)
    
    def _calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        try:
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            return williams_r
        except:
            return pd.Series(index=close.index, dtype=float)
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=period).mean()
            return atr
        except:
            return pd.Series(index=close.index, dtype=float)
    
    async def _add_volume_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add volume analysis to market data"""
        try:
            if 'data' not in data or not data['data']:
                return data
            
            df = pd.DataFrame(data['data'])
            
            if 'volume' not in df.columns:
                return data
            
            # Volume analysis
            volume_analysis = {
                'volume_trend': self._calculate_volume_trend(df['volume']),
                'volume_profile': self._calculate_volume_profile(df),
                'volume_anomalies': self._detect_volume_anomalies(df['volume']),
                'accumulation_distribution': self._calculate_accumulation_distribution(df)
            }
            
            data['volume_analysis'] = volume_analysis
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding volume analysis: {e}")
            return data
    
    def _calculate_volume_trend(self, volume: pd.Series) -> Dict[str, Any]:
        """Calculate volume trend"""
        try:
            # Simple volume trend
            volume_sma = volume.rolling(20).mean()
            current_volume = volume.iloc[-1] if len(volume) > 0 else 0
            avg_volume = volume_sma.iloc[-1] if len(volume_sma) > 0 else 0
            
            trend = 'increasing' if current_volume > avg_volume * 1.2 else 'decreasing' if current_volume < avg_volume * 0.8 else 'stable'
            
            return {
                'trend': trend,
                'current_volume': current_volume,
                'average_volume': avg_volume,
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1
            }
        except:
            return {'trend': 'unknown', 'current_volume': 0, 'average_volume': 0, 'volume_ratio': 1}
    
    def _calculate_volume_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume profile"""
        try:
            if 'high' not in df.columns or 'low' not in df.columns or 'volume' not in df.columns:
                return {}
            
            # Simple volume profile
            price_range = df['high'].max() - df['low'].min()
            volume_at_high = df[df['high'] == df['high'].max()]['volume'].sum()
            volume_at_low = df[df['low'] == df['low'].min()]['volume'].sum()
            
            return {
                'price_range': price_range,
                'volume_at_high': volume_at_high,
                'volume_at_low': volume_at_low,
                'volume_imbalance': volume_at_high - volume_at_low
            }
        except:
            return {}
    
    def _detect_volume_anomalies(self, volume: pd.Series) -> List[Dict[str, Any]]:
        """Detect volume anomalies"""
        try:
            anomalies = []
            volume_sma = volume.rolling(20).mean()
            volume_std = volume.rolling(20).std()
            
            # Detect spikes (volume > 2 standard deviations above mean)
            spikes = volume > (volume_sma + 2 * volume_std)
            spike_indices = volume[spikes].index.tolist()
            
            for idx in spike_indices:
                anomalies.append({
                    'type': 'volume_spike',
                    'timestamp': idx,
                    'volume': volume[idx],
                    'normal_volume': volume_sma[idx],
                    'deviation': (volume[idx] - volume_sma[idx]) / volume_std[idx] if volume_std[idx] > 0 else 0
                })
            
            return anomalies
        except:
            return []
    
    def _calculate_accumulation_distribution(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Accumulation/Distribution Line"""
        try:
            if 'high' not in df.columns or 'low' not in df.columns or 'close' not in df.columns or 'volume' not in df.columns:
                return pd.Series(dtype=float)
            
            # A/D Line = Previous A/D + Current Period's Money Flow Volume
            money_flow_multiplier = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            money_flow_volume = money_flow_multiplier * df['volume']
            ad_line = money_flow_volume.cumsum()
            
            return ad_line
        except:
            return pd.Series(dtype=float)
    
    async def _add_sentiment_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add sentiment data to market data"""
        try:
            # This would integrate with sentiment analysis service
            # For now, return placeholder
            sentiment_data = {
                'news_sentiment': 0.0,
                'social_sentiment': 0.0,
                'overall_sentiment': 0.0,
                'sentiment_trend': 'neutral'
            }
            
            data['sentiment'] = sentiment_data
            return data
            
        except Exception as e:
            logger.error(f"Error adding sentiment data: {e}")
            return data
    
    async def _add_microstructure_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add market microstructure data"""
        try:
            if 'data' not in data or not data['data']:
                return data
            
            df = pd.DataFrame(data['data'])
            
            # Calculate bid-ask spread proxy (using high-low range)
            if 'high' in df.columns and 'low' in df.columns:
                df['spread_proxy'] = (df['high'] - df['low']) / df['close']
            
            # Calculate price impact
            if 'volume' in df.columns and 'close' in df.columns:
                df['price_change'] = df['close'].pct_change()
                df['volume_change'] = df['volume'].pct_change()
                df['price_impact'] = df['price_change'] / df['volume_change'].abs()
            
            # Update data
            data['data'] = df.to_dict('records')
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding microstructure data: {e}")
            return data
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def _cache_data(self, cache_key: str, data: Dict[str, Any], ttl: int = 300):
        """Cache data with TTL"""
        try:
            self.redis_client.setex(cache_key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Error caching data: {e}")
    
    async def get_real_time_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time price untuk symbol"""
        try:
            # Check cache first
            cache_key = f"realtime_price_{symbol}"
            cached_price = await self._get_from_cache(cache_key)
            if cached_price:
                return cached_price
            
            # Get real-time data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            real_time_data = {
                'symbol': symbol,
                'price': info.get('currentPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache for 30 seconds
            await self._cache_data(cache_key, real_time_data, ttl=30)
            
            return real_time_data
            
        except Exception as e:
            logger.error(f"Error getting real-time price: {e}")
            return {'error': str(e)}
    
    async def start_real_time_streaming(self, symbols: List[str]) -> Dict[str, Any]:
        """Start real-time data streaming untuk symbols"""
        try:
            for symbol in symbols:
                self.real_time_symbols.add(symbol)
            
            # Start WebSocket connections
            asyncio.create_task(self._maintain_websocket_connections())
            
            return {
                'success': True,
                'symbols': list(self.real_time_symbols),
                'message': 'Real-time streaming started'
            }
            
        except Exception as e:
            logger.error(f"Error starting real-time streaming: {e}")
            return {'error': str(e)}
    
    async def _maintain_websocket_connections(self):
        """Maintain WebSocket connections untuk real-time data"""
        try:
            while self.real_time_symbols:
                # This would implement actual WebSocket connections
                # For now, simulate with periodic data updates
                for symbol in list(self.real_time_symbols):
                    try:
                        # Get latest data
                        latest_data = await self.get_real_time_price(symbol)
                        
                        # Store in database
                        await self._store_real_time_data(symbol, latest_data)
                        
                    except Exception as e:
                        logger.error(f"Error updating real-time data for {symbol}: {e}")
                
                # Wait before next update
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except Exception as e:
            logger.error(f"Error maintaining WebSocket connections: {e}")
    
    async def _store_real_time_data(self, symbol: str, data: Dict[str, Any]):
        """Store real-time data ke database"""
        try:
            if 'error' in data:
                return
            
            # Create market data record
            market_data = MarketData(
                symbol=symbol,
                open_price=data.get('price', 0),
                high_price=data.get('price', 0),
                low_price=data.get('price', 0),
                close_price=data.get('price', 0),
                volume=data.get('volume', 0),
                timestamp=datetime.now()
            )
            
            self.db.add(market_data)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing real-time data: {e}")
            self.db.rollback()
    
    async def stop_real_time_streaming(self, symbols: List[str]) -> Dict[str, Any]:
        """Stop real-time streaming untuk symbols"""
        try:
            for symbol in symbols:
                self.real_time_symbols.discard(symbol)
            
            return {
                'success': True,
                'symbols': list(self.real_time_symbols),
                'message': 'Real-time streaming stopped'
            }
            
        except Exception as e:
            logger.error(f"Error stopping real-time streaming: {e}")
            return {'error': str(e)}
