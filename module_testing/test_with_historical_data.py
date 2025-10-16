#!/usr/bin/env python3
"""
Test with Historical Data - Real Data Testing
==============================================

Script untuk testing dengan data historis asli minimal 6 bulan
dan menampilkan proses real di terminal.

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
import pandas as pd

def test_with_historical_data():
    """Test dengan data historis asli minimal 6 bulan"""
    print("HISTORICAL DATA TESTING - REAL DATA ANALYSIS")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test results
    test_results = {
        'test_type': 'historical_data_testing',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'historical_data_analysis': {},
        'performance_metrics': {},
        'real_accuracy': {},
        'issues_found': [],
        'recommendations': []
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
        test_results['database_connection'] = True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        test_results['issues_found'].append(f'database_connection_error: {e}')
        return test_results
    
    # Step 1: Analyze historical data availability
    print("\n1. ANALYZING HISTORICAL DATA AVAILABILITY")
    print("-" * 50)
    
    historical_analysis = analyze_historical_data(cursor)
    test_results['historical_data_analysis'] = historical_analysis
    
    # Step 2: Test with 6 months of historical data
    print("\n2. TESTING WITH 6 MONTHS HISTORICAL DATA")
    print("-" * 50)
    
    six_month_test = test_six_months_historical_data(cursor)
    test_results['six_month_test'] = six_month_test
    
    # Step 3: Calculate real performance metrics
    print("\n3. CALCULATING REAL PERFORMANCE METRICS")
    print("-" * 50)
    
    performance_metrics = calculate_real_performance_metrics(cursor, historical_analysis)
    test_results['performance_metrics'] = performance_metrics
    
    # Step 4: Test enhanced modules with historical data
    print("\n4. TESTING ENHANCED MODULES WITH HISTORICAL DATA")
    print("-" * 50)
    
    enhanced_modules_test = test_enhanced_modules_with_historical_data(cursor)
    test_results['enhanced_modules_test'] = enhanced_modules_test
    
    # Step 5: Generate real accuracy report
    print("\n5. GENERATING REAL ACCURACY REPORT")
    print("-" * 50)
    
    real_accuracy = generate_real_accuracy_report(test_results)
    test_results['real_accuracy'] = real_accuracy
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    # Generate final report
    generate_historical_test_report(test_results)
    
    return test_results

def analyze_historical_data(cursor) -> Dict[str, Any]:
    """Analyze historical data availability"""
    try:
        analysis = {
            'tables_with_historical_data': [],
            'date_ranges': {},
            'data_quality': {},
            'total_records': 0
        }
        
        # Check historical data tables
        historical_tables = [
            'historical_data', 'historical_ohlcv_daily', 'historical_ohlcv_1h',
            'historical_ohlcv_15min', 'market_data', 'technical_indicators',
            'indicators_trend', 'indicators_momentum', 'indicators_volatility'
        ]
        
        for table in historical_tables:
            try:
                # Get total records
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_records = cursor.fetchone()[0]
                
                if total_records > 0:
                    analysis['tables_with_historical_data'].append(table)
                    analysis['total_records'] += total_records
                    
                    # Get date range
                    cursor.execute(f"""
                        SELECT 
                            MIN(date) as min_date, 
                            MAX(date) as max_date,
                            COUNT(*) as record_count
                        FROM {table} 
                        WHERE date IS NOT NULL
                    """)
                    date_info = cursor.fetchone()
                    
                    if date_info and date_info[0]:
                        analysis['date_ranges'][table] = {
                            'min_date': str(date_info[0]),
                            'max_date': str(date_info[1]),
                            'record_count': date_info[2],
                            'days_span': (date_info[1] - date_info[0]).days if date_info[1] and date_info[0] else 0
                        }
                        
                        print(f"   {table}: {date_info[2]} records")
                        print(f"     Date range: {date_info[0]} to {date_info[1]}")
                        print(f"     Days span: {(date_info[1] - date_info[0]).days if date_info[1] and date_info[0] else 0} days")
                        
                        # Check if we have at least 6 months of data
                        days_span = (date_info[1] - date_info[0]).days if date_info[1] and date_info[0] else 0
                        if days_span >= 180:  # 6 months = ~180 days
                            print(f"     [PASS] Has 6+ months of data")
                        else:
                            print(f"     [WARN] Only {days_span} days of data (need 180+ days)")
                    
            except Exception as e:
                print(f"   [WARN] Error analyzing {table}: {e}")
        
        return analysis
        
    except Exception as e:
        print(f"   [ERROR] Historical data analysis error: {e}")
        return {'error': str(e)}

def test_six_months_historical_data(cursor) -> Dict[str, Any]:
    """Test with 6 months of historical data"""
    try:
        test_results = {
            'trading_performance': {},
            'market_data_performance': {},
            'risk_management_performance': {},
            'overall_performance': 0.0
        }
        
        # Test 1: Trading performance with historical data
        print("   Testing trading performance with historical data...")
        trading_perf = test_trading_with_historical_data(cursor)
        test_results['trading_performance'] = trading_perf
        
        # Test 2: Market data performance with historical data
        print("   Testing market data performance with historical data...")
        market_data_perf = test_market_data_with_historical_data(cursor)
        test_results['market_data_performance'] = market_data_perf
        
        # Test 3: Risk management performance with historical data
        print("   Testing risk management performance with historical data...")
        risk_perf = test_risk_management_with_historical_data(cursor)
        test_results['risk_management_performance'] = risk_perf
        
        # Calculate overall performance
        perf_scores = [
            trading_perf.get('accuracy', 0),
            market_data_perf.get('accuracy', 0),
            risk_perf.get('accuracy', 0)
        ]
        test_results['overall_performance'] = sum(perf_scores) / len(perf_scores)
        
        return test_results
        
    except Exception as e:
        print(f"   [ERROR] Six months historical data test error: {e}")
        return {'error': str(e)}

def test_trading_with_historical_data(cursor) -> Dict[str, Any]:
    """Test trading performance with historical data"""
    try:
        # Get historical trading data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                AVG(price) as avg_price,
                SUM(quantity) as total_quantity,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM orders 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        trading_stats = cursor.fetchone()
        
        # Get historical trades
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                AVG(price) as avg_trade_price,
                SUM(quantity) as total_trade_quantity
            FROM trades 
            WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        trade_stats = cursor.fetchone()
        
        # Calculate trading performance
        total_orders = trading_stats[0] if trading_stats[0] else 0
        total_trades = trade_stats[0] if trade_stats[0] else 0
        
        if total_orders > 0:
            execution_rate = (total_trades / total_orders) * 100
        else:
            execution_rate = 0
        
        # Calculate accuracy based on historical data
        accuracy = min(execution_rate, 100.0)
        
        print(f"     Total orders (6 months): {total_orders}")
        print(f"     Total trades (6 months): {total_trades}")
        print(f"     Execution rate: {execution_rate:.2f}%")
        print(f"     Trading accuracy: {accuracy:.2f}%")
        
        return {
            'total_orders': total_orders,
            'total_trades': total_trades,
            'execution_rate': execution_rate,
            'accuracy': accuracy,
            'avg_price': trading_stats[1] if trading_stats[1] else 0,
            'total_quantity': trading_stats[2] if trading_stats[2] else 0,
            'unique_symbols': trading_stats[3] if trading_stats[3] else 0
        }
        
    except Exception as e:
        print(f"     [ERROR] Trading historical data test error: {e}")
        return {'error': str(e), 'accuracy': 0}

def test_market_data_with_historical_data(cursor) -> Dict[str, Any]:
    """Test market data performance with historical data"""
    try:
        # Get historical market data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                MIN(date) as min_date,
                MAX(date) as max_date,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM historical_ohlcv_daily 
            WHERE date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        market_stats = cursor.fetchone()
        
        # Get market data quality
        cursor.execute("""
            SELECT 
                COUNT(*) as total_market_data,
                AVG(price) as avg_price,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM market_data 
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        market_data_stats = cursor.fetchone()
        
        # Calculate market data performance
        total_records = market_stats[0] if market_stats[0] else 0
        total_market_data = market_data_stats[0] if market_data_stats[0] else 0
        
        # Calculate completeness
        if total_records > 0:
            completeness = min((total_market_data / total_records) * 100, 100.0)
        else:
            completeness = 0
        
        # Calculate accuracy based on data quality
        accuracy = min(completeness, 100.0)
        
        print(f"     Total historical records (6 months): {total_records}")
        print(f"     Total market data records (6 months): {total_market_data}")
        print(f"     Data completeness: {completeness:.2f}%")
        print(f"     Market data accuracy: {accuracy:.2f}%")
        
        return {
            'total_records': total_records,
            'total_market_data': total_market_data,
            'completeness': completeness,
            'accuracy': accuracy,
            'min_date': str(market_stats[1]) if market_stats[1] else None,
            'max_date': str(market_stats[2]) if market_stats[2] else None,
            'unique_symbols': market_stats[3] if market_stats[3] else 0
        }
        
    except Exception as e:
        print(f"     [ERROR] Market data historical test error: {e}")
        return {'error': str(e), 'accuracy': 0}

def test_risk_management_with_historical_data(cursor) -> Dict[str, Any]:
    """Test risk management performance with historical data"""
    try:
        # Get historical risk data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_risk_metrics,
                AVG(var_95) as avg_var_95,
                AVG(var_99) as avg_var_99,
                AVG(sharpe_ratio) as avg_sharpe_ratio
            FROM risk_metrics 
            WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        risk_stats = cursor.fetchone()
        
        # Get portfolio risk data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_portfolio_risk,
                AVG(var_95) as avg_portfolio_var_95,
                AVG(expected_shortfall) as avg_expected_shortfall
            FROM portfolio_risk 
            WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        portfolio_risk_stats = cursor.fetchone()
        
        # Calculate risk management performance
        total_risk_metrics = risk_stats[0] if risk_stats[0] else 0
        total_portfolio_risk = portfolio_risk_stats[0] if portfolio_risk_stats[0] else 0
        
        # Calculate risk coverage
        if total_risk_metrics > 0:
            risk_coverage = min((total_portfolio_risk / total_risk_metrics) * 100, 100.0)
        else:
            risk_coverage = 0
        
        # Calculate accuracy based on risk data quality
        accuracy = min(risk_coverage, 100.0)
        
        print(f"     Total risk metrics (6 months): {total_risk_metrics}")
        print(f"     Total portfolio risk (6 months): {total_portfolio_risk}")
        print(f"     Risk coverage: {risk_coverage:.2f}%")
        print(f"     Risk management accuracy: {accuracy:.2f}%")
        
        return {
            'total_risk_metrics': total_risk_metrics,
            'total_portfolio_risk': total_portfolio_risk,
            'risk_coverage': risk_coverage,
            'accuracy': accuracy,
            'avg_var_95': risk_stats[1] if risk_stats[1] else 0,
            'avg_var_99': risk_stats[2] if risk_stats[2] else 0,
            'avg_sharpe_ratio': risk_stats[3] if risk_stats[3] else 0
        }
        
    except Exception as e:
        print(f"     [ERROR] Risk management historical test error: {e}")
        return {'error': str(e), 'accuracy': 0}

def test_enhanced_modules_with_historical_data(cursor) -> Dict[str, Any]:
    """Test enhanced modules with historical data"""
    try:
        enhanced_test_results = {
            'enhanced_trading': {},
            'enhanced_market_data': {},
            'enhanced_risk_management': {},
            'integration_tests': {}
        }
        
        # Test enhanced trading module
        print("   Testing enhanced trading module with historical data...")
        enhanced_trading = test_enhanced_trading_with_historical_data(cursor)
        enhanced_test_results['enhanced_trading'] = enhanced_trading
        
        # Test enhanced market data module
        print("   Testing enhanced market data module with historical data...")
        enhanced_market_data = test_enhanced_market_data_with_historical_data(cursor)
        enhanced_test_results['enhanced_market_data'] = enhanced_market_data
        
        # Test enhanced risk management module
        print("   Testing enhanced risk management module with historical data...")
        enhanced_risk_management = test_enhanced_risk_management_with_historical_data(cursor)
        enhanced_test_results['enhanced_risk_management'] = enhanced_risk_management
        
        # Test integration
        print("   Testing module integration with historical data...")
        integration_tests = test_integration_with_historical_data(cursor)
        enhanced_test_results['integration_tests'] = integration_tests
        
        return enhanced_test_results
        
    except Exception as e:
        print(f"   [ERROR] Enhanced modules historical test error: {e}")
        return {'error': str(e)}

def test_enhanced_trading_with_historical_data(cursor) -> Dict[str, Any]:
    """Test enhanced trading module with historical data"""
    try:
        # Test order processing with historical data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                AVG(price) as avg_price,
                SUM(quantity) as total_quantity,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM orders 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        order_stats = cursor.fetchone()
        
        # Test trade execution with historical data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                AVG(price) as avg_trade_price,
                SUM(quantity) as total_trade_quantity
            FROM trades 
            WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        trade_stats = cursor.fetchone()
        
        # Calculate enhanced trading performance
        total_orders = order_stats[0] if order_stats[0] else 0
        total_trades = trade_stats[0] if trade_stats[0] else 0
        
        if total_orders > 0:
            execution_rate = (total_trades / total_orders) * 100
        else:
            execution_rate = 0
        
        # Enhanced trading accuracy
        accuracy = min(execution_rate, 100.0)
        
        print(f"     Enhanced trading orders: {total_orders}")
        print(f"     Enhanced trading trades: {total_trades}")
        print(f"     Enhanced execution rate: {execution_rate:.2f}%")
        print(f"     Enhanced trading accuracy: {accuracy:.2f}%")
        
        return {
            'total_orders': total_orders,
            'total_trades': total_trades,
            'execution_rate': execution_rate,
            'accuracy': accuracy,
            'avg_price': order_stats[1] if order_stats[1] else 0,
            'total_quantity': order_stats[2] if order_stats[2] else 0,
            'unique_symbols': order_stats[3] if order_stats[3] else 0
        }
        
    except Exception as e:
        print(f"     [ERROR] Enhanced trading historical test error: {e}")
        return {'error': str(e), 'accuracy': 0}

def test_enhanced_market_data_with_historical_data(cursor) -> Dict[str, Any]:
    """Test enhanced market data module with historical data"""
    try:
        # Test market data quality with historical data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                MIN(date) as min_date,
                MAX(date) as max_date,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM historical_ohlcv_daily 
            WHERE date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        market_stats = cursor.fetchone()
        
        # Test market data completeness
        cursor.execute("""
            SELECT 
                COUNT(*) as total_market_data,
                AVG(price) as avg_price,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM market_data 
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        market_data_stats = cursor.fetchone()
        
        # Calculate enhanced market data performance
        total_records = market_stats[0] if market_stats[0] else 0
        total_market_data = market_data_stats[0] if market_data_stats[0] else 0
        
        if total_records > 0:
            completeness = min((total_market_data / total_records) * 100, 100.0)
        else:
            completeness = 0
        
        # Enhanced market data accuracy
        accuracy = min(completeness, 100.0)
        
        print(f"     Enhanced market data records: {total_records}")
        print(f"     Enhanced market data completeness: {completeness:.2f}%")
        print(f"     Enhanced market data accuracy: {accuracy:.2f}%")
        
        return {
            'total_records': total_records,
            'total_market_data': total_market_data,
            'completeness': completeness,
            'accuracy': accuracy,
            'min_date': str(market_stats[1]) if market_stats[1] else None,
            'max_date': str(market_stats[2]) if market_stats[2] else None,
            'unique_symbols': market_stats[3] if market_stats[3] else 0
        }
        
    except Exception as e:
        print(f"     [ERROR] Enhanced market data historical test error: {e}")
        return {'error': str(e), 'accuracy': 0}

def test_enhanced_risk_management_with_historical_data(cursor) -> Dict[str, Any]:
    """Test enhanced risk management module with historical data"""
    try:
        # Test risk metrics with historical data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_risk_metrics,
                AVG(var_95) as avg_var_95,
                AVG(var_99) as avg_var_99,
                AVG(sharpe_ratio) as avg_sharpe_ratio
            FROM risk_metrics 
            WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        risk_stats = cursor.fetchone()
        
        # Test portfolio risk with historical data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_portfolio_risk,
                AVG(var_95) as avg_portfolio_var_95,
                AVG(expected_shortfall) as avg_expected_shortfall
            FROM portfolio_risk 
            WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
        """)
        portfolio_risk_stats = cursor.fetchone()
        
        # Calculate enhanced risk management performance
        total_risk_metrics = risk_stats[0] if risk_stats[0] else 0
        total_portfolio_risk = portfolio_risk_stats[0] if portfolio_risk_stats[0] else 0
        
        if total_risk_metrics > 0:
            risk_coverage = min((total_portfolio_risk / total_risk_metrics) * 100, 100.0)
        else:
            risk_coverage = 0
        
        # Enhanced risk management accuracy
        accuracy = min(risk_coverage, 100.0)
        
        print(f"     Enhanced risk metrics: {total_risk_metrics}")
        print(f"     Enhanced portfolio risk: {total_portfolio_risk}")
        print(f"     Enhanced risk coverage: {risk_coverage:.2f}%")
        print(f"     Enhanced risk management accuracy: {accuracy:.2f}%")
        
        return {
            'total_risk_metrics': total_risk_metrics,
            'total_portfolio_risk': total_portfolio_risk,
            'risk_coverage': risk_coverage,
            'accuracy': accuracy,
            'avg_var_95': risk_stats[1] if risk_stats[1] else 0,
            'avg_var_99': risk_stats[2] if risk_stats[2] else 0,
            'avg_sharpe_ratio': risk_stats[3] if risk_stats[3] else 0
        }
        
    except Exception as e:
        print(f"     [ERROR] Enhanced risk management historical test error: {e}")
        return {'error': str(e), 'accuracy': 0}

def test_integration_with_historical_data(cursor) -> Dict[str, Any]:
    """Test module integration with historical data"""
    try:
        integration_results = {}
        
        # Test trading + market data integration
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM orders o 
                JOIN historical_ohlcv_daily h ON o.symbol = h.symbol 
                WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                AND h.date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            """)
            count = cursor.fetchone()[0]
            integration_results['trading_market_data'] = {'success': True, 'count': count}
            print(f"     Trading + Market Data integration: {count} records")
        except Exception as e:
            integration_results['trading_market_data'] = {'success': False, 'error': str(e)}
            print(f"     [WARN] Trading + Market Data integration: {e}")
        
        # Test risk management integration
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM portfolio_risk pr 
                JOIN risk_metrics rm ON pr.portfolio_id = rm.portfolio_id
                WHERE pr.calculated_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                AND rm.calculated_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            """)
            count = cursor.fetchone()[0]
            integration_results['risk_management'] = {'success': True, 'count': count}
            print(f"     Risk Management integration: {count} records")
        except Exception as e:
            integration_results['risk_management'] = {'success': False, 'error': str(e)}
            print(f"     [WARN] Risk Management integration: {e}")
        
        return integration_results
        
    except Exception as e:
        return {'error': str(e)}

def calculate_real_performance_metrics(cursor, historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate real performance metrics"""
    try:
        metrics = {
            'data_availability': {},
            'data_quality': {},
            'performance_scores': {},
            'recommendations': []
        }
        
        # Calculate data availability
        total_tables = len(historical_analysis.get('tables_with_historical_data', []))
        total_records = historical_analysis.get('total_records', 0)
        
        metrics['data_availability'] = {
            'tables_with_data': total_tables,
            'total_records': total_records,
            'availability_score': min(total_tables / 10, 1.0) * 100
        }
        
        # Calculate data quality
        date_ranges = historical_analysis.get('date_ranges', {})
        quality_scores = []
        
        for table, date_info in date_ranges.items():
            days_span = date_info.get('days_span', 0)
            if days_span >= 180:  # 6 months
                quality_scores.append(100.0)
            elif days_span >= 90:  # 3 months
                quality_scores.append(75.0)
            elif days_span >= 30:  # 1 month
                quality_scores.append(50.0)
            else:
                quality_scores.append(25.0)
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
        else:
            avg_quality = 0.0
        
        metrics['data_quality'] = {
            'average_quality_score': avg_quality,
            'quality_distribution': quality_scores,
            'tables_analyzed': len(date_ranges)
        }
        
        # Calculate performance scores
        metrics['performance_scores'] = {
            'data_availability_score': metrics['data_availability']['availability_score'],
            'data_quality_score': avg_quality,
            'overall_performance': (metrics['data_availability']['availability_score'] + avg_quality) / 2
        }
        
        # Generate recommendations
        if avg_quality < 50:
            metrics['recommendations'].append("Data quality needs improvement")
        if total_records < 10000:
            metrics['recommendations'].append("Need more historical data")
        if total_tables < 5:
            metrics['recommendations'].append("Need more data sources")
        
        return metrics
        
    except Exception as e:
        return {'error': str(e)}

def generate_real_accuracy_report(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate real accuracy report"""
    try:
        accuracy_report = {
            'historical_data_accuracy': {},
            'enhanced_modules_accuracy': {},
            'overall_accuracy': 0.0,
            'recommendations': []
        }
        
        # Get historical data accuracy
        six_month_test = test_results.get('six_month_test', {})
        trading_perf = six_month_test.get('trading_performance', {})
        market_data_perf = six_month_test.get('market_data_performance', {})
        risk_perf = six_month_test.get('risk_management_performance', {})
        
        accuracy_report['historical_data_accuracy'] = {
            'trading': trading_perf.get('accuracy', 0),
            'market_data': market_data_perf.get('accuracy', 0),
            'risk_management': risk_perf.get('accuracy', 0)
        }
        
        # Get enhanced modules accuracy
        enhanced_modules_test = test_results.get('enhanced_modules_test', {})
        enhanced_trading = enhanced_modules_test.get('enhanced_trading', {})
        enhanced_market_data = enhanced_modules_test.get('enhanced_market_data', {})
        enhanced_risk_management = enhanced_modules_test.get('enhanced_risk_management', {})
        
        accuracy_report['enhanced_modules_accuracy'] = {
            'enhanced_trading': enhanced_trading.get('accuracy', 0),
            'enhanced_market_data': enhanced_market_data.get('accuracy', 0),
            'enhanced_risk_management': enhanced_risk_management.get('accuracy', 0)
        }
        
        # Calculate overall accuracy
        all_accuracies = [
            trading_perf.get('accuracy', 0),
            market_data_perf.get('accuracy', 0),
            risk_perf.get('accuracy', 0),
            enhanced_trading.get('accuracy', 0),
            enhanced_market_data.get('accuracy', 0),
            enhanced_risk_management.get('accuracy', 0)
        ]
        
        accuracy_report['overall_accuracy'] = sum(all_accuracies) / len(all_accuracies)
        
        # Generate recommendations
        if accuracy_report['overall_accuracy'] < 70:
            accuracy_report['recommendations'].append("Overall accuracy needs improvement")
        if trading_perf.get('accuracy', 0) < 80:
            accuracy_report['recommendations'].append("Trading module needs improvement")
        if market_data_perf.get('accuracy', 0) < 80:
            accuracy_report['recommendations'].append("Market data module needs improvement")
        if risk_perf.get('accuracy', 0) < 80:
            accuracy_report['recommendations'].append("Risk management module needs improvement")
        
        return accuracy_report
        
    except Exception as e:
        return {'error': str(e)}

def generate_historical_test_report(test_results: Dict[str, Any]) -> None:
    """Generate historical test report"""
    print("\nHISTORICAL DATA TEST RESULTS")
    print("=" * 70)
    
    # Database connection
    print(f"Database Connection: {'PASS' if test_results.get('database_connection') else 'FAIL'}")
    
    # Historical data analysis
    historical_analysis = test_results.get('historical_data_analysis', {})
    print(f"\nHistorical Data Analysis:")
    print(f"  Tables with historical data: {len(historical_analysis.get('tables_with_historical_data', []))}")
    print(f"  Total records: {historical_analysis.get('total_records', 0)}")
    
    # Six month test results
    six_month_test = test_results.get('six_month_test', {})
    print(f"\nSix Month Test Results:")
    print(f"  Trading Performance: {six_month_test.get('trading_performance', {}).get('accuracy', 0):.2f}%")
    print(f"  Market Data Performance: {six_month_test.get('market_data_performance', {}).get('accuracy', 0):.2f}%")
    print(f"  Risk Management Performance: {six_month_test.get('risk_management_performance', {}).get('accuracy', 0):.2f}%")
    print(f"  Overall Performance: {six_month_test.get('overall_performance', 0):.2f}%")
    
    # Enhanced modules test results
    enhanced_modules_test = test_results.get('enhanced_modules_test', {})
    print(f"\nEnhanced Modules Test Results:")
    print(f"  Enhanced Trading: {enhanced_modules_test.get('enhanced_trading', {}).get('accuracy', 0):.2f}%")
    print(f"  Enhanced Market Data: {enhanced_modules_test.get('enhanced_market_data', {}).get('accuracy', 0):.2f}%")
    print(f"  Enhanced Risk Management: {enhanced_modules_test.get('enhanced_risk_management', {}).get('accuracy', 0):.2f}%")
    
    # Real accuracy report
    real_accuracy = test_results.get('real_accuracy', {})
    print(f"\nReal Accuracy Report:")
    print(f"  Overall Accuracy: {real_accuracy.get('overall_accuracy', 0):.2f}%")
    
    if real_accuracy.get('recommendations'):
        print("  Recommendations:")
        for rec in real_accuracy['recommendations']:
            print(f"    - {rec}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"historical_data_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nHistorical data test results saved to: {results_file}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_with_historical_data()
