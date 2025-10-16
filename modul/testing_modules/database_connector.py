#!/usr/bin/env python3
"""
Database Connector - Konektor untuk akses data historis
======================================================

Konektor ini mengakses database scalper untuk:
1. Mengambil data historis
2. Mengambil data prediksi
3. Membandingkan akurasi prediksi
4. Time lapse simulation

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import sqlite3
import mysql.connector
from urllib.parse import urlparse

class DatabaseConnector:
    """Konektor untuk akses database scalper"""
    
    def __init__(self, db_config: Dict[str, Any] = None):
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'scalper',
            'port': 3306
        }
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """Koneksi ke database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                port=self.db_config['port']
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print(f"✅ Connected to database: {self.db_config['database']}")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Tutup koneksi database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Database connection closed")
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Ambil data historis untuk symbol tertentu"""
        
        query = """
        SELECT * FROM historical_data 
        WHERE symbol = %s 
        AND date BETWEEN %s AND %s 
        ORDER BY date ASC
        """
        
        try:
            self.cursor.execute(query, (symbol, start_date, end_date))
            data = self.cursor.fetchall()
            print(f"📊 Retrieved {len(data)} historical records for {symbol}")
            return data
        except Exception as e:
            print(f"❌ Error getting historical data: {str(e)}")
            return []
    
    def get_predictions(self, symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Ambil data prediksi untuk symbol tertentu"""
        
        query = """
        SELECT * FROM predictions 
        WHERE symbol = %s 
        AND prediction_date BETWEEN %s AND %s 
        ORDER BY prediction_date ASC
        """
        
        try:
            self.cursor.execute(query, (symbol, start_date, end_date))
            data = self.cursor.fetchall()
            print(f"🔮 Retrieved {len(data)} prediction records for {symbol}")
            return data
        except Exception as e:
            print(f"❌ Error getting predictions: {str(e)}")
            return []
    
    def get_available_symbols(self) -> List[str]:
        """Ambil daftar symbol yang tersedia"""
        
        query = "SELECT DISTINCT symbol FROM historical_data ORDER BY symbol"
        
        try:
            self.cursor.execute(query)
            symbols = [row['symbol'] for row in self.cursor.fetchall()]
            print(f"📈 Found {len(symbols)} symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
            return symbols
        except Exception as e:
            print(f"❌ Error getting symbols: {str(e)}")
            return []
    
    def get_date_range(self, symbol: str) -> Tuple[str, str]:
        """Ambil range tanggal untuk symbol tertentu"""
        
        query = """
        SELECT MIN(date) as min_date, MAX(date) as max_date 
        FROM historical_data 
        WHERE symbol = %s
        """
        
        try:
            self.cursor.execute(query, (symbol,))
            result = self.cursor.fetchone()
            if result:
                return result['min_date'], result['max_date']
            return None, None
        except Exception as e:
            print(f"❌ Error getting date range: {str(e)}")
            return None, None
    
    def calculate_prediction_accuracy(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Hitung akurasi prediksi untuk periode tertentu"""
        
        # Ambil data historis
        historical_data = self.get_historical_data(symbol, start_date, end_date)
        
        # Ambil data prediksi
        predictions = self.get_predictions(symbol, start_date, end_date)
        
        if not historical_data or not predictions:
            return {
                'symbol': symbol,
                'period': f"{start_date} to {end_date}",
                'total_predictions': 0,
                'accuracy': 0.0,
                'error': 'No data available'
            }
        
        # Buat dictionary untuk lookup data historis
        hist_dict = {row['date']: row for row in historical_data}
        
        # Hitung akurasi
        correct_predictions = 0
        total_predictions = 0
        prediction_details = []
        
        for pred in predictions:
            pred_date = pred['prediction_date']
            actual_date = pred_date + timedelta(days=1)  # Asumsi prediksi untuk hari berikutnya
            
            if actual_date.strftime('%Y-%m-%d') in hist_dict:
                actual_data = hist_dict[actual_date.strftime('%Y-%m-%d')]
                
                # Bandingkan prediksi dengan data aktual
                predicted_direction = pred.get('predicted_direction', 'up')  # up/down
                actual_price = actual_data.get('close_price', 0)
                previous_price = hist_dict.get(pred_date.strftime('%Y-%m-%d'), {}).get('close_price', 0)
                
                if actual_price > previous_price:
                    actual_direction = 'up'
                else:
                    actual_direction = 'down'
                
                is_correct = predicted_direction == actual_direction
                if is_correct:
                    correct_predictions += 1
                
                total_predictions += 1
                
                prediction_details.append({
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'predicted_direction': predicted_direction,
                    'actual_direction': actual_direction,
                    'is_correct': is_correct,
                    'actual_price': actual_price,
                    'previous_price': previous_price
                })
        
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        return {
            'symbol': symbol,
            'period': f"{start_date} to {end_date}",
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'accuracy': accuracy,
            'prediction_details': prediction_details
        }
    
    def get_module_performance(self, module_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Hitung performa modul berdasarkan prediksi"""
        
        # Ambil semua symbol
        symbols = self.get_available_symbols()
        
        module_performance = {
            'module_name': module_name,
            'period': f"{start_date} to {end_date}",
            'total_symbols': len(symbols),
            'symbols_analyzed': 0,
            'overall_accuracy': 0.0,
            'symbol_performance': [],
            'best_symbol': None,
            'worst_symbol': None,
            'average_accuracy': 0.0
        }
        
        symbol_accuracies = []
        
        for symbol in symbols:
            print(f"🔍 Analyzing {module_name} performance for {symbol}...")
            
            accuracy_data = self.calculate_prediction_accuracy(symbol, start_date, end_date)
            
            if accuracy_data['total_predictions'] > 0:
                module_performance['symbols_analyzed'] += 1
                symbol_accuracies.append(accuracy_data['accuracy'])
                
                module_performance['symbol_performance'].append({
                    'symbol': symbol,
                    'accuracy': accuracy_data['accuracy'],
                    'total_predictions': accuracy_data['total_predictions'],
                    'correct_predictions': accuracy_data['correct_predictions']
                })
        
        if symbol_accuracies:
            module_performance['average_accuracy'] = sum(symbol_accuracies) / len(symbol_accuracies)
            module_performance['overall_accuracy'] = module_performance['average_accuracy']
            
            # Find best and worst performing symbols
            best_perf = max(module_performance['symbol_performance'], key=lambda x: x['accuracy'])
            worst_perf = min(module_performance['symbol_performance'], key=lambda x: x['accuracy'])
            
            module_performance['best_symbol'] = {
                'symbol': best_perf['symbol'],
                'accuracy': best_perf['accuracy']
            }
            
            module_performance['worst_symbol'] = {
                'symbol': worst_perf['symbol'],
                'accuracy': worst_perf['accuracy']
            }
        
        return module_performance
    
    def save_performance_data(self, performance_data: Dict[str, Any], filename: str = None) -> str:
        """Simpan data performa ke file"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"module_performance_{performance_data['module_name']}_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(performance_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Performance data saved to: {filepath}")
        return filepath

def main():
    """Test database connector"""
    
    print("🔌 DATABASE CONNECTOR - Testing Database Access")
    print("=" * 50)
    
    # Initialize connector
    connector = DatabaseConnector()
    
    # Connect to database
    if not connector.connect():
        print("❌ Cannot connect to database. Please check configuration.")
        return
    
    try:
        # Test basic functionality
        print("\n📊 Testing database functionality...")
        
        # Get available symbols
        symbols = connector.get_available_symbols()
        if symbols:
            print(f"✅ Found {len(symbols)} symbols")
            
            # Test with first symbol
            test_symbol = symbols[0]
            print(f"🔍 Testing with symbol: {test_symbol}")
            
            # Get date range
            min_date, max_date = connector.get_date_range(test_symbol)
            if min_date and max_date:
                print(f"📅 Date range: {min_date} to {max_date}")
                
                # Test historical data
                hist_data = connector.get_historical_data(test_symbol, min_date, max_date)
                print(f"📊 Historical data: {len(hist_data)} records")
                
                # Test predictions
                pred_data = connector.get_predictions(test_symbol, min_date, max_date)
                print(f"🔮 Predictions: {len(pred_data)} records")
                
                # Test accuracy calculation
                if hist_data and pred_data:
                    accuracy = connector.calculate_prediction_accuracy(test_symbol, min_date, max_date)
                    print(f"🎯 Accuracy: {accuracy['accuracy']:.2f}%")
        
        print("\n✅ Database connector test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    finally:
        connector.disconnect()

if __name__ == "__main__":
    main()
