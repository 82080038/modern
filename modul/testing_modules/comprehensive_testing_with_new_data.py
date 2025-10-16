#!/usr/bin/env python3
"""
Comprehensive Testing with New Data
==================================

Script untuk melakukan testing komprehensif dengan data saham Indonesia
yang baru saja di-fetch dari Yahoo Finance.

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

def comprehensive_testing_with_new_data():
    """Comprehensive testing with new data"""
    print("COMPREHENSIVE TESTING WITH NEW DATA")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test results
    test_results = {
        'test_type': 'comprehensive_testing_with_new_data',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'data_analysis': {},
        'module_performance': {},
        'symbol_coverage': {},
        'data_quality': {},
        'production_readiness': {},
        'final_recommendations': {},
        'issues_fixed': [],
        'new_issues': []
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
        test_results['issues_fixed'].append(f'database_connection_error: {e}')
        return test_results
    
    # Step 1: Analyze new data comprehensively
    print("\n1. ANALYZING NEW DATA COMPREHENSIVELY")
    print("-" * 60)
    
    data_analysis = analyze_new_data_comprehensively(cursor)
    test_results['data_analysis'] = data_analysis
    print(f"   New data analysis completed")
    
    # Step 2: Test module performance with new data
    print("\n2. TESTING MODULE PERFORMANCE WITH NEW DATA")
    print("-" * 60)
    
    module_performance = test_module_performance_with_new_data(cursor)
    test_results['module_performance'] = module_performance
    print(f"   Module performance testing completed")
    
    # Step 3: Test symbol coverage with new data
    print("\n3. TESTING SYMBOL COVERAGE WITH NEW DATA")
    print("-" * 60)
    
    symbol_coverage = test_symbol_coverage_with_new_data(cursor)
    test_results['symbol_coverage'] = symbol_coverage
    print(f"   Symbol coverage testing completed")
    
    # Step 4: Test data quality with new data
    print("\n4. TESTING DATA QUALITY WITH NEW DATA")
    print("-" * 60)
    
    data_quality = test_data_quality_with_new_data(cursor)
    test_results['data_quality'] = data_quality
    print(f"   Data quality testing completed")
    
    # Step 5: Assess production readiness with new data
    print("\n5. ASSESSING PRODUCTION READINESS WITH NEW DATA")
    print("-" * 60)
    
    production_readiness = assess_production_readiness_with_new_data(test_results)
    test_results['production_readiness'] = production_readiness
    print(f"   Production readiness assessment completed")
    
    # Step 6: Generate final recommendations
    print("\n6. GENERATING FINAL RECOMMENDATIONS")
    print("-" * 60)
    
    final_recommendations = generate_final_recommendations_with_new_data(test_results)
    test_results['final_recommendations'] = final_recommendations
    print(f"   Final recommendations generated")
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    # Generate comprehensive report
    generate_comprehensive_report_with_new_data(test_results)
    
    return test_results

def analyze_new_data_comprehensively(cursor) -> Dict[str, Any]:
    """Analyze new data comprehensively"""
    try:
        analysis = {
            'trading_data': {},
            'market_data': {},
            'historical_data': {},
            'technical_data': {},
            'fundamental_data': {},
            'sentiment_data': {},
            'overall_analysis': {}
        }
    
        # Analyze trading data
        print("   Analyzing trading data...")
        try:
            cursor.execute("SELECT COUNT(*) FROM orders")
            orders_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trades")
            trades_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM orders")
            orders_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM trades")
            trades_symbols = cursor.fetchone()[0]
            
            analysis['trading_data'] = {
                'orders_count': orders_count,
                'trades_count': trades_count,
                'orders_symbols': orders_symbols,
                'trades_symbols': trades_symbols,
                'execution_rate': (trades_count / orders_count * 100) if orders_count > 0 else 0
            }
            print(f"     Trading data: {orders_count} orders, {trades_count} trades, {orders_symbols} symbols")
            
        except Exception as e:
            analysis['trading_data'] = {'error': str(e)}
            print(f"     [ERROR] Trading data analysis: {e}")
        
        # Analyze market data
        print("   Analyzing market data...")
        try:
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data")
            market_data_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily")
            historical_daily_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_ohlcv_daily")
            historical_daily_symbols = cursor.fetchone()[0]
            
            analysis['market_data'] = {
                'market_data_count': market_data_count,
                'market_data_symbols': market_data_symbols,
                'historical_daily_count': historical_daily_count,
                'historical_daily_symbols': historical_daily_symbols,
                'data_completeness': (market_data_count / historical_daily_count * 100) if historical_daily_count > 0 else 0
            }
            print(f"     Market data: {market_data_count} records, {market_data_symbols} symbols")
            print(f"     Historical daily: {historical_daily_count} records, {historical_daily_symbols} symbols")
            
        except Exception as e:
            analysis['market_data'] = {'error': str(e)}
            print(f"     [ERROR] Market data analysis: {e}")
        
        # Analyze historical data
        print("   Analyzing historical data...")
        try:
            cursor.execute("SELECT COUNT(*) FROM historical_data")
            historical_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_data")
            historical_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_1h")
            historical_1h_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_ohlcv_1h")
            historical_1h_symbols = cursor.fetchone()[0]
            
            analysis['historical_data'] = {
                'historical_count': historical_count,
                'historical_symbols': historical_symbols,
                'historical_1h_count': historical_1h_count,
                'historical_1h_symbols': historical_1h_symbols,
                'data_coverage': (historical_count + historical_1h_count) / 1000
            }
            print(f"     Historical data: {historical_count} records, {historical_symbols} symbols")
            print(f"     Historical 1h: {historical_1h_count} records, {historical_1h_symbols} symbols")
            
        except Exception as e:
            analysis['historical_data'] = {'error': str(e)}
            print(f"     [ERROR] Historical data analysis: {e}")
        
        # Analyze technical data
        print("   Analyzing technical data...")
        try:
            cursor.execute("SELECT COUNT(*) FROM technical_indicators")
            technical_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM technical_indicators")
            technical_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM indicators_trend")
            trend_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM indicators_trend")
            trend_symbols = cursor.fetchone()[0]
            
            analysis['technical_data'] = {
                'technical_count': technical_count,
                'technical_symbols': technical_symbols,
                'trend_count': trend_count,
                'trend_symbols': trend_symbols,
                'indicator_coverage': (technical_count + trend_count) / 1000
            }
            print(f"     Technical indicators: {technical_count} records, {technical_symbols} symbols")
            print(f"     Trend indicators: {trend_count} records, {trend_symbols} symbols")
            
        except Exception as e:
            analysis['technical_data'] = {'error': str(e)}
            print(f"     [ERROR] Technical data analysis: {e}")
        
        # Analyze fundamental data
        print("   Analyzing fundamental data...")
        try:
            cursor.execute("SELECT COUNT(*) FROM fundamental_data")
            fundamental_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM fundamental_data")
            fundamental_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM company_fundamentals")
            company_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM company_fundamentals")
            company_symbols = cursor.fetchone()[0]
            
            analysis['fundamental_data'] = {
                'fundamental_count': fundamental_count,
                'fundamental_symbols': fundamental_symbols,
                'company_count': company_count,
                'company_symbols': company_symbols,
                'fundamental_coverage': (fundamental_count + company_count) / 100
            }
            print(f"     Fundamental data: {fundamental_count} records, {fundamental_symbols} symbols")
            print(f"     Company fundamentals: {company_count} records, {company_symbols} symbols")
            
        except Exception as e:
            analysis['fundamental_data'] = {'error': str(e)}
            print(f"     [ERROR] Fundamental data analysis: {e}")
        
        # Analyze sentiment data
        print("   Analyzing sentiment data...")
        try:
            cursor.execute("SELECT COUNT(*) FROM sentiment_data")
            sentiment_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM sentiment_data")
            sentiment_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM news_sentiment")
            news_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM news_sentiment")
            news_symbols = cursor.fetchone()[0]
            
            analysis['sentiment_data'] = {
                'sentiment_count': sentiment_count,
                'sentiment_symbols': sentiment_symbols,
                'news_count': news_count,
                'news_symbols': news_symbols,
                'sentiment_coverage': (sentiment_count + news_count) / 100
            }
            print(f"     Sentiment data: {sentiment_count} records, {sentiment_symbols} symbols")
            print(f"     News sentiment: {news_count} records, {news_symbols} symbols")
            
        except Exception as e:
            analysis['sentiment_data'] = {'error': str(e)}
            print(f"     [ERROR] Sentiment data analysis: {e}")
        
        # Calculate overall analysis
        data_scores = []
        for data_type, data_info in analysis.items():
            if isinstance(data_info, dict) and 'error' not in data_info:
                if 'execution_rate' in data_info:
                    data_scores.append(data_info['execution_rate'])
                elif 'data_completeness' in data_info:
                    data_scores.append(data_info['data_completeness'])
                elif 'data_coverage' in data_info:
                    data_scores.append(data_info['data_coverage'])
                elif 'indicator_coverage' in data_info:
                    data_scores.append(data_info['indicator_coverage'])
                elif 'fundamental_coverage' in data_info:
                    data_scores.append(data_info['fundamental_coverage'])
                elif 'sentiment_coverage' in data_info:
                    data_scores.append(data_info['sentiment_coverage'])
        
        analysis['overall_analysis'] = {
            'data_scores': data_scores,
            'overall_score': sum(data_scores) / len(data_scores) if data_scores else 0
        }
        
        return analysis
        
    except Exception as e:
        return {'error': str(e)}

def test_module_performance_with_new_data(cursor) -> Dict[str, Any]:
    """Test module performance with new data"""
    try:
        performance = {
            'trading_module': {},
            'market_data_module': {},
            'risk_management_module': {},
            'technical_analysis_module': {},
            'fundamental_analysis_module': {},
            'sentiment_analysis_module': {},
            'overall_performance': {}
        }
        
        # Test trading module
        print("   Testing trading module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM orders WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_orders = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trades WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_trades = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM orders WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            orders_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM trades WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            trades_symbols = cursor.fetchone()[0]
            
            execution_rate = (recent_trades / recent_orders * 100) if recent_orders > 0 else 0
            symbol_coverage = (trades_symbols / orders_symbols * 100) if orders_symbols > 0 else 0
            
            performance['trading_module'] = {
                'recent_orders': recent_orders,
                'recent_trades': recent_trades,
                'orders_symbols': orders_symbols,
                'trades_symbols': trades_symbols,
                'execution_rate': execution_rate,
                'symbol_coverage': symbol_coverage,
                'performance_score': (execution_rate + symbol_coverage) / 2
            }
            print(f"     Trading module: {execution_rate:.1f}% execution rate, {symbol_coverage:.1f}% symbol coverage")
            
        except Exception as e:
            performance['trading_module'] = {'error': str(e)}
            print(f"     [ERROR] Trading module test: {e}")
        
        # Test market data module
        print("   Testing market data module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_market_data = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_historical = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            market_data_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_ohlcv_daily WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            historical_symbols = cursor.fetchone()[0]
            
            data_completeness = (recent_market_data / recent_historical * 100) if recent_historical > 0 else 0
            symbol_coverage = (market_data_symbols / historical_symbols * 100) if historical_symbols > 0 else 0
            
            performance['market_data_module'] = {
                'recent_market_data': recent_market_data,
                'recent_historical': recent_historical,
                'market_data_symbols': market_data_symbols,
                'historical_symbols': historical_symbols,
                'data_completeness': data_completeness,
                'symbol_coverage': symbol_coverage,
                'performance_score': (data_completeness + symbol_coverage) / 2
            }
            print(f"     Market data module: {data_completeness:.1f}% completeness, {symbol_coverage:.1f}% symbol coverage")
            
        except Exception as e:
            performance['market_data_module'] = {'error': str(e)}
            print(f"     [ERROR] Market data module test: {e}")
        
        # Test risk management module
        print("   Testing risk management module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM risk_metrics WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_risk_metrics = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM portfolio_risk WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_portfolio_risk = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM risk_metrics WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            risk_metrics_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM portfolio_risk WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            portfolio_risk_symbols = cursor.fetchone()[0]
            
            risk_coverage = (recent_portfolio_risk / recent_risk_metrics * 100) if recent_risk_metrics > 0 else 0
            symbol_coverage = (portfolio_risk_symbols / risk_metrics_symbols * 100) if risk_metrics_symbols > 0 else 0
            
            performance['risk_management_module'] = {
                'recent_risk_metrics': recent_risk_metrics,
                'recent_portfolio_risk': recent_portfolio_risk,
                'risk_metrics_symbols': risk_metrics_symbols,
                'portfolio_risk_symbols': portfolio_risk_symbols,
                'risk_coverage': risk_coverage,
                'symbol_coverage': symbol_coverage,
                'performance_score': (risk_coverage + symbol_coverage) / 2
            }
            print(f"     Risk management module: {risk_coverage:.1f}% coverage, {symbol_coverage:.1f}% symbol coverage")
            
        except Exception as e:
            performance['risk_management_module'] = {'error': str(e)}
            print(f"     [ERROR] Risk management module test: {e}")
        
        # Test technical analysis module
        print("   Testing technical analysis module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_technical = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM indicators_trend WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_trends = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM technical_indicators WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            technical_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM indicators_trend WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            trend_symbols = cursor.fetchone()[0]
            
            indicator_coverage = (recent_trends / recent_technical * 100) if recent_technical > 0 else 0
            symbol_coverage = (trend_symbols / technical_symbols * 100) if technical_symbols > 0 else 0
            
            performance['technical_analysis_module'] = {
                'recent_technical': recent_technical,
                'recent_trends': recent_trends,
                'technical_symbols': technical_symbols,
                'trend_symbols': trend_symbols,
                'indicator_coverage': indicator_coverage,
                'symbol_coverage': symbol_coverage,
                'performance_score': (indicator_coverage + symbol_coverage) / 2
            }
            print(f"     Technical analysis module: {indicator_coverage:.1f}% coverage, {symbol_coverage:.1f}% symbol coverage")
            
        except Exception as e:
            performance['technical_analysis_module'] = {'error': str(e)}
            print(f"     [ERROR] Technical analysis module test: {e}")
        
        # Test fundamental analysis module
        print("   Testing fundamental analysis module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_fundamental = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM company_fundamentals WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_company = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM fundamental_data WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            fundamental_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM company_fundamentals WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            company_symbols = cursor.fetchone()[0]
            
            fundamental_coverage = (recent_company / recent_fundamental * 100) if recent_fundamental > 0 else 0
            symbol_coverage = (company_symbols / fundamental_symbols * 100) if fundamental_symbols > 0 else 0
            
            performance['fundamental_analysis_module'] = {
                'recent_fundamental': recent_fundamental,
                'recent_company': recent_company,
                'fundamental_symbols': fundamental_symbols,
                'company_symbols': company_symbols,
                'fundamental_coverage': fundamental_coverage,
                'symbol_coverage': symbol_coverage,
                'performance_score': (fundamental_coverage + symbol_coverage) / 2
            }
            print(f"     Fundamental analysis module: {fundamental_coverage:.1f}% coverage, {symbol_coverage:.1f}% symbol coverage")
            
        except Exception as e:
            performance['fundamental_analysis_module'] = {'error': str(e)}
            print(f"     [ERROR] Fundamental analysis module test: {e}")
        
        # Test sentiment analysis module
        print("   Testing sentiment analysis module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE published_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_sentiment = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM news_sentiment WHERE published_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            recent_news = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM sentiment_data WHERE published_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            sentiment_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM news_sentiment WHERE published_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            news_symbols = cursor.fetchone()[0]
            
            sentiment_coverage = (recent_news / recent_sentiment * 100) if recent_sentiment > 0 else 0
            symbol_coverage = (news_symbols / sentiment_symbols * 100) if sentiment_symbols > 0 else 0
            
            performance['sentiment_analysis_module'] = {
                'recent_sentiment': recent_sentiment,
                'recent_news': recent_news,
                'sentiment_symbols': sentiment_symbols,
                'news_symbols': news_symbols,
                'sentiment_coverage': sentiment_coverage,
                'symbol_coverage': symbol_coverage,
                'performance_score': (sentiment_coverage + symbol_coverage) / 2
            }
            print(f"     Sentiment analysis module: {sentiment_coverage:.1f}% coverage, {symbol_coverage:.1f}% symbol coverage")
            
        except Exception as e:
            performance['sentiment_analysis_module'] = {'error': str(e)}
            print(f"     [ERROR] Sentiment analysis module test: {e}")
        
        # Calculate overall performance
        performance_scores = []
        for module_name, module_data in performance.items():
            if isinstance(module_data, dict) and 'performance_score' in module_data:
                performance_scores.append(module_data['performance_score'])
        
        performance['overall_performance'] = {
            'performance_scores': performance_scores,
            'overall_score': sum(performance_scores) / len(performance_scores) if performance_scores else 0
        }
        
        return performance
        
    except Exception as e:
        return {'error': str(e)}

def test_symbol_coverage_with_new_data(cursor) -> Dict[str, Any]:
    """Test symbol coverage with new data"""
    try:
        coverage = {
            'unique_symbols': set(),
            'symbol_counts': {},
            'coverage_analysis': {}
        }
        
        # Get unique symbols from all tables
        print("   Testing symbol coverage with new data...")
        try:
            # Get symbols from orders
            cursor.execute("SELECT DISTINCT symbol FROM orders WHERE symbol IS NOT NULL")
            order_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(order_symbols)
            coverage['symbol_counts']['orders'] = len(order_symbols)
            
            # Get symbols from trades
            cursor.execute("SELECT DISTINCT symbol FROM trades WHERE symbol IS NOT NULL")
            trade_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(trade_symbols)
            coverage['symbol_counts']['trades'] = len(trade_symbols)
            
            # Get symbols from market_data
            cursor.execute("SELECT DISTINCT symbol FROM market_data WHERE symbol IS NOT NULL")
            market_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(market_symbols)
            coverage['symbol_counts']['market_data'] = len(market_symbols)
            
            # Get symbols from historical_ohlcv_daily
            cursor.execute("SELECT DISTINCT symbol FROM historical_ohlcv_daily WHERE symbol IS NOT NULL")
            historical_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(historical_symbols)
            coverage['symbol_counts']['historical'] = len(historical_symbols)
            
            # Get symbols from technical_indicators
            cursor.execute("SELECT DISTINCT symbol FROM technical_indicators WHERE symbol IS NOT NULL")
            technical_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(technical_symbols)
            coverage['symbol_counts']['technical'] = len(technical_symbols)
            
            # Get symbols from fundamental_data
            cursor.execute("SELECT DISTINCT symbol FROM fundamental_data WHERE symbol IS NOT NULL")
            fundamental_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(fundamental_symbols)
            coverage['symbol_counts']['fundamental'] = len(fundamental_symbols)
            
            # Get symbols from sentiment_data
            cursor.execute("SELECT DISTINCT symbol FROM sentiment_data WHERE symbol IS NOT NULL")
            sentiment_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(sentiment_symbols)
            coverage['symbol_counts']['sentiment'] = len(sentiment_symbols)
            
        except Exception as e:
            print(f"     [ERROR] Symbol coverage test: {e}")
        
        # Convert set to list for JSON serialization
        coverage['unique_symbols'] = list(coverage['unique_symbols'])
        
        # Analyze coverage
        unique_symbol_count = len(coverage['unique_symbols'])
        coverage['coverage_analysis'] = {
            'unique_symbol_count': unique_symbol_count,
            'coverage_score': min(unique_symbol_count / 10 * 100, 100),
            'sufficient_for_testing': unique_symbol_count >= 5,
            'recommended_symbols': ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'UNVR.JK']
        }
        
        print(f"     Unique symbols: {unique_symbol_count}")
        print(f"     Coverage score: {coverage['coverage_analysis']['coverage_score']:.1f}%")
        print(f"     Sufficient for testing: {coverage['coverage_analysis']['sufficient_for_testing']}")
        
        return coverage
        
    except Exception as e:
        return {'error': str(e)}

def test_data_quality_with_new_data(cursor) -> Dict[str, Any]:
    """Test data quality with new data"""
    try:
        quality = {
            'completeness_scores': {},
            'consistency_scores': {},
            'timeliness_scores': {},
            'overall_quality_score': 0.0
        }
        
        # Test completeness
        print("   Testing data completeness with new data...")
        try:
            # Check orders completeness
            cursor.execute("SELECT COUNT(*) FROM orders WHERE symbol IS NOT NULL AND created_at IS NOT NULL")
            orders_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM orders")
            orders_total = cursor.fetchone()[0]
            orders_completeness = (orders_complete / orders_total * 100) if orders_total > 0 else 0
            
            # Check trades completeness
            cursor.execute("SELECT COUNT(*) FROM trades WHERE symbol IS NOT NULL AND executed_at IS NOT NULL")
            trades_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trades")
            trades_total = cursor.fetchone()[0]
            trades_completeness = (trades_complete / trades_total * 100) if trades_total > 0 else 0
            
            # Check market_data completeness
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol IS NOT NULL AND timestamp IS NOT NULL")
            market_data_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_total = cursor.fetchone()[0]
            market_data_completeness = (market_data_complete / market_data_total * 100) if market_data_total > 0 else 0
            
            quality['completeness_scores'] = {
                'orders': orders_completeness,
                'trades': trades_completeness,
                'market_data': market_data_completeness
            }
            
            print(f"     Orders completeness: {orders_completeness:.1f}%")
            print(f"     Trades completeness: {trades_completeness:.1f}%")
            print(f"     Market data completeness: {market_data_completeness:.1f}%")
            
        except Exception as e:
            quality['completeness_scores'] = {'error': str(e)}
            print(f"     [ERROR] Completeness test: {e}")
        
        # Test consistency
        print("   Testing data consistency with new data...")
        try:
            # Check symbol consistency
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM orders")
            orders_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM trades")
            trades_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data")
            market_data_symbols = cursor.fetchone()[0]
            
            # Calculate consistency score
            symbol_counts = [orders_symbols, trades_symbols, market_data_symbols]
            consistency_score = min(symbol_counts) / max(symbol_counts) * 100 if max(symbol_counts) > 0 else 0
            
            quality['consistency_scores'] = {
                'orders_symbols': orders_symbols,
                'trades_symbols': trades_symbols,
                'market_data_symbols': market_data_symbols,
                'consistency_score': consistency_score
            }
            
            print(f"     Orders symbols: {orders_symbols}")
            print(f"     Trades symbols: {trades_symbols}")
            print(f"     Market data symbols: {market_data_symbols}")
            print(f"     Consistency score: {consistency_score:.1f}%")
            
        except Exception as e:
            quality['consistency_scores'] = {'error': str(e)}
            print(f"     [ERROR] Consistency test: {e}")
        
        # Test timeliness
        print("   Testing data timeliness with new data...")
        try:
            # Check recent data
            cursor.execute("SELECT COUNT(*) FROM orders WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            recent_orders = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trades WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            recent_trades = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            recent_market_data = cursor.fetchone()[0]
            
            # Calculate timeliness score
            recent_data_total = recent_orders + recent_trades + recent_market_data
            timeliness_score = min(recent_data_total / 100, 100) if recent_data_total > 0 else 0
            
            quality['timeliness_scores'] = {
                'recent_orders': recent_orders,
                'recent_trades': recent_trades,
                'recent_market_data': recent_market_data,
                'timeliness_score': timeliness_score
            }
            
            print(f"     Recent orders (7 days): {recent_orders}")
            print(f"     Recent trades (7 days): {recent_trades}")
            print(f"     Recent market data (7 days): {recent_market_data}")
            print(f"     Timeliness score: {timeliness_score:.1f}%")
            
        except Exception as e:
            quality['timeliness_scores'] = {'error': str(e)}
            print(f"     [ERROR] Timeliness test: {e}")
        
        # Calculate overall quality score
        completeness_avg = sum(quality['completeness_scores'].values()) / len(quality['completeness_scores']) if quality['completeness_scores'] else 0
        consistency_score = quality['consistency_scores'].get('consistency_score', 0)
        timeliness_score = quality['timeliness_scores'].get('timeliness_score', 0)
        
        quality['overall_quality_score'] = (completeness_avg + consistency_score + timeliness_score) / 3
        
        return quality
        
    except Exception as e:
        return {'error': str(e)}

def assess_production_readiness_with_new_data(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Assess production readiness with new data"""
    try:
        readiness = {
            'readiness_status': '',
            'deployment_strategy': '',
            'monitoring_requirements': {},
            'risk_level': '',
            'recommendations': []
        }
        
        # Analyze module performance
        module_performance = test_results.get('module_performance', {})
        overall_performance = module_performance.get('overall_performance', {})
        overall_score = overall_performance.get('overall_score', 0)
        
        # Analyze symbol coverage
        symbol_coverage = test_results.get('symbol_coverage', {})
        coverage_analysis = symbol_coverage.get('coverage_analysis', {})
        coverage_score = coverage_analysis.get('coverage_score', 0)
        sufficient_for_testing = coverage_analysis.get('sufficient_for_testing', False)
        
        # Analyze data quality
        data_quality = test_results.get('data_quality', {})
        overall_quality_score = data_quality.get('overall_quality_score', 0)
        
        # Determine readiness status
        if overall_score >= 80 and coverage_score >= 80 and overall_quality_score >= 80:
            readiness['readiness_status'] = 'READY_FOR_PRODUCTION'
            readiness['deployment_strategy'] = 'IMMEDIATE_DEPLOYMENT'
            readiness['risk_level'] = 'LOW'
        elif overall_score >= 60 and coverage_score >= 60 and overall_quality_score >= 60:
            readiness['readiness_status'] = 'READY_WITH_MONITORING'
            readiness['deployment_strategy'] = 'GRADUAL_DEPLOYMENT'
            readiness['risk_level'] = 'MEDIUM'
        elif overall_score >= 40 and coverage_score >= 40 and overall_quality_score >= 40:
            readiness['readiness_status'] = 'READY_WITH_IMPROVEMENTS'
            readiness['deployment_strategy'] = 'PHASED_DEPLOYMENT'
            readiness['risk_level'] = 'HIGH'
        else:
            readiness['readiness_status'] = 'NOT_READY'
            readiness['deployment_strategy'] = 'DEVELOPMENT_CONTINUATION'
            readiness['risk_level'] = 'CRITICAL'
        
        # Set monitoring requirements
        readiness['monitoring_requirements'] = {
            'trading_module': 'LOW' if module_performance.get('trading_module', {}).get('performance_score', 0) >= 80 else 'HIGH',
            'market_data_module': 'LOW' if module_performance.get('market_data_module', {}).get('performance_score', 0) >= 80 else 'HIGH',
            'risk_management_module': 'LOW' if module_performance.get('risk_management_module', {}).get('performance_score', 0) >= 80 else 'HIGH',
            'technical_analysis_module': 'LOW' if module_performance.get('technical_analysis_module', {}).get('performance_score', 0) >= 80 else 'HIGH',
            'fundamental_analysis_module': 'LOW' if module_performance.get('fundamental_analysis_module', {}).get('performance_score', 0) >= 80 else 'HIGH',
            'sentiment_analysis_module': 'LOW' if module_performance.get('sentiment_analysis_module', {}).get('performance_score', 0) >= 80 else 'HIGH'
        }
        
        # Generate recommendations
        if overall_score < 80:
            readiness['recommendations'].append(f"Improve overall performance from {overall_score:.1f}% to 80%+")
        
        if coverage_score < 80:
            readiness['recommendations'].append(f"Improve symbol coverage from {coverage_score:.1f}% to 80%+")
        
        if overall_quality_score < 80:
            readiness['recommendations'].append(f"Improve data quality from {overall_quality_score:.1f}% to 80%+")
        
        if not sufficient_for_testing:
            readiness['recommendations'].append("Add more symbols for comprehensive testing")
        
        if readiness['risk_level'] in ['HIGH', 'CRITICAL']:
            readiness['recommendations'].append("Implement comprehensive monitoring and rollback plans")
        
        return readiness
        
    except Exception as e:
        return {'error': str(e)}

def generate_final_recommendations_with_new_data(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final recommendations with new data"""
    try:
        recommendations = {
            'deployment_plan': {},
            'monitoring_strategy': {},
            'maintenance_plan': {},
            'success_metrics': {},
            'next_steps': []
        }
        
        # Analyze test results
        production_readiness = test_results.get('production_readiness', {})
        readiness_status = production_readiness.get('readiness_status', 'UNKNOWN')
        
        # Deployment plan
        if readiness_status == 'READY_FOR_PRODUCTION':
            recommendations['deployment_plan'] = {
                'phase': 'IMMEDIATE_DEPLOYMENT',
                'modules_to_deploy': 'ALL_MODULES',
                'rollback_plan': 'STANDARD',
                'monitoring': 'STANDARD'
            }
        elif readiness_status == 'READY_WITH_MONITORING':
            recommendations['deployment_plan'] = {
                'phase': 'GRADUAL_DEPLOYMENT',
                'modules_to_deploy': 'WORKING_MODULES',
                'rollback_plan': 'ENHANCED',
                'monitoring': 'ENHANCED'
            }
        else:
            recommendations['deployment_plan'] = {
                'phase': 'DEVELOPMENT_CONTINUATION',
                'modules_to_deploy': 'NONE',
                'rollback_plan': 'COMPREHENSIVE',
                'monitoring': 'INTENSIVE'
            }
        
        # Monitoring strategy
        recommendations['monitoring_strategy'] = {
            'frequency': 'REAL_TIME' if readiness_status == 'READY_FOR_PRODUCTION' else 'FREQUENT',
            'alerts': 'STANDARD' if readiness_status == 'READY_FOR_PRODUCTION' else 'ENHANCED',
            'reporting': 'DAILY' if readiness_status == 'READY_FOR_PRODUCTION' else 'HOURLY'
        }
        
        # Maintenance plan
        recommendations['maintenance_plan'] = {
            'schedule': 'WEEKLY' if readiness_status == 'READY_FOR_PRODUCTION' else 'DAILY',
            'updates': 'MONTHLY' if readiness_status == 'READY_FOR_PRODUCTION' else 'WEEKLY',
            'backups': 'DAILY' if readiness_status == 'READY_FOR_PRODUCTION' else 'HOURLY'
        }
        
        # Success metrics
        recommendations['success_metrics'] = {
            'performance_target': 80.0,
            'uptime_target': 99.0,
            'error_rate_target': 1.0,
            'response_time_target': 1000.0
        }
        
        # Next steps
        if readiness_status == 'READY_FOR_PRODUCTION':
            recommendations['next_steps'] = [
                "Deploy all modules immediately",
                "Monitor system performance",
                "Maintain system health",
                "Plan for future enhancements"
            ]
        elif readiness_status == 'READY_WITH_MONITORING':
            recommendations['next_steps'] = [
                "Deploy working modules with monitoring",
                "Fix problematic modules",
                "Monitor system performance closely",
                "Plan for full deployment"
            ]
        else:
            recommendations['next_steps'] = [
                "Fix all problematic modules",
                "Improve overall performance",
                "Continue development",
                "Plan deployment after fixes"
            ]
        
        return recommendations
        
    except Exception as e:
        return {'error': str(e)}

def generate_comprehensive_report_with_new_data(test_results: Dict[str, Any]) -> None:
    """Generate comprehensive report with new data"""
    print("\nCOMPREHENSIVE TESTING REPORT WITH NEW DATA")
    print("=" * 80)
    
    # Data analysis
    data_analysis = test_results.get('data_analysis', {})
    print(f"Data Analysis:")
    print(f"  Overall Score: {data_analysis.get('overall_analysis', {}).get('overall_score', 0):.1f}%")
    
    trading_data = data_analysis.get('trading_data', {})
    print(f"  Trading Data: {trading_data.get('orders_count', 0)} orders, {trading_data.get('trades_count', 0)} trades")
    print(f"    Execution Rate: {trading_data.get('execution_rate', 0):.1f}%")
    
    market_data = data_analysis.get('market_data', {})
    print(f"  Market Data: {market_data.get('market_data_count', 0)} records, {market_data.get('market_data_symbols', 0)} symbols")
    print(f"    Data Completeness: {market_data.get('data_completeness', 0):.1f}%")
    
    # Module performance
    module_performance = test_results.get('module_performance', {})
    print(f"\nModule Performance:")
    print(f"  Overall Performance: {module_performance.get('overall_performance', {}).get('overall_score', 0):.1f}%")
    
    for module_name, module_data in module_performance.items():
        if isinstance(module_data, dict) and 'performance_score' in module_data:
            print(f"  {module_name}: {module_data['performance_score']:.1f}%")
    
    # Symbol coverage
    symbol_coverage = test_results.get('symbol_coverage', {})
    print(f"\nSymbol Coverage:")
    print(f"  Unique Symbols: {len(symbol_coverage.get('unique_symbols', []))}")
    print(f"  Coverage Score: {symbol_coverage.get('coverage_analysis', {}).get('coverage_score', 0):.1f}%")
    print(f"  Sufficient for Testing: {symbol_coverage.get('coverage_analysis', {}).get('sufficient_for_testing', False)}")
    
    # Data quality
    data_quality = test_results.get('data_quality', {})
    print(f"\nData Quality:")
    print(f"  Overall Quality: {data_quality.get('overall_quality_score', 0):.1f}%")
    
    completeness_scores = data_quality.get('completeness_scores', {})
    print(f"  Completeness Scores:")
    for table, score in completeness_scores.items():
        if isinstance(score, (int, float)):
            print(f"    {table}: {score:.1f}%")
    
    # Production readiness
    production_readiness = test_results.get('production_readiness', {})
    print(f"\nProduction Readiness:")
    print(f"  Status: {production_readiness.get('readiness_status', 'UNKNOWN')}")
    print(f"  Deployment Strategy: {production_readiness.get('deployment_strategy', 'UNKNOWN')}")
    print(f"  Risk Level: {production_readiness.get('risk_level', 'UNKNOWN')}")
    
    recommendations = production_readiness.get('recommendations', [])
    if recommendations:
        print(f"  Recommendations:")
        for rec in recommendations:
            print(f"    - {rec}")
    
    # Final recommendations
    final_recommendations = test_results.get('final_recommendations', {})
    print(f"\nFinal Recommendations:")
    deployment_plan = final_recommendations.get('deployment_plan', {})
    print(f"  Deployment Phase: {deployment_plan.get('phase', 'UNKNOWN')}")
    print(f"  Modules to Deploy: {deployment_plan.get('modules_to_deploy', 'UNKNOWN')}")
    
    next_steps = final_recommendations.get('next_steps', [])
    if next_steps:
        print(f"  Next Steps:")
        for step in next_steps:
            print(f"    - {step}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"comprehensive_testing_with_new_data_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nComprehensive testing results saved to: {results_file}")
    print(f"Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    comprehensive_testing_with_new_data()
