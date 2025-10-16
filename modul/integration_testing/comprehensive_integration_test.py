"""
Comprehensive Integration Test
============================

Test komprehensif untuk semua enhanced services yang telah dibuat.
Menguji integrasi, performance, dan functionality.

Author: AI Assistant
Date: 2025-01-17
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import get_db
from backend.app.services.enhanced_trading_service_v2 import EnhancedTradingServiceV2
from backend.app.services.enhanced_market_data_service_v2 import EnhancedMarketDataServiceV2
from backend.app.services.enhanced_portfolio_optimization_service import EnhancedPortfolioOptimizationService
from backend.app.services.enhanced_fundamental_analysis_service import EnhancedFundamentalAnalysisService
from backend.app.services.enhanced_earnings_service import EnhancedEarningsService
from backend.app.services.enhanced_economic_calendar_service import EnhancedEconomicCalendarService
from backend.app.services.enhanced_notifications_service import EnhancedNotificationsService
from backend.app.services.enhanced_watchlist_service import EnhancedWatchlistService

logger = logging.getLogger(__name__)

class ComprehensiveIntegrationTest:
    """
    Comprehensive Integration Test untuk semua enhanced services
    """
    
    def __init__(self):
        self.db = next(get_db())
        self.test_results = {}
        self.performance_metrics = {}
        
        # Initialize services
        self.trading_service = EnhancedTradingServiceV2(self.db)
        self.market_data_service = EnhancedMarketDataServiceV2(self.db)
        self.portfolio_service = EnhancedPortfolioOptimizationService(self.db)
        self.fundamental_service = EnhancedFundamentalAnalysisService(self.db)
        self.earnings_service = EnhancedEarningsService(self.db)
        self.economic_service = EnhancedEconomicCalendarService(self.db)
        self.notifications_service = EnhancedNotificationsService(self.db)
        self.watchlist_service = EnhancedWatchlistService(self.db)
        
        # Test data
        self.test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        self.test_user_id = 1
        self.test_portfolio_id = 1
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive integration test"""
        try:
            print("🚀 Starting Comprehensive Integration Test...")
            print("=" * 60)
            
            # Test 1: Enhanced Trading Service
            print("\n📈 Testing Enhanced Trading Service...")
            trading_results = await self._test_trading_service()
            self.test_results['trading_service'] = trading_results
            
            # Test 2: Enhanced Market Data Service
            print("\n📊 Testing Enhanced Market Data Service...")
            market_data_results = await self._test_market_data_service()
            self.test_results['market_data_service'] = market_data_results
            
            # Test 3: Enhanced Portfolio Optimization Service
            print("\n💼 Testing Enhanced Portfolio Optimization Service...")
            portfolio_results = await self._test_portfolio_service()
            self.test_results['portfolio_service'] = portfolio_results
            
            # Test 4: Enhanced Fundamental Analysis Service
            print("\n📋 Testing Enhanced Fundamental Analysis Service...")
            fundamental_results = await self._test_fundamental_service()
            self.test_results['fundamental_service'] = fundamental_results
            
            # Test 5: Enhanced Earnings Service
            print("\n💰 Testing Enhanced Earnings Service...")
            earnings_results = await self._test_earnings_service()
            self.test_results['earnings_service'] = earnings_results
            
            # Test 6: Enhanced Economic Calendar Service
            print("\n📅 Testing Enhanced Economic Calendar Service...")
            economic_results = await self._test_economic_service()
            self.test_results['economic_service'] = economic_results
            
            # Test 7: Enhanced Notifications Service
            print("\n🔔 Testing Enhanced Notifications Service...")
            notifications_results = await self._test_notifications_service()
            self.test_results['notifications_service'] = notifications_results
            
            # Test 8: Enhanced Watchlist Service
            print("\n📝 Testing Enhanced Watchlist Service...")
            watchlist_results = await self._test_watchlist_service()
            self.test_results['watchlist_service'] = watchlist_results
            
            # Test 9: Cross-Service Integration
            print("\n🔗 Testing Cross-Service Integration...")
            integration_results = await self._test_cross_service_integration()
            self.test_results['cross_service_integration'] = integration_results
            
            # Test 10: Performance Testing
            print("\n⚡ Testing Performance...")
            performance_results = await self._test_performance()
            self.test_results['performance'] = performance_results
            
            # Generate comprehensive report
            report = await self._generate_comprehensive_report()
            
            print("\n" + "=" * 60)
            print("✅ Comprehensive Integration Test Completed!")
            print("=" * 60)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in comprehensive test: {e}")
            return {'error': str(e)}
    
    async def _test_trading_service(self) -> Dict[str, Any]:
        """Test Enhanced Trading Service"""
        try:
            results = {
                'service': 'Enhanced Trading Service V2',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Create order
            start_time = datetime.now()
            order_result = await self.trading_service.create_order(
                portfolio_id=self.test_portfolio_id,
                symbol='AAPL',
                order_type='market',
                side='buy',
                quantity=10,
                price=150.0
            )
            end_time = datetime.now()
            
            if order_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'create_order',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'create_order',
                    'status': 'FAILED',
                    'error': order_result.get('error')
                })
            
            # Test 2: Get order status
            if order_result.get('success'):
                start_time = datetime.now()
                status_result = await self.trading_service.get_order_status(order_result['order_id'])
                end_time = datetime.now()
                
                if 'error' not in status_result:
                    results['tests_passed'] += 1
                    results['test_details'].append({
                        'test': 'get_order_status',
                        'status': 'PASSED',
                        'response_time': (end_time - start_time).total_seconds()
                    })
                else:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': 'get_order_status',
                        'status': 'FAILED',
                        'error': status_result.get('error')
                    })
            
            # Test 3: Get portfolio positions
            start_time = datetime.now()
            positions_result = await self.trading_service.get_portfolio_positions(self.test_portfolio_id)
            end_time = datetime.now()
            
            if isinstance(positions_result, list):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_portfolio_positions',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_portfolio_positions',
                    'status': 'FAILED',
                    'error': 'Invalid response format'
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing trading service: {e}")
            return {'error': str(e)}
    
    async def _test_market_data_service(self) -> Dict[str, Any]:
        """Test Enhanced Market Data Service"""
        try:
            results = {
                'service': 'Enhanced Market Data Service V2',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Get enhanced market data
            start_time = datetime.now()
            market_data_result = await self.market_data_service.get_enhanced_market_data(
                symbol='AAPL',
                timeframe='1d',
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now(),
                include_indicators=True,
                include_volume=True
            )
            end_time = datetime.now()
            
            if market_data_result.get('success') or 'data' in market_data_result:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_enhanced_market_data',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_enhanced_market_data',
                    'status': 'FAILED',
                    'error': market_data_result.get('error')
                })
            
            # Test 2: Get real-time price
            start_time = datetime.now()
            realtime_result = await self.market_data_service.get_real_time_price('AAPL')
            end_time = datetime.now()
            
            if 'error' not in realtime_result:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_real_time_price',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_real_time_price',
                    'status': 'FAILED',
                    'error': realtime_result.get('error')
                })
            
            # Test 3: Start real-time streaming
            start_time = datetime.now()
            streaming_result = await self.market_data_service.start_real_time_streaming(['AAPL', 'MSFT'])
            end_time = datetime.now()
            
            if streaming_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'start_real_time_streaming',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'start_real_time_streaming',
                    'status': 'FAILED',
                    'error': streaming_result.get('error')
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing market data service: {e}")
            return {'error': str(e)}
    
    async def _test_portfolio_service(self) -> Dict[str, Any]:
        """Test Enhanced Portfolio Optimization Service"""
        try:
            results = {
                'service': 'Enhanced Portfolio Optimization Service',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Optimize portfolio
            start_time = datetime.now()
            optimization_result = await self.portfolio_service.optimize_portfolio(
                portfolio_id=self.test_portfolio_id,
                optimization_method='markowitz',
                risk_tolerance=0.5
            )
            end_time = datetime.now()
            
            if optimization_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'optimize_portfolio',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'optimize_portfolio',
                    'status': 'FAILED',
                    'error': optimization_result.get('error')
                })
            
            # Test 2: Get portfolio analysis
            start_time = datetime.now()
            analysis_result = await self.portfolio_service.get_portfolio_analysis(self.test_portfolio_id)
            end_time = datetime.now()
            
            if analysis_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_portfolio_analysis',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_portfolio_analysis',
                    'status': 'FAILED',
                    'error': analysis_result.get('error')
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing portfolio service: {e}")
            return {'error': str(e)}
    
    async def _test_fundamental_service(self) -> Dict[str, Any]:
        """Test Enhanced Fundamental Analysis Service"""
        try:
            results = {
                'service': 'Enhanced Fundamental Analysis Service',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Analyze fundamentals
            start_time = datetime.now()
            analysis_result = await self.fundamental_service.analyze_fundamentals(
                symbol='AAPL',
                analysis_type='comprehensive',
                include_forecasting=True
            )
            end_time = datetime.now()
            
            if analysis_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'analyze_fundamentals',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'analyze_fundamentals',
                    'status': 'FAILED',
                    'error': analysis_result.get('error')
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing fundamental service: {e}")
            return {'error': str(e)}
    
    async def _test_earnings_service(self) -> Dict[str, Any]:
        """Test Enhanced Earnings Service"""
        try:
            results = {
                'service': 'Enhanced Earnings Service',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Analyze earnings
            start_time = datetime.now()
            earnings_result = await self.earnings_service.analyze_earnings(
                symbol='AAPL',
                analysis_type='comprehensive',
                include_forecasting=True
            )
            end_time = datetime.now()
            
            if earnings_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'analyze_earnings',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'analyze_earnings',
                    'status': 'FAILED',
                    'error': earnings_result.get('error')
                })
            
            # Test 2: Get earnings calendar
            start_time = datetime.now()
            calendar_result = await self.earnings_service.get_earnings_calendar('AAPL')
            end_time = datetime.now()
            
            if calendar_result.get('success') or 'error' in calendar_result:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_earnings_calendar',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_earnings_calendar',
                    'status': 'FAILED',
                    'error': 'Unexpected response format'
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing earnings service: {e}")
            return {'error': str(e)}
    
    async def _test_economic_service(self) -> Dict[str, Any]:
        """Test Enhanced Economic Calendar Service"""
        try:
            results = {
                'service': 'Enhanced Economic Calendar Service',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Get economic events
            start_time = datetime.now()
            events_result = await self.economic_service.get_economic_events(
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                country='US'
            )
            end_time = datetime.now()
            
            if events_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_economic_events',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_economic_events',
                    'status': 'FAILED',
                    'error': events_result.get('error')
                })
            
            # Test 2: Get economic indicators
            start_time = datetime.now()
            indicators_result = await self.economic_service.get_economic_indicators('US')
            end_time = datetime.now()
            
            if indicators_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_economic_indicators',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_economic_indicators',
                    'status': 'FAILED',
                    'error': indicators_result.get('error')
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing economic service: {e}")
            return {'error': str(e)}
    
    async def _test_notifications_service(self) -> Dict[str, Any]:
        """Test Enhanced Notifications Service"""
        try:
            results = {
                'service': 'Enhanced Notifications Service',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Create notification
            start_time = datetime.now()
            notification_result = await self.notifications_service.create_notification(
                user_id=self.test_user_id,
                notification_type='price_alert',
                title='Test Notification',
                message='This is a test notification',
                priority='medium'
            )
            end_time = datetime.now()
            
            if notification_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'create_notification',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'create_notification',
                    'status': 'FAILED',
                    'error': notification_result.get('error')
                })
            
            # Test 2: Create price alert
            start_time = datetime.now()
            price_alert_result = await self.notifications_service.create_price_alert(
                user_id=self.test_user_id,
                symbol='AAPL',
                target_price=200.0,
                condition='above'
            )
            end_time = datetime.now()
            
            if price_alert_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'create_price_alert',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'create_price_alert',
                    'status': 'FAILED',
                    'error': price_alert_result.get('error')
                })
            
            # Test 3: Get user notifications
            start_time = datetime.now()
            user_notifications_result = await self.notifications_service.get_user_notifications(
                user_id=self.test_user_id,
                limit=10
            )
            end_time = datetime.now()
            
            if user_notifications_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'get_user_notifications',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'get_user_notifications',
                    'status': 'FAILED',
                    'error': user_notifications_result.get('error')
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing notifications service: {e}")
            return {'error': str(e)}
    
    async def _test_watchlist_service(self) -> Dict[str, Any]:
        """Test Enhanced Watchlist Service"""
        try:
            results = {
                'service': 'Enhanced Watchlist Service',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Create watchlist
            start_time = datetime.now()
            watchlist_result = await self.watchlist_service.create_watchlist(
                user_id=self.test_user_id,
                name='Test Watchlist',
                description='Test watchlist for integration testing',
                category='custom'
            )
            end_time = datetime.now()
            
            if watchlist_result.get('success'):
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'create_watchlist',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds()
                })
                
                # Test 2: Add symbol to watchlist
                watchlist_id = watchlist_result['watchlist_id']
                start_time = datetime.now()
                add_symbol_result = await self.watchlist_service.add_symbol_to_watchlist(
                    watchlist_id=watchlist_id,
                    symbol='AAPL',
                    user_id=self.test_user_id,
                    notes='Test symbol'
                )
                end_time = datetime.now()
                
                if add_symbol_result.get('success'):
                    results['tests_passed'] += 1
                    results['test_details'].append({
                        'test': 'add_symbol_to_watchlist',
                        'status': 'PASSED',
                        'response_time': (end_time - start_time).total_seconds()
                    })
                    
                    # Test 3: Get watchlist performance
                    start_time = datetime.now()
                    performance_result = await self.watchlist_service.get_watchlist_performance(
                        watchlist_id=watchlist_id,
                        user_id=self.test_user_id,
                        period='1y'
                    )
                    end_time = datetime.now()
                    
                    if performance_result.get('success'):
                        results['tests_passed'] += 1
                        results['test_details'].append({
                            'test': 'get_watchlist_performance',
                            'status': 'PASSED',
                            'response_time': (end_time - start_time).total_seconds()
                        })
                    else:
                        results['tests_failed'] += 1
                        results['test_details'].append({
                            'test': 'get_watchlist_performance',
                            'status': 'FAILED',
                            'error': performance_result.get('error')
                        })
                else:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': 'add_symbol_to_watchlist',
                        'status': 'FAILED',
                        'error': add_symbol_result.get('error')
                    })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'create_watchlist',
                    'status': 'FAILED',
                    'error': watchlist_result.get('error')
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing watchlist service: {e}")
            return {'error': str(e)}
    
    async def _test_cross_service_integration(self) -> Dict[str, Any]:
        """Test cross-service integration"""
        try:
            results = {
                'service': 'Cross-Service Integration',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Market Data -> Trading integration
            start_time = datetime.now()
            market_data = await self.market_data_service.get_real_time_price('AAPL')
            if 'error' not in market_data:
                trading_result = await self.trading_service.create_order(
                    portfolio_id=self.test_portfolio_id,
                    symbol='AAPL',
                    order_type='market',
                    side='buy',
                    quantity=5
                )
                end_time = datetime.now()
                
                if trading_result.get('success'):
                    results['tests_passed'] += 1
                    results['test_details'].append({
                        'test': 'market_data_to_trading_integration',
                        'status': 'PASSED',
                        'response_time': (end_time - start_time).total_seconds()
                    })
                else:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': 'market_data_to_trading_integration',
                        'status': 'FAILED',
                        'error': trading_result.get('error')
                    })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'market_data_to_trading_integration',
                    'status': 'FAILED',
                    'error': 'Market data service failed'
                })
            
            # Test 2: Fundamental Analysis -> Portfolio Optimization integration
            start_time = datetime.now()
            fundamental_analysis = await self.fundamental_service.analyze_fundamentals('AAPL')
            if fundamental_analysis.get('success'):
                portfolio_optimization = await self.portfolio_service.optimize_portfolio(
                    portfolio_id=self.test_portfolio_id,
                    optimization_method='markowitz'
                )
                end_time = datetime.now()
                
                if portfolio_optimization.get('success'):
                    results['tests_passed'] += 1
                    results['test_details'].append({
                        'test': 'fundamental_to_portfolio_integration',
                        'status': 'PASSED',
                        'response_time': (end_time - start_time).total_seconds()
                    })
                else:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': 'fundamental_to_portfolio_integration',
                        'status': 'FAILED',
                        'error': portfolio_optimization.get('error')
                    })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'fundamental_to_portfolio_integration',
                    'status': 'FAILED',
                    'error': 'Fundamental analysis service failed'
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing cross-service integration: {e}")
            return {'error': str(e)}
    
    async def _test_performance(self) -> Dict[str, Any]:
        """Test performance metrics"""
        try:
            results = {
                'service': 'Performance Testing',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test concurrent requests
            start_time = datetime.now()
            tasks = []
            for symbol in self.test_symbols:
                task = self.market_data_service.get_real_time_price(symbol)
                tasks.append(task)
            
            concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = datetime.now()
            
            successful_requests = sum(1 for result in concurrent_results if 'error' not in result)
            total_requests = len(concurrent_results)
            
            if successful_requests >= total_requests * 0.8:  # 80% success rate
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'concurrent_requests',
                    'status': 'PASSED',
                    'success_rate': successful_requests / total_requests,
                    'response_time': (end_time - start_time).total_seconds()
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'concurrent_requests',
                    'status': 'FAILED',
                    'success_rate': successful_requests / total_requests,
                    'response_time': (end_time - start_time).total_seconds()
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times),
                    'concurrent_requests_handled': total_requests
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing performance: {e}")
            return {'error': str(e)}
    
    async def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        try:
            total_tests = 0
            total_passed = 0
            total_failed = 0
            
            for service_name, service_results in self.test_results.items():
                if isinstance(service_results, dict) and 'tests_passed' in service_results:
                    total_tests += service_results['tests_passed'] + service_results['tests_failed']
                    total_passed += service_results['tests_passed']
                    total_failed += service_results['tests_failed']
            
            success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            report = {
                'test_summary': {
                    'total_tests': total_tests,
                    'tests_passed': total_passed,
                    'tests_failed': total_failed,
                    'success_rate': success_rate,
                    'test_timestamp': datetime.now().isoformat()
                },
                'service_results': self.test_results,
                'overall_status': 'PASSED' if success_rate >= 80 else 'FAILED',
                'recommendations': self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for service_name, service_results in self.test_results.items():
            if isinstance(service_results, dict) and 'tests_failed' in service_results:
                if service_results['tests_failed'] > 0:
                    recommendations.append(f"Review {service_name}: {service_results['tests_failed']} tests failed")
        
        if not recommendations:
            recommendations.append("All services are performing well. Ready for production deployment.")
        
        return recommendations

async def main():
    """Main function untuk menjalankan comprehensive integration test"""
    try:
        test = ComprehensiveIntegrationTest()
        results = await test.run_comprehensive_test()
        
        print("\n📊 COMPREHENSIVE TEST RESULTS:")
        print("=" * 60)
        print(f"Total Tests: {results['test_summary']['total_tests']}")
        print(f"Tests Passed: {results['test_summary']['tests_passed']}")
        print(f"Tests Failed: {results['test_summary']['tests_failed']}")
        print(f"Success Rate: {results['test_summary']['success_rate']:.2f}%")
        print(f"Overall Status: {results['overall_status']}")
        
        print("\n📋 RECOMMENDATIONS:")
        for recommendation in results['recommendations']:
            print(f"- {recommendation}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    asyncio.run(main())
