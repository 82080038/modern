#!/usr/bin/env python3
"""
Verify Database Schema
=====================

Script untuk memverifikasi bahwa database schema sudah diperbaiki
sesuai dengan kebutuhan untuk Yahoo Finance data fetching.

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

def verify_database_schema():
    """Verify database schema"""
    print("VERIFYING DATABASE SCHEMA")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Verification results
    verification_results = {
        'test_type': 'verify_database_schema',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'table_verification': {},
        'column_verification': {},
        'constraint_verification': {},
        'schema_status': {},
        'recommendations': [],
        'errors': []
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
        verification_results['database_connection'] = True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        verification_results['errors'].append(f'database_connection_error: {e}')
        return verification_results
    
    # Step 1: Verify required tables exist
    print("\n1. VERIFYING REQUIRED TABLES")
    print("-" * 60)
    
    required_tables = [
        'market_data',
        'historical_ohlcv_daily',
        'fundamental_data',
        'sentiment_data',
        'news_sentiment',
        'technical_indicators',
        'orders',
        'trades'
    ]
    
    table_verification = {}
    for table in required_tables:
        try:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            table_verification[table] = result is not None
            status = "EXISTS" if result else "MISSING"
            print(f"   {table}: {status}")
        except Exception as e:
            table_verification[table] = False
            print(f"   {table}: ERROR - {e}")
            verification_results['errors'].append(f"Error checking table {table}: {e}")
    
    verification_results['table_verification'] = table_verification
    
    # Step 2: Verify market_data table columns
    print("\n2. VERIFYING MARKET_DATA TABLE COLUMNS")
    print("-" * 60)
    
    try:
        cursor.execute("DESCRIBE market_data")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        required_columns = ['symbol', 'timestamp', 'date', 'price', 'volume', 'high', 'low', 'open', 'close']
        market_data_columns = {}
        
        for col in required_columns:
            market_data_columns[col] = col in column_names
            status = "EXISTS" if col in column_names else "MISSING"
            print(f"   {col}: {status}")
        
        verification_results['column_verification']['market_data'] = market_data_columns
        
    except Exception as e:
        print(f"   [ERROR] Failed to verify market_data columns: {e}")
        verification_results['errors'].append(f"Error verifying market_data columns: {e}")
    
    # Step 3: Verify historical_ohlcv_daily table columns
    print("\n3. VERIFYING HISTORICAL_OHLCV_DAILY TABLE COLUMNS")
    print("-" * 60)
    
    try:
        cursor.execute("DESCRIBE historical_ohlcv_daily")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        required_columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        historical_columns = {}
        
        for col in required_columns:
            historical_columns[col] = col in column_names
            status = "EXISTS" if col in column_names else "MISSING"
            print(f"   {col}: {status}")
        
        verification_results['column_verification']['historical_ohlcv_daily'] = historical_columns
        
    except Exception as e:
        print(f"   [ERROR] Failed to verify historical_ohlcv_daily columns: {e}")
        verification_results['errors'].append(f"Error verifying historical_ohlcv_daily columns: {e}")
    
    # Step 4: Verify fundamental_data table columns
    print("\n4. VERIFYING FUNDAMENTAL_DATA TABLE COLUMNS")
    print("-" * 60)
    
    try:
        cursor.execute("DESCRIBE fundamental_data")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        required_columns = ['symbol', 'date', 'pe_ratio', 'pb_ratio', 'roe', 'roa', 'debt_to_equity', 
                          'current_ratio', 'market_cap', 'enterprise_value', 'revenue', 'profit_margin', 
                          'dividend_yield', 'beta', 'sector', 'industry']
        fundamental_columns = {}
        
        for col in required_columns:
            fundamental_columns[col] = col in column_names
            status = "EXISTS" if col in column_names else "MISSING"
            print(f"   {col}: {status}")
        
        verification_results['column_verification']['fundamental_data'] = fundamental_columns
        
    except Exception as e:
        print(f"   [ERROR] Failed to verify fundamental_data columns: {e}")
        verification_results['errors'].append(f"Error verifying fundamental_data columns: {e}")
    
    # Step 5: Verify sentiment_data table columns
    print("\n5. VERIFYING SENTIMENT_DATA TABLE COLUMNS")
    print("-" * 60)
    
    try:
        cursor.execute("DESCRIBE sentiment_data")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        required_columns = ['symbol', 'title', 'summary', 'publisher', 'published_at', 'sentiment_score', 'confidence']
        sentiment_columns = {}
        
        for col in required_columns:
            sentiment_columns[col] = col in column_names
            status = "EXISTS" if col in column_names else "MISSING"
            print(f"   {col}: {status}")
        
        verification_results['column_verification']['sentiment_data'] = sentiment_columns
        
    except Exception as e:
        print(f"   [ERROR] Failed to verify sentiment_data columns: {e}")
        verification_results['errors'].append(f"Error verifying sentiment_data columns: {e}")
    
    # Step 6: Verify unique constraints
    print("\n6. VERIFYING UNIQUE CONSTRAINTS")
    print("-" * 60)
    
    constraint_verification = {}
    
    # Check historical_ohlcv_daily unique constraint
    try:
        cursor.execute("SHOW INDEX FROM historical_ohlcv_daily WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        constraint_verification['historical_ohlcv_daily_unique'] = result is not None
        status = "EXISTS" if result else "MISSING"
        print(f"   historical_ohlcv_daily unique constraint: {status}")
    except Exception as e:
        constraint_verification['historical_ohlcv_daily_unique'] = False
        print(f"   historical_ohlcv_daily unique constraint: ERROR - {e}")
    
    # Check technical_indicators unique constraint
    try:
        cursor.execute("SHOW INDEX FROM technical_indicators WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        constraint_verification['technical_indicators_unique'] = result is not None
        status = "EXISTS" if result else "MISSING"
        print(f"   technical_indicators unique constraint: {status}")
    except Exception as e:
        constraint_verification['technical_indicators_unique'] = False
        print(f"   technical_indicators unique constraint: ERROR - {e}")
    
    # Check fundamental_data unique constraint
    try:
        cursor.execute("SHOW INDEX FROM fundamental_data WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        constraint_verification['fundamental_data_unique'] = result is not None
        status = "EXISTS" if result else "MISSING"
        print(f"   fundamental_data unique constraint: {status}")
    except Exception as e:
        constraint_verification['fundamental_data_unique'] = False
        print(f"   fundamental_data unique constraint: ERROR - {e}")
    
    verification_results['constraint_verification'] = constraint_verification
    
    # Step 7: Generate schema status
    print("\n7. GENERATING SCHEMA STATUS")
    print("-" * 60)
    
    schema_status = {
        'tables_ready': sum(1 for status in table_verification.values() if status),
        'tables_total': len(table_verification),
        'columns_ready': 0,
        'columns_total': 0,
        'constraints_ready': sum(1 for status in constraint_verification.values() if status),
        'constraints_total': len(constraint_verification),
        'overall_ready': False
    }
    
    # Calculate columns ready
    for table, columns in verification_results['column_verification'].items():
        schema_status['columns_ready'] += sum(1 for status in columns.values() if status)
        schema_status['columns_total'] += len(columns)
    
    # Calculate overall readiness
    tables_ready_pct = (schema_status['tables_ready'] / schema_status['tables_total']) * 100
    columns_ready_pct = (schema_status['columns_ready'] / schema_status['columns_total']) * 100 if schema_status['columns_total'] > 0 else 100
    constraints_ready_pct = (schema_status['constraints_ready'] / schema_status['constraints_total']) * 100 if schema_status['constraints_total'] > 0 else 100
    
    overall_ready_pct = (tables_ready_pct + columns_ready_pct + constraints_ready_pct) / 3
    schema_status['overall_ready'] = overall_ready_pct >= 80
    
    verification_results['schema_status'] = schema_status
    
    print(f"   Tables Ready: {schema_status['tables_ready']}/{schema_status['tables_total']} ({tables_ready_pct:.1f}%)")
    print(f"   Columns Ready: {schema_status['columns_ready']}/{schema_status['columns_total']} ({columns_ready_pct:.1f}%)")
    print(f"   Constraints Ready: {schema_status['constraints_ready']}/{schema_status['constraints_total']} ({constraints_ready_pct:.1f}%)")
    print(f"   Overall Ready: {overall_ready_pct:.1f}% - {'YES' if schema_status['overall_ready'] else 'NO'}")
    
    # Step 8: Generate recommendations
    print("\n8. GENERATING RECOMMENDATIONS")
    print("-" * 60)
    
    recommendations = []
    
    if not schema_status['overall_ready']:
        recommendations.append("Database schema needs additional fixes before data fetching")
    
    if tables_ready_pct < 100:
        missing_tables = [table for table, status in table_verification.items() if not status]
        recommendations.append(f"Create missing tables: {', '.join(missing_tables)}")
    
    if columns_ready_pct < 100:
        recommendations.append("Add missing columns to existing tables")
    
    if constraints_ready_pct < 100:
        recommendations.append("Add missing unique constraints")
    
    if schema_status['overall_ready']:
        recommendations.append("Database schema is ready for data fetching")
        recommendations.append("Proceed with Yahoo Finance data fetching")
    
    verification_results['recommendations'] = recommendations
    
    for rec in recommendations:
        print(f"   - {rec}")
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    # Generate comprehensive report
    generate_verification_report(verification_results)
    
    return verification_results

def generate_verification_report(verification_results: Dict[str, Any]) -> None:
    """Generate verification report"""
    print("\nDATABASE SCHEMA VERIFICATION REPORT")
    print("=" * 80)
    
    # Table verification
    table_verification = verification_results.get('table_verification', {})
    print(f"Table Verification:")
    for table, status in table_verification.items():
        print(f"  {table}: {'EXISTS' if status else 'MISSING'}")
    
    # Column verification
    column_verification = verification_results.get('column_verification', {})
    print(f"\nColumn Verification:")
    for table, columns in column_verification.items():
        print(f"  {table}:")
        for col, status in columns.items():
            print(f"    {col}: {'EXISTS' if status else 'MISSING'}")
    
    # Constraint verification
    constraint_verification = verification_results.get('constraint_verification', {})
    print(f"\nConstraint Verification:")
    for constraint, status in constraint_verification.items():
        print(f"  {constraint}: {'EXISTS' if status else 'MISSING'}")
    
    # Schema status
    schema_status = verification_results.get('schema_status', {})
    print(f"\nSchema Status:")
    print(f"  Tables Ready: {schema_status.get('tables_ready', 0)}/{schema_status.get('tables_total', 0)}")
    print(f"  Columns Ready: {schema_status.get('columns_ready', 0)}/{schema_status.get('columns_total', 0)}")
    print(f"  Constraints Ready: {schema_status.get('constraints_ready', 0)}/{schema_status.get('constraints_total', 0)}")
    print(f"  Overall Ready: {'YES' if schema_status.get('overall_ready', False) else 'NO'}")
    
    # Recommendations
    recommendations = verification_results.get('recommendations', [])
    print(f"\nRecommendations:")
    for rec in recommendations:
        print(f"  - {rec}")
    
    # Errors
    errors = verification_results.get('errors', [])
    if errors:
        print(f"\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"database_schema_verification_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(verification_results, f, indent=2)
    
    print(f"\nVerification results saved to: {results_file}")
    print(f"Verification completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    verify_database_schema()
