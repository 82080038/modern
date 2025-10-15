#!/usr/bin/env python3
"""
Script to check database connection and data
"""
import sys
import os
sys.path.append('backend')

from backend.app.database import engine
from sqlalchemy import text

def check_database():
    """Check database connection and tables"""
    try:
        print("Checking database connection...")
        
        with engine.connect() as conn:
            # Check if database exists and is accessible
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"Connected to database: {db_name}")
            
            # Show tables
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
            
            # Check if fundamental tables have data
            fundamental_tables = ['company_profiles', 'financial_ratios', 'financial_statements']
            for table in fundamental_tables:
                if table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"  {table}: {count} records")
                else:
                    print(f"  {table}: Table not found")
            
            # Check market data tables
            market_tables = ['market_data', 'historical_data', 'symbol_info']
            for table in market_tables:
                if table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"  {table}: {count} records")
                else:
                    print(f"  {table}: Table not found")
                    
    except Exception as e:
        print(f"Database error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_database()