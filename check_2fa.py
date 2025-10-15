#!/usr/bin/env python3
"""
Script to check Two-Factor Authentication status
"""
import sys
import os
sys.path.append('backend')

from backend.app.database import engine
from sqlalchemy import text

def check_2fa():
    """Check 2FA configuration and database"""
    try:
        print("Checking Two-Factor Authentication...")
        
        with engine.connect() as conn:
            # Check if 2FA table exists
            result = conn.execute(text("SHOW TABLES LIKE 'two_factor%'"))
            tables = [row[0] for row in result]
            print(f"2FA Tables: {tables}")
            
            # Check if two_factor_auth table exists
            if 'two_factor_auth' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM two_factor_auth"))
                count = result.fetchone()[0]
                print(f"2FA Records: {count}")
            else:
                print("❌ two_factor_auth table not found")
            
            # Check users table
            result = conn.execute(text("SHOW TABLES LIKE 'users'"))
            users_table = [row[0] for row in result]
            if users_table:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.fetchone()[0]
                print(f"Users: {user_count}")
            else:
                print("❌ users table not found")
                
    except Exception as e:
        print(f"❌ Error checking 2FA: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_2fa()
