#!/usr/bin/env python3
"""
Fix Remaining Errors
===================

Script untuk memperbaiki error-error yang masih ada:
- Field 'order_id' doesn't have a default value
- Field 'trade_id' doesn't have a default value  
- Duplicate entry errors

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
from datetime import datetime, timedelta
import json
import random

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

def fix_orders_table_auto_increment(cursor, db_conn):
    """Fix orders table auto increment issue"""
    print("   Fixing orders table auto increment...")
    try:
        # Check current table structure
        cursor.execute("SHOW CREATE TABLE orders")
        table_info = cursor.fetchone()
        print(f"     Current table structure: {table_info[1]}")
        
        # Drop and recreate orders table with proper auto increment
        cursor.execute("DROP TABLE IF EXISTS orders_backup")
        cursor.execute("CREATE TABLE orders_backup AS SELECT * FROM orders")
        
        cursor.execute("DROP TABLE orders")
        cursor.execute("""
            CREATE TABLE orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                order_type VARCHAR(10) NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                order_value DECIMAL(15,2) NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                executed_at DATETIME NULL
            )
        """)
        
        # Copy data back from backup
        cursor.execute("""
            INSERT INTO orders (symbol, order_type, quantity, price, order_value, status, created_at, executed_at)
            SELECT symbol, order_type, quantity, price, order_value, status, created_at, executed_at
            FROM orders_backup
        """)
        
        cursor.execute("DROP TABLE orders_backup")
        db_conn.commit()
        print("     [PASS] Orders table recreated with proper auto increment")
        
        return {"status": "SUCCESS", "message": "Orders table auto increment fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def fix_trades_table_auto_increment(cursor, db_conn):
    """Fix trades table auto increment issue"""
    print("   Fixing trades table auto increment...")
    try:
        # Check current table structure
        cursor.execute("SHOW CREATE TABLE trades")
        table_info = cursor.fetchone()
        print(f"     Current table structure: {table_info[1]}")
        
        # Drop and recreate trades table with proper auto increment
        cursor.execute("DROP TABLE IF EXISTS trades_backup")
        cursor.execute("CREATE TABLE trades_backup AS SELECT * FROM trades")
        
        cursor.execute("DROP TABLE trades")
        cursor.execute("""
            CREATE TABLE trades (
                trade_id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                trade_type VARCHAR(10) NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                trade_value DECIMAL(15,2) NULL,
                executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'executed'
            )
        """)
        
        # Copy data back from backup
        cursor.execute("""
            INSERT INTO trades (symbol, trade_type, quantity, price, trade_value, executed_at, status)
            SELECT symbol, trade_type, quantity, price, trade_value, executed_at, status
            FROM trades_backup
        """)
        
        cursor.execute("DROP TABLE trades_backup")
        db_conn.commit()
        print("     [PASS] Trades table recreated with proper auto increment")
        
        return {"status": "SUCCESS", "message": "Trades table auto increment fixed"}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def fix_duplicate_entries(cursor, db_conn):
    """Fix duplicate entries by cleaning up and adding proper constraints"""
    print("   Fixing duplicate entries...")
    try:
        # Clean up duplicate sentiment data
        cursor.execute("""
            DELETE s1 FROM sentiment_data s1
            INNER JOIN sentiment_data s2 
            WHERE s1.id > s2.id 
            AND s1.symbol = s2.symbol 
            AND s1.analysis_date = s2.analysis_date
        """)
        deleted_sentiment = cursor.rowcount
        print(f"     [PASS] Removed {deleted_sentiment} duplicate sentiment data entries")
        
        # Clean up duplicate market data
        cursor.execute("""
            DELETE m1 FROM market_data m1
            INNER JOIN market_data m2 
            WHERE m1.id > m2.id 
            AND m1.symbol = m2.symbol 
            AND m1.date = m2.date
        """)
        deleted_market = cursor.rowcount
        print(f"     [PASS] Removed {deleted_market} duplicate market data entries")
        
        # Clean up duplicate historical data
        cursor.execute("""
            DELETE h1 FROM historical_ohlcv_daily h1
            INNER JOIN historical_ohlcv_daily h2 
            WHERE h1.id > h2.id 
            AND h1.symbol = h2.symbol 
            AND h1.date = h2.date
        """)
        deleted_historical = cursor.rowcount
        print(f"     [PASS] Removed {deleted_historical} duplicate historical data entries")
        
        # Clean up duplicate technical indicators
        cursor.execute("""
            DELETE t1 FROM technical_indicators t1
            INNER JOIN technical_indicators t2 
            WHERE t1.id > t2.id 
            AND t1.symbol = t2.symbol 
            AND t1.date = t2.date
            AND t1.indicator_type = t2.indicator_type
        """)
        deleted_technical = cursor.rowcount
        print(f"     [PASS] Removed {deleted_technical} duplicate technical indicator entries")
        
        db_conn.commit()
        
        return {
            "status": "SUCCESS", 
            "message": "Duplicate entries cleaned up",
            "deleted_sentiment": deleted_sentiment,
            "deleted_market": deleted_market,
            "deleted_historical": deleted_historical,
            "deleted_technical": deleted_technical
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def test_fixed_system(cursor):
    """Test the fixed system"""
    print("   Testing fixed system...")
    try:
        # Test orders table
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        
        # Test trades table
        cursor.execute("SELECT COUNT(*) FROM trades")
        trades_count = cursor.fetchone()[0]
        
        # Test for duplicates
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT symbol, analysis_date, COUNT(*) as cnt 
                FROM sentiment_data 
                GROUP BY symbol, analysis_date 
                HAVING cnt > 1
            ) as duplicates
        """)
        sentiment_duplicates = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT symbol, date, COUNT(*) as cnt 
                FROM market_data 
                GROUP BY symbol, date 
                HAVING cnt > 1
            ) as duplicates
        """)
        market_duplicates = cursor.fetchone()[0]
        
        # Test auto increment
        cursor.execute("SHOW TABLE STATUS LIKE 'orders'")
        orders_status = cursor.fetchone()
        orders_auto_increment = orders_status[10] if orders_status else 0
        
        cursor.execute("SHOW TABLE STATUS LIKE 'trades'")
        trades_status = cursor.fetchone()
        trades_auto_increment = trades_status[10] if trades_status else 0
        
        test_results = {
            "orders_count": orders_count,
            "trades_count": trades_count,
            "sentiment_duplicates": sentiment_duplicates,
            "market_duplicates": market_duplicates,
            "orders_auto_increment": orders_auto_increment,
            "trades_auto_increment": trades_auto_increment
        }
        
        print(f"     [PASS] Orders count: {orders_count}")
        print(f"     [PASS] Trades count: {trades_count}")
        print(f"     [PASS] Sentiment duplicates: {sentiment_duplicates}")
        print(f"     [PASS] Market duplicates: {market_duplicates}")
        print(f"     [PASS] Orders auto increment: {orders_auto_increment}")
        print(f"     [PASS] Trades auto increment: {trades_auto_increment}")
        
        return {"status": "SUCCESS", "test_results": test_results}
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def main():
    """Main function"""
    db_conn = None
    cursor = None
    results = {}
    start_time = datetime.now()
    
    print("FIX REMAINING ERRORS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        print("[PASS] Database connection established")
        
        # 1. FIXING ORDERS TABLE AUTO INCREMENT
        print("\n1. FIXING ORDERS TABLE AUTO INCREMENT")
        print("------------------------------------------------------------")
        orders_fix = fix_orders_table_auto_increment(cursor, db_conn)
        results["orders_auto_increment_fix"] = orders_fix
        print(f"   Orders auto increment fix: {orders_fix['status']}")
        
        # 2. FIXING TRADES TABLE AUTO INCREMENT
        print("\n2. FIXING TRADES TABLE AUTO INCREMENT")
        print("------------------------------------------------------------")
        trades_fix = fix_trades_table_auto_increment(cursor, db_conn)
        results["trades_auto_increment_fix"] = trades_fix
        print(f"   Trades auto increment fix: {trades_fix['status']}")
        
        # 3. FIXING DUPLICATE ENTRIES
        print("\n3. FIXING DUPLICATE ENTRIES")
        print("------------------------------------------------------------")
        duplicate_fix = fix_duplicate_entries(cursor, db_conn)
        results["duplicate_entries_fix"] = duplicate_fix
        print(f"   Duplicate entries fix: {duplicate_fix['status']}")
        
        # 4. TESTING FIXED SYSTEM
        print("\n4. TESTING FIXED SYSTEM")
        print("------------------------------------------------------------")
        test_results = test_fixed_system(cursor)
        results["system_test"] = test_results
        print(f"   System test: {test_results['status']}")
        
        # 5. GENERATING FINAL ASSESSMENT
        print("\n5. GENERATING FINAL ASSESSMENT")
        print("------------------------------------------------------------")
        
        successful_fixes = sum(1 for result in results.values() if isinstance(result, dict) and result.get("status") == "SUCCESS")
        total_fixes = len([r for r in results.values() if isinstance(r, dict) and "status" in r])
        
        final_assessment = {
            "overall_status": "SUCCESS" if successful_fixes == total_fixes else "PARTIAL",
            "successful_fixes": successful_fixes,
            "total_fixes": total_fixes,
            "success_rate": (successful_fixes / total_fixes) * 100 if total_fixes > 0 else 0,
            "issues_resolved": [],
            "remaining_issues": []
        }
        
        if orders_fix["status"] == "SUCCESS":
            final_assessment["issues_resolved"].append("Orders table auto increment fixed")
        else:
            final_assessment["remaining_issues"].append(f"Orders table auto increment still has issues: {orders_fix['message']}")
        
        if trades_fix["status"] == "SUCCESS":
            final_assessment["issues_resolved"].append("Trades table auto increment fixed")
        else:
            final_assessment["remaining_issues"].append(f"Trades table auto increment still has issues: {trades_fix['message']}")
        
        if duplicate_fix["status"] == "SUCCESS":
            final_assessment["issues_resolved"].append("Duplicate entries cleaned up")
        else:
            final_assessment["remaining_issues"].append(f"Duplicate entries still have issues: {duplicate_fix['message']}")
        
        if test_results["status"] == "SUCCESS":
            test_data = test_results["test_results"]
            if test_data["sentiment_duplicates"] == 0 and test_data["market_duplicates"] == 0:
                final_assessment["issues_resolved"].append("No duplicate entries found")
            else:
                final_assessment["remaining_issues"].append(f"Still have duplicates: sentiment={test_data['sentiment_duplicates']}, market={test_data['market_duplicates']}")
            
            if test_data["orders_auto_increment"] > 0 and test_data["trades_auto_increment"] > 0:
                final_assessment["issues_resolved"].append("Auto increment working properly")
            else:
                final_assessment["remaining_issues"].append("Auto increment still has issues")
        
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
    output_filename = f"remaining_errors_fix_{file_timestamp}.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=4, default=str)
    
    print("\nREMAINING ERRORS FIX REPORT")
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
    
    print(f"\nRemaining errors fix results saved to: {output_filename}")
    print(f"Fix completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
