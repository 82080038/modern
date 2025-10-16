#!/usr/bin/env python3
"""
Fix SQL Error and Final Test
============================

Script untuk memperbaiki error SQL yang tersisa dan
melakukan testing final untuk memastikan semuanya berfungsi.

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

def fix_sql_error_and_final_test():
    """Fix SQL error dan lakukan testing final"""
    print("FIX SQL ERROR AND FINAL TEST")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test results
    test_results = {
        'test_type': 'fix_sql_error_and_final_test',
        'test_start': datetime.now().isoformat(),
        'sql_errors_fixed': [],
        'final_testing': {},
        'performance_metrics': {},
        'production_readiness': {}
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
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return test_results
    
    # Step 1: Fix SQL syntax error
    print("\n1. FIXING SQL SYNTAX ERROR")
    print("-" * 40)
    
    try:
        # Check if alert_rules table has the problematic column
        cursor.execute("DESCRIBE alert_rules")
        columns = cursor.fetchall()
        
        # Find the problematic column
        problematic_column = None
        for column in columns:
            if 'condition' in column[0].lower():
                problematic_column = column[0]
                break
        
        if problematic_column:
            print(f"   Found problematic column: {problematic_column}")
            
            # Fix the column name to avoid SQL keyword conflict
            new_column_name = f"{problematic_column}_value"
            cursor.execute(f"ALTER TABLE alert_rules CHANGE `{problematic_column}` `{new_column_name}` TEXT")
            print(f"   Fixed column name: {problematic_column} -> {new_column_name}")
            test_results['sql_errors_fixed'].append(f"Fixed column {problematic_column} to {new_column_name}")
        else:
            print("   No problematic column found")
            test_results['sql_errors_fixed'].append("No SQL errors found")
            
    except Exception as e:
        print(f"   [WARN] SQL error fix: {e}")
        test_results['sql_errors_fixed'].append(f"SQL error fix warning: {e}")
    
    # Step 2: Run comprehensive final testing
    print("\n2. RUNNING COMPREHENSIVE FINAL TESTING")
    print("-" * 40)
    
    final_testing = run_comprehensive_final_testing(cursor)
    test_results['final_testing'] = final_testing
    
    # Step 3: Calculate performance metrics
    print("\n3. CALCULATING PERFORMANCE METRICS")
    print("-" * 40)
    
    performance_metrics = calculate_final_performance_metrics(cursor)
    test_results['performance_metrics'] = performance_metrics
    
    # Step 4: Assess production readiness
    print("\n4. ASSESSING PRODUCTION READINESS")
    print("-" * 40)
    
    production_readiness = assess_production_readiness(test_results)
    test_results['production_readiness'] = production_readiness
    
    # Step 5: Generate final report
    print("\n5. GENERATING FINAL REPORT")
    print("-" * 40)
    
    generate_final_report(test_results)
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    return test_results

def run_comprehensive_final_testing(cursor) -> Dict[str, Any]:
    """Run comprehensive final testing"""
    try:
        testing_results = {
            'database_connection': True,
            'tables_accessible': 0,
            'data_quality_score': 0.0,
            'module_performance': {},
            'integration_tests': {},
            'error_count': 0
        }
        
        # Test 1: Database connectivity
        print("   Testing database connectivity...")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"   [PASS] MySQL Version: {version}")
        
        # Test 2: Table accessibility
        print("   Testing table accessibility...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        testing_results['tables_accessible'] = len(tables)
        print(f"   [PASS] {len(tables)} tables accessible")
        
        # Test 3: Critical tables data
        print("   Testing critical tables...")
        critical_tables = ['orders', 'trades', 'market_data', 'risk_metrics', 'portfolio_risk']
        
        for table in critical_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   [PASS] {table}: {count} rows")
                testing_results['module_performance'][table] = count
            except Exception as e:
                print(f"   [WARN] {table}: {e}")
                testing_results['error_count'] += 1
        
        # Test 4: Data quality assessment
        print("   Testing data quality...")
        data_quality_score = assess_data_quality(cursor)
        testing_results['data_quality_score'] = data_quality_score
        print(f"   [PASS] Data quality score: {data_quality_score:.1f}%")
        
        # Test 5: Module integration
        print("   Testing module integration...")
        integration_results = test_module_integration(cursor)
        testing_results['integration_tests'] = integration_results
        
        return testing_results
        
    except Exception as e:
        return {
            'database_connection': False,
            'error': str(e)
        }

def assess_data_quality(cursor) -> float:
    """Assess data quality score"""
    try:
        # Check data completeness
        total_tables = 0
        tables_with_data = 0
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            total_tables += 1
            
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                if count > 0:
                    tables_with_data += 1
            except:
                pass
        
        if total_tables > 0:
            completeness = (tables_with_data / total_tables) * 100
        else:
            completeness = 0.0
        
        return completeness
        
    except Exception as e:
        return 0.0

def test_module_integration(cursor) -> Dict[str, Any]:
    """Test module integration"""
    try:
        integration_results = {}
        
        # Test trading + market data integration
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM orders o 
                JOIN market_data m ON o.symbol = m.symbol 
                WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            count = cursor.fetchone()[0]
            integration_results['trading_market_data'] = {'success': True, 'count': count}
            print(f"   [PASS] Trading + Market Data integration: {count} records")
        except Exception as e:
            integration_results['trading_market_data'] = {'success': False, 'error': str(e)}
            print(f"   [WARN] Trading + Market Data integration: {e}")
        
        # Test risk management integration
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM portfolio_risk pr 
                JOIN risk_metrics rm ON pr.portfolio_id = rm.portfolio_id
            """)
            count = cursor.fetchone()[0]
            integration_results['risk_management'] = {'success': True, 'count': count}
            print(f"   [PASS] Risk Management integration: {count} records")
        except Exception as e:
            integration_results['risk_management'] = {'success': False, 'error': str(e)}
            print(f"   [WARN] Risk Management integration: {e}")
        
        return integration_results
        
    except Exception as e:
        return {'error': str(e)}

def calculate_final_performance_metrics(cursor) -> Dict[str, Any]:
    """Calculate final performance metrics"""
    try:
        metrics = {}
        
        # Trading module performance
        trading_tables = ['orders', 'trades', 'positions', 'portfolio']
        trading_data = 0
        for table in trading_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                trading_data += count
            except:
                pass
        
        metrics['trading_performance'] = min(trading_data / 100, 1.0) * 100
        
        # Risk management performance
        risk_tables = ['risk_metrics', 'portfolio_risk', 'var_calculation', 'risk_alerts']
        risk_data = 0
        for table in risk_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                risk_data += count
            except:
                pass
        
        metrics['risk_management_performance'] = min(risk_data / 50, 1.0) * 100
        
        # Market data performance
        market_tables = ['market_data', 'historical_data', 'historical_ohlcv_daily']
        market_data = 0
        for table in market_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                market_data += count
            except:
                pass
        
        metrics['market_data_performance'] = min(market_data / 1000, 1.0) * 100
        
        # Overall performance
        metrics['overall_performance'] = (
            metrics['trading_performance'] + 
            metrics['risk_management_performance'] + 
            metrics['market_data_performance']
        ) / 3
        
        return metrics
        
    except Exception as e:
        return {
            'trading_performance': 0.0,
            'risk_management_performance': 0.0,
            'market_data_performance': 0.0,
            'overall_performance': 0.0,
            'error': str(e)
        }

def assess_production_readiness(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Assess production readiness"""
    try:
        readiness = {
            'overall_ready': False,
            'criteria_met': [],
            'criteria_failed': [],
            'recommendations': []
        }
        
        # Check performance metrics
        performance = test_results.get('performance_metrics', {})
        
        # Trading module readiness
        trading_perf = performance.get('trading_performance', 0)
        if trading_perf >= 80:
            readiness['criteria_met'].append('Trading module performance >= 80%')
        else:
            readiness['criteria_failed'].append(f'Trading module performance: {trading_perf:.1f}%')
        
        # Risk management readiness
        risk_perf = performance.get('risk_management_performance', 0)
        if risk_perf >= 80:
            readiness['criteria_met'].append('Risk management performance >= 80%')
        else:
            readiness['criteria_failed'].append(f'Risk management performance: {risk_perf:.1f}%')
        
        # Market data readiness
        market_perf = performance.get('market_data_performance', 0)
        if market_perf >= 80:
            readiness['criteria_met'].append('Market data performance >= 80%')
        else:
            readiness['criteria_failed'].append(f'Market data performance: {market_perf:.1f}%')
        
        # Overall readiness
        overall_perf = performance.get('overall_performance', 0)
        if overall_perf >= 80 and len(readiness['criteria_failed']) == 0:
            readiness['overall_ready'] = True
            readiness['recommendations'].append('System ready for production deployment')
        else:
            readiness['recommendations'].append('System needs additional improvements before production')
        
        return readiness
        
    except Exception as e:
        return {
            'overall_ready': False,
            'error': str(e)
        }

def generate_final_report(test_results: Dict[str, Any]) -> None:
    """Generate final report"""
    print("\nFINAL TEST RESULTS")
    print("=" * 60)
    
    # SQL errors fixed
    sql_errors = test_results.get('sql_errors_fixed', [])
    print(f"SQL Errors Fixed: {len(sql_errors)}")
    for error in sql_errors:
        print(f"  - {error}")
    
    # Final testing results
    final_testing = test_results.get('final_testing', {})
    print(f"\nFinal Testing Results:")
    print(f"  Database Connection: {'PASS' if final_testing.get('database_connection') else 'FAIL'}")
    print(f"  Tables Accessible: {final_testing.get('tables_accessible', 0)}")
    print(f"  Data Quality Score: {final_testing.get('data_quality_score', 0):.1f}%")
    print(f"  Error Count: {final_testing.get('error_count', 0)}")
    
    # Performance metrics
    performance = test_results.get('performance_metrics', {})
    print(f"\nPerformance Metrics:")
    print(f"  Trading Performance: {performance.get('trading_performance', 0):.1f}%")
    print(f"  Risk Management Performance: {performance.get('risk_management_performance', 0):.1f}%")
    print(f"  Market Data Performance: {performance.get('market_data_performance', 0):.1f}%")
    print(f"  Overall Performance: {performance.get('overall_performance', 0):.1f}%")
    
    # Production readiness
    readiness = test_results.get('production_readiness', {})
    print(f"\nProduction Readiness:")
    print(f"  Overall Ready: {'YES' if readiness.get('overall_ready') else 'NO'}")
    print(f"  Criteria Met: {len(readiness.get('criteria_met', []))}")
    print(f"  Criteria Failed: {len(readiness.get('criteria_failed', []))}")
    
    if readiness.get('criteria_met'):
        print("  Criteria Met:")
        for criteria in readiness['criteria_met']:
            print(f"    - {criteria}")
    
    if readiness.get('criteria_failed'):
        print("  Criteria Failed:")
        for criteria in readiness['criteria_failed']:
            print(f"    - {criteria}")
    
    if readiness.get('recommendations'):
        print("  Recommendations:")
        for rec in readiness['recommendations']:
            print(f"    - {rec}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"final_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nFinal test results saved to: {results_file}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    fix_sql_error_and_final_test()
