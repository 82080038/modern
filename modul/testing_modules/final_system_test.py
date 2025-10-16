#!/usr/bin/env python3
"""
Final System Test
=================

Script untuk melakukan testing final sistem setelah semua perbaikan
dan memverifikasi kesiapan untuk production deployment.

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

def final_system_test():
    """Final system test"""
    print("FINAL SYSTEM TEST")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test results
    test_results = {
        'test_type': 'final_system_test',
        'test_start': datetime.now().isoformat(),
        'database_connection': False,
        'working_modules': {},
        'problematic_modules': {},
        'overall_performance': {},
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
    
    # Step 1: Test all modules comprehensively
    print("\n1. TESTING ALL MODULES COMPREHENSIVELY")
    print("-" * 60)
    
    all_modules_test = test_all_modules_comprehensively(cursor)
    test_results['working_modules'] = all_modules_test.get('working_modules', {})
    test_results['problematic_modules'] = all_modules_test.get('problematic_modules', {})
    print(f"   Working modules: {len(test_results['working_modules'])}")
    print(f"   Problematic modules: {len(test_results['problematic_modules'])}")
    
    # Step 2: Calculate overall performance
    print("\n2. CALCULATING OVERALL PERFORMANCE")
    print("-" * 60)
    
    overall_performance = calculate_overall_performance(test_results['working_modules'], test_results['problematic_modules'])
    test_results['overall_performance'] = overall_performance
    print(f"   Overall performance calculated: {overall_performance.get('overall_score', 0):.1f}%")
    
    # Step 3: Assess production readiness
    print("\n3. ASSESSING PRODUCTION READINESS")
    print("-" * 60)
    
    production_readiness = assess_production_readiness(test_results)
    test_results['production_readiness'] = production_readiness
    print(f"   Production readiness: {production_readiness.get('readiness_status', 'UNKNOWN')}")
    
    # Step 4: Generate final recommendations
    print("\n4. GENERATING FINAL RECOMMENDATIONS")
    print("-" * 60)
    
    final_recommendations = generate_final_recommendations(test_results)
    test_results['final_recommendations'] = final_recommendations
    print(f"   Final recommendations generated")
    
    # Close database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("\n[PASS] Database connection closed")
    
    # Generate final report
    generate_final_report(test_results)
    
    return test_results

def test_all_modules_comprehensively(cursor) -> Dict[str, Any]:
    """Test all modules comprehensively"""
    try:
        working_modules = {}
        problematic_modules = {}
        
        # Test Trading Module
        print("   Testing Trading Module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM orders WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            orders_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trades WHERE executed_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            trades_count = cursor.fetchone()[0]
            
            if orders_count > 0:
                execution_rate = (trades_count / orders_count) * 100
            else:
                execution_rate = 0
            
            if execution_rate >= 80:
                working_modules['trading_module'] = {
                    'performance': execution_rate,
                    'status': 'WORKING',
                    'orders_count': orders_count,
                    'trades_count': trades_count
                }
            else:
                problematic_modules['trading_module'] = {
                    'performance': execution_rate,
                    'status': 'PROBLEMATIC',
                    'orders_count': orders_count,
                    'trades_count': trades_count
                }
            
            print(f"     Trading Module: {execution_rate:.1f}% - {'WORKING' if execution_rate >= 80 else 'PROBLEMATIC'}")
            
        except Exception as e:
            problematic_modules['trading_module'] = {'error': str(e), 'status': 'ERROR'}
            print(f"     [ERROR] Trading Module: {e}")
        
        # Test Market Data Module
        print("   Testing Market Data Module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            market_data_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            historical_count = cursor.fetchone()[0]
            
            if historical_count > 0:
                completeness = (market_data_count / historical_count) * 100
            else:
                completeness = 0
            
            if completeness >= 80:
                working_modules['market_data_module'] = {
                    'performance': completeness,
                    'status': 'WORKING',
                    'market_data_count': market_data_count,
                    'historical_count': historical_count
                }
            else:
                problematic_modules['market_data_module'] = {
                    'performance': completeness,
                    'status': 'PROBLEMATIC',
                    'market_data_count': market_data_count,
                    'historical_count': historical_count
                }
            
            print(f"     Market Data Module: {completeness:.1f}% - {'WORKING' if completeness >= 80 else 'PROBLEMATIC'}")
            
        except Exception as e:
            problematic_modules['market_data_module'] = {'error': str(e), 'status': 'ERROR'}
            print(f"     [ERROR] Market Data Module: {e}")
        
        # Test Risk Management Module
        print("   Testing Risk Management Module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM risk_metrics WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            risk_metrics_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM portfolio_risk WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            portfolio_risk_count = cursor.fetchone()[0]
            
            if risk_metrics_count > 0:
                risk_coverage = (portfolio_risk_count / risk_metrics_count) * 100
            else:
                risk_coverage = 0
            
            if risk_coverage >= 80:
                working_modules['risk_management_module'] = {
                    'performance': risk_coverage,
                    'status': 'WORKING',
                    'risk_metrics_count': risk_metrics_count,
                    'portfolio_risk_count': portfolio_risk_count
                }
            else:
                problematic_modules['risk_management_module'] = {
                    'performance': risk_coverage,
                    'status': 'PROBLEMATIC',
                    'risk_metrics_count': risk_metrics_count,
                    'portfolio_risk_count': portfolio_risk_count
                }
            
            print(f"     Risk Management Module: {risk_coverage:.1f}% - {'WORKING' if risk_coverage >= 80 else 'PROBLEMATIC'}")
            
        except Exception as e:
            problematic_modules['risk_management_module'] = {'error': str(e), 'status': 'ERROR'}
            print(f"     [ERROR] Risk Management Module: {e}")
        
        # Test Technical Analysis Module
        print("   Testing Technical Analysis Module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            technical_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM indicators_trend WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            trend_count = cursor.fetchone()[0]
            
            if technical_count > 0:
                technical_coverage = (trend_count / technical_count) * 100
            else:
                technical_coverage = 0
            
            if technical_coverage >= 80:
                working_modules['technical_analysis_module'] = {
                    'performance': technical_coverage,
                    'status': 'WORKING',
                    'technical_count': technical_count,
                    'trend_count': trend_count
                }
            else:
                problematic_modules['technical_analysis_module'] = {
                    'performance': technical_coverage,
                    'status': 'PROBLEMATIC',
                    'technical_count': technical_count,
                    'trend_count': trend_count
                }
            
            print(f"     Technical Analysis Module: {technical_coverage:.1f}% - {'WORKING' if technical_coverage >= 80 else 'PROBLEMATIC'}")
            
        except Exception as e:
            problematic_modules['technical_analysis_module'] = {'error': str(e), 'status': 'ERROR'}
            print(f"     [ERROR] Technical Analysis Module: {e}")
        
        # Test Fundamental Analysis Module
        print("   Testing Fundamental Analysis Module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            fundamental_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM company_fundamentals WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)")
            company_count = cursor.fetchone()[0]
            
            if fundamental_count > 0:
                fundamental_coverage = (company_count / fundamental_count) * 100
            else:
                fundamental_coverage = 0
            
            if fundamental_coverage >= 80:
                working_modules['fundamental_analysis_module'] = {
                    'performance': fundamental_coverage,
                    'status': 'WORKING',
                    'fundamental_count': fundamental_count,
                    'company_count': company_count
                }
            else:
                problematic_modules['fundamental_analysis_module'] = {
                    'performance': fundamental_coverage,
                    'status': 'PROBLEMATIC',
                    'fundamental_count': fundamental_count,
                    'company_count': company_count
                }
            
            print(f"     Fundamental Analysis Module: {fundamental_coverage:.1f}% - {'WORKING' if fundamental_coverage >= 80 else 'PROBLEMATIC'}")
            
        except Exception as e:
            problematic_modules['fundamental_analysis_module'] = {'error': str(e), 'status': 'ERROR'}
            print(f"     [ERROR] Fundamental Analysis Module: {e}")
        
        # Test Sentiment Analysis Module
        print("   Testing Sentiment Analysis Module...")
        try:
            cursor.execute("SELECT COUNT(*) FROM sentiment_data")
            sentiment_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM news_sentiment")
            news_count = cursor.fetchone()[0]
            
            if sentiment_count > 0:
                sentiment_coverage = (news_count / sentiment_count) * 100
            else:
                sentiment_coverage = 0
            
            if sentiment_coverage >= 80:
                working_modules['sentiment_analysis_module'] = {
                    'performance': sentiment_coverage,
                    'status': 'WORKING',
                    'sentiment_count': sentiment_count,
                    'news_count': news_count
                }
            else:
                problematic_modules['sentiment_analysis_module'] = {
                    'performance': sentiment_coverage,
                    'status': 'PROBLEMATIC',
                    'sentiment_count': sentiment_count,
                    'news_count': news_count
                }
            
            print(f"     Sentiment Analysis Module: {sentiment_coverage:.1f}% - {'WORKING' if sentiment_coverage >= 80 else 'PROBLEMATIC'}")
            
        except Exception as e:
            problematic_modules['sentiment_analysis_module'] = {'error': str(e), 'status': 'ERROR'}
            print(f"     [ERROR] Sentiment Analysis Module: {e}")
        
        return {
            'working_modules': working_modules,
            'problematic_modules': problematic_modules
        }
        
    except Exception as e:
        return {'error': str(e)}

def calculate_overall_performance(working_modules: Dict[str, Any], problematic_modules: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall performance"""
    try:
        performance = {
            'working_modules_count': len(working_modules),
            'problematic_modules_count': len(problematic_modules),
            'total_modules': len(working_modules) + len(problematic_modules),
            'working_percentage': 0.0,
            'overall_score': 0.0
        }
        
        # Calculate working percentage
        if performance['total_modules'] > 0:
            performance['working_percentage'] = (performance['working_modules_count'] / performance['total_modules']) * 100
        
        # Calculate overall score
        working_scores = [module.get('performance', 0) for module in working_modules.values()]
        problematic_scores = [module.get('performance', 0) for module in problematic_modules.values()]
        
        all_scores = working_scores + problematic_scores
        if all_scores:
            performance['overall_score'] = sum(all_scores) / len(all_scores)
        
        return performance
        
    except Exception as e:
        return {'error': str(e)}

def assess_production_readiness(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Assess production readiness"""
    try:
        readiness = {
            'readiness_status': '',
            'deployment_strategy': '',
            'monitoring_requirements': {},
            'risk_level': '',
            'recommendations': []
        }
        
        # Analyze working modules
        working_modules = test_results.get('working_modules', {})
        problematic_modules = test_results.get('problematic_modules', {})
        overall_performance = test_results.get('overall_performance', {})
        
        working_count = len(working_modules)
        problematic_count = len(problematic_modules)
        total_count = working_count + problematic_count
        
        # Determine readiness status
        if working_count >= total_count * 0.8:
            readiness['readiness_status'] = 'READY_FOR_PRODUCTION'
            readiness['deployment_strategy'] = 'IMMEDIATE_DEPLOYMENT'
            readiness['risk_level'] = 'LOW'
        elif working_count >= total_count * 0.6:
            readiness['readiness_status'] = 'READY_WITH_MONITORING'
            readiness['deployment_strategy'] = 'GRADUAL_DEPLOYMENT'
            readiness['risk_level'] = 'MEDIUM'
        elif working_count >= total_count * 0.4:
            readiness['readiness_status'] = 'READY_WITH_IMPROVEMENTS'
            readiness['deployment_strategy'] = 'PHASED_DEPLOYMENT'
            readiness['risk_level'] = 'HIGH'
        else:
            readiness['readiness_status'] = 'NOT_READY'
            readiness['deployment_strategy'] = 'DEVELOPMENT_CONTINUATION'
            readiness['risk_level'] = 'CRITICAL'
        
        # Set monitoring requirements
        readiness['monitoring_requirements'] = {
            'trading_module': 'LOW' if 'trading_module' in working_modules else 'HIGH',
            'market_data_module': 'LOW' if 'market_data_module' in working_modules else 'HIGH',
            'risk_management_module': 'LOW' if 'risk_management_module' in working_modules else 'HIGH',
            'technical_analysis_module': 'LOW' if 'technical_analysis_module' in working_modules else 'HIGH',
            'fundamental_analysis_module': 'LOW' if 'fundamental_analysis_module' in working_modules else 'HIGH',
            'sentiment_analysis_module': 'LOW' if 'sentiment_analysis_module' in working_modules else 'HIGH'
        }
        
        # Generate recommendations
        if problematic_count > 0:
            readiness['recommendations'].append(f"Fix {problematic_count} problematic modules before full deployment")
        
        if overall_performance.get('overall_score', 0) < 80:
            readiness['recommendations'].append("Improve overall performance to 80%+ before production")
        
        if readiness['risk_level'] in ['HIGH', 'CRITICAL']:
            readiness['recommendations'].append("Implement comprehensive monitoring and rollback plans")
        
        return readiness
        
    except Exception as e:
        return {'error': str(e)}

def generate_final_recommendations(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final recommendations"""
    try:
        recommendations = {
            'deployment_plan': {},
            'monitoring_strategy': {},
            'maintenance_plan': {},
            'success_metrics': {},
            'next_steps': []
        }
        
        # Analyze test results
        working_modules = test_results.get('working_modules', {})
        problematic_modules = test_results.get('problematic_modules', {})
        production_readiness = test_results.get('production_readiness', {})
        
        # Deployment plan
        readiness_status = production_readiness.get('readiness_status', 'UNKNOWN')
        if readiness_status == 'READY_FOR_PRODUCTION':
            recommendations['deployment_plan'] = {
                'phase': 'IMMEDIATE_DEPLOYMENT',
                'modules_to_deploy': list(working_modules.keys()),
                'modules_to_fix': list(problematic_modules.keys()),
                'rollback_plan': 'STANDARD'
            }
        elif readiness_status == 'READY_WITH_MONITORING':
            recommendations['deployment_plan'] = {
                'phase': 'GRADUAL_DEPLOYMENT',
                'modules_to_deploy': list(working_modules.keys()),
                'modules_to_fix': list(problematic_modules.keys()),
                'rollback_plan': 'ENHANCED'
            }
        else:
            recommendations['deployment_plan'] = {
                'phase': 'DEVELOPMENT_CONTINUATION',
                'modules_to_deploy': [],
                'modules_to_fix': list(problematic_modules.keys()),
                'rollback_plan': 'COMPREHENSIVE'
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
                "Deploy working modules immediately",
                "Monitor system performance",
                "Fix problematic modules in parallel",
                "Plan full system deployment"
            ]
        elif readiness_status == 'READY_WITH_MONITORING':
            recommendations['next_steps'] = [
                "Deploy working modules with monitoring",
                "Fix problematic modules",
                "Monitor system performance closely",
                "Plan gradual deployment"
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

def generate_final_report(test_results: Dict[str, Any]) -> None:
    """Generate final report"""
    print("\nFINAL SYSTEM TEST REPORT")
    print("=" * 80)
    
    # Working modules
    working_modules = test_results.get('working_modules', {})
    print(f"Working Modules: {len(working_modules)}")
    for module_name, module_data in working_modules.items():
        performance = module_data.get('performance', 0)
        print(f"  {module_name}: {performance:.1f}% (WORKING)")
    
    # Problematic modules
    problematic_modules = test_results.get('problematic_modules', {})
    print(f"\nProblematic Modules: {len(problematic_modules)}")
    for module_name, module_data in problematic_modules.items():
        performance = module_data.get('performance', 0)
        status = module_data.get('status', 'UNKNOWN')
        print(f"  {module_name}: {performance:.1f}% ({status})")
    
    # Overall performance
    overall_performance = test_results.get('overall_performance', {})
    print(f"\nOverall Performance:")
    print(f"  Working Modules: {overall_performance.get('working_modules_count', 0)}")
    print(f"  Problematic Modules: {overall_performance.get('problematic_modules_count', 0)}")
    print(f"  Working Percentage: {overall_performance.get('working_percentage', 0):.1f}%")
    print(f"  Overall Score: {overall_performance.get('overall_score', 0):.1f}%")
    
    # Production readiness
    production_readiness = test_results.get('production_readiness', {})
    print(f"\nProduction Readiness:")
    print(f"  Status: {production_readiness.get('readiness_status', 'UNKNOWN')}")
    print(f"  Deployment Strategy: {production_readiness.get('deployment_strategy', 'UNKNOWN')}")
    print(f"  Risk Level: {production_readiness.get('risk_level', 'UNKNOWN')}")
    
    # Recommendations
    final_recommendations = test_results.get('final_recommendations', {})
    print(f"\nFinal Recommendations:")
    deployment_plan = final_recommendations.get('deployment_plan', {})
    print(f"  Deployment Phase: {deployment_plan.get('phase', 'UNKNOWN')}")
    print(f"  Modules to Deploy: {len(deployment_plan.get('modules_to_deploy', []))}")
    print(f"  Modules to Fix: {len(deployment_plan.get('modules_to_fix', []))}")
    
    # Next steps
    next_steps = final_recommendations.get('next_steps', [])
    print(f"\nNext Steps:")
    for i, step in enumerate(next_steps, 1):
        print(f"  {i}. {step}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"final_system_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nFinal system test results saved to: {results_file}")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    final_system_test()
