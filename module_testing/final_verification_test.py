#!/usr/bin/env python3
"""
Final Verification Test
=======================

Script untuk melakukan testing final setelah perbaikan module-module
berdasarkan best practices dari internet research 2024.

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

def final_verification_test():
    """Final verification test after advanced fixes"""
    print("FINAL VERIFICATION TEST - AFTER ADVANCED FIXES")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test results
    test_results = {
        'test_type': 'final_verification_test',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'module_performance_after_fixes': {},
        'data_quality_after_fixes': {},
        'production_readiness_after_fixes': {},
        'final_recommendations': {},
        'overall_assessment': {}
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
    
    # Step 1: Test module performance after fixes
    print("\n1. TESTING MODULE PERFORMANCE AFTER FIXES")
    print("-" * 60)
    
    module_performance = test_module_performance_after_fixes(cursor)
    test_results['module_performance_after_fixes'] = module_performance
    print(f"   Module performance testing completed")
    
    # Step 2: Test data quality after fixes
    print("\n2. TESTING DATA QUALITY AFTER FIXES")
    print("-" * 60)
    
    data_quality = test_data_quality_after_fixes(cursor)
    test_results['data_quality_after_fixes'] = data_quality
    print(f"   Data quality testing completed")
    
    # Step 3: Assess production readiness after fixes
    print("\n3. ASSESSING PRODUCTION READINESS AFTER FIXES")
    print("-" * 60)
    
    production_readiness = assess_production_readiness_after_fixes(test_results)
    test_results['production_readiness_after_fixes'] = production_readiness
    print(f"   Production readiness assessment completed")
    
    # Step 4: Generate final recommendations
    print("\n4. GENERATING FINAL RECOMMENDATIONS")
    print("-" * 60)
    
    final_recommendations = generate_final_recommendations_after_fixes(test_results)
    test_results['final_recommendations'] = final_recommendations
    print(f"   Final recommendations generated")
    
    # Step 5: Overall assessment
    print("\n5. OVERALL ASSESSMENT")
    print("-" * 60)
    
    overall_assessment = generate_overall_assessment(test_results)
    test_results['overall_assessment'] = overall_assessment
    print(f"   Overall assessment completed")
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    # Generate final report
    generate_final_verification_report(test_results)
    
    return test_results

def test_module_performance_after_fixes(cursor) -> Dict[str, Any]:
    """Test module performance after fixes"""
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
            cursor.execute("SELECT COUNT(*) FROM market_data_quality_metrics")
            quality_metrics_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM market_data_aggregated")
            aggregated_count = cursor.fetchone()[0]
            cursor.execute("SELECT AVG(overall_quality_score) FROM market_data_quality_metrics")
            avg_quality_score = cursor.fetchone()[0] or 0
            
            performance['market_data_module'] = {
                'market_data_count': market_data_count,
                'quality_metrics_count': quality_metrics_count,
                'aggregated_count': aggregated_count,
                'avg_quality_score': float(avg_quality_score),
                'performance_score': float(avg_quality_score)
            }
            print(f"     Market data module: {market_data_count:,} records, {quality_metrics_count} quality metrics, {avg_quality_score:.1f}% avg quality")
            
        except Exception as e:
            performance['market_data_module'] = {'error': str(e)}
            print(f"     [ERROR] Market data module test: {e}")
        
        # Test risk management module
        print("   Testing risk management module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM risk_metrics WHERE symbol IS NOT NULL")
            risk_metrics_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM advanced_risk_metrics")
            advanced_metrics_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM portfolio_risk")
            portfolio_risk_count = cursor.fetchone()[0]
            
            risk_coverage = (advanced_metrics_count / risk_metrics_count * 100) if risk_metrics_count > 0 else 0
            symbol_coverage = (portfolio_risk_count / risk_metrics_count * 100) if risk_metrics_count > 0 else 0
            
            performance['risk_management_module'] = {
                'risk_metrics_count': risk_metrics_count,
                'advanced_metrics_count': advanced_metrics_count,
                'portfolio_risk_count': portfolio_risk_count,
                'risk_coverage': risk_coverage,
                'symbol_coverage': symbol_coverage,
                'performance_score': (risk_coverage + symbol_coverage) / 2
            }
            print(f"     Risk management module: {risk_metrics_count} risk metrics, {advanced_metrics_count} advanced metrics, {portfolio_risk_count} portfolio risk")
            
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
            print(f"     Technical analysis module: {technical_count:,} indicators, {trend_count:,} trends, {technical_symbols} symbols")
            
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
            cursor.execute("SELECT COUNT(*) FROM fundamental_ratios")
            ratios_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM fundamental_data")
            fundamental_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM company_fundamentals")
            company_symbols = cursor.fetchone()[0]
            
            fundamental_coverage = (company_count / fundamental_count * 100) if fundamental_count > 0 else 0
            symbol_coverage = (company_symbols / fundamental_symbols * 100) if fundamental_symbols > 0 else 0
            ratios_coverage = (ratios_count / fundamental_count * 100) if fundamental_count > 0 else 0
            
            performance['fundamental_analysis_module'] = {
                'fundamental_count': fundamental_count,
                'company_count': company_count,
                'ratios_count': ratios_count,
                'fundamental_symbols': fundamental_symbols,
                'company_symbols': company_symbols,
                'fundamental_coverage': fundamental_coverage,
                'symbol_coverage': symbol_coverage,
                'ratios_coverage': ratios_coverage,
                'performance_score': (fundamental_coverage + symbol_coverage + ratios_coverage) / 3
            }
            print(f"     Fundamental analysis module: {fundamental_count} fundamentals, {company_count} companies, {ratios_count} ratios")
            
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
            cursor.execute("SELECT COUNT(*) FROM sentiment_aggregation")
            aggregation_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM sentiment_data")
            sentiment_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM news_sentiment")
            news_symbols = cursor.fetchone()[0]
            
            sentiment_coverage = (news_count / sentiment_count * 100) if sentiment_count > 0 else 0
            symbol_coverage = (news_symbols / sentiment_symbols * 100) if sentiment_symbols > 0 else 0
            aggregation_coverage = (aggregation_count / sentiment_count * 100) if sentiment_count > 0 else 0
            
            performance['sentiment_analysis_module'] = {
                'sentiment_count': sentiment_count,
                'news_count': news_count,
                'aggregation_count': aggregation_count,
                'sentiment_symbols': sentiment_symbols,
                'news_symbols': news_symbols,
                'sentiment_coverage': sentiment_coverage,
                'symbol_coverage': symbol_coverage,
                'aggregation_coverage': aggregation_coverage,
                'performance_score': (sentiment_coverage + symbol_coverage + aggregation_coverage) / 3
            }
            print(f"     Sentiment analysis module: {sentiment_count} sentiment, {news_count} news, {aggregation_count} aggregation")
            
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

def test_data_quality_after_fixes(cursor) -> Dict[str, Any]:
    """Test data quality after fixes"""
    try:
        quality = {
            'completeness_scores': {},
            'consistency_scores': {},
            'timeliness_scores': {},
            'overall_quality_score': 0.0
        }
        
        # Test completeness
        print("   Testing data completeness after fixes...")
        try:
            # Check market data completeness
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol IS NOT NULL AND timestamp IS NOT NULL AND price IS NOT NULL")
            market_data_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_data_total = cursor.fetchone()[0]
            market_data_completeness = (market_data_complete / market_data_total * 100) if market_data_total > 0 else 0
            
            # Check quality metrics completeness
            cursor.execute("SELECT COUNT(*) FROM market_data_quality_metrics WHERE symbol IS NOT NULL AND date IS NOT NULL")
            quality_metrics_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM market_data_quality_metrics")
            quality_metrics_total = cursor.fetchone()[0]
            quality_metrics_completeness = (quality_metrics_complete / quality_metrics_total * 100) if quality_metrics_total > 0 else 0
            
            # Check fundamental data completeness
            cursor.execute("SELECT COUNT(*) FROM company_fundamentals WHERE symbol IS NOT NULL AND company_name IS NOT NULL")
            company_fundamentals_complete = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM company_fundamentals")
            company_fundamentals_total = cursor.fetchone()[0]
            company_fundamentals_completeness = (company_fundamentals_complete / company_fundamentals_total * 100) if company_fundamentals_total > 0 else 0
            
            quality['completeness_scores'] = {
                'market_data': market_data_completeness,
                'quality_metrics': quality_metrics_completeness,
                'company_fundamentals': company_fundamentals_completeness
            }
            
            print(f"     Market data completeness: {market_data_completeness:.1f}%")
            print(f"     Quality metrics completeness: {quality_metrics_completeness:.1f}%")
            print(f"     Company fundamentals completeness: {company_fundamentals_completeness:.1f}%")
            
        except Exception as e:
            quality['completeness_scores'] = {'error': str(e)}
            print(f"     [ERROR] Completeness test: {e}")
        
        # Test consistency
        print("   Testing data consistency after fixes...")
        try:
            # Check symbol consistency across modules
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data WHERE symbol LIKE '%.JK'")
            market_data_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM fundamental_data WHERE symbol LIKE '%.JK'")
            fundamental_symbols = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM technical_indicators WHERE symbol LIKE '%.JK'")
            technical_symbols = cursor.fetchone()[0]
            
            # Calculate consistency score
            symbol_counts = [market_data_symbols, fundamental_symbols, technical_symbols]
            consistency_score = min(symbol_counts) / max(symbol_counts) * 100 if max(symbol_counts) > 0 else 0
            
            quality['consistency_scores'] = {
                'market_data_symbols': market_data_symbols,
                'fundamental_symbols': fundamental_symbols,
                'technical_symbols': technical_symbols,
                'consistency_score': consistency_score
            }
            
            print(f"     Market data symbols: {market_data_symbols}")
            print(f"     Fundamental symbols: {fundamental_symbols}")
            print(f"     Technical symbols: {technical_symbols}")
            print(f"     Consistency score: {consistency_score:.1f}%")
            
        except Exception as e:
            quality['consistency_scores'] = {'error': str(e)}
            print(f"     [ERROR] Consistency test: {e}")
        
        # Test timeliness
        print("   Testing data timeliness after fixes...")
        try:
            # Check recent data
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            recent_market_data = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM market_data_quality_metrics WHERE date >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            recent_quality_metrics = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM company_fundamentals WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
            recent_company_fundamentals = cursor.fetchone()[0]
            
            # Calculate timeliness score
            recent_data_total = recent_market_data + recent_quality_metrics + recent_company_fundamentals
            timeliness_score = min(recent_data_total / 1000, 100) if recent_data_total > 0 else 0
            
            quality['timeliness_scores'] = {
                'recent_market_data': recent_market_data,
                'recent_quality_metrics': recent_quality_metrics,
                'recent_company_fundamentals': recent_company_fundamentals,
                'timeliness_score': timeliness_score
            }
            
            print(f"     Recent market data (7 days): {recent_market_data}")
            print(f"     Recent quality metrics (7 days): {recent_quality_metrics}")
            print(f"     Recent company fundamentals (7 days): {recent_company_fundamentals}")
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

def assess_production_readiness_after_fixes(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Assess production readiness after fixes"""
    try:
        readiness = {
            'readiness_status': '',
            'deployment_strategy': '',
            'monitoring_requirements': {},
            'risk_level': '',
            'recommendations': []
        }
        
        # Analyze module performance
        module_performance = test_results.get('module_performance_after_fixes', {})
        overall_performance = module_performance.get('overall_performance', {})
        overall_score = overall_performance.get('overall_score', 0)
        
        # Analyze data quality
        data_quality = test_results.get('data_quality_after_fixes', {})
        overall_quality_score = data_quality.get('overall_quality_score', 0)
        
        # Determine readiness status
        if overall_score >= 80 and overall_quality_score >= 80:
            readiness['readiness_status'] = 'READY_FOR_PRODUCTION'
            readiness['deployment_strategy'] = 'IMMEDIATE_DEPLOYMENT'
            readiness['risk_level'] = 'LOW'
        elif overall_score >= 60 and overall_quality_score >= 60:
            readiness['readiness_status'] = 'READY_WITH_MONITORING'
            readiness['deployment_strategy'] = 'GRADUAL_DEPLOYMENT'
            readiness['risk_level'] = 'MEDIUM'
        elif overall_score >= 40 and overall_quality_score >= 40:
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
        
        if overall_quality_score < 80:
            readiness['recommendations'].append(f"Improve data quality from {overall_quality_score:.1f}% to 80%+")
        
        if readiness['risk_level'] in ['HIGH', 'CRITICAL']:
            readiness['recommendations'].append("Implement comprehensive monitoring and rollback plans")
        
        return readiness
        
    except Exception as e:
        return {'error': str(e)}

def generate_final_recommendations_after_fixes(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final recommendations after fixes"""
    try:
        recommendations = {
            'deployment_plan': {},
            'monitoring_strategy': {},
            'maintenance_plan': {},
            'success_metrics': {},
            'next_steps': []
        }
        
        # Analyze readiness
        production_readiness = test_results.get('production_readiness_after_fixes', {})
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

def generate_overall_assessment(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate overall assessment"""
    try:
        assessment = {
            'overall_status': '',
            'production_ready': False,
            'key_achievements': [],
            'remaining_issues': [],
            'final_score': 0.0
        }
        
        # Analyze all results
        module_performance = test_results.get('module_performance_after_fixes', {})
        overall_performance = module_performance.get('overall_performance', {})
        overall_score = overall_performance.get('overall_score', 0)
        
        data_quality = test_results.get('data_quality_after_fixes', {})
        overall_quality_score = data_quality.get('overall_quality_score', 0)
        
        production_readiness = test_results.get('production_readiness_after_fixes', {})
        readiness_status = production_readiness.get('readiness_status', 'UNKNOWN')
        
        # Calculate final score
        final_score = (overall_score + overall_quality_score) / 2
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
        if overall_score >= 80:
            assessment['key_achievements'].append(f"Module performance achieved {overall_score:.1f}%")
        
        if overall_quality_score >= 80:
            assessment['key_achievements'].append(f"Data quality achieved {overall_quality_score:.1f}%")
        
        if readiness_status == 'READY_FOR_PRODUCTION':
            assessment['key_achievements'].append("System ready for production deployment")
        
        # Remaining issues
        if overall_score < 80:
            assessment['remaining_issues'].append(f"Module performance needs improvement ({overall_score:.1f}%)")
        
        if overall_quality_score < 80:
            assessment['remaining_issues'].append(f"Data quality needs improvement ({overall_quality_score:.1f}%)")
        
        if readiness_status != 'READY_FOR_PRODUCTION':
            assessment['remaining_issues'].append(f"Production readiness: {readiness_status}")
        
        return assessment
        
    except Exception as e:
        return {'error': str(e)}

def generate_final_verification_report(test_results: Dict[str, Any]) -> None:
    """Generate final verification report"""
    print("\nFINAL VERIFICATION REPORT - AFTER ADVANCED FIXES")
    print("=" * 80)
    
    # Module performance
    module_performance = test_results.get('module_performance_after_fixes', {})
    print(f"Module Performance After Fixes:")
    print(f"  Overall Performance: {module_performance.get('overall_performance', {}).get('overall_score', 0):.1f}%")
    
    for module_name, module_data in module_performance.items():
        if isinstance(module_data, dict) and 'performance_score' in module_data:
            print(f"  {module_name}: {module_data['performance_score']:.1f}%")
    
    # Data quality
    data_quality = test_results.get('data_quality_after_fixes', {})
    print(f"\nData Quality After Fixes:")
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
    
    # Production readiness
    production_readiness = test_results.get('production_readiness_after_fixes', {})
    print(f"\nProduction Readiness After Fixes:")
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
    
    # Overall assessment
    overall_assessment = test_results.get('overall_assessment', {})
    print(f"\nOverall Assessment:")
    print(f"  Overall Status: {overall_assessment.get('overall_status', 'UNKNOWN')}")
    print(f"  Production Ready: {overall_assessment.get('production_ready', False)}")
    print(f"  Final Score: {overall_assessment.get('final_score', 0):.1f}%")
    
    key_achievements = overall_assessment.get('key_achievements', [])
    if key_achievements:
        print(f"  Key Achievements:")
        for achievement in key_achievements:
            print(f"    - {achievement}")
    
    remaining_issues = overall_assessment.get('remaining_issues', [])
    if remaining_issues:
        print(f"  Remaining Issues:")
        for issue in remaining_issues:
            print(f"    - {issue}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"final_verification_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nFinal verification test results saved to: {results_file}")
    print(f"Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    final_verification_test()
