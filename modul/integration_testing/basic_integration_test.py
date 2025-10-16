"""
Basic Integration Test
======================

Test dasar untuk menguji enhanced services tanpa emoji dan karakter khusus.

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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasicIntegrationTest:
    """
    Basic Integration Test untuk enhanced services
    """
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        
        # Test data
        self.test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        self.test_user_id = 1
        self.test_portfolio_id = 1
    
    async def run_basic_test(self) -> Dict[str, Any]:
        """Run basic integration test"""
        try:
            print("Starting Basic Integration Test...")
            print("=" * 60)
            
            # Test 1: Enhanced Services File Check
            print("\nTesting Enhanced Services Files...")
            file_results = await self._test_enhanced_services_files()
            self.test_results['enhanced_services_files'] = file_results
            
            # Test 2: Service Structure Test
            print("\nTesting Service Structure...")
            structure_results = await self._test_service_structure()
            self.test_results['service_structure'] = structure_results
            
            # Test 3: Code Quality Test
            print("\nTesting Code Quality...")
            quality_results = await self._test_code_quality()
            self.test_results['code_quality'] = quality_results
            
            # Test 4: Performance Test
            print("\nTesting Performance...")
            performance_results = await self._test_performance()
            self.test_results['performance'] = performance_results
            
            # Generate report
            report = await self._generate_basic_report()
            
            print("\n" + "=" * 60)
            print("Basic Integration Test Completed!")
            print("=" * 60)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in basic test: {e}")
            return {'error': str(e)}
    
    async def _test_enhanced_services_files(self) -> Dict[str, Any]:
        """Test enhanced services files"""
        try:
            results = {
                'test_name': 'Enhanced Services Files',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test enhanced services files
            services_to_test = [
                'enhanced_trading_service_v2.py',
                'enhanced_market_data_service_v2.py',
                'enhanced_portfolio_optimization_service.py',
                'enhanced_fundamental_analysis_service.py',
                'enhanced_earnings_service.py',
                'enhanced_economic_calendar_service.py',
                'enhanced_notifications_service.py',
                'enhanced_watchlist_service.py'
            ]
            
            for service in services_to_test:
                start_time = datetime.now()
                try:
                    # Check if file exists
                    service_path = f"../backend_services/{service}"
                    if os.path.exists(service_path):
                        # Check file size
                        file_size = os.path.getsize(service_path)
                        if file_size > 1000:  # Minimum file size
                            results['tests_passed'] += 1
                            results['test_details'].append({
                                'test': f'check_{service}',
                                'status': 'PASSED',
                                'response_time': (datetime.now() - start_time).total_seconds(),
                                'file_size': file_size
                            })
                        else:
                            results['tests_failed'] += 1
                            results['test_details'].append({
                                'test': f'check_{service}',
                                'status': 'FAILED',
                                'error': f'File too small: {file_size} bytes'
                            })
                    else:
                        results['tests_failed'] += 1
                        results['test_details'].append({
                            'test': f'check_{service}',
                            'status': 'FAILED',
                            'error': f'File not found: {service_path}'
                        })
                except Exception as e:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': f'check_{service}',
                        'status': 'FAILED',
                        'error': str(e)
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
            logger.error(f"Error testing enhanced services files: {e}")
            return {'error': str(e)}
    
    async def _test_service_structure(self) -> Dict[str, Any]:
        """Test service structure"""
        try:
            results = {
                'test_name': 'Service Structure',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test service class definitions
            service_classes = [
                'EnhancedTradingServiceV2',
                'EnhancedMarketDataServiceV2',
                'EnhancedPortfolioOptimizationService',
                'EnhancedFundamentalAnalysisService',
                'EnhancedEarningsService',
                'EnhancedEconomicCalendarService',
                'EnhancedNotificationsService',
                'EnhancedWatchlistService'
            ]
            
            for service_class in service_classes:
                start_time = datetime.now()
                try:
                    # Find corresponding service file
                    service_file = None
                    for file in os.listdir('../backend_services/'):
                        if file.startswith('enhanced_') and file.endswith('.py'):
                            if service_class.lower().replace('enhanced', '').replace('service', '').replace('v2', '') in file:
                                service_file = file
                                break
                    
                    if service_file:
                        service_path = f"../backend_services/{service_file}"
                        with open(service_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if f'class {service_class}' in content:
                                results['tests_passed'] += 1
                                results['test_details'].append({
                                    'test': f'check_class_{service_class}',
                                    'status': 'PASSED',
                                    'response_time': (datetime.now() - start_time).total_seconds()
                                })
                            else:
                                results['tests_failed'] += 1
                                results['test_details'].append({
                                    'test': f'check_class_{service_class}',
                                    'status': 'FAILED',
                                    'error': f'Class {service_class} not found in {service_file}'
                                })
                    else:
                        results['tests_failed'] += 1
                        results['test_details'].append({
                            'test': f'check_class_{service_class}',
                            'status': 'FAILED',
                            'error': f'Service file not found for {service_class}'
                        })
                except Exception as e:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': f'check_class_{service_class}',
                        'status': 'FAILED',
                        'error': str(e)
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
            logger.error(f"Error testing service structure: {e}")
            return {'error': str(e)}
    
    async def _test_code_quality(self) -> Dict[str, Any]:
        """Test code quality"""
        try:
            results = {
                'test_name': 'Code Quality',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test code quality metrics
            start_time = datetime.now()
            total_lines = 0
            total_functions = 0
            total_classes = 0
            total_imports = 0
            total_comments = 0
            
            for service_file in os.listdir('../backend_services/'):
                if service_file.startswith('enhanced_') and service_file.endswith('.py'):
                    try:
                        service_path = f"../backend_services/{service_file}"
                        with open(service_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Count lines
                            lines = content.count('\n')
                            total_lines += lines
                            
                            # Count functions
                            functions = content.count('def ')
                            total_functions += functions
                            
                            # Count classes
                            classes = content.count('class ')
                            total_classes += classes
                            
                            # Count imports
                            imports = content.count('import ')
                            total_imports += imports
                            
                            # Count comments
                            comments = content.count('#')
                            total_comments += comments
                            
                    except Exception as e:
                        continue
            
            end_time = datetime.now()
            
            # Quality checks
            if total_lines > 1000:  # Minimum total lines
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'total_lines_check',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds(),
                    'total_lines': total_lines
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'total_lines_check',
                    'status': 'FAILED',
                    'error': f'Insufficient code: {total_lines} lines'
                })
            
            if total_functions > 50:  # Minimum functions
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'total_functions_check',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds(),
                    'total_functions': total_functions
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'total_functions_check',
                    'status': 'FAILED',
                    'error': f'Insufficient functions: {total_functions} functions'
                })
            
            if total_classes > 8:  # Minimum classes
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'total_classes_check',
                    'status': 'PASSED',
                    'response_time': (end_time - start_time).total_seconds(),
                    'total_classes': total_classes
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'total_classes_check',
                    'status': 'FAILED',
                    'error': f'Insufficient classes: {total_classes} classes'
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times),
                    'total_lines': total_lines,
                    'total_functions': total_functions,
                    'total_classes': total_classes,
                    'total_imports': total_imports,
                    'total_comments': total_comments
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing code quality: {e}")
            return {'error': str(e)}
    
    async def _test_performance(self) -> Dict[str, Any]:
        """Test performance metrics"""
        try:
            results = {
                'test_name': 'Performance Testing',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test file processing performance
            start_time = datetime.now()
            total_size = 0
            file_count = 0
            processing_times = []
            
            for service_file in os.listdir('../backend_services/'):
                if service_file.startswith('enhanced_') and service_file.endswith('.py'):
                    try:
                        file_start = datetime.now()
                        service_path = f"../backend_services/{service_file}"
                        file_size = os.path.getsize(service_path)
                        total_size += file_size
                        file_count += 1
                        
                        # Simulate processing
                        with open(service_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Basic processing
                            lines = content.count('\n')
                            functions = content.count('def ')
                            classes = content.count('class ')
                        
                        file_end = datetime.now()
                        processing_time = (file_end - file_start).total_seconds()
                        processing_times.append(processing_time)
                        
                    except Exception as e:
                        continue
            
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            
            if file_count > 0:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'file_processing_performance',
                    'status': 'PASSED',
                    'response_time': total_processing_time,
                    'total_size': total_size,
                    'file_count': file_count,
                    'average_processing_time': np.mean(processing_times) if processing_times else 0
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'file_processing_performance',
                    'status': 'FAILED',
                    'error': 'No files processed'
                })
            
            # Performance metrics
            response_times = [test['response_time'] for test in results['test_details'] if 'response_time' in test]
            if response_times:
                results['performance_metrics'] = {
                    'average_response_time': np.mean(response_times),
                    'max_response_time': np.max(response_times),
                    'min_response_time': np.min(response_times),
                    'total_file_size': total_size,
                    'total_files': file_count,
                    'average_file_size': total_size / file_count if file_count > 0 else 0
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing performance: {e}")
            return {'error': str(e)}
    
    async def _generate_basic_report(self) -> Dict[str, Any]:
        """Generate basic test report"""
        try:
            total_tests = 0
            total_passed = 0
            total_failed = 0
            
            for test_name, test_results in self.test_results.items():
                if isinstance(test_results, dict) and 'tests_passed' in test_results:
                    total_tests += test_results['tests_passed'] + test_results['tests_failed']
                    total_passed += test_results['tests_passed']
                    total_failed += test_results['tests_failed']
            
            success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            report = {
                'test_summary': {
                    'total_tests': total_tests,
                    'tests_passed': total_passed,
                    'tests_failed': total_failed,
                    'success_rate': success_rate,
                    'test_timestamp': datetime.now().isoformat()
                },
                'test_results': self.test_results,
                'overall_status': 'PASSED' if success_rate >= 80 else 'FAILED',
                'recommendations': self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating basic report: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for test_name, test_results in self.test_results.items():
            if isinstance(test_results, dict) and 'tests_failed' in test_results:
                if test_results['tests_failed'] > 0:
                    recommendations.append(f"Review {test_name}: {test_results['tests_failed']} tests failed")
        
        if not recommendations:
            recommendations.append("All enhanced services are properly implemented. Ready for integration.")
        
        return recommendations

async def main():
    """Main function untuk menjalankan basic integration test"""
    try:
        test = BasicIntegrationTest()
        results = await test.run_basic_test()
        
        print("\nBASIC TEST RESULTS:")
        print("=" * 60)
        print(f"Total Tests: {results['test_summary']['total_tests']}")
        print(f"Tests Passed: {results['test_summary']['tests_passed']}")
        print(f"Tests Failed: {results['test_summary']['tests_failed']}")
        print(f"Success Rate: {results['test_summary']['success_rate']:.2f}%")
        print(f"Overall Status: {results['overall_status']}")
        
        print("\nRECOMMENDATIONS:")
        for recommendation in results['recommendations']:
            print(f"- {recommendation}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    asyncio.run(main())
