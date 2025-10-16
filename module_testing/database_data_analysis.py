#!/usr/bin/env python3
"""
Database Data Analysis
=====================

Script untuk menganalisis data di database dan memastikan ada data yang cukup
untuk testing dengan multiple saham, bukan hanya 1 saham saja.

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

def database_data_analysis():
    """Database data analysis"""
    print("DATABASE DATA ANALYSIS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Analysis results
    analysis_results = {
        'test_type': 'database_data_analysis',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'data_availability': {},
        'symbol_coverage': {},
        'data_quality': {},
        'recommendations': {},
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
        analysis_results['database_connection'] = True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        analysis_results['issues_fixed'].append(f'database_connection_error: {e}')
        return analysis_results
    
    # Step 1: Analyze data availability
    print("\n1. ANALYZING DATA AVAILABILITY")
    print("-" * 60)
    
    data_availability = analyze_data_availability(cursor)
    analysis_results['data_availability'] = data_availability
    print(f"   Data availability analysis completed")
    
    # Step 2: Analyze symbol coverage
    print("\n2. ANALYZING SYMBOL COVERAGE")
    print("-" * 60)
    
    symbol_coverage = analyze_symbol_coverage(cursor)
    analysis_results['symbol_coverage'] = symbol_coverage
    print(f"   Symbol coverage analysis completed")
    
    # Step 3: Analyze data quality
    print("\n3. ANALYZING DATA QUALITY")
    print("-" * 60)
    
    data_quality = analyze_data_quality(cursor)
    analysis_results['data_quality'] = data_quality
    print(f"   Data quality analysis completed")
    
    # Step 4: Generate recommendations
    print("\n4. GENERATING RECOMMENDATIONS")
    print("-" * 60)
    
    recommendations = generate_data_recommendations(analysis_results)
    analysis_results['recommendations'] = recommendations
    print(f"   Recommendations generated")
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    # Generate comprehensive report
    generate_analysis_report(analysis_results)
    
    return analysis_results

def analyze_data_availability(cursor) -> Dict[str, Any]:
    """Analyze data availability"""
    try:
        availability = {
            'trading_data': {},
            'market_data': {},
            'historical_data': {},
            'technical_data': {},
            'fundamental_data': {},
            'sentiment_data': {},
            'overall_availability': 0.0
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
            
            availability['trading_data'] = {
                'orders_count': orders_count,
                'trades_count': trades_count,
                'orders_symbols': orders_symbols,
                'trades_symbols': trades_symbols,
                'availability_score': min((orders_count + trades_count) / 100, 100)
            }
            print(f"     Trading data: {orders_count} orders, {trades_count} trades, {orders_symbols} symbols")
            
        except Exception as e:
            availability['trading_data'] = {'error': str(e)}
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
            
            availability['market_data'] = {
                'market_data_count': market_data_count,
                'market_data_symbols': market_data_symbols,
                'historical_daily_count': historical_daily_count,
                'historical_daily_symbols': historical_daily_symbols,
                'availability_score': min((market_data_count + historical_daily_count) / 1000, 100)
            }
            print(f"     Market data: {market_data_count} records, {market_data_symbols} symbols")
            print(f"     Historical daily: {historical_daily_count} records, {historical_daily_symbols} symbols")
            
        except Exception as e:
            availability['market_data'] = {'error': str(e)}
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
            
            availability['historical_data'] = {
                'historical_count': historical_count,
                'historical_symbols': historical_symbols,
                'historical_1h_count': historical_1h_count,
                'historical_1h_symbols': historical_1h_symbols,
                'availability_score': min((historical_count + historical_1h_count) / 1000, 100)
            }
            print(f"     Historical data: {historical_count} records, {historical_symbols} symbols")
            print(f"     Historical 1h: {historical_1h_count} records, {historical_1h_symbols} symbols")
            
        except Exception as e:
            availability['historical_data'] = {'error': str(e)}
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
            
            availability['technical_data'] = {
                'technical_count': technical_count,
                'technical_symbols': technical_symbols,
                'trend_count': trend_count,
                'trend_symbols': trend_symbols,
                'availability_score': min((technical_count + trend_count) / 1000, 100)
            }
            print(f"     Technical indicators: {technical_count} records, {technical_symbols} symbols")
            print(f"     Trend indicators: {trend_count} records, {trend_symbols} symbols")
            
        except Exception as e:
            availability['technical_data'] = {'error': str(e)}
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
            
            availability['fundamental_data'] = {
                'fundamental_count': fundamental_count,
                'fundamental_symbols': fundamental_symbols,
                'company_count': company_count,
                'company_symbols': company_symbols,
                'availability_score': min((fundamental_count + company_count) / 100, 100)
            }
            print(f"     Fundamental data: {fundamental_count} records, {fundamental_symbols} symbols")
            print(f"     Company fundamentals: {company_count} records, {company_symbols} symbols")
            
        except Exception as e:
            availability['fundamental_data'] = {'error': str(e)}
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
            
            availability['sentiment_data'] = {
                'sentiment_count': sentiment_count,
                'sentiment_symbols': sentiment_symbols,
                'news_count': news_count,
                'news_symbols': news_symbols,
                'availability_score': min((sentiment_count + news_count) / 100, 100)
            }
            print(f"     Sentiment data: {sentiment_count} records, {sentiment_symbols} symbols")
            print(f"     News sentiment: {news_count} records, {news_symbols} symbols")
            
        except Exception as e:
            availability['sentiment_data'] = {'error': str(e)}
            print(f"     [ERROR] Sentiment data analysis: {e}")
        
        # Calculate overall availability
        availability_scores = [
            availability['trading_data'].get('availability_score', 0),
            availability['market_data'].get('availability_score', 0),
            availability['historical_data'].get('availability_score', 0),
            availability['technical_data'].get('availability_score', 0),
            availability['fundamental_data'].get('availability_score', 0),
            availability['sentiment_data'].get('availability_score', 0)
        ]
        
        availability['overall_availability'] = sum(availability_scores) / len(availability_scores)
        
        return availability
        
    except Exception as e:
        return {'error': str(e)}

def analyze_symbol_coverage(cursor) -> Dict[str, Any]:
    """Analyze symbol coverage"""
    try:
        coverage = {
            'unique_symbols': set(),
            'symbol_counts': {},
            'symbol_coverage_score': 0.0,
            'recommended_symbols': []
        }
        
        # Get unique symbols from all tables
        print("   Analyzing symbol coverage...")
        try:
            # Get symbols from orders
            cursor.execute("SELECT DISTINCT symbol FROM orders WHERE symbol IS NOT NULL")
            order_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(order_symbols)
            print(f"     Order symbols: {len(order_symbols)} - {order_symbols[:10]}")
            
            # Get symbols from trades
            cursor.execute("SELECT DISTINCT symbol FROM trades WHERE symbol IS NOT NULL")
            trade_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(trade_symbols)
            print(f"     Trade symbols: {len(trade_symbols)} - {trade_symbols[:10]}")
            
            # Get symbols from market_data
            cursor.execute("SELECT DISTINCT symbol FROM market_data WHERE symbol IS NOT NULL")
            market_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(market_symbols)
            print(f"     Market data symbols: {len(market_symbols)} - {market_symbols[:10]}")
            
            # Get symbols from historical_ohlcv_daily
            cursor.execute("SELECT DISTINCT symbol FROM historical_ohlcv_daily WHERE symbol IS NOT NULL")
            historical_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(historical_symbols)
            print(f"     Historical symbols: {len(historical_symbols)} - {historical_symbols[:10]}")
            
            # Get symbols from technical_indicators
            cursor.execute("SELECT DISTINCT symbol FROM technical_indicators WHERE symbol IS NOT NULL")
            technical_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(technical_symbols)
            print(f"     Technical symbols: {len(technical_symbols)} - {technical_symbols[:10]}")
            
            # Get symbols from fundamental_data
            cursor.execute("SELECT DISTINCT symbol FROM fundamental_data WHERE symbol IS NOT NULL")
            fundamental_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(fundamental_symbols)
            print(f"     Fundamental symbols: {len(fundamental_symbols)} - {fundamental_symbols[:10]}")
            
            # Get symbols from sentiment_data
            cursor.execute("SELECT DISTINCT symbol FROM sentiment_data WHERE symbol IS NOT NULL")
            sentiment_symbols = [row[0] for row in cursor.fetchall()]
            coverage['unique_symbols'].update(sentiment_symbols)
            print(f"     Sentiment symbols: {len(sentiment_symbols)} - {sentiment_symbols[:10]}")
            
        except Exception as e:
            print(f"     [ERROR] Symbol coverage analysis: {e}")
        
        # Convert set to list for JSON serialization
        coverage['unique_symbols'] = list(coverage['unique_symbols'])
        
        # Calculate symbol coverage score
        unique_symbol_count = len(coverage['unique_symbols'])
        if unique_symbol_count >= 10:
            coverage['symbol_coverage_score'] = 100.0
        elif unique_symbol_count >= 5:
            coverage['symbol_coverage_score'] = 80.0
        elif unique_symbol_count >= 3:
            coverage['symbol_coverage_score'] = 60.0
        elif unique_symbol_count >= 1:
            coverage['symbol_coverage_score'] = 40.0
        else:
            coverage['symbol_coverage_score'] = 0.0
        
        # Generate recommended symbols
        coverage['recommended_symbols'] = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
            'NVDA', 'META', 'NFLX', 'AMD', 'INTC',
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO'
        ]
        
        print(f"     Total unique symbols: {unique_symbol_count}")
        print(f"     Symbol coverage score: {coverage['symbol_coverage_score']:.1f}%")
        
        return coverage
        
    except Exception as e:
        return {'error': str(e)}

def analyze_data_quality(cursor) -> Dict[str, Any]:
    """Analyze data quality"""
    try:
        quality = {
            'completeness_scores': {},
            'consistency_scores': {},
            'timeliness_scores': {},
            'overall_quality_score': 0.0
        }
        
        # Analyze completeness
        print("   Analyzing data completeness...")
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
            print(f"     [ERROR] Completeness analysis: {e}")
        
        # Analyze consistency
        print("   Analyzing data consistency...")
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
            print(f"     [ERROR] Consistency analysis: {e}")
        
        # Analyze timeliness
        print("   Analyzing data timeliness...")
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
            print(f"     [ERROR] Timeliness analysis: {e}")
        
        # Calculate overall quality score
        completeness_avg = sum(quality['completeness_scores'].values()) / len(quality['completeness_scores']) if quality['completeness_scores'] else 0
        consistency_score = quality['consistency_scores'].get('consistency_score', 0)
        timeliness_score = quality['timeliness_scores'].get('timeliness_score', 0)
        
        quality['overall_quality_score'] = (completeness_avg + consistency_score + timeliness_score) / 3
        
        return quality
        
    except Exception as e:
        return {'error': str(e)}

def generate_data_recommendations(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate data recommendations"""
    try:
        recommendations = {
            'data_issues': [],
            'symbol_issues': [],
            'quality_issues': [],
            'improvement_actions': [],
            'testing_recommendations': []
        }
        
        # Analyze data availability
        data_availability = analysis_results.get('data_availability', {})
        overall_availability = data_availability.get('overall_availability', 0)
        
        if overall_availability < 50:
            recommendations['data_issues'].append("Low data availability - need more data")
            recommendations['improvement_actions'].append("Populate database with more historical data")
        
        # Analyze symbol coverage
        symbol_coverage = analysis_results.get('symbol_coverage', {})
        symbol_coverage_score = symbol_coverage.get('symbol_coverage_score', 0)
        unique_symbols = symbol_coverage.get('unique_symbols', [])
        
        if symbol_coverage_score < 80:
            recommendations['symbol_issues'].append(f"Low symbol coverage - only {len(unique_symbols)} symbols")
            recommendations['improvement_actions'].append("Add data for more symbols")
        
        if len(unique_symbols) < 5:
            recommendations['symbol_issues'].append("Insufficient symbols for testing - need at least 5 symbols")
            recommendations['improvement_actions'].append("Add data for multiple symbols (AAPL, GOOGL, MSFT, AMZN, TSLA)")
        
        # Analyze data quality
        data_quality = analysis_results.get('data_quality', {})
        overall_quality_score = data_quality.get('overall_quality_score', 0)
        
        if overall_quality_score < 80:
            recommendations['quality_issues'].append("Low data quality - need data improvement")
            recommendations['improvement_actions'].append("Improve data completeness, consistency, and timeliness")
        
        # Generate testing recommendations
        if len(unique_symbols) >= 5:
            recommendations['testing_recommendations'].append("Sufficient symbols for comprehensive testing")
        else:
            recommendations['testing_recommendations'].append("Need more symbols for comprehensive testing")
        
        if overall_availability >= 50:
            recommendations['testing_recommendations'].append("Sufficient data for testing")
        else:
            recommendations['testing_recommendations'].append("Need more data for testing")
        
        if overall_quality_score >= 80:
            recommendations['testing_recommendations'].append("Data quality sufficient for testing")
        else:
            recommendations['testing_recommendations'].append("Need to improve data quality for testing")
        
        return recommendations
        
    except Exception as e:
        return {'error': str(e)}

def generate_analysis_report(analysis_results: Dict[str, Any]) -> None:
    """Generate analysis report"""
    print("\nDATABASE DATA ANALYSIS REPORT")
    print("=" * 80)
    
    # Data availability
    data_availability = analysis_results.get('data_availability', {})
    print(f"Data Availability Analysis:")
    print(f"  Overall Availability: {data_availability.get('overall_availability', 0):.1f}%")
    
    trading_data = data_availability.get('trading_data', {})
    print(f"  Trading Data: {trading_data.get('orders_count', 0)} orders, {trading_data.get('trades_count', 0)} trades")
    print(f"    Symbols: {trading_data.get('orders_symbols', 0)} orders, {trading_data.get('trades_symbols', 0)} trades")
    
    market_data = data_availability.get('market_data', {})
    print(f"  Market Data: {market_data.get('market_data_count', 0)} records, {market_data.get('market_data_symbols', 0)} symbols")
    print(f"    Historical Daily: {market_data.get('historical_daily_count', 0)} records, {market_data.get('historical_daily_symbols', 0)} symbols")
    
    # Symbol coverage
    symbol_coverage = analysis_results.get('symbol_coverage', {})
    print(f"\nSymbol Coverage Analysis:")
    print(f"  Unique Symbols: {len(symbol_coverage.get('unique_symbols', []))}")
    print(f"  Coverage Score: {symbol_coverage.get('symbol_coverage_score', 0):.1f}%")
    print(f"  Symbols: {symbol_coverage.get('unique_symbols', [])[:10]}")
    
    # Data quality
    data_quality = analysis_results.get('data_quality', {})
    print(f"\nData Quality Analysis:")
    print(f"  Overall Quality: {data_quality.get('overall_quality_score', 0):.1f}%")
    
    completeness_scores = data_quality.get('completeness_scores', {})
    print(f"  Completeness Scores:")
    for table, score in completeness_scores.items():
        if isinstance(score, (int, float)):
            print(f"    {table}: {score:.1f}%")
    
    consistency_scores = data_quality.get('consistency_scores', {})
    print(f"  Consistency Score: {consistency_scores.get('consistency_score', 0):.1f}%")
    
    timeliness_scores = data_quality.get('timeliness_scores', {})
    print(f"  Timeliness Score: {timeliness_scores.get('timeliness_score', 0):.1f}%")
    
    # Recommendations
    recommendations = analysis_results.get('recommendations', {})
    print(f"\nRecommendations:")
    
    data_issues = recommendations.get('data_issues', [])
    if data_issues:
        print(f"  Data Issues:")
        for issue in data_issues:
            print(f"    - {issue}")
    
    symbol_issues = recommendations.get('symbol_issues', [])
    if symbol_issues:
        print(f"  Symbol Issues:")
        for issue in symbol_issues:
            print(f"    - {issue}")
    
    quality_issues = recommendations.get('quality_issues', [])
    if quality_issues:
        print(f"  Quality Issues:")
        for issue in quality_issues:
            print(f"    - {issue}")
    
    improvement_actions = recommendations.get('improvement_actions', [])
    if improvement_actions:
        print(f"  Improvement Actions:")
        for action in improvement_actions:
            print(f"    - {action}")
    
    testing_recommendations = recommendations.get('testing_recommendations', [])
    if testing_recommendations:
        print(f"  Testing Recommendations:")
        for rec in testing_recommendations:
            print(f"    - {rec}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"database_data_analysis_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\nDatabase data analysis results saved to: {results_file}")
    print(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    database_data_analysis()
