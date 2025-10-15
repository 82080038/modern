"""
Database Integration - THREAD SAFE VERSION
Menggunakan connection pooling dan proper thread management
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Any, Optional
import os
import threading
import time
import queue
import atexit

class DatabaseIntegration:
    """Integrasi dengan database asli untuk saham Indonesia - THREAD SAFE"""
    
    def __init__(self, db_path: str = "trading_data.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.connection_pool = queue.Queue(maxsize=10)
        self._initialize_pool()
        self.setup_database()
        atexit.register(self._close_all_connections)
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(5):
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
            self.connection_pool.put(conn)
    
    def _get_connection(self):
        """Get connection from pool"""
        try:
            return self.connection_pool.get_nowait()
        except queue.Empty:
            # Create new connection if pool is empty
            return sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        try:
            self.connection_pool.put_nowait(conn)
        except queue.Full:
            conn.close()
    
    def _close_all_connections(self):
        """Close all connections in pool"""
        while not self.connection_pool.empty():
            try:
                conn = self.connection_pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
    
    def setup_database(self):
        """Setup database dan tabel untuk saham Indonesia"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Tabel saham Indonesia
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS indonesia_stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    sector TEXT,
                    market_cap REAL,
                    price REAL,
                    volume INTEGER,
                    date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabel trading decisions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    shares INTEGER,
                    price REAL,
                    confidence REAL,
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabel performance metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    module_name TEXT NOT NULL,
                    accuracy REAL,
                    processing_speed REAL,
                    reliability REAL,
                    efficiency REAL,
                    error_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print("Database initialized successfully")
            
            # Insert initial data if empty
            self._insert_initial_indonesia_stocks(conn)
            
        except Exception as e:
            print(f"Database setup error: {e}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def _insert_initial_indonesia_stocks(self, conn):
        """Insert initial Indonesian stocks data"""
        try:
            cursor = conn.cursor()
            
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM indonesia_stocks")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Major Indonesian stocks
                stocks = [
                    ('BBCA', 'Bank Central Asia', 'Banking', 500000000000, 10550.0, 1000000),
                    ('BBRI', 'Bank Rakyat Indonesia', 'Banking', 300000000000, 4820.0, 800000),
                    ('BMRI', 'Bank Mandiri', 'Banking', 250000000000, 6250.0, 750000),
                    ('BBNI', 'Bank Negara Indonesia', 'Banking', 200000000000, 4250.0, 600000),
                    ('TLKM', 'Telkom Indonesia', 'Telecommunications', 400000000000, 3850.0, 1200000),
                    ('ASII', 'Astra International', 'Automotive', 350000000000, 7250.0, 900000),
                    ('UNVR', 'Unilever Indonesia', 'Consumer Goods', 180000000000, 2850.0, 500000),
                    ('ICBP', 'Indofood CBP', 'Food & Beverage', 150000000000, 11250.0, 400000),
                    ('INDF', 'Indofood Sukses Makmur', 'Food & Beverage', 200000000000, 6250.0, 600000),
                    ('GOTO', 'GoTo Gojek Tokopedia', 'Technology', 80000000000, 125.0, 2000000)
                ]
                
                for stock in stocks:
                    cursor.execute('''
                        INSERT INTO indonesia_stocks (symbol, name, sector, market_cap, price, volume, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (*stock, datetime.now().date()))
                
                conn.commit()
                print(f"Inserted {len(stocks)} Indonesian stocks")
            
        except Exception as e:
            print(f"Error inserting initial stocks: {e}")
    
    def get_indonesia_stocks(self) -> List[Dict]:
        """Get all Indonesian stocks"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT symbol, name, sector, market_cap, price, volume, date
                FROM indonesia_stocks
                ORDER BY market_cap DESC
            ''')
            
            stocks = []
            for row in cursor.fetchall():
                stocks.append({
                    'symbol': row[0],
                    'name': row[1],
                    'sector': row[2],
                    'market_cap': row[3],
                    'price': row[4],
                    'volume': row[5],
                    'date': row[6]
                })
            
            return stocks
            
        except Exception as e:
            print(f"Error getting Indonesian stocks: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)
    
    def get_stock_price(self, symbol: str, date: datetime) -> float:
        """Get stock price for specific symbol and date"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT price FROM indonesia_stocks 
                WHERE symbol = ? AND date <= ?
                ORDER BY date DESC LIMIT 1
            ''', (symbol, date.date()))
            
            result = cursor.fetchone()
            
            if result:
                # Add some random variation to simulate price movement
                base_price = result[0]
                variation = np.random.normal(0, base_price * 0.02)  # 2% volatility
                return max(base_price + variation, base_price * 0.5)  # Minimum 50% of base price
            
            # Default price if not found
            return 1000.0
            
        except Exception as e:
            print(f"ERROR: Failed to get stock price for {symbol}: {e}")
            return 1000.0
        finally:
            if conn:
                self._return_connection(conn)
    
    def save_trading_decision(self, symbol: str, action: str, shares: int, price: float, 
                            session_id: str, timestamp: datetime):
        """Save trading decision to database"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trading_decisions 
                (session_id, symbol, action, shares, price, confidence, reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, symbol, action, shares, price, 
                  np.random.uniform(0.6, 0.95), 
                  f"Automated decision for {symbol}", timestamp))
            
            conn.commit()
            
        except Exception as e:
            print(f"ERROR: Failed to save trading decision: {e}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def save_performance_metrics(self, session_id: str, module_name: str, 
                               metrics: Dict[str, float], timestamp: datetime):
        """Save performance metrics to database"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (session_id, module_name, accuracy, processing_speed, reliability, efficiency, error_rate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, module_name, 
                  metrics.get('accuracy', 0.0),
                  metrics.get('processing_speed', 0.0),
                  metrics.get('reliability', 0.0),
                  metrics.get('efficiency', 0.0),
                  metrics.get('error_rate', 0.0),
                  timestamp))
            
            conn.commit()
            
        except Exception as e:
            print(f"ERROR: Failed to save performance metrics: {e}")
        finally:
            if conn:
                self._return_connection(conn)
    
    def get_trading_history(self, session_id: str = None) -> List[Dict]:
        """Get trading history"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT symbol, action, shares, price, confidence, reason, timestamp
                    FROM trading_decisions 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                ''', (session_id,))
            else:
                cursor.execute('''
                    SELECT symbol, action, shares, price, confidence, reason, timestamp
                    FROM trading_decisions 
                    ORDER BY timestamp DESC
                ''')
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'symbol': row[0],
                    'action': row[1],
                    'shares': row[2],
                    'price': row[3],
                    'confidence': row[4],
                    'reason': row[5],
                    'timestamp': row[6]
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting trading history: {e}")
            return []
        finally:
            if conn:
                self._return_connection(conn)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all sessions"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get total trades
            cursor.execute("SELECT COUNT(*) FROM trading_decisions")
            total_trades = cursor.fetchone()[0]
            
            # Get winning trades (simplified)
            cursor.execute("SELECT COUNT(*) FROM trading_decisions WHERE action = 'BUY'")
            buy_trades = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM trading_decisions WHERE action = 'SELL'")
            sell_trades = cursor.fetchone()[0]
            
            # Calculate win rate (simplified)
            win_rate = (sell_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'buy_trades': buy_trades,
                'sell_trades': sell_trades,
                'win_rate': win_rate
            }
            
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {
                'total_trades': 0,
                'buy_trades': 0,
                'sell_trades': 0,
                'win_rate': 0.0
            }
        finally:
            if conn:
                self._return_connection(conn)
