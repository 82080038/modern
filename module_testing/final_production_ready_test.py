#!/usr/bin/env python3
"""
Final Production Ready Test
===========================

Script final untuk melakukan testing komprehensif sistem trading
yang sudah diperbaiki untuk menentukan kesiapan production.

Author: AI Assistant
Date: 2025-01-17
"""

import sys
import os
import json
import time
import mysql.connector
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class FinalProductionReadyTest:
    """Final Production Ready Test"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection = None
        self.cursor = None
    
    def connect_database(self):
        """Connect to database with proper configuration"""
        try:
            self.connection = mysql.connector.connect(
                **self.db_config,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            self.cursor = self.connection.cursor()
            print("[PASS] Database connection established")
            return True
        except Exception as e:
            print(f"[FAIL] Database connection failed: {e}")
            return False
    
    def disconnect_database(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("[PASS] Database connection closed")
    
    def test_data_completeness(self) -> Dict[str, Any]:
        """Test data completeness across all modules"""
        try:
            print("   Testing data completeness...")
            
            completeness_results = {
                'market_data_completeness': {},
                'historical_data_completeness': {},
                'fundamental_data_completeness': {},
                'technical_data_completeness': {},
                'sentiment_data_completeness': {},
                'trading_data_completeness': {},
                'risk_data_completeness': {},
                'overall_completeness_score': 0.0
            }
            
            # Test market data completeness
            try:
                self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol LIKE '%.JK'")
                market_data_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data WHERE symbol LIKE '%.JK'")
                market_symbols_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol LIKE '%.JK' AND date >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
                recent_market_data_count = self.cursor.fetchone()[0]
                
                market_completeness_score = min(100, (market_data_count / 1000 * 100)) if market_data_count > 0 else 0
                
                completeness_results['market_data_completeness'] = {
                    'status': 'PASS',
                    'total_records': market_data_count,
                    'unique_symbols': market_symbols_count,
                    'recent_records': recent_market_data_count,
                    'completeness_score': market_completeness_score
                }
                
                print(f"     Market data completeness: {market_completeness_score:.1f}%")
                
            except Exception as e:
                completeness_results['market_data_completeness'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Market data completeness: {e}")
            
            # Test historical data completeness
            try:
                self.cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily WHERE symbol LIKE '%.JK'")
                historical_data_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(DISTINCT symbol) FROM historical_ohlcv_daily WHERE symbol LIKE '%.JK'")
                historical_symbols_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily WHERE symbol LIKE '%.JK' AND date >= DATE_SUB(NOW(), INTERVAL 365 DAY)")
                recent_historical_data_count = self.cursor.fetchone()[0]
                
                historical_completeness_score = min(100, (historical_data_count / 10000 * 100)) if historical_data_count > 0 else 0
                
                completeness_results['historical_data_completeness'] = {
                    'status': 'PASS',
                    'total_records': historical_data_count,
                    'unique_symbols': historical_symbols_count,
                    'recent_records': recent_historical_data_count,
                    'completeness_score': historical_completeness_score
                }
                
                print(f"     Historical data completeness: {historical_completeness_score:.1f}%")
                
            except Exception as e:
                completeness_results['historical_data_completeness'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Historical data completeness: {e}")
            
            # Test fundamental data completeness
            try:
                self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE symbol LIKE '%.JK'")
                fundamental_data_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(DISTINCT symbol) FROM fundamental_data WHERE symbol LIKE '%.JK'")
                fundamental_symbols_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE symbol LIKE '%.JK' AND pe_ratio IS NOT NULL")
                pe_ratio_count = self.cursor.fetchone()[0]
                
                fundamental_completeness_score = min(100, (fundamental_data_count / 100 * 100)) if fundamental_data_count > 0 else 0
                
                completeness_results['fundamental_data_completeness'] = {
                    'status': 'PASS',
                    'total_records': fundamental_data_count,
                    'unique_symbols': fundamental_symbols_count,
                    'pe_ratio_records': pe_ratio_count,
                    'completeness_score': fundamental_completeness_score
                }
                
                print(f"     Fundamental data completeness: {fundamental_completeness_score:.1f}%")
                
            except Exception as e:
                completeness_results['fundamental_data_completeness'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Fundamental data completeness: {e}")
            
            # Test technical data completeness
            try:
                self.cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE symbol LIKE '%.JK'")
                technical_data_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(DISTINCT symbol) FROM technical_indicators WHERE symbol LIKE '%.JK'")
                technical_symbols_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE symbol LIKE '%.JK' AND indicator_type IS NOT NULL")
                typed_indicators_count = self.cursor.fetchone()[0]
                
                technical_completeness_score = min(100, (technical_data_count / 1000 * 100)) if technical_data_count > 0 else 0
                
                completeness_results['technical_data_completeness'] = {
                    'status': 'PASS',
                    'total_records': technical_data_count,
                    'unique_symbols': technical_symbols_count,
                    'typed_indicators': typed_indicators_count,
                    'completeness_score': technical_completeness_score
                }
                
                print(f"     Technical data completeness: {technical_completeness_score:.1f}%")
                
            except Exception as e:
                completeness_results['technical_data_completeness'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Technical data completeness: {e}")
            
            # Test sentiment data completeness
            try:
                self.cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE symbol LIKE '%.JK'")
                sentiment_data_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(DISTINCT symbol) FROM sentiment_data WHERE symbol LIKE '%.JK'")
                sentiment_symbols_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE symbol LIKE '%.JK' AND sentiment_score IS NOT NULL")
                scored_sentiment_count = self.cursor.fetchone()[0]
                
                sentiment_completeness_score = min(100, (sentiment_data_count / 50 * 100)) if sentiment_data_count > 0 else 0
                
                completeness_results['sentiment_data_completeness'] = {
                    'status': 'PASS',
                    'total_records': sentiment_data_count,
                    'unique_symbols': sentiment_symbols_count,
                    'scored_sentiment': scored_sentiment_count,
                    'completeness_score': sentiment_completeness_score
                }
                
                print(f"     Sentiment data completeness: {sentiment_completeness_score:.1f}%")
                
            except Exception as e:
                completeness_results['sentiment_data_completeness'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Sentiment data completeness: {e}")
            
            # Test trading data completeness
            try:
                self.cursor.execute("SELECT COUNT(*) FROM orders")
                orders_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM trades")
                trades_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM orders WHERE executed_at IS NOT NULL")
                executed_orders_count = self.cursor.fetchone()[0]
                
                trading_completeness_score = min(100, ((orders_count + trades_count) / 100 * 100)) if (orders_count + trades_count) > 0 else 0
                
                completeness_results['trading_data_completeness'] = {
                    'status': 'PASS',
                    'orders_count': orders_count,
                    'trades_count': trades_count,
                    'executed_orders': executed_orders_count,
                    'completeness_score': trading_completeness_score
                }
                
                print(f"     Trading data completeness: {trading_completeness_score:.1f}%")
                
            except Exception as e:
                completeness_results['trading_data_completeness'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Trading data completeness: {e}")
            
            # Test risk data completeness
            try:
                self.cursor.execute("SELECT COUNT(*) FROM risk_metrics")
                risk_metrics_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM portfolio_risk")
                portfolio_risk_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM risk_alerts")
                risk_alerts_count = self.cursor.fetchone()[0]
                
                risk_completeness_score = min(100, ((risk_metrics_count + portfolio_risk_count + risk_alerts_count) / 50 * 100)) if (risk_metrics_count + portfolio_risk_count + risk_alerts_count) > 0 else 0
                
                completeness_results['risk_data_completeness'] = {
                    'status': 'PASS',
                    'risk_metrics_count': risk_metrics_count,
                    'portfolio_risk_count': portfolio_risk_count,
                    'risk_alerts_count': risk_alerts_count,
                    'completeness_score': risk_completeness_score
                }
                
                print(f"     Risk data completeness: {risk_completeness_score:.1f}%")
                
            except Exception as e:
                completeness_results['risk_data_completeness'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Risk data completeness: {e}")
            
            # Calculate overall completeness score
            completeness_scores = []
            for module, data in completeness_results.items():
                if isinstance(data, dict) and 'completeness_score' in data:
                    completeness_scores.append(data['completeness_score'])
            
            overall_completeness_score = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
            completeness_results['overall_completeness_score'] = overall_completeness_score
            
            print(f"     Overall data completeness: {overall_completeness_score:.1f}%")
            
            return completeness_results
            
        except Exception as e:
            return {'error': str(e)}
    
    def test_system_performance(self) -> Dict[str, Any]:
        """Test system performance across all modules"""
        try:
            print("   Testing system performance...")
            
            performance_results = {
                'trading_module_performance': {},
                'market_data_module_performance': {},
                'risk_management_module_performance': {},
                'technical_analysis_module_performance': {},
                'fundamental_analysis_module_performance': {},
                'sentiment_analysis_module_performance': {},
                'overall_performance_score': 0.0
            }
            
            # Test trading module performance
            try:
                self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'executed'")
                executed_orders = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM orders")
                total_orders = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT AVG(TIMESTAMPDIFF(MICROSECOND, created_at, executed_at)) FROM orders WHERE executed_at IS NOT NULL")
                avg_execution_time = self.cursor.fetchone()[0] or 0
                
                execution_rate = (executed_orders / total_orders * 100) if total_orders > 0 else 0
                execution_speed_score = max(0, 100 - (avg_execution_time / 1000000))  # Convert to seconds
                
                trading_performance_score = (execution_rate + execution_speed_score) / 2
                
                performance_results['trading_module_performance'] = {
                    'status': 'PASS',
                    'execution_rate': execution_rate,
                    'execution_speed_score': execution_speed_score,
                    'performance_score': trading_performance_score
                }
                
                print(f"     Trading module performance: {trading_performance_score:.1f}%")
                
            except Exception as e:
                performance_results['trading_module_performance'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Trading module performance: {e}")
            
            # Test market data module performance
            try:
                self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol LIKE '%.JK' AND date >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
                recent_market_data = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol LIKE '%.JK'")
                total_market_data = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT AVG(overall_quality_score) FROM market_data_quality_metrics")
                data_quality_score = self.cursor.fetchone()[0] or 0
                
                market_data_performance_score = (recent_market_data / total_market_data * 100) if total_market_data > 0 else 0
                market_data_performance_score = (market_data_performance_score + float(data_quality_score)) / 2
                
                performance_results['market_data_module_performance'] = {
                    'status': 'PASS',
                    'recent_data_count': recent_market_data,
                    'total_data_count': total_market_data,
                    'data_quality_score': float(data_quality_score),
                    'performance_score': market_data_performance_score
                }
                
                print(f"     Market data module performance: {market_data_performance_score:.1f}%")
                
            except Exception as e:
                performance_results['market_data_module_performance'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Market data module performance: {e}")
            
            # Test risk management module performance
            try:
                self.cursor.execute("SELECT COUNT(*) FROM risk_metrics WHERE symbol IS NOT NULL")
                risk_metrics_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM portfolio_risk")
                portfolio_risk_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT AVG(sharpe_ratio) FROM risk_metrics WHERE sharpe_ratio IS NOT NULL")
                avg_sharpe_ratio = self.cursor.fetchone()[0] or 0
                
                risk_management_performance_score = (risk_metrics_count / 10 * 100) if risk_metrics_count > 0 else 0
                risk_management_performance_score = (risk_management_performance_score + float(avg_sharpe_ratio) * 10) / 2
                
                performance_results['risk_management_module_performance'] = {
                    'status': 'PASS',
                    'risk_metrics_count': risk_metrics_count,
                    'portfolio_risk_count': portfolio_risk_count,
                    'avg_sharpe_ratio': float(avg_sharpe_ratio),
                    'performance_score': risk_management_performance_score
                }
                
                print(f"     Risk management module performance: {risk_management_performance_score:.1f}%")
                
            except Exception as e:
                performance_results['risk_management_module_performance'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Risk management module performance: {e}")
            
            # Test technical analysis module performance
            try:
                self.cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE symbol LIKE '%.JK' AND indicator_type IS NOT NULL")
                typed_indicators_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE symbol LIKE '%.JK'")
                total_indicators_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(DISTINCT indicator_type) FROM technical_indicators WHERE indicator_type IS NOT NULL")
                unique_indicator_types = self.cursor.fetchone()[0]
                
                technical_analysis_performance_score = (typed_indicators_count / total_indicators_count * 100) if total_indicators_count > 0 else 0
                
                performance_results['technical_analysis_module_performance'] = {
                    'status': 'PASS',
                    'typed_indicators_count': typed_indicators_count,
                    'total_indicators_count': total_indicators_count,
                    'unique_indicator_types': unique_indicator_types,
                    'performance_score': technical_analysis_performance_score
                }
                
                print(f"     Technical analysis module performance: {technical_analysis_performance_score:.1f}%")
                
            except Exception as e:
                performance_results['technical_analysis_module_performance'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Technical analysis module performance: {e}")
            
            # Test fundamental analysis module performance
            try:
                self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE symbol LIKE '%.JK' AND pe_ratio IS NOT NULL")
                pe_ratio_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE symbol LIKE '%.JK'")
                total_fundamental_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT AVG(pe_ratio) FROM fundamental_data WHERE pe_ratio IS NOT NULL")
                avg_pe_ratio = self.cursor.fetchone()[0] or 0
                
                fundamental_analysis_performance_score = (pe_ratio_count / total_fundamental_count * 100) if total_fundamental_count > 0 else 0
                
                performance_results['fundamental_analysis_module_performance'] = {
                    'status': 'PASS',
                    'pe_ratio_count': pe_ratio_count,
                    'total_fundamental_count': total_fundamental_count,
                    'avg_pe_ratio': float(avg_pe_ratio),
                    'performance_score': fundamental_analysis_performance_score
                }
                
                print(f"     Fundamental analysis module performance: {fundamental_analysis_performance_score:.1f}%")
                
            except Exception as e:
                performance_results['fundamental_analysis_module_performance'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Fundamental analysis module performance: {e}")
            
            # Test sentiment analysis module performance
            try:
                self.cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE symbol LIKE '%.JK' AND sentiment_score IS NOT NULL")
                scored_sentiment_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE symbol LIKE '%.JK'")
                total_sentiment_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT AVG(confidence) FROM sentiment_data WHERE confidence IS NOT NULL")
                avg_confidence = self.cursor.fetchone()[0] or 0
                
                sentiment_analysis_performance_score = (scored_sentiment_count / total_sentiment_count * 100) if total_sentiment_count > 0 else 0
                sentiment_analysis_performance_score = (sentiment_analysis_performance_score + float(avg_confidence)) / 2
                
                performance_results['sentiment_analysis_module_performance'] = {
                    'status': 'PASS',
                    'scored_sentiment_count': scored_sentiment_count,
                    'total_sentiment_count': total_sentiment_count,
                    'avg_confidence': float(avg_confidence),
                    'performance_score': sentiment_analysis_performance_score
                }
                
                print(f"     Sentiment analysis module performance: {sentiment_analysis_performance_score:.1f}%")
                
            except Exception as e:
                performance_results['sentiment_analysis_module_performance'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Sentiment analysis module performance: {e}")
            
            # Calculate overall performance score
            performance_scores = []
            for module, data in performance_results.items():
                if isinstance(data, dict) and 'performance_score' in data:
                    performance_scores.append(data['performance_score'])
            
            overall_performance_score = sum(performance_scores) / len(performance_scores) if performance_scores else 0
            performance_results['overall_performance_score'] = overall_performance_score
            
            print(f"     Overall system performance: {overall_performance_score:.1f}%")
            
            return performance_results
            
        except Exception as e:
            return {'error': str(e)}
    
    def test_production_readiness(self) -> Dict[str, Any]:
        """Test production readiness"""
        try:
            print("   Testing production readiness...")
            
            readiness_results = {
                'data_availability': {},
                'system_stability': {},
                'performance_metrics': {},
                'security_compliance': {},
                'monitoring_capabilities': {},
                'overall_readiness_score': 0.0
            }
            
            # Test data availability
            try:
                self.cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data WHERE symbol LIKE '%.JK'")
                available_symbols = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE date >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
                recent_data_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily WHERE date >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
                historical_data_count = self.cursor.fetchone()[0]
                
                data_availability_score = min(100, (available_symbols / 10 * 100)) if available_symbols > 0 else 0
                
                readiness_results['data_availability'] = {
                    'status': 'PASS',
                    'available_symbols': available_symbols,
                    'recent_data_count': recent_data_count,
                    'historical_data_count': historical_data_count,
                    'availability_score': data_availability_score
                }
                
                print(f"     Data availability: {data_availability_score:.1f}%")
                
            except Exception as e:
                readiness_results['data_availability'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Data availability: {e}")
            
            # Test system stability
            try:
                self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'executed'")
                executed_orders = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'failed'")
                failed_orders = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM orders")
                total_orders = self.cursor.fetchone()[0]
                
                success_rate = (executed_orders / total_orders * 100) if total_orders > 0 else 0
                failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
                
                system_stability_score = max(0, success_rate - failure_rate)
                
                readiness_results['system_stability'] = {
                    'status': 'PASS',
                    'executed_orders': executed_orders,
                    'failed_orders': failed_orders,
                    'total_orders': total_orders,
                    'success_rate': success_rate,
                    'failure_rate': failure_rate,
                    'stability_score': system_stability_score
                }
                
                print(f"     System stability: {system_stability_score:.1f}%")
                
            except Exception as e:
                readiness_results['system_stability'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] System stability: {e}")
            
            # Test performance metrics
            try:
                self.cursor.execute("SELECT AVG(TIMESTAMPDIFF(MICROSECOND, created_at, executed_at)) FROM orders WHERE executed_at IS NOT NULL")
                avg_execution_time = self.cursor.fetchone()[0] or 0
                
                self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE date >= DATE_SUB(NOW(), INTERVAL 1 HOUR)")
                hourly_data_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT AVG(overall_quality_score) FROM market_data_quality_metrics")
                data_quality_score = self.cursor.fetchone()[0] or 0
                
                performance_metrics_score = max(0, 100 - (avg_execution_time / 1000000))  # Convert to seconds
                performance_metrics_score = (performance_metrics_score + float(data_quality_score)) / 2
                
                readiness_results['performance_metrics'] = {
                    'status': 'PASS',
                    'avg_execution_time': avg_execution_time,
                    'hourly_data_count': hourly_data_count,
                    'data_quality_score': float(data_quality_score),
                    'performance_score': performance_metrics_score
                }
                
                print(f"     Performance metrics: {performance_metrics_score:.1f}%")
                
            except Exception as e:
                readiness_results['performance_metrics'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Performance metrics: {e}")
            
            # Test security compliance
            try:
                self.cursor.execute("SELECT COUNT(*) FROM trading_risk_rules WHERE is_active = TRUE")
                active_risk_rules = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM trading_execution_rules WHERE is_active = TRUE")
                active_execution_rules = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM risk_alerts")
                risk_alerts_count = self.cursor.fetchone()[0]
                
                security_compliance_score = (active_risk_rules + active_execution_rules + risk_alerts_count) / 3 * 100
                
                readiness_results['security_compliance'] = {
                    'status': 'PASS',
                    'active_risk_rules': active_risk_rules,
                    'active_execution_rules': active_execution_rules,
                    'risk_alerts_count': risk_alerts_count,
                    'compliance_score': security_compliance_score
                }
                
                print(f"     Security compliance: {security_compliance_score:.1f}%")
                
            except Exception as e:
                readiness_results['security_compliance'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Security compliance: {e}")
            
            # Test monitoring capabilities
            try:
                self.cursor.execute("SELECT COUNT(*) FROM system_monitoring")
                system_monitoring_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM performance_metrics")
                performance_metrics_count = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM alerting_system")
                alerting_system_count = self.cursor.fetchone()[0]
                
                monitoring_capabilities_score = (system_monitoring_count + performance_metrics_count + alerting_system_count) / 3 * 100
                
                readiness_results['monitoring_capabilities'] = {
                    'status': 'PASS',
                    'system_monitoring_count': system_monitoring_count,
                    'performance_metrics_count': performance_metrics_count,
                    'alerting_system_count': alerting_system_count,
                    'monitoring_score': monitoring_capabilities_score
                }
                
                print(f"     Monitoring capabilities: {monitoring_capabilities_score:.1f}%")
                
            except Exception as e:
                readiness_results['monitoring_capabilities'] = {'status': 'ERROR', 'message': str(e)}
                print(f"     [ERROR] Monitoring capabilities: {e}")
            
            # Calculate overall readiness score
            readiness_scores = []
            for capability, data in readiness_results.items():
                if isinstance(data, dict) and 'score' in data:
                    readiness_scores.append(data['score'])
            
            overall_readiness_score = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0
            readiness_results['overall_readiness_score'] = overall_readiness_score
            
            print(f"     Overall production readiness: {overall_readiness_score:.1f}%")
            
            return readiness_results
            
        except Exception as e:
            return {'error': str(e)}
    
    def run_final_test(self) -> Dict[str, Any]:
        """Run final production ready test"""
        try:
            print("FINAL PRODUCTION READY TEST")
            print("=" * 80)
            print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            
            # Results
            results = {
                'test_type': 'final_production_ready_test',
                'test_start': datetime.now().isoformat(),
                'database_connection': False,
                'data_completeness_test': {},
                'system_performance_test': {},
                'production_readiness_test': {},
                'final_assessment': {}
            }
            
            # Connect to database
            if not self.connect_database():
                return results
            
            results['database_connection'] = True
            
            # Step 1: Test data completeness
            print("\n1. TESTING DATA COMPLETENESS")
            print("-" * 60)
            
            data_completeness_test = self.test_data_completeness()
            results['data_completeness_test'] = data_completeness_test
            print(f"   Data completeness test completed")
            
            # Step 2: Test system performance
            print("\n2. TESTING SYSTEM PERFORMANCE")
            print("-" * 60)
            
            system_performance_test = self.test_system_performance()
            results['system_performance_test'] = system_performance_test
            print(f"   System performance test completed")
            
            # Step 3: Test production readiness
            print("\n3. TESTING PRODUCTION READINESS")
            print("-" * 60)
            
            production_readiness_test = self.test_production_readiness()
            results['production_readiness_test'] = production_readiness_test
            print(f"   Production readiness test completed")
            
            # Step 4: Generate final assessment
            print("\n4. GENERATING FINAL ASSESSMENT")
            print("-" * 60)
            
            final_assessment = self.generate_final_assessment(results)
            results['final_assessment'] = final_assessment
            print(f"   Final assessment completed")
            
            # Close database connection
            self.disconnect_database()
            
            # Generate comprehensive report
            self.generate_comprehensive_report(results)
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Final test failed: {e}")
            return {'error': str(e)}
    
    def generate_final_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final assessment"""
        try:
            assessment = {
                'overall_status': '',
                'production_ready': False,
                'key_achievements': [],
                'remaining_issues': [],
                'final_score': 0.0,
                'recommendations': []
            }
            
            # Analyze data completeness
            data_completeness = results.get('data_completeness_test', {})
            overall_completeness_score = data_completeness.get('overall_completeness_score', 0)
            
            # Analyze system performance
            system_performance = results.get('system_performance_test', {})
            overall_performance_score = system_performance.get('overall_performance_score', 0)
            
            # Analyze production readiness
            production_readiness = results.get('production_readiness_test', {})
            overall_readiness_score = production_readiness.get('overall_readiness_score', 0)
            
            # Calculate final score
            final_score = (overall_completeness_score + overall_performance_score + overall_readiness_score) / 3
            assessment['final_score'] = final_score
            
            # Determine overall status
            if final_score >= 90:
                assessment['overall_status'] = 'EXCELLENT'
                assessment['production_ready'] = True
            elif final_score >= 80:
                assessment['overall_status'] = 'GOOD'
                assessment['production_ready'] = True
            elif final_score >= 70:
                assessment['overall_status'] = 'FAIR'
                assessment['production_ready'] = False
            else:
                assessment['overall_status'] = 'POOR'
                assessment['production_ready'] = False
            
            # Key achievements
            if overall_completeness_score >= 80:
                assessment['key_achievements'].append(f"Data completeness: {overall_completeness_score:.1f}%")
            
            if overall_performance_score >= 80:
                assessment['key_achievements'].append(f"System performance: {overall_performance_score:.1f}%")
            
            if overall_readiness_score >= 80:
                assessment['key_achievements'].append(f"Production readiness: {overall_readiness_score:.1f}%")
            
            # Remaining issues
            if overall_completeness_score < 80:
                assessment['remaining_issues'].append(f"Data completeness needs improvement ({overall_completeness_score:.1f}%)")
            
            if overall_performance_score < 80:
                assessment['remaining_issues'].append(f"System performance needs improvement ({overall_performance_score:.1f}%)")
            
            if overall_readiness_score < 80:
                assessment['remaining_issues'].append(f"Production readiness needs improvement ({overall_readiness_score:.1f}%)")
            
            # Recommendations
            if final_score >= 80:
                assessment['recommendations'].append("System ready for production deployment")
                assessment['recommendations'].append("Implement continuous monitoring and alerting")
                assessment['recommendations'].append("Plan for regular system updates and maintenance")
            else:
                assessment['recommendations'].append("Continue development and testing")
                assessment['recommendations'].append("Fix identified issues before deployment")
                assessment['recommendations'].append("Implement additional testing phases")
            
            return assessment
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive report"""
        print("\nFINAL PRODUCTION READY TEST REPORT")
        print("=" * 80)
        
        # Data completeness test
        data_completeness = results.get('data_completeness_test', {})
        print(f"Data Completeness Test:")
        print(f"  Overall Completeness Score: {data_completeness.get('overall_completeness_score', 0):.1f}%")
        
        market_data = data_completeness.get('market_data_completeness', {})
        if market_data.get('status') == 'PASS':
            print(f"  Market Data: {market_data.get('completeness_score', 0):.1f}% ({market_data.get('total_records', 0):,} records)")
        
        historical_data = data_completeness.get('historical_data_completeness', {})
        if historical_data.get('status') == 'PASS':
            print(f"  Historical Data: {historical_data.get('completeness_score', 0):.1f}% ({historical_data.get('total_records', 0):,} records)")
        
        fundamental_data = data_completeness.get('fundamental_data_completeness', {})
        if fundamental_data.get('status') == 'PASS':
            print(f"  Fundamental Data: {fundamental_data.get('completeness_score', 0):.1f}% ({fundamental_data.get('total_records', 0):,} records)")
        
        technical_data = data_completeness.get('technical_data_completeness', {})
        if technical_data.get('status') == 'PASS':
            print(f"  Technical Data: {technical_data.get('completeness_score', 0):.1f}% ({technical_data.get('total_records', 0):,} records)")
        
        sentiment_data = data_completeness.get('sentiment_data_completeness', {})
        if sentiment_data.get('status') == 'PASS':
            print(f"  Sentiment Data: {sentiment_data.get('completeness_score', 0):.1f}% ({sentiment_data.get('total_records', 0):,} records)")
        
        trading_data = data_completeness.get('trading_data_completeness', {})
        if trading_data.get('status') == 'PASS':
            print(f"  Trading Data: {trading_data.get('completeness_score', 0):.1f}% ({trading_data.get('orders_count', 0):,} orders, {trading_data.get('trades_count', 0):,} trades)")
        
        risk_data = data_completeness.get('risk_data_completeness', {})
        if risk_data.get('status') == 'PASS':
            print(f"  Risk Data: {risk_data.get('completeness_score', 0):.1f}% ({risk_data.get('risk_metrics_count', 0):,} metrics)")
        
        # System performance test
        system_performance = results.get('system_performance_test', {})
        print(f"\nSystem Performance Test:")
        print(f"  Overall Performance Score: {system_performance.get('overall_performance_score', 0):.1f}%")
        
        trading_performance = system_performance.get('trading_module_performance', {})
        if trading_performance.get('status') == 'PASS':
            print(f"  Trading Module: {trading_performance.get('performance_score', 0):.1f}%")
        
        market_performance = system_performance.get('market_data_module_performance', {})
        if market_performance.get('status') == 'PASS':
            print(f"  Market Data Module: {market_performance.get('performance_score', 0):.1f}%")
        
        risk_performance = system_performance.get('risk_management_module_performance', {})
        if risk_performance.get('status') == 'PASS':
            print(f"  Risk Management Module: {risk_performance.get('performance_score', 0):.1f}%")
        
        technical_performance = system_performance.get('technical_analysis_module_performance', {})
        if technical_performance.get('status') == 'PASS':
            print(f"  Technical Analysis Module: {technical_performance.get('performance_score', 0):.1f}%")
        
        fundamental_performance = system_performance.get('fundamental_analysis_module_performance', {})
        if fundamental_performance.get('status') == 'PASS':
            print(f"  Fundamental Analysis Module: {fundamental_performance.get('performance_score', 0):.1f}%")
        
        sentiment_performance = system_performance.get('sentiment_analysis_module_performance', {})
        if sentiment_performance.get('status') == 'PASS':
            print(f"  Sentiment Analysis Module: {sentiment_performance.get('performance_score', 0):.1f}%")
        
        # Production readiness test
        production_readiness = results.get('production_readiness_test', {})
        print(f"\nProduction Readiness Test:")
        print(f"  Overall Readiness Score: {production_readiness.get('overall_readiness_score', 0):.1f}%")
        
        data_availability = production_readiness.get('data_availability', {})
        if data_availability.get('status') == 'PASS':
            print(f"  Data Availability: {data_availability.get('availability_score', 0):.1f}%")
        
        system_stability = production_readiness.get('system_stability', {})
        if system_stability.get('status') == 'PASS':
            print(f"  System Stability: {system_stability.get('stability_score', 0):.1f}%")
        
        performance_metrics = production_readiness.get('performance_metrics', {})
        if performance_metrics.get('status') == 'PASS':
            print(f"  Performance Metrics: {performance_metrics.get('performance_score', 0):.1f}%")
        
        security_compliance = production_readiness.get('security_compliance', {})
        if security_compliance.get('status') == 'PASS':
            print(f"  Security Compliance: {security_compliance.get('compliance_score', 0):.1f}%")
        
        monitoring_capabilities = production_readiness.get('monitoring_capabilities', {})
        if monitoring_capabilities.get('status') == 'PASS':
            print(f"  Monitoring Capabilities: {monitoring_capabilities.get('monitoring_score', 0):.1f}%")
        
        # Final assessment
        final_assessment = results.get('final_assessment', {})
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
        
        recommendations = final_assessment.get('recommendations', [])
        if recommendations:
            print(f"  Recommendations:")
            for recommendation in recommendations:
                print(f"    - {recommendation}")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"final_production_ready_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nFinal production ready test results saved to: {results_file}")
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'scalper',
        'port': 3306
    }
    
    # Create final production ready test instance
    final_test = FinalProductionReadyTest(db_config)
    
    # Run final test
    results = final_test.run_final_test()
    
    return results

if __name__ == "__main__":
    main()
