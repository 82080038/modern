#!/usr/bin/env python3
"""
Final Production Test
====================

Script untuk melakukan testing final sebelum production deployment
dengan data saham Indonesia yang sudah diperkaya.

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

def final_production_test():
    """Final production test with enriched data"""
    print("FINAL PRODUCTION TEST WITH ENRICHED DATA")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test results
    test_results = {
        'test_type': 'final_production_test',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'data_enrichment_status': {},
        'module_performance_final': {},
        'production_readiness_final': {},
        'deployment_recommendations': {},
        'final_assessment': {}
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
        return test_results
    
    # Step 1: Assess data enrichment status
    print("\n1. ASSESSING DATA ENRICHMENT STATUS")
    print("-" * 60)
    
    data_enrichment = assess_data_enrichment_status(cursor)
    test_results['data_enrichment_status'] = data_enrichment
    print(f"   Data enrichment assessment completed")
    
    # Step 2: Test final module performance
    print("\n2. TESTING FINAL MODULE PERFORMANCE")
    print("-" * 60)
    
    module_performance = test_final_module_performance(cursor)
    test_results['module_performance_final'] = module_performance
    print(f"   Final module performance testing completed")
    
    # Step 3: Assess final production readiness
    print("\n3. ASSESSING FINAL PRODUCTION READINESS")
    print("-" * 60)
    
    production_readiness = assess_final_production_readiness(test_results)
    test_results['production_readiness_final'] = production_readiness
    print(f"   Final production readiness assessment completed")
    
    # Step 4: Generate deployment recommendations
    print("\n4. GENERATING DEPLOYMENT RECOMMENDATIONS")
    print("-" * 60)
    
    deployment_recommendations = generate_deployment_recommendations(test_results)
    test_results['deployment_recommendations'] = deployment_recommendations
    print(f"   Deployment recommendations generated")
    
    # Step 5: Final assessment
    print("\n5. FINAL ASSESSMENT")
    print("-" * 60)
    
    final_assessment = generate_final_assessment(test_results)
    test_results['final_assessment'] = final_assessment
    print(f"   Final assessment completed")
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    # Generate final report
    generate_final_production_report(test_results)
    
    return test_results

def assess_data_enrichment_status(cursor) -> Dict[str, Any]:
    """Assess data enrichment status"""
    try:
        enrichment = {
            'indonesian_stocks': {},
            'data_volume': {},
            'data_quality': {},
            'enrichment_score': 0.0
        }
        
        # Check Indonesian stocks data
        print("   Checking Indonesian stocks data...")
        try:
            # Check for Indonesian stock symbols (.JK)
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data WHERE symbol LIKE '%.JK'")
            indonesian_market_symbols = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_ohlcv_daily WHERE symbol LIKE '%.JK'")
            indonesian_historical_symbols = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM fundamental_data WHERE symbol LIKE '%.JK'")
            indonesian_fundamental_symbols = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM technical_indicators WHERE symbol LIKE '%.JK'")
            indonesian_technical_symbols = cursor.fetchone()[0]
            
            enrichment['indonesian_stocks'] = {
                'market_symbols': indonesian_market_symbols,
                'historical_symbols': indonesian_historical_symbols,
                'fundamental_symbols': indonesian_fundamental_symbols,
                'technical_symbols': indonesian_technical_symbols,
                'coverage_score': min(indonesian_market_symbols, indonesian_historical_symbols, indonesian_fundamental_symbols, indonesian_technical_symbols) / 20 * 100
            }
            
            print(f"     Indonesian market symbols: {indonesian_market_symbols}")
            print(f"     Indonesian historical symbols: {indonesian_historical_symbols}")
            print(f"     Indonesian fundamental symbols: {indonesian_fundamental_symbols}")
            print(f"     Indonesian technical symbols: {indonesian_technical_symbols}")
            print(f"     Coverage score: {enrichment['indonesian_stocks']['coverage_score']:.1f}%")
            
        except Exception as e:
            enrichment['indonesian_stocks'] = {'error': str(e)}
            print(f"     [ERROR] Indonesian stocks check: {e}")
        
        # Check data volume
        print("   Checking data volume...")
        try:
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily")
            historical_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM fundamental_data")
            fundamental_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM technical_indicators")
            technical_count = cursor.fetchone()[0]
            
            enrichment['data_volume'] = {
                'market_data_count': market_data_count,
                'historical_count': historical_count,
                'fundamental_count': fundamental_count,
                'technical_count': technical_count,
                'total_data_points': market_data_count + historical_count + fundamental_count + technical_count,
                'volume_score': min(market_data_count / 10000, historical_count / 100000, fundamental_count / 100, technical_count / 1000) * 100
            }
            
            print(f"     Market data: {market_data_count:,} records")
            print(f"     Historical data: {historical_count:,} records")
            print(f"     Fundamental data: {fundamental_count:,} records")
            print(f"     Technical data: {technical_count:,} records")
            print(f"     Volume score: {enrichment['data_volume']['volume_score']:.1f}%")
            
        except Exception as e:
            enrichment['data_volume'] = {'error': str(e)}
            print(f"     [ERROR] Data volume check: {e}")
        
        # Check data quality
        print("   Checking data quality...")
        try:
            # Check data completeness
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol IS NOT NULL AND timestamp IS NOT NULL AND price IS NOT NULL")
            market_data_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_total = cursor.fetchone()[0]
            market_data_completeness = (market_data_complete / market_data_total * 100) if market_data_total > 0 else 0
            
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily WHERE symbol IS NOT NULL AND date IS NOT NULL AND close IS NOT NULL")
            historical_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily")
            historical_total = cursor.fetchone()[0]
            historical_completeness = (historical_complete / historical_total * 100) if historical_total > 0 else 0
            
            cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE symbol IS NOT NULL AND date IS NOT NULL")
            fundamental_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM fundamental_data")
            fundamental_total = cursor.fetchone()[0]
            fundamental_completeness = (fundamental_complete / fundamental_total * 100) if fundamental_total > 0 else 0
            
            enrichment['data_quality'] = {
                'market_data_completeness': market_data_completeness,
                'historical_completeness': historical_completeness,
                'fundamental_completeness': fundamental_completeness,
                'overall_completeness': (market_data_completeness + historical_completeness + fundamental_completeness) / 3,
                'quality_score': (market_data_completeness + historical_completeness + fundamental_completeness) / 3
            }
            
            print(f"     Market data completeness: {market_data_completeness:.1f}%")
            print(f"     Historical completeness: {historical_completeness:.1f}%")
            print(f"     Fundamental completeness: {fundamental_completeness:.1f}%")
            print(f"     Overall completeness: {enrichment['data_quality']['overall_completeness']:.1f}%")
            
        except Exception as e:
            enrichment['data_quality'] = {'error': str(e)}
            print(f"     [ERROR] Data quality check: {e}")
        
        # Calculate enrichment score
        coverage_score = enrichment['indonesian_stocks'].get('coverage_score', 0)
        volume_score = enrichment['data_volume'].get('volume_score', 0)
        quality_score = enrichment['data_quality'].get('quality_score', 0)
        
        enrichment['enrichment_score'] = (coverage_score + volume_score + quality_score) / 3
        
        return enrichment
        
    except Exception as e:
        return {'error': str(e)}

def test_final_module_performance(cursor) -> Dict[str, Any]:
    """Test final module performance"""
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
            cursor.execute("SELECT COUNT(*) FROM orders")
            orders_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trades")
            trades_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM orders")
            orders_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM trades")
            trades_symbols = cursor.fetchone()[0]
            
            execution_rate = (trades_count / orders_count * 100) if orders_count > 0 else 0
            symbol_coverage = (trades_symbols / orders_symbols * 100) if orders_symbols > 0 else 0
            
            performance['trading_module'] = {
                'orders_count': orders_count,
                'trades_count': trades_count,
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
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily")
            historical_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data")
            market_data_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_ohlcv_daily")
            historical_symbols = cursor.fetchone()[0]
            
            data_completeness = (market_data_count / historical_count * 100) if historical_count > 0 else 0
            symbol_coverage = (market_data_symbols / historical_symbols * 100) if historical_symbols > 0 else 0
            
            performance['market_data_module'] = {
                'market_data_count': market_data_count,
                'historical_count': historical_count,
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
            cursor.execute("SELECT COUNT(*) FROM risk_metrics")
            risk_metrics_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM portfolio_risk")
            portfolio_risk_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM risk_metrics")
            risk_metrics_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM portfolio_risk")
            portfolio_risk_symbols = cursor.fetchone()[0]
            
            risk_coverage = (portfolio_risk_count / risk_metrics_count * 100) if risk_metrics_count > 0 else 0
            symbol_coverage = (portfolio_risk_symbols / risk_metrics_symbols * 100) if risk_metrics_symbols > 0 else 0
            
            performance['risk_management_module'] = {
                'risk_metrics_count': risk_metrics_count,
                'portfolio_risk_count': portfolio_risk_count,
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
            cursor.execute("SELECT COUNT(*) FROM technical_indicators")
            technical_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM indicators_trend")
            trend_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM technical_indicators")
            technical_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM indicators_trend")
            trend_symbols = cursor.fetchone()[0]
            
            indicator_coverage = (trend_count / technical_count * 100) if technical_count > 0 else 0
            symbol_coverage = (trend_symbols / technical_symbols * 100) if technical_symbols > 0 else 0
            
            performance['technical_analysis_module'] = {
                'technical_count': technical_count,
                'trend_count': trend_count,
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
            cursor.execute("SELECT COUNT(*) FROM fundamental_data")
            fundamental_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM company_fundamentals")
            company_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM fundamental_data")
            fundamental_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM company_fundamentals")
            company_symbols = cursor.fetchone()[0]
            
            fundamental_coverage = (company_count / fundamental_count * 100) if fundamental_count > 0 else 0
            symbol_coverage = (company_symbols / fundamental_symbols * 100) if fundamental_symbols > 0 else 0
            
            performance['fundamental_analysis_module'] = {
                'fundamental_count': fundamental_count,
                'company_count': company_count,
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
            cursor.execute("SELECT COUNT(*) FROM sentiment_data")
            sentiment_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM news_sentiment")
            news_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM sentiment_data")
            sentiment_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM news_sentiment")
            news_symbols = cursor.fetchone()[0]
            
            sentiment_coverage = (news_count / sentiment_count * 100) if sentiment_count > 0 else 0
            symbol_coverage = (news_symbols / sentiment_symbols * 100) if sentiment_symbols > 0 else 0
            
            performance['sentiment_analysis_module'] = {
                'sentiment_count': sentiment_count,
                'news_count': news_count,
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

def assess_final_production_readiness(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Assess final production readiness"""
    try:
        readiness = {
            'readiness_status': '',
            'deployment_strategy': '',
            'monitoring_requirements': {},
            'risk_level': '',
            'recommendations': []
        }
        
        # Analyze data enrichment
        data_enrichment = test_results.get('data_enrichment_status', {})
        enrichment_score = data_enrichment.get('enrichment_score', 0)
        
        # Analyze module performance
        module_performance = test_results.get('module_performance_final', {})
        overall_performance = module_performance.get('overall_performance', {})
        overall_score = overall_performance.get('overall_score', 0)
        
        # Determine readiness status
        if enrichment_score >= 80 and overall_score >= 80:
            readiness['readiness_status'] = 'READY_FOR_PRODUCTION'
            readiness['deployment_strategy'] = 'IMMEDIATE_DEPLOYMENT'
            readiness['risk_level'] = 'LOW'
        elif enrichment_score >= 60 and overall_score >= 60:
            readiness['readiness_status'] = 'READY_WITH_MONITORING'
            readiness['deployment_strategy'] = 'GRADUAL_DEPLOYMENT'
            readiness['risk_level'] = 'MEDIUM'
        elif enrichment_score >= 40 and overall_score >= 40:
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
        if enrichment_score < 80:
            readiness['recommendations'].append(f"Improve data enrichment from {enrichment_score:.1f}% to 80%+")
        
        if overall_score < 80:
            readiness['recommendations'].append(f"Improve overall performance from {overall_score:.1f}% to 80%+")
        
        if readiness['risk_level'] in ['HIGH', 'CRITICAL']:
            readiness['recommendations'].append("Implement comprehensive monitoring and rollback plans")
        
        return readiness
        
    except Exception as e:
        return {'error': str(e)}

def generate_deployment_recommendations(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate deployment recommendations"""
    try:
        recommendations = {
            'deployment_plan': {},
            'monitoring_strategy': {},
            'maintenance_plan': {},
            'success_metrics': {},
            'next_steps': []
        }
        
        # Analyze readiness
        production_readiness = test_results.get('production_readiness_final', {})
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

def generate_final_assessment(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final assessment"""
    try:
        assessment = {
            'overall_status': '',
            'production_ready': False,
            'key_achievements': [],
            'remaining_issues': [],
            'final_score': 0.0
        }
        
        # Analyze all results
        data_enrichment = test_results.get('data_enrichment_status', {})
        enrichment_score = data_enrichment.get('enrichment_score', 0)
        
        module_performance = test_results.get('module_performance_final', {})
        overall_performance = module_performance.get('overall_performance', {})
        overall_score = overall_performance.get('overall_score', 0)
        
        production_readiness = test_results.get('production_readiness_final', {})
        readiness_status = production_readiness.get('readiness_status', 'UNKNOWN')
        
        # Calculate final score
        final_score = (enrichment_score + overall_score) / 2
        assessment['final_score'] = final_score
        
        # Determine overall status
        if final_score >= 80:
            assessment['overall_status'] = 'EXCELLENT'
            assessment['production_ready'] = True
        elif final_score >= 60:
            assessment['overall_status'] = 'GOOD'
            assessment['production_ready'] = True
        elif final_score >= 40:
            assessment['overall_status'] = 'FAIR'
            assessment['production_ready'] = False
        else:
            assessment['overall_status'] = 'POOR'
            assessment['production_ready'] = False
        
        # Key achievements
        if enrichment_score >= 80:
            assessment['key_achievements'].append(f"Data enrichment achieved {enrichment_score:.1f}%")
        
        if overall_score >= 80:
            assessment['key_achievements'].append(f"Module performance achieved {overall_score:.1f}%")
        
        if readiness_status == 'READY_FOR_PRODUCTION':
            assessment['key_achievements'].append("System ready for production deployment")
        
        # Remaining issues
        if enrichment_score < 80:
            assessment['remaining_issues'].append(f"Data enrichment needs improvement ({enrichment_score:.1f}%)")
        
        if overall_score < 80:
            assessment['remaining_issues'].append(f"Module performance needs improvement ({overall_score:.1f}%)")
        
        if readiness_status != 'READY_FOR_PRODUCTION':
            assessment['remaining_issues'].append(f"Production readiness: {readiness_status}")
        
        return assessment
        
    except Exception as e:
        return {'error': str(e)}

def generate_final_production_report(test_results: Dict[str, Any]) -> None:
    """Generate final production report"""
    print("\nFINAL PRODUCTION TEST REPORT")
    print("=" * 80)
    
    # Data enrichment status
    data_enrichment = test_results.get('data_enrichment_status', {})
    print(f"Data Enrichment Status:")
    print(f"  Enrichment Score: {data_enrichment.get('enrichment_score', 0):.1f}%")
    
    indonesian_stocks = data_enrichment.get('indonesian_stocks', {})
    print(f"  Indonesian Stocks Coverage: {indonesian_stocks.get('coverage_score', 0):.1f}%")
    print(f"    Market symbols: {indonesian_stocks.get('market_symbols', 0)}")
    print(f"    Historical symbols: {indonesian_stocks.get('historical_symbols', 0)}")
    print(f"    Fundamental symbols: {indonesian_stocks.get('fundamental_symbols', 0)}")
    print(f"    Technical symbols: {indonesian_stocks.get('technical_symbols', 0)}")
    
    data_volume = data_enrichment.get('data_volume', {})
    print(f"  Data Volume: {data_volume.get('volume_score', 0):.1f}%")
    print(f"    Market data: {data_volume.get('market_data_count', 0):,} records")
    print(f"    Historical data: {data_volume.get('historical_count', 0):,} records")
    print(f"    Fundamental data: {data_volume.get('fundamental_count', 0):,} records")
    print(f"    Technical data: {data_volume.get('technical_count', 0):,} records")
    
    data_quality = data_enrichment.get('data_quality', {})
    print(f"  Data Quality: {data_quality.get('quality_score', 0):.1f}%")
    print(f"    Market data completeness: {data_quality.get('market_data_completeness', 0):.1f}%")
    print(f"    Historical completeness: {data_quality.get('historical_completeness', 0):.1f}%")
    print(f"    Fundamental completeness: {data_quality.get('fundamental_completeness', 0):.1f}%")
    
    # Module performance
    module_performance = test_results.get('module_performance_final', {})
    print(f"\nModule Performance:")
    print(f"  Overall Performance: {module_performance.get('overall_performance', {}).get('overall_score', 0):.1f}%")
    
    for module_name, module_data in module_performance.items():
        if isinstance(module_data, dict) and 'performance_score' in module_data:
            print(f"  {module_name}: {module_data['performance_score']:.1f}%")
    
    # Production readiness
    production_readiness = test_results.get('production_readiness_final', {})
    print(f"\nProduction Readiness:")
    print(f"  Status: {production_readiness.get('readiness_status', 'UNKNOWN')}")
    print(f"  Deployment Strategy: {production_readiness.get('deployment_strategy', 'UNKNOWN')}")
    print(f"  Risk Level: {production_readiness.get('risk_level', 'UNKNOWN')}")
    
    recommendations = production_readiness.get('recommendations', [])
    if recommendations:
        print(f"  Recommendations:")
        for rec in recommendations:
            print(f"    - {rec}")
    
    # Final assessment
    final_assessment = test_results.get('final_assessment', {})
    print(f"\nFinal Assessment:")
    print(f"  Overall Status: {final_assessment.get('overall_status', 'UNKNOWN')}")
    print(f"  Production Ready: {final_assessment.get('production_ready', False)}")
    print(f"  Final Score: {final_assessment.get('final_score', 0):.1f}%")
    
    key_achievements = final_assessment.get('key_achievements', [])
    if key_achievements:
        print(f"  Key Achievements:")
        for achievement in key_achievements:
            print(f"    - {achievement}")
    
    remaining_issues = final_assessment.get('remaining_issues', [])
    if remaining_issues:
        print(f"  Remaining Issues:")
        for issue in remaining_issues:
            print(f"    - {issue}")
    
    # Deployment recommendations
    deployment_recommendations = test_results.get('deployment_recommendations', {})
    print(f"\nDeployment Recommendations:")
    deployment_plan = deployment_recommendations.get('deployment_plan', {})
    print(f"  Deployment Phase: {deployment_plan.get('phase', 'UNKNOWN')}")
    print(f"  Modules to Deploy: {deployment_plan.get('modules_to_deploy', 'UNKNOWN')}")
    
    next_steps = deployment_recommendations.get('next_steps', [])
    if next_steps:
        print(f"  Next Steps:")
        for step in next_steps:
            print(f"    - {step}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"final_production_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nFinal production test results saved to: {results_file}")
    print(f"Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    final_production_test()
