"""
Database Schema Checker
======================

Script untuk memeriksa struktur database MySQL scalper.

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
from mysql.connector import Error

def check_database_schema():
    """Check database schema and table structure"""
    try:
        # Database configuration
        db_config = {
            'host': 'localhost',
            'database': 'scalper',
            'user': 'root',
            'password': '',  # Sesuaikan dengan password MySQL Anda
            'port': 3306
        }
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("Database Connection Successful!")
        print("=" * 60)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in database:")
        for table in tables:
            print(f"- {table[0]}")
        
        print("\n" + "=" * 60)
        
        # Check market_data table structure
        print("Checking market_data table structure...")
        cursor.execute("DESCRIBE market_data")
        columns = cursor.fetchall()
        
        print("\nmarket_data table columns:")
        for column in columns:
            print(f"- {column[0]} ({column[1]})")
        
        print("\n" + "=" * 60)
        
        # Get sample data
        print("Sample data from market_data table:")
        cursor.execute("SELECT * FROM market_data LIMIT 5")
        sample_data = cursor.fetchall()
        
        for row in sample_data:
            print(f"Row: {row}")
        
        print("\n" + "=" * 60)
        
        # Get unique symbols
        print("Unique symbols in market_data:")
        cursor.execute("SELECT DISTINCT symbol FROM market_data LIMIT 10")
        symbols = cursor.fetchall()
        
        for symbol in symbols:
            print(f"- {symbol[0]}")
        
        print("\n" + "=" * 60)
        
        # Get date range
        print("Date range in market_data:")
        cursor.execute("SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date FROM market_data")
        date_range = cursor.fetchone()
        
        print(f"Date range: {date_range[0]} to {date_range[1]}")
        
        print("\n" + "=" * 60)
        
        # Get record count
        print("Record count in market_data:")
        cursor.execute("SELECT COUNT(*) FROM market_data")
        count = cursor.fetchone()
        
        print(f"Total records: {count[0]}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_database_schema()
