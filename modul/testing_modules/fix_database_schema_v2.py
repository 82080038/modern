#!/usr/bin/env python3
"""
Fix Database Schema V2
=====================

Script untuk memperbaiki schema database dengan handling unread result.

Author: AI Assistant
Date: 2025-01-16
"""

import sys
import os
import json
import time
import mysql.connector
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def fix_database_schema_v2():
    """Fix database schema with proper error handling"""
    print("FIXING DATABASE SCHEMA V2")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Fix results
    fix_results = {
        'test_type': 'fix_database_schema_v2',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'schema_fixes': [],
        'tables_created': [],
        'columns_added': [],
        'errors': [],
        'summary': {}
    }
    
    # Connect to database
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='scalper',
            port=3306
        )
        cursor = connection.cursor()
        print("[PASS] Database connection established")
        fix_results['database_connection'] = True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        fix_results['errors'].append(f'database_connection_error: {e}')
        return fix_results
    
    # Step 1: Fix market_data table
    print("\n1. FIXING MARKET_DATA TABLE")
    print("-" * 60)
    
    try:
        # Check if date column exists, if not add it
        cursor.execute("SHOW COLUMNS FROM market_data LIKE 'date'")
        result = cursor.fetchone()
        if not result:
            cursor.execute("ALTER TABLE market_data ADD COLUMN date DATE AFTER timestamp")
            fix_results['columns_added'].append("Added date column to market_data")
            print("   [PASS] Added date column to market_data")
        else:
            print("   [INFO] Date column already exists in market_data")
        
        # Check if date column has default value
        cursor.execute("ALTER TABLE market_data MODIFY COLUMN date DATE DEFAULT (CURDATE())")
        fix_results['schema_fixes'].append("Set default value for date column in market_data")
        print("   [PASS] Set default value for date column in market_data")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['errors'].append(f"Error fixing market_data table: {e}")
        print(f"   [ERROR] Failed to fix market_data table: {e}")
    
    # Step 2: Fix fundamental_data table
    print("\n2. FIXING FUNDAMENTAL_DATA TABLE")
    print("-" * 60)
    
    try:
        # Add missing columns to fundamental_data
        columns_to_add = [
            "market_cap BIGINT",
            "enterprise_value BIGINT", 
            "revenue BIGINT",
            "profit_margin DECIMAL(5,4)",
            "dividend_yield DECIMAL(5,4)",
            "beta DECIMAL(5,4)",
            "sector VARCHAR(100)",
            "industry VARCHAR(100)"
        ]
        
        for column_def in columns_to_add:
            column_name = column_def.split()[0]
            try:
                cursor.execute(f"ALTER TABLE fundamental_data ADD COLUMN {column_def}")
                fix_results['columns_added'].append(f"Added {column_name} column to fundamental_data")
                print(f"   [PASS] Added {column_name} column to fundamental_data")
            except mysql.connector.Error as e:
                if "Duplicate column name" in str(e):
                    print(f"   [INFO] Column {column_name} already exists in fundamental_data")
                else:
                    raise e
        
        fix_results['schema_fixes'].append("Added missing columns to fundamental_data")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['errors'].append(f"Error fixing fundamental_data table: {e}")
        print(f"   [ERROR] Failed to fix fundamental_data table: {e}")
    
    # Step 3: Fix sentiment_data table
    print("\n3. FIXING SENTIMENT_DATA TABLE")
    print("-" * 60)
    
    try:
        # Check if sentiment_data table exists
        cursor.execute("SHOW TABLES LIKE 'sentiment_data'")
        result = cursor.fetchone()
        if not result:
            # Create sentiment_data table
            cursor.execute("""
                CREATE TABLE sentiment_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    title TEXT,
                    summary TEXT,
                    publisher VARCHAR(100),
                    published_at TIMESTAMP,
                    sentiment_score DECIMAL(5,4),
                    confidence DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_symbol (symbol),
                    INDEX idx_published_at (published_at)
                )
            """)
            fix_results['tables_created'].append("Created sentiment_data table")
            print("   [PASS] Created sentiment_data table")
        else:
            print("   [INFO] sentiment_data table already exists")
        
        # Add missing columns if needed
        columns_to_add = [
            "title TEXT",
            "summary TEXT", 
            "publisher VARCHAR(100)",
            "published_at TIMESTAMP",
            "sentiment_score DECIMAL(5,4)",
            "confidence DECIMAL(5,4)"
        ]
        
        for column_def in columns_to_add:
            column_name = column_def.split()[0]
            try:
                cursor.execute(f"ALTER TABLE sentiment_data ADD COLUMN {column_def}")
                fix_results['columns_added'].append(f"Added {column_name} column to sentiment_data")
                print(f"   [PASS] Added {column_name} column to sentiment_data")
            except mysql.connector.Error as e:
                if "Duplicate column name" in str(e):
                    print(f"   [INFO] Column {column_name} already exists in sentiment_data")
                else:
                    raise e
        
        fix_results['schema_fixes'].append("Fixed sentiment_data table")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['errors'].append(f"Error fixing sentiment_data table: {e}")
        print(f"   [ERROR] Failed to fix sentiment_data table: {e}")
    
    # Step 4: Fix news_sentiment table
    print("\n4. FIXING NEWS_SENTIMENT TABLE")
    print("-" * 60)
    
    try:
        # Check if news_sentiment table exists
        cursor.execute("SHOW TABLES LIKE 'news_sentiment'")
        result = cursor.fetchone()
        if not result:
            # Create news_sentiment table
            cursor.execute("""
                CREATE TABLE news_sentiment (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    title TEXT,
                    summary TEXT,
                    publisher VARCHAR(100),
                    published_at TIMESTAMP,
                    sentiment_score DECIMAL(5,4),
                    confidence DECIMAL(5,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_symbol (symbol),
                    INDEX idx_published_at (published_at)
                )
            """)
            fix_results['tables_created'].append("Created news_sentiment table")
            print("   [PASS] Created news_sentiment table")
        else:
            print("   [INFO] news_sentiment table already exists")
        
        fix_results['schema_fixes'].append("Fixed news_sentiment table")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['errors'].append(f"Error fixing news_sentiment table: {e}")
        print(f"   [ERROR] Failed to fix news_sentiment table: {e}")
    
    # Step 5: Fix historical_ohlcv_daily table
    print("\n5. FIXING HISTORICAL_OHLCV_DAILY TABLE")
    print("-" * 60)
    
    try:
        # Check if unique constraint exists
        cursor.execute("SHOW INDEX FROM historical_ohlcv_daily WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        if not result:
            # Add unique constraint
            cursor.execute("ALTER TABLE historical_ohlcv_daily ADD CONSTRAINT unique_symbol_date UNIQUE (symbol, date)")
            fix_results['schema_fixes'].append("Added unique constraint to historical_ohlcv_daily")
            print("   [PASS] Added unique constraint to historical_ohlcv_daily")
        else:
            print("   [INFO] Unique constraint already exists in historical_ohlcv_daily")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['errors'].append(f"Error fixing historical_ohlcv_daily table: {e}")
        print(f"   [ERROR] Failed to fix historical_ohlcv_daily table: {e}")
    
    # Step 6: Fix technical_indicators table
    print("\n6. FIXING TECHNICAL_INDICATORS TABLE")
    print("-" * 60)
    
    try:
        # Check if unique constraint exists
        cursor.execute("SHOW INDEX FROM technical_indicators WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        if not result:
            # Add unique constraint
            cursor.execute("ALTER TABLE technical_indicators ADD CONSTRAINT unique_symbol_date UNIQUE (symbol, date)")
            fix_results['schema_fixes'].append("Added unique constraint to technical_indicators")
            print("   [PASS] Added unique constraint to technical_indicators")
        else:
            print("   [INFO] Unique constraint already exists in technical_indicators")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['errors'].append(f"Error fixing technical_indicators table: {e}")
        print(f"   [ERROR] Failed to fix technical_indicators table: {e}")
    
    # Step 7: Fix fundamental_data table constraints
    print("\n7. FIXING FUNDAMENTAL_DATA TABLE CONSTRAINTS")
    print("-" * 60)
    
    try:
        # Check if unique constraint exists
        cursor.execute("SHOW INDEX FROM fundamental_data WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        if not result:
            # Add unique constraint
            cursor.execute("ALTER TABLE fundamental_data ADD CONSTRAINT unique_symbol_date UNIQUE (symbol, date)")
            fix_results['schema_fixes'].append("Added unique constraint to fundamental_data")
            print("   [PASS] Added unique constraint to fundamental_data")
        else:
            print("   [INFO] Unique constraint already exists in fundamental_data")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['errors'].append(f"Error fixing fundamental_data table constraints: {e}")
        print(f"   [ERROR] Failed to fix fundamental_data table constraints: {e}")
    
    # Commit all changes
    try:
        connection.commit()
        print("\n[PASS] All changes committed to database")
    except Exception as e:
        print(f"\n[ERROR] Failed to commit changes: {e}")
        fix_results['errors'].append(f"Commit error: {e}")
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("[PASS] Database connection closed")
    
    # Generate summary
    fix_results['summary'] = {
        'schema_fixes_applied': len(fix_results['schema_fixes']),
        'tables_created': len(fix_results['tables_created']),
        'columns_added': len(fix_results['columns_added']),
        'errors_encountered': len(fix_results['errors']),
        'fix_success_rate': ((len(fix_results['schema_fixes']) + len(fix_results['tables_created']) + len(fix_results['columns_added'])) / (len(fix_results['schema_fixes']) + len(fix_results['tables_created']) + len(fix_results['columns_added']) + len(fix_results['errors'])) * 100) if (len(fix_results['schema_fixes']) + len(fix_results['tables_created']) + len(fix_results['columns_added']) + len(fix_results['errors'])) > 0 else 0
    }
    
    # Generate comprehensive report
    generate_schema_fix_report(fix_results)
    
    return fix_results

def generate_schema_fix_report(fix_results: Dict[str, Any]) -> None:
    """Generate schema fix report"""
    print("\nDATABASE SCHEMA FIX REPORT")
    print("=" * 80)
    
    # Schema fixes
    schema_fixes = fix_results.get('schema_fixes', [])
    print(f"Schema Fixes Applied: {len(schema_fixes)}")
    for fix in schema_fixes:
        print(f"  - {fix}")
    
    # Tables created
    tables_created = fix_results.get('tables_created', [])
    print(f"\nTables Created: {len(tables_created)}")
    for table in tables_created:
        print(f"  - {table}")
    
    # Columns added
    columns_added = fix_results.get('columns_added', [])
    print(f"\nColumns Added: {len(columns_added)}")
    for column in columns_added:
        print(f"  - {column}")
    
    # Errors
    errors = fix_results.get('errors', [])
    if errors:
        print(f"\nErrors Encountered: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    
    # Summary
    summary = fix_results.get('summary', {})
    print(f"\nSummary:")
    print(f"  Schema Fixes Applied: {summary.get('schema_fixes_applied', 0)}")
    print(f"  Tables Created: {summary.get('tables_created', 0)}")
    print(f"  Columns Added: {summary.get('columns_added', 0)}")
    print(f"  Errors Encountered: {summary.get('errors_encountered', 0)}")
    print(f"  Fix Success Rate: {summary.get('fix_success_rate', 0):.1f}%")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"database_schema_fix_v2_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(fix_results, f, indent=2)
    
    print(f"\nSchema fix results saved to: {results_file}")
    print(f"Schema fix completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    fix_database_schema_v2()
