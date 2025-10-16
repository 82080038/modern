#!/usr/bin/env python3
"""
Comprehensive Database Schema Fix
===============================

Script untuk memperbaiki semua database schema issues yang ditemukan
dalam ultimate tuning system.

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
from datetime import datetime, timedelta
import json
import time

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='scalper',
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci',
        autocommit=False
    )

def execute_query(cursor, query, params=None, fetch=False):
    """Execute query with error handling"""
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        return True
    except mysql.connector.Error as err:
        print(f"     [ERROR] {err}")
        return False

def fix_risk_metrics_schema(cursor, db_conn):
    """Fix risk_metrics table schema"""
    print("   Fixing risk_metrics table schema...")
    try:
        # Add calculated_at column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM risk_metrics LIKE 'calculated_at'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE risk_metrics ADD COLUMN calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            db_conn.commit()
            print("     [PASS] Added calculated_at column to risk_metrics table")
        else:
            print("     [PASS] calculated_at column already exists")
        
        # Add portfolio_id column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM risk_metrics LIKE 'portfolio_id'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE risk_metrics ADD COLUMN portfolio_id INT NULL")
            db_conn.commit()
            print("     [PASS] Added portfolio_id column to risk_metrics table")
        else:
            print("     [PASS] portfolio_id column already exists")
        
        # Update existing records with calculated_at if NULL
        execute_query(cursor, "UPDATE risk_metrics SET calculated_at = NOW() WHERE calculated_at IS NULL")
        db_conn.commit()
        print("     [PASS] Updated existing risk_metrics with calculated_at timestamps")
        
        return {"status": "SUCCESS", "message": "Risk metrics schema fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def fix_fundamental_data_schema(cursor, db_conn):
    """Fix fundamental_data table schema"""
    print("   Fixing fundamental_data table schema...")
    try:
        # Add updated_at column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM fundamental_data LIKE 'updated_at'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE fundamental_data ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            db_conn.commit()
            print("     [PASS] Added updated_at column to fundamental_data table")
        else:
            print("     [PASS] updated_at column already exists")
        
        # Update existing records with updated_at if NULL
        execute_query(cursor, "UPDATE fundamental_data SET updated_at = NOW() WHERE updated_at IS NULL")
        db_conn.commit()
        print("     [PASS] Updated existing fundamental_data with updated_at timestamps")
        
        return {"status": "SUCCESS", "message": "Fundamental data schema fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def fix_sentiment_data_schema(cursor, db_conn):
    """Fix sentiment_data table schema"""
    print("   Fixing sentiment_data table schema...")
    try:
        # Add published_at column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM sentiment_data LIKE 'published_at'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE sentiment_data ADD COLUMN published_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            db_conn.commit()
            print("     [PASS] Added published_at column to sentiment_data table")
        else:
            print("     [PASS] published_at column already exists")
        
        # Update existing records with published_at if NULL
        execute_query(cursor, "UPDATE sentiment_data SET published_at = NOW() WHERE published_at IS NULL")
        db_conn.commit()
        print("     [PASS] Updated existing sentiment_data with published_at timestamps")
        
        return {"status": "SUCCESS", "message": "Sentiment data schema fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def fix_technical_indicators_schema(cursor, db_conn):
    """Fix technical_indicators table schema"""
    print("   Fixing technical_indicators table schema...")
    try:
        # Add calculated_at column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM technical_indicators LIKE 'calculated_at'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE technical_indicators ADD COLUMN calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            db_conn.commit()
            print("     [PASS] Added calculated_at column to technical_indicators table")
        else:
            print("     [PASS] calculated_at column already exists")
        
        # Update existing records with calculated_at if NULL
        execute_query(cursor, "UPDATE technical_indicators SET calculated_at = NOW() WHERE calculated_at IS NULL")
        db_conn.commit()
        print("     [PASS] Updated existing technical_indicators with calculated_at timestamps")
        
        return {"status": "SUCCESS", "message": "Technical indicators schema fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def fix_orders_table_schema(cursor, db_conn):
    """Fix orders table schema"""
    print("   Fixing orders table schema...")
    try:
        # Add executed_at column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM orders LIKE 'executed_at'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE orders ADD COLUMN executed_at DATETIME NULL")
            db_conn.commit()
            print("     [PASS] Added executed_at column to orders table")
        else:
            print("     [PASS] executed_at column already exists")
        
        # Add status column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM orders LIKE 'status'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'pending'")
            db_conn.commit()
            print("     [PASS] Added status column to orders table")
        else:
            print("     [PASS] status column already exists")
        
        return {"status": "SUCCESS", "message": "Orders table schema fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def fix_trades_table_schema(cursor, db_conn):
    """Fix trades table schema"""
    print("   Fixing trades table schema...")
    try:
        # Add executed_at column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM trades LIKE 'executed_at'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE trades ADD COLUMN executed_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            db_conn.commit()
            print("     [PASS] Added executed_at column to trades table")
        else:
            print("     [PASS] executed_at column already exists")
        
        # Add status column if it doesn't exist
        cursor.execute("SHOW COLUMNS FROM trades LIKE 'status'")
        if not cursor.fetchone():
            execute_query(cursor, "ALTER TABLE trades ADD COLUMN status VARCHAR(50) DEFAULT 'executed'")
            db_conn.commit()
            print("     [PASS] Added status column to trades table")
        else:
            print("     [PASS] status column already exists")
        
        return {"status": "SUCCESS", "message": "Trades table schema fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def main():
    """Main function"""
    db_conn = None
    cursor = None
    results = {}
    start_time = datetime.now()
    
    print("COMPREHENSIVE DATABASE SCHEMA FIX")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        print("[PASS] Database connection established")
        
        # 1. FIXING RISK_METRICS TABLE SCHEMA
        print("\n1. FIXING RISK_METRICS TABLE SCHEMA")
        print("------------------------------------------------------------")
        risk_metrics_fix = fix_risk_metrics_schema(cursor, db_conn)
        results["risk_metrics_fix"] = risk_metrics_fix
        print(f"   Risk metrics fix: {risk_metrics_fix['status']}")
        
        # 2. FIXING FUNDAMENTAL_DATA TABLE SCHEMA
        print("\n2. FIXING FUNDAMENTAL_DATA TABLE SCHEMA")
        print("------------------------------------------------------------")
        fundamental_data_fix = fix_fundamental_data_schema(cursor, db_conn)
        results["fundamental_data_fix"] = fundamental_data_fix
        print(f"   Fundamental data fix: {fundamental_data_fix['status']}")
        
        # 3. FIXING SENTIMENT_DATA TABLE SCHEMA
        print("\n3. FIXING SENTIMENT_DATA TABLE SCHEMA")
        print("------------------------------------------------------------")
        sentiment_data_fix = fix_sentiment_data_schema(cursor, db_conn)
        results["sentiment_data_fix"] = sentiment_data_fix
        print(f"   Sentiment data fix: {sentiment_data_fix['status']}")
        
        # 4. FIXING TECHNICAL_INDICATORS TABLE SCHEMA
        print("\n4. FIXING TECHNICAL_INDICATORS TABLE SCHEMA")
        print("------------------------------------------------------------")
        technical_indicators_fix = fix_technical_indicators_schema(cursor, db_conn)
        results["technical_indicators_fix"] = technical_indicators_fix
        print(f"   Technical indicators fix: {technical_indicators_fix['status']}")
        
        # 5. FIXING ORDERS TABLE SCHEMA
        print("\n5. FIXING ORDERS TABLE SCHEMA")
        print("------------------------------------------------------------")
        orders_fix = fix_orders_table_schema(cursor, db_conn)
        results["orders_fix"] = orders_fix
        print(f"   Orders fix: {orders_fix['status']}")
        
        # 6. FIXING TRADES TABLE SCHEMA
        print("\n6. FIXING TRADES TABLE SCHEMA")
        print("------------------------------------------------------------")
        trades_fix = fix_trades_table_schema(cursor, db_conn)
        results["trades_fix"] = trades_fix
        print(f"   Trades fix: {trades_fix['status']}")
        
        # 7. GENERATING FINAL ASSESSMENT
        print("\n7. GENERATING FINAL ASSESSMENT")
        print("------------------------------------------------------------")
        successful_fixes = sum(1 for fix in results.values() if fix["status"] == "SUCCESS")
        total_fixes = len(results)
        
        final_assessment = {
            "overall_status": "SUCCESS" if successful_fixes == total_fixes else "PARTIAL",
            "successful_fixes": successful_fixes,
            "total_fixes": total_fixes,
            "success_rate": (successful_fixes / total_fixes) * 100,
            "issues_resolved": [],
            "remaining_issues": []
        }
        
        for fix_name, fix_result in results.items():
            if fix_result["status"] == "SUCCESS":
                final_assessment["issues_resolved"].append(f"{fix_name}: {fix_result['message']}")
            else:
                final_assessment["remaining_issues"].append(f"{fix_name}: {fix_result['message']}")
        
        results["final_assessment"] = final_assessment
        print("   Final assessment completed")
        
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")
        results["error"] = str(err)
    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()
            print("[PASS] Database connection closed")
    
    end_time = datetime.now()
    file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"database_schema_fix_{file_timestamp}.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=4, default=str)
    
    print("\nDATABASE SCHEMA FIX REPORT")
    print("=" * 80)
    print(f"Overall Status: {results['final_assessment']['overall_status']}")
    print(f"Successful Fixes: {results['final_assessment']['successful_fixes']}/{results['final_assessment']['total_fixes']}")
    print(f"Success Rate: {results['final_assessment']['success_rate']:.1f}%")
    
    if results['final_assessment']['issues_resolved']:
        print("\nIssues Resolved:")
        for issue in results['final_assessment']['issues_resolved']:
            print(f"  - {issue}")
    
    if results['final_assessment']['remaining_issues']:
        print("\nRemaining Issues:")
        for issue in results['final_assessment']['remaining_issues']:
            print(f"  - {issue}")
    
    print(f"\nDatabase schema fix results saved to: {output_filename}")
    print(f"Fix completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
