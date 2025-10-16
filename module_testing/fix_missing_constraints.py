#!/usr/bin/env python3
"""
Fix Missing Constraints
======================

Script untuk memperbaiki missing unique constraints yang teridentifikasi
dalam database schema verification.

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

def fix_missing_constraints():
    """Fix missing constraints"""
    print("FIXING MISSING CONSTRAINTS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Fix results
    fix_results = {
        'test_type': 'fix_missing_constraints',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'constraints_fixed': [],
        'constraints_failed': [],
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
    
    # Step 1: Fix technical_indicators unique constraint
    print("\n1. FIXING TECHNICAL_INDICATORS UNIQUE CONSTRAINT")
    print("-" * 60)
    
    try:
        # Check if unique constraint exists
        cursor.execute("SHOW INDEX FROM technical_indicators WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        
        if not result:
            # Add unique constraint
            cursor.execute("ALTER TABLE technical_indicators ADD CONSTRAINT unique_symbol_date UNIQUE (symbol, date)")
            fix_results['constraints_fixed'].append("Added unique constraint to technical_indicators")
            print("   [PASS] Added unique constraint to technical_indicators")
        else:
            print("   [INFO] Unique constraint already exists in technical_indicators")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['constraints_failed'].append(f"Failed to add unique constraint to technical_indicators: {e}")
        print(f"   [ERROR] Failed to add unique constraint to technical_indicators: {e}")
        fix_results['errors'].append(f"Error fixing technical_indicators constraint: {e}")
    
    # Step 2: Fix fundamental_data unique constraint
    print("\n2. FIXING FUNDAMENTAL_DATA UNIQUE CONSTRAINT")
    print("-" * 60)
    
    try:
        # Check if unique constraint exists
        cursor.execute("SHOW INDEX FROM fundamental_data WHERE Key_name = 'unique_symbol_date'")
        result = cursor.fetchone()
        
        if not result:
            # Add unique constraint
            cursor.execute("ALTER TABLE fundamental_data ADD CONSTRAINT unique_symbol_date UNIQUE (symbol, date)")
            fix_results['constraints_fixed'].append("Added unique constraint to fundamental_data")
            print("   [PASS] Added unique constraint to fundamental_data")
        else:
            print("   [INFO] Unique constraint already exists in fundamental_data")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['constraints_failed'].append(f"Failed to add unique constraint to fundamental_data: {e}")
        print(f"   [ERROR] Failed to add unique constraint to fundamental_data: {e}")
        fix_results['errors'].append(f"Error fixing fundamental_data constraint: {e}")
    
    # Step 3: Add additional constraints for data integrity
    print("\n3. ADDING ADDITIONAL CONSTRAINTS FOR DATA INTEGRITY")
    print("-" * 60)
    
    # Add market_data unique constraint
    try:
        cursor.execute("SHOW INDEX FROM market_data WHERE Key_name = 'unique_symbol_timestamp'")
        result = cursor.fetchone()
        
        if not result:
            cursor.execute("ALTER TABLE market_data ADD CONSTRAINT unique_symbol_timestamp UNIQUE (symbol, timestamp)")
            fix_results['constraints_fixed'].append("Added unique constraint to market_data")
            print("   [PASS] Added unique constraint to market_data")
        else:
            print("   [INFO] Unique constraint already exists in market_data")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['constraints_failed'].append(f"Failed to add unique constraint to market_data: {e}")
        print(f"   [ERROR] Failed to add unique constraint to market_data: {e}")
        fix_results['errors'].append(f"Error fixing market_data constraint: {e}")
    
    # Add sentiment_data unique constraint
    try:
        cursor.execute("SHOW INDEX FROM sentiment_data WHERE Key_name = 'unique_symbol_published'")
        result = cursor.fetchone()
        
        if not result:
            cursor.execute("ALTER TABLE sentiment_data ADD CONSTRAINT unique_symbol_published UNIQUE (symbol, published_at)")
            fix_results['constraints_fixed'].append("Added unique constraint to sentiment_data")
            print("   [PASS] Added unique constraint to sentiment_data")
        else:
            print("   [INFO] Unique constraint already exists in sentiment_data")
        
        # Clear any unread results
        while cursor.nextset():
            pass
        
    except Exception as e:
        fix_results['constraints_failed'].append(f"Failed to add unique constraint to sentiment_data: {e}")
        print(f"   [ERROR] Failed to add unique constraint to sentiment_data: {e}")
        fix_results['errors'].append(f"Error fixing sentiment_data constraint: {e}")
    
    # Step 4: Add indexes for better performance
    print("\n4. ADDING INDEXES FOR BETTER PERFORMANCE")
    print("-" * 60)
    
    # Add indexes for better query performance
    indexes_to_add = [
        ("market_data", "idx_symbol", "symbol"),
        ("market_data", "idx_timestamp", "timestamp"),
        ("historical_ohlcv_daily", "idx_symbol", "symbol"),
        ("historical_ohlcv_daily", "idx_date", "date"),
        ("fundamental_data", "idx_symbol", "symbol"),
        ("fundamental_data", "idx_date", "date"),
        ("sentiment_data", "idx_symbol", "symbol"),
        ("sentiment_data", "idx_published_at", "published_at"),
        ("technical_indicators", "idx_symbol", "symbol"),
        ("technical_indicators", "idx_date", "date")
    ]
    
    for table, index_name, column in indexes_to_add:
        try:
            cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name = '{index_name}'")
            result = cursor.fetchone()
            
            if not result:
                cursor.execute(f"ALTER TABLE {table} ADD INDEX {index_name} ({column})")
                fix_results['constraints_fixed'].append(f"Added index {index_name} to {table}")
                print(f"   [PASS] Added index {index_name} to {table}")
            else:
                print(f"   [INFO] Index {index_name} already exists in {table}")
            
            # Clear any unread results
            while cursor.nextset():
                pass
            
        except Exception as e:
            fix_results['constraints_failed'].append(f"Failed to add index {index_name} to {table}: {e}")
            print(f"   [ERROR] Failed to add index {index_name} to {table}: {e}")
            fix_results['errors'].append(f"Error adding index {index_name} to {table}: {e}")
    
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
        'constraints_fixed': len(fix_results['constraints_fixed']),
        'constraints_failed': len(fix_results['constraints_failed']),
        'errors_encountered': len(fix_results['errors']),
        'fix_success_rate': (len(fix_results['constraints_fixed']) / (len(fix_results['constraints_fixed']) + len(fix_results['constraints_failed'])) * 100) if (len(fix_results['constraints_fixed']) + len(fix_results['constraints_failed'])) > 0 else 0
    }
    
    # Generate comprehensive report
    generate_constraint_fix_report(fix_results)
    
    return fix_results

def generate_constraint_fix_report(fix_results: Dict[str, Any]) -> None:
    """Generate constraint fix report"""
    print("\nCONSTRAINT FIX REPORT")
    print("=" * 80)
    
    # Constraints fixed
    constraints_fixed = fix_results.get('constraints_fixed', [])
    print(f"Constraints Fixed: {len(constraints_fixed)}")
    for constraint in constraints_fixed:
        print(f"  - {constraint}")
    
    # Constraints failed
    constraints_failed = fix_results.get('constraints_failed', [])
    if constraints_failed:
        print(f"\nConstraints Failed: {len(constraints_failed)}")
        for constraint in constraints_failed:
            print(f"  - {constraint}")
    
    # Errors
    errors = fix_results.get('errors', [])
    if errors:
        print(f"\nErrors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    
    # Summary
    summary = fix_results.get('summary', {})
    print(f"\nSummary:")
    print(f"  Constraints Fixed: {summary.get('constraints_fixed', 0)}")
    print(f"  Constraints Failed: {summary.get('constraints_failed', 0)}")
    print(f"  Errors Encountered: {summary.get('errors_encountered', 0)}")
    print(f"  Fix Success Rate: {summary.get('fix_success_rate', 0):.1f}%")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"constraint_fix_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(fix_results, f, indent=2)
    
    print(f"\nConstraint fix results saved to: {results_file}")
    print(f"Constraint fix completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    fix_missing_constraints()
