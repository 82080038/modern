"""
Smart Data Caching Service
Mencegah re-downloading data yang sudah ada untuk menghemat waktu dan kuota
"""
from sqlalchemy.orm import Session
from app.models.market_data import CandlestickData, RealtimePrice
from app.services.data_service import DataService
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import hashlib
import json
import redis
from functools import wraps

logger = logging.getLogger(__name__)

class CacheService:
    """Service untuk smart data caching"""
    
    def __init__(self, db: Session, redis_client: redis.Redis = None):
        self.db = db
        self.redis = redis_client
        self.data_service = DataService(db)
        
        # Cache configuration
        self.cache_ttl = {
            'realtime': 60,  # 1 minute
            'historical': 3600,  # 1 hour
            'fundamental': 86400,  # 24 hours
            'sentiment': 1800,  # 30 minutes
            'metadata': 3600  # 1 hour
        }
    
    def get_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key"""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_string = f"{prefix}:{':'.join(f'{k}={v}' for k, v in sorted_kwargs)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def cache_wrapper(self, cache_type: str, ttl: int = None):
        """Decorator untuk caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.get_cache_key(
                    f"{func.__name__}_{cache_type}",
                    **{k: v for k, v in kwargs.items() if k not in ['db', 'self']}
                )
                
                # Try to get from cache
                if self.redis:
                    try:
                        cached_data = self.redis.get(cache_key)
                        if cached_data:
                            logger.debug(f"Cache hit for {cache_key}")
                            return json.loads(cached_data)
                    except Exception as e:
                        logger.warning(f"Redis cache error: {e}")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                if self.redis and result:
                    try:
                        cache_ttl = ttl or self.cache_ttl.get(cache_type, 3600)
                        self.redis.setex(
                            cache_key,
                            cache_ttl,
                            json.dumps(result, default=str)
                        )
                        logger.debug(f"Cached result for {cache_key}")
                    except Exception as e:
                        logger.warning(f"Redis cache set error: {e}")
                
                return result
            return wrapper
        return decorator
    
    def get_candlestick_data(self, 
                           symbol: str,
                           timeframe: str,
                           start_date: datetime,
                           end_date: datetime,
                           force_refresh: bool = False) -> List[Dict]:
        """Get candlestick data dengan smart caching"""
        try:
            # Check if we have data in database
            if not force_refresh:
                db_data = self.db.query(CandlestickData).filter(
                    CandlestickData.symbol == symbol.upper(),
                    CandlestickData.timeframe == timeframe,
                    CandlestickData.timestamp >= start_date,
                    CandlestickData.timestamp <= end_date
                ).order_by(CandlestickData.timestamp).all()
                
                if db_data:
                    logger.info(f"Found {len(db_data)} candlestick data points in DB for {symbol} {timeframe}")
                    return [self._candlestick_to_dict(candle) for candle in db_data]
            
            # Fetch from external source
            logger.info(f"Fetching candlestick data from external source for {symbol} {timeframe}")
            external_data = self.data_service.get_historical_candlestick_data(
                symbol, timeframe, start_date, end_date
            )
            
            if not external_data:
                return []
            
            # Store in database
            stored_count = 0
            for item in external_data:
                try:
                    # Check if already exists
                    existing = self.db.query(CandlestickData).filter(
                        CandlestickData.symbol == symbol.upper(),
                        CandlestickData.timeframe == timeframe,
                        CandlestickData.timestamp == item['timestamp']
                    ).first()
                    
                    if not existing:
                        db_candlestick = CandlestickData(
                            symbol=symbol.upper(),
                            timeframe=timeframe,
                            timestamp=item['timestamp'],
                            open=item['open'],
                            high=item['high'],
                            low=item['low'],
                            close=item['close'],
                            volume=item['volume']
                        )
                        self.db.add(db_candlestick)
                        stored_count += 1
                except Exception as e:
                    logger.warning(f"Error storing candlestick data: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"Stored {stored_count} new candlestick data points for {symbol} {timeframe}")
            
            return external_data
            
        except Exception as e:
            logger.error(f"Error getting candlestick data: {e}")
            return []
    
    def get_realtime_price(self, symbol: str, force_refresh: bool = False) -> Optional[Dict]:
        """Get real-time price dengan caching"""
        try:
            # Check cache first
            cache_key = self.get_cache_key("realtime_price", symbol=symbol)
            
            if not force_refresh and self.redis:
                try:
                    cached_data = self.redis.get(cache_key)
                    if cached_data:
                        logger.debug(f"Cache hit for realtime price {symbol}")
                        return json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"Redis cache error: {e}")
            
            # Fetch from external source
            price_data = self.data_service.get_real_time_price(symbol)
            
            if price_data:
                # Cache the result
                if self.redis:
                    try:
                        self.redis.setex(
                            cache_key,
                            self.cache_ttl['realtime'],
                            json.dumps(price_data, default=str)
                        )
                    except Exception as e:
                        logger.warning(f"Redis cache set error: {e}")
                
                # Store in database
                try:
                    db_price = RealtimePrice(
                        symbol=symbol.upper(),
                        price=price_data['price']
                    )
                    self.db.add(db_price)
                    self.db.commit()
                except Exception as e:
                    logger.warning(f"Error storing realtime price: {e}")
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error getting realtime price: {e}")
            return None
    
    def get_fundamental_data(self, symbol: str, force_refresh: bool = False) -> Optional[Dict]:
        """Get fundamental data dengan caching"""
        try:
            cache_key = self.get_cache_key("fundamental", symbol=symbol)
            
            if not force_refresh and self.redis:
                try:
                    cached_data = self.redis.get(cache_key)
                    if cached_data:
                        logger.debug(f"Cache hit for fundamental data {symbol}")
                        return json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"Redis cache error: {e}")
            
            # Fetch from external source
            fundamental_data = self.data_service.get_fundamental_data(symbol)
            
            if fundamental_data and self.redis:
                try:
                    self.redis.setex(
                        cache_key,
                        self.cache_ttl['fundamental'],
                        json.dumps(fundamental_data, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Redis cache set error: {e}")
            
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Error getting fundamental data: {e}")
            return None
    
    def get_sentiment_data(self, symbol: str, force_refresh: bool = False) -> Optional[Dict]:
        """Get sentiment data dengan caching"""
        try:
            cache_key = self.get_cache_key("sentiment", symbol=symbol)
            
            if not force_refresh and self.redis:
                try:
                    cached_data = self.redis.get(cache_key)
                    if cached_data:
                        logger.debug(f"Cache hit for sentiment data {symbol}")
                        return json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"Redis cache error: {e}")
            
            # Fetch from external source
            sentiment_data = self.data_service.get_sentiment_data(symbol)
            
            if sentiment_data and self.redis:
                try:
                    self.redis.setex(
                        cache_key,
                        self.cache_ttl['sentiment'],
                        json.dumps(sentiment_data, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Redis cache set error: {e}")
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error getting sentiment data: {e}")
            return None
    
    def get_data_coverage(self, symbol: str) -> Dict:
        """Get data coverage information"""
        try:
            # Check candlestick data coverage
            candlestick_coverage = {}
            timeframes = ['1m', '5m', '15m', '1h', '4h', '1D', '1W', '1M']
            
            for tf in timeframes:
                count = self.db.query(CandlestickData).filter(
                    CandlestickData.symbol == symbol.upper(),
                    CandlestickData.timeframe == tf
                ).count()
                
                if count > 0:
                    earliest = self.db.query(CandlestickData).filter(
                        CandlestickData.symbol == symbol.upper(),
                        CandlestickData.timeframe == tf
                    ).order_by(CandlestickData.timestamp.asc()).first()
                    
                    latest = self.db.query(CandlestickData).filter(
                        CandlestickData.symbol == symbol.upper(),
                        CandlestickData.timeframe == tf
                    ).order_by(CandlestickData.timestamp.desc()).first()
                    
                    candlestick_coverage[tf] = {
                        'count': count,
                        'earliest': earliest.timestamp.isoformat() if earliest else None,
                        'latest': latest.timestamp.isoformat() if latest else None
                    }
            
            # Check realtime data coverage
            realtime_count = self.db.query(RealtimePrice).filter(
                RealtimePrice.symbol == symbol.upper()
            ).count()
            
            return {
                'symbol': symbol.upper(),
                'candlestick_coverage': candlestick_coverage,
                'realtime_count': realtime_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting data coverage: {e}")
            return {'error': str(e)}
    
    def cleanup_old_data(self, days: int = 30) -> Dict:
        """Clean up old data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Clean up old realtime prices
            realtime_deleted = self.db.query(RealtimePrice).filter(
                RealtimePrice.timestamp < cutoff_date
            ).delete()
            
            # Clean up old candlestick data (keep more recent data)
            candlestick_deleted = self.db.query(CandlestickData).filter(
                CandlestickData.timestamp < cutoff_date
            ).delete()
            
            self.db.commit()
            
            return {
                'realtime_deleted': realtime_deleted,
                'candlestick_deleted': candlestick_deleted,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            self.db.rollback()
            return {'error': str(e)}
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            stats = {
                'redis_connected': False,
                'redis_info': {},
                'cache_keys': 0,
                'memory_usage': 0
            }
            
            if self.redis:
                try:
                    stats['redis_connected'] = True
                    stats['redis_info'] = self.redis.info()
                    stats['cache_keys'] = self.redis.dbsize()
                    stats['memory_usage'] = self.redis.info().get('used_memory_human', '0B')
                except Exception as e:
                    logger.warning(f"Redis info error: {e}")
            
            # Database stats
            candlestick_count = self.db.query(CandlestickData).count()
            realtime_count = self.db.query(RealtimePrice).count()
            
            stats['database_stats'] = {
                'candlestick_records': candlestick_count,
                'realtime_records': realtime_count
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    def clear_cache(self, cache_type: str = None) -> Dict:
        """Clear cache"""
        try:
            if not self.redis:
                return {'error': 'Redis not available'}
            
            if cache_type:
                # Clear specific cache type
                pattern = f"*{cache_type}*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                return {'cleared_keys': len(keys), 'pattern': pattern}
            else:
                # Clear all cache
                self.redis.flushdb()
                return {'message': 'All cache cleared'}
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {'error': str(e)}
    
    def _candlestick_to_dict(self, candle: CandlestickData) -> Dict:
        """Convert candlestick model to dict"""
        return {
            'timestamp': candle.timestamp.isoformat(),
            'open': candle.open,
            'high': candle.high,
            'low': candle.low,
            'close': candle.close,
            'volume': candle.volume
        }
    
    def preload_data(self, symbols: List[str], timeframes: List[str] = None) -> Dict:
        """Preload data untuk multiple symbols"""
        try:
            if not timeframes:
                timeframes = ['1D', '1W', '1M']
            
            results = {}
            
            for symbol in symbols:
                symbol_results = {}
                
                # Preload candlestick data
                for tf in timeframes:
                    try:
                        data = self.get_candlestick_data(
                            symbol=symbol,
                            timeframe=tf,
                            start_date=datetime.now() - timedelta(days=365),
                            end_date=datetime.now()
                        )
                        symbol_results[tf] = len(data)
                    except Exception as e:
                        logger.warning(f"Error preloading {symbol} {tf}: {e}")
                        symbol_results[tf] = 0
                
                # Preload realtime price
                try:
                    price_data = self.get_realtime_price(symbol)
                    symbol_results['realtime'] = 1 if price_data else 0
                except Exception as e:
                    logger.warning(f"Error preloading realtime {symbol}: {e}")
                    symbol_results['realtime'] = 0
                
                results[symbol] = symbol_results
            
            return {
                'preloaded_symbols': len(symbols),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error preloading data: {e}")
            return {'error': str(e)}
