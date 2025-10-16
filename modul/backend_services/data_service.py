"""
Data Service untuk fetching market data dengan rate limiting
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.market_data import MarketData, HistoricalData, DataUpdateLog, SymbolInfo, MarketStatus
from app.database import get_db
import time
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

class DataService:
    """Service untuk fetching dan managing market data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rate_limit_delay = 1.0  # 1 second delay between requests
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting untuk menghindari blocking"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_yfinance_symbol(self, symbol: str) -> str:
        """Convert IDX symbol ke yfinance format"""
        # IDX symbols biasanya sudah compatible dengan yfinance
        # Tapi kadang perlu suffix .JK untuk Jakarta
        if not symbol.endswith('.JK'):
            return f"{symbol}.JK"
        return symbol
    
    def fetch_historical_data(self, symbol: str, timeframe: str, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """Fetch historical data dari yfinance dengan rate limiting"""
        try:
            self._rate_limit()
            
            yf_symbol = self.get_yfinance_symbol(symbol)
            
            # Convert timeframe ke yfinance interval
            interval_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '4h': '4h', '1D': '1d', '1W': '1wk', 
                '1M': '1mo', '3M': '3mo', '6M': '6mo', '1Y': '1y'
            }
            
            interval = interval_map.get(timeframe, '1d')
            
            # Fetch data
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=True,
                prepost=True,
                threads=True
            )
            
            if data.empty:
                logger.warning(f"No data found for {symbol} {timeframe} from {start_date} to {end_date}")
                return None
            
            # Clean data
            data = data.dropna()
            data = data.reset_index()
            
            # Rename columns untuk consistency
            column_mapping = {
                'Open': 'open_price',
                'High': 'high_price', 
                'Low': 'low_price',
                'Close': 'close_price',
                'Volume': 'volume',
                'Adj Close': 'adjusted_close'
            }
            
            data = data.rename(columns=column_mapping)
            
            # Add timeframe column
            data['timeframe'] = timeframe
            data['symbol'] = symbol
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def save_historical_data(self, symbol: str, timeframe: str, data: pd.DataFrame) -> int:
        """Save historical data ke database dengan smart update"""
        try:
            saved_count = 0
            
            for _, row in data.iterrows():
                # Check if data already exists
                existing = self.db.query(HistoricalData).filter(
                    HistoricalData.symbol == symbol,
                    HistoricalData.timeframe == timeframe,
                    HistoricalData.date == row['Date'].date()
                ).first()
                
                if existing:
                    # Update existing record
                    existing.open_price = row.get('open_price')
                    existing.high_price = row.get('high_price')
                    existing.low_price = row.get('low_price')
                    existing.close_price = row.get('close_price')
                    existing.volume = row.get('volume')
                    existing.adjusted_close = row.get('adjusted_close')
                    existing.updated_at = datetime.now()
                else:
                    # Create new record
                    new_data = HistoricalData(
                        symbol=symbol,
                        timeframe=timeframe,
                        date=row['Date'].date(),
                        timestamp=row['Date'],
                        open_price=row.get('open_price'),
                        high_price=row.get('high_price'),
                        low_price=row.get('low_price'),
                        close_price=row.get('close_price'),
                        volume=row.get('volume'),
                        adjusted_close=row.get('adjusted_close'),
                        data_source="yfinance"
                    )
                    self.db.add(new_data)
                    saved_count += 1
            
            self.db.commit()
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving historical data for {symbol}: {e}")
            self.db.rollback()
            return 0
    
    def get_latest_data_date(self, symbol: str, timeframe: str) -> Optional[date]:
        """Get latest data date untuk symbol dan timeframe"""
        try:
            latest = self.db.query(HistoricalData).filter(
                HistoricalData.symbol == symbol,
                HistoricalData.timeframe == timeframe
            ).order_by(HistoricalData.date.desc()).first()
            
            return latest.date if latest else None
            
        except Exception as e:
            logger.error(f"Error getting latest data date for {symbol}: {e}")
            return None
    
    def update_historical_data(self, symbol: str, timeframe: str, days_back: int = 730) -> Dict:
        """Update historical data dengan smart caching"""
        try:
            # Get latest data date
            latest_date = self.get_latest_data_date(symbol, timeframe)
            
            # Calculate start date
            if latest_date:
                start_date = latest_date + timedelta(days=1)
                logger.info(f"Updating {symbol} {timeframe} from {start_date}")
            else:
                start_date = date.today() - timedelta(days=days_back)
                logger.info(f"Downloading {symbol} {timeframe} from {start_date} (first time)")
            
            end_date = date.today()
            
            # Skip if start_date >= end_date (data sudah up to date)
            if start_date >= end_date:
                return {
                    "status": "up_to_date",
                    "message": f"Data for {symbol} {timeframe} is already up to date",
                    "records_saved": 0
                }
            
            # Fetch data
            data = self.fetch_historical_data(symbol, timeframe, start_date, end_date)
            
            if data is None or data.empty:
                return {
                    "status": "no_data",
                    "message": f"No data available for {symbol} {timeframe}",
                    "records_saved": 0
                }
            
            # Save data
            records_saved = self.save_historical_data(symbol, timeframe, data)
            
            # Update log
            self._update_data_log(symbol, timeframe, "success", records_saved)
            
            return {
                "status": "success",
                "message": f"Updated {symbol} {timeframe} with {records_saved} new records",
                "records_saved": records_saved,
                "date_range": f"{start_date} to {end_date}"
            }
            
        except Exception as e:
            logger.error(f"Error updating historical data for {symbol}: {e}")
            self._update_data_log(symbol, timeframe, "error", 0, str(e))
            return {
                "status": "error",
                "message": f"Error updating {symbol} {timeframe}: {str(e)}",
                "records_saved": 0
            }
    
    def _update_data_log(self, symbol: str, timeframe: str, status: str, records_saved: int, error_message: str = None):
        """Update data update log"""
        try:
            log_entry = DataUpdateLog(
                symbol=symbol,
                timeframe=timeframe,
                last_update=datetime.now(),
                last_data_date=date.today(),
                total_records=records_saved,
                data_source="yfinance",
                status=status,
                error_message=error_message
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error updating data log: {e}")
    
    def get_popular_idx_symbols(self) -> List[str]:
        """Get list of popular IDX symbols untuk initial data download"""
        return [
            "BBCA", "BBRI", "BMRI", "BNII", "BBNI", "BTPN", "BJTM", "BBNI",
            "TLKM", "ISAT", "EXCL", "FREN", "TINS", "ANTM", "ADRO", "BUMI",
            "UNVR", "ICBP", "INDF", "MYOR", "ASII", "AUTO", "GGRM", "HMSP",
            "INCO", "PGAS", "PERT", "UNTR", "WIKA", "WSKT", "ADHI", "JSMR"
        ]
    
    def initialize_symbol_data(self, symbols: List[str], timeframes: List[str]) -> Dict:
        """Initialize data untuk multiple symbols dan timeframes"""
        results = {}
        
        for symbol in symbols:
            results[symbol] = {}
            
            for timeframe in timeframes:
                logger.info(f"Initializing data for {symbol} {timeframe}")
                result = self.update_historical_data(symbol, timeframe)
                results[symbol][timeframe] = result
                
                # Rate limiting between symbols
                time.sleep(0.5)
        
        return results
    
    def get_market_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """Get market data untuk display"""
        try:
            data = self.db.query(HistoricalData).filter(
                HistoricalData.symbol == symbol,
                HistoricalData.timeframe == timeframe
            ).order_by(HistoricalData.date.desc()).limit(limit).all()
            
            return [
                {
                    "date": row.date.isoformat(),
                    "timestamp": row.timestamp.isoformat(),
                    "open": row.open_price,
                    "high": row.high_price,
                    "low": row.low_price,
                    "close": row.close_price,
                    "volume": row.volume,
                    "adjusted_close": row.adjusted_close
                }
                for row in data
            ]
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return []
    
    def get_real_time_price(self, symbol: str) -> Optional[Dict]:
        """Get real-time price untuk symbol"""
        try:
            self._rate_limit()
            
            yf_symbol = self.get_yfinance_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "price": info.get('currentPrice'),
                "change": info.get('regularMarketChange'),
                "change_percent": info.get('regularMarketChangePercent'),
                "volume": info.get('volume'),
                "market_cap": info.get('marketCap'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time price for {symbol}: {e}")
            return None
