"""
Volatility Fix Analysis
======================

Script untuk menganalisis dan memperbaiki masalah NaN/infinity dalam volatility calculation.

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np

def analyze_volatility_issues():
    """Analyze volatility calculation issues"""
    try:
        # Database configuration
        db_config = {
            'host': 'localhost',
            'database': 'scalper',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("Analyzing Volatility Issues...")
        print("=" * 60)
        
        # Get sample data for analysis
        symbols = ['BBCA.JK', 'TLKM.JK', 'UNVR.JK', 'ASII.JK', 'BMRI.JK']
        
        for symbol in symbols:
            print(f"\nAnalyzing {symbol}:")
            
            # Get data
            query = """
            SELECT date, close
            FROM market_data 
            WHERE symbol = %s 
            ORDER BY date
            LIMIT 10
            """
            
            cursor.execute(query, (symbol,))
            data = cursor.fetchall()
            
            if data:
                df = pd.DataFrame(data, columns=['date', 'close'])
                df['close'] = df['close'].astype(float)
                
                print(f"Sample prices: {df['close'].tolist()}")
                
                # Calculate returns
                returns = df['close'].pct_change().dropna()
                print(f"Returns: {returns.tolist()}")
                
                # Calculate volatility
                volatility = returns.std()
                print(f"Volatility: {volatility}")
                
                # Check for issues
                if np.isnan(volatility) or np.isinf(volatility):
                    print(f"❌ ISSUE: Volatility is {volatility}")
                else:
                    print(f"✅ OK: Volatility is {volatility}")
                
                # Check for zero volatility
                if volatility == 0:
                    print(f"❌ ISSUE: Zero volatility detected")
                
                # Check for very small volatility
                if volatility < 0.001:
                    print(f"⚠️  WARNING: Very small volatility: {volatility}")
            else:
                print(f"No data for {symbol}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error: {e}")
        return False

def test_volatility_fixes():
    """Test different volatility calculation methods"""
    try:
        print("\n" + "=" * 60)
        print("Testing Volatility Fixes...")
        print("=" * 60)
        
        # Simulate problematic data
        test_data = {
            'constant_prices': [100, 100, 100, 100, 100],  # Zero volatility
            'single_price': [100],  # Single data point
            'normal_prices': [100, 102, 101, 103, 105],  # Normal volatility
            'extreme_prices': [100, 0.001, 100, 0.001, 100]  # Extreme volatility
        }
        
        for test_name, prices in test_data.items():
            print(f"\nTesting {test_name}: {prices}")
            
            df = pd.DataFrame({'close': prices})
            returns = df['close'].pct_change().dropna()
            
            print(f"Returns: {returns.tolist()}")
            
            # Method 1: Standard deviation
            vol1 = returns.std()
            print(f"Method 1 (std): {vol1}")
            
            # Method 2: Handle NaN/Inf
            vol2 = returns.std()
            if np.isnan(vol2) or np.isinf(vol2):
                vol2 = 0.01  # Default volatility
            print(f"Method 2 (with NaN fix): {vol2}")
            
            # Method 3: Minimum volatility threshold
            vol3 = max(returns.std(), 0.01)  # Minimum 1% volatility
            print(f"Method 3 (min threshold): {vol3}")
            
            # Method 4: Robust volatility (using median absolute deviation)
            if len(returns) > 1:
                vol4 = np.median(np.abs(returns - returns.median())) * 1.4826
            else:
                vol4 = 0.01
            print(f"Method 4 (robust): {vol4}")
            
            # Method 5: Equal weight fallback
            if np.isnan(vol1) or np.isinf(vol1) or vol1 == 0:
                vol5 = 0.01  # Equal weight fallback
            else:
                vol5 = vol1
            print(f"Method 5 (fallback): {vol5}")
        
        return True
        
    except Exception as e:
        print(f"Error in testing: {e}")
        return False

if __name__ == "__main__":
    analyze_volatility_issues()
    test_volatility_fixes()
