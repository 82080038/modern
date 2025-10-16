"""
Database Integration untuk Time Lapse Simulator
Menggunakan database asli untuk saham Indonesia
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Any, Optional
import os
import threading
import time

class DatabaseIntegration:
    """Integrasi dengan database asli untuk saham Indonesia"""
    
    def __init__(self, db_path: str = "trading_data.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.setup_database()
    
    def get_connection(self):
        """Get thread-safe database connection"""
        # Create new connection for each thread to avoid thread issues
        return sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
    
    def setup_database(self):
        """Setup database dan tabel untuk saham Indonesia"""
        try:
            conn = self.get_connection()
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
                    processing_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Insert initial data
            self._insert_initial_indonesia_stocks()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database setup error: {e}")
    
    def _insert_initial_indonesia_stocks(self):
        """Insert data saham Indonesia awal"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM indonesia_stocks")
            count = cursor.fetchone()[0]
            
            if count == 0:
                indonesia_stocks = [
                    ('BBCA', 'Bank Central Asia', 'Banking', 500000000000, 5000, 1000000),
                    ('BBRI', 'Bank Rakyat Indonesia', 'Banking', 400000000000, 4000, 800000),
                    ('BMRI', 'Bank Mandiri', 'Banking', 350000000000, 3500, 700000),
                    ('BBNI', 'Bank Negara Indonesia', 'Banking', 200000000000, 2000, 500000),
                    ('TLKM', 'Telkom Indonesia', 'Telecommunications', 300000000000, 3000, 600000),
                    ('ASII', 'Astra International', 'Automotive', 250000000000, 2500, 400000),
                    ('UNVR', 'Unilever Indonesia', 'Consumer Goods', 150000000000, 1500, 300000),
                    ('ICBP', 'Indofood CBP', 'Food & Beverage', 100000000000, 1000, 200000),
                    ('INDF', 'Indofood Sukses Makmur', 'Food & Beverage', 80000000000, 800, 150000),
                    ('GOTO', 'GoTo Group', 'Technology', 50000000000, 500, 100000)
                ]
                
                for stock in indonesia_stocks:
                    cursor.execute('''
                        INSERT INTO indonesia_stocks (symbol, name, sector, market_cap, price, volume, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (*stock, datetime.now().strftime('%Y-%m-%d')))
                
                conn.commit()
                print("Indonesian stocks data inserted successfully")
            
            conn.close()
        except Exception as e:
            print(f"Error inserting Indonesian stocks: {e}")
    
    def get_indonesia_stocks(self) -> List[Dict]:
        """Get list of Indonesian stocks"""
        try:
            conn = self.get_connection()
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
            
            conn.close()
            return stocks
        except Exception as e:
            print(f"Error getting Indonesian stocks: {e}")
            return []
    
    def get_stock_price(self, symbol: str) -> float:
        """Get current stock price"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT price FROM indonesia_stocks 
                WHERE symbol = ? 
                ORDER BY date DESC LIMIT 1
            ''', (symbol,))
            
            result = cursor.fetchone()
            if result:
                # Add some random variation to simulate price changes
                base_price = result[0]
                variation = np.random.uniform(-0.05, 0.05)  # ±5% variation
                new_price = base_price * (1 + variation)
                
                # Update price in database
                cursor.execute('''
                    UPDATE indonesia_stocks 
                    SET price = ?, date = ?
                    WHERE symbol = ?
                ''', (new_price, datetime.now().strftime('%Y-%m-%d'), symbol))
                conn.commit()
                
                conn.close()
                return new_price
            else:
                conn.close()
                return 1000.0  # Default price
        except Exception as e:
            print(f"ERROR: Failed to get stock price for {symbol}: {e}")
            return 1000.0  # Default price
    
    def save_trading_decision(self, session_id: str, symbol: str, action: str, 
                            shares: int, price: float, confidence: float, reason: str):
        """Save trading decision to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trading_decisions 
                (session_id, symbol, action, shares, price, confidence, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, symbol, action, shares, price, confidence, reason))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"ERROR: Failed to save trading decision: {e}")
    
    def save_performance_metrics(self, session_id: str, module_name: str, 
                               accuracy: float, processing_speed: float, 
                               reliability: float, efficiency: float, 
                               error_rate: float, processing_time: float):
        """Save performance metrics to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (session_id, module_name, accuracy, processing_speed, 
                 reliability, efficiency, error_rate, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, module_name, accuracy, processing_speed, 
                  reliability, efficiency, error_rate, processing_time))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"ERROR: Failed to save performance metrics: {e}")
    
    def get_trading_history(self, limit: int = 100) -> List[Dict]:
        """Get trading history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, symbol, action, shares, price, confidence, reason, timestamp
                FROM trading_decisions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'session_id': row[0],
                    'symbol': row[1],
                    'action': row[2],
                    'shares': row[3],
                    'price': row[4],
                    'confidence': row[5],
                    'reason': row[6],
                    'timestamp': row[7]
                })
            
            conn.close()
            return history
        except Exception as e:
            print(f"Error getting trading history: {e}")
            return []
