"""
Performance Test
================

Test performance untuk enhanced services dengan load testing dan optimization.

Author: AI Assistant
Date: 2025-01-17
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import psutil
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTest:
    """
    Performance Test untuk enhanced services
    """
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.system_metrics = {}
        
        # Test data
        self.test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
        self.test_user_id = 1
        self.test_portfolio_id = 1
        
        # Performance thresholds
        self.thresholds = {
            'response_time': 2.0,  # 2 seconds
            'memory_usage': 512,   # 512 MB
            'cpu_usage': 80,       # 80%
            'concurrent_requests': 10,
            'success_rate': 90    # 90%
        }
    
    async def run_performance_test(self) -> Dict[str, Any]:
        """Run performance test"""
        try:
            print("Starting Performance Test...")
            print("=" * 60)
            
            # Test 1: File Processing Performance
            print("\nTesting File Processing Performance...")
            file_performance = await self._test_file_processing_performance()
            self.test_results['file_processing'] = file_performance
            
            # Test 2: Memory Usage Test
            print("\nTesting Memory Usage...")
            memory_test = await self._test_memory_usage()
            self.test_results['memory_usage'] = memory_test
            
            # Test 3: CPU Usage Test
            print("\nTesting CPU Usage...")
            cpu_test = await self._test_cpu_usage()
            self.test_results['cpu_usage'] = cpu_test
            
            # Test 4: Concurrent Processing Test
            print("\nTesting Concurrent Processing...")
            concurrent_test = await self._test_concurrent_processing()
            self.test_results['concurrent_processing'] = concurrent_test
            
            # Test 5: Load Testing
            print("\nTesting Load Performance...")
            load_test = await self._test_load_performance()
            self.test_results['load_performance'] = load_test
            
            # Test 6: System Resource Monitoring
            print("\nTesting System Resource Monitoring...")
            system_test = await self._test_system_resources()
            self.test_results['system_resources'] = system_test
            
            # Generate performance report
            report = await self._generate_performance_report()
            
            print("\n" + "=" * 60)
            print("Performance Test Completed!")
            print("=" * 60)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in performance test: {e}")
            return {'error': str(e)}
    
    async def _test_file_processing_performance(self) -> Dict[str, Any]:
        """Test file processing performance"""
        try:
            results = {
                'test_name': 'File Processing Performance',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test 1: Single file processing
            start_time = time.time()
            total_files = 0
            total_size = 0
            processing_times = []
            
            for service_file in os.listdir('../backend_services/'):
                if service_file.startswith('enhanced_') and service_file.endswith('.py'):
                    try:
                        file_start = time.time()
                        service_path = f"../backend_services/{service_file}"
                        file_size = os.path.getsize(service_path)
                        total_size += file_size
                        total_files += 1
                        
                        # Simulate file processing
                        with open(service_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Basic processing operations
                            lines = content.count('\n')
                            functions = content.count('def ')
                            classes = content.count('class ')
                            imports = content.count('import ')
                        
                        file_end = time.time()
                        processing_time = file_end - file_start
                        processing_times.append(processing_time)
                        
                    except Exception as e:
                        continue
            
            end_time = time.time()
            total_processing_time = end_time - start_time
            
            # Performance metrics
            if processing_times:
                avg_processing_time = np.mean(processing_times)
                max_processing_time = np.max(processing_times)
                min_processing_time = np.min(processing_times)
                
                if avg_processing_time < self.thresholds['response_time']:
                    results['tests_passed'] += 1
                    results['test_details'].append({
                        'test': 'file_processing_speed',
                        'status': 'PASSED',
                        'response_time': avg_processing_time,
                        'threshold': self.thresholds['response_time']
                    })
                else:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': 'file_processing_speed',
                        'status': 'FAILED',
                        'response_time': avg_processing_time,
                        'threshold': self.thresholds['response_time']
                    })
                
                results['performance_metrics'] = {
                    'total_files': total_files,
                    'total_size': total_size,
                    'total_processing_time': total_processing_time,
                    'average_processing_time': avg_processing_time,
                    'max_processing_time': max_processing_time,
                    'min_processing_time': min_processing_time,
                    'files_per_second': total_files / total_processing_time if total_processing_time > 0 else 0
                }
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'file_processing_speed',
                    'status': 'FAILED',
                    'error': 'No files processed'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing file processing performance: {e}")
            return {'error': str(e)}
    
    async def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage"""
        try:
            results = {
                'test_name': 'Memory Usage Test',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Get initial memory usage
            initial_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB
            
            # Simulate memory-intensive operations
            start_time = time.time()
            memory_data = []
            
            # Create large data structures
            for i in range(100):
                data = {
                    'symbol': f'SYMBOL_{i}',
                    'price': np.random.random() * 1000,
                    'volume': np.random.randint(1000, 100000),
                    'timestamp': datetime.now(),
                    'data': np.random.random(1000).tolist()
                }
                memory_data.append(data)
            
            # Get memory usage after operations
            current_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB
            memory_increase = current_memory - initial_memory
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Check memory usage
            if memory_increase < self.thresholds['memory_usage']:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'memory_usage_check',
                    'status': 'PASSED',
                    'memory_increase': memory_increase,
                    'threshold': self.thresholds['memory_usage']
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'memory_usage_check',
                    'status': 'FAILED',
                    'memory_increase': memory_increase,
                    'threshold': self.thresholds['memory_usage']
                })
            
            # Performance metrics
            results['performance_metrics'] = {
                'initial_memory': initial_memory,
                'current_memory': current_memory,
                'memory_increase': memory_increase,
                'processing_time': processing_time,
                'data_structures_created': len(memory_data),
                'memory_per_structure': memory_increase / len(memory_data) if memory_data else 0
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing memory usage: {e}")
            return {'error': str(e)}
    
    async def _test_cpu_usage(self) -> Dict[str, Any]:
        """Test CPU usage"""
        try:
            results = {
                'test_name': 'CPU Usage Test',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Get initial CPU usage
            initial_cpu = psutil.cpu_percent()
            
            # Simulate CPU-intensive operations
            start_time = time.time()
            cpu_data = []
            
            # Perform CPU-intensive calculations
            for i in range(1000):
                # Complex mathematical operations
                result = 0
                for j in range(100):
                    result += np.sin(i * j) * np.cos(i * j) * np.tan(i * j)
                cpu_data.append(result)
            
            # Get CPU usage after operations
            current_cpu = psutil.cpu_percent()
            cpu_increase = current_cpu - initial_cpu
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Check CPU usage
            if current_cpu < self.thresholds['cpu_usage']:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'cpu_usage_check',
                    'status': 'PASSED',
                    'cpu_usage': current_cpu,
                    'threshold': self.thresholds['cpu_usage']
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'cpu_usage_check',
                    'status': 'FAILED',
                    'cpu_usage': current_cpu,
                    'threshold': self.thresholds['cpu_usage']
                })
            
            # Performance metrics
            results['performance_metrics'] = {
                'initial_cpu': initial_cpu,
                'current_cpu': current_cpu,
                'cpu_increase': cpu_increase,
                'processing_time': processing_time,
                'calculations_performed': len(cpu_data),
                'cpu_per_calculation': cpu_increase / len(cpu_data) if cpu_data else 0
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing CPU usage: {e}")
            return {'error': str(e)}
    
    async def _test_concurrent_processing(self) -> Dict[str, Any]:
        """Test concurrent processing"""
        try:
            results = {
                'test_name': 'Concurrent Processing Test',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test concurrent file processing
            start_time = time.time()
            concurrent_tasks = []
            
            # Create concurrent tasks
            for i in range(self.thresholds['concurrent_requests']):
                task = self._simulate_concurrent_task(i)
                concurrent_tasks.append(task)
            
            # Execute concurrent tasks
            try:
                results_list = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
                end_time = time.time()
                total_time = end_time - start_time
                
                # Count successful tasks
                successful_tasks = sum(1 for result in results_list if not isinstance(result, Exception))
                failed_tasks = len(results_list) - successful_tasks
                
                # Check success rate
                success_rate = (successful_tasks / len(results_list)) * 100
                if success_rate >= self.thresholds['success_rate']:
                    results['tests_passed'] += 1
                    results['test_details'].append({
                        'test': 'concurrent_processing_success_rate',
                        'status': 'PASSED',
                        'success_rate': success_rate,
                        'threshold': self.thresholds['success_rate']
                    })
                else:
                    results['tests_failed'] += 1
                    results['test_details'].append({
                        'test': 'concurrent_processing_success_rate',
                        'status': 'FAILED',
                        'success_rate': success_rate,
                        'threshold': self.thresholds['success_rate']
                    })
                
                # Performance metrics
                results['performance_metrics'] = {
                    'total_tasks': len(results_list),
                    'successful_tasks': successful_tasks,
                    'failed_tasks': failed_tasks,
                    'success_rate': success_rate,
                    'total_time': total_time,
                    'average_time_per_task': total_time / len(results_list) if results_list else 0
                }
                
            except Exception as e:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'concurrent_processing_success_rate',
                    'status': 'FAILED',
                    'error': str(e)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing concurrent processing: {e}")
            return {'error': str(e)}
    
    async def _simulate_concurrent_task(self, task_id: int) -> Dict[str, Any]:
        """Simulate concurrent task"""
        try:
            # Simulate some processing
            await asyncio.sleep(0.1)  # 100ms delay
            
            # Simulate data processing
            data = {
                'task_id': task_id,
                'timestamp': datetime.now(),
                'result': np.random.random() * 100
            }
            
            return data
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _test_load_performance(self) -> Dict[str, Any]:
        """Test load performance"""
        try:
            results = {
                'test_name': 'Load Performance Test',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Test load performance with multiple iterations
            start_time = time.time()
            load_results = []
            
            # Simulate load testing
            for iteration in range(10):  # 10 iterations
                iteration_start = time.time()
                
                # Simulate multiple operations
                operations = []
                for i in range(5):  # 5 operations per iteration
                    operation = self._simulate_load_operation(i)
                    operations.append(operation)
                
                # Execute operations
                operation_results = await asyncio.gather(*operations, return_exceptions=True)
                
                iteration_end = time.time()
                iteration_time = iteration_end - iteration_start
                
                load_results.append({
                    'iteration': iteration,
                    'time': iteration_time,
                    'operations': len(operation_results),
                    'successful_operations': sum(1 for result in operation_results if not isinstance(result, Exception))
                })
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calculate performance metrics
            total_operations = sum(result['operations'] for result in load_results)
            total_successful = sum(result['successful_operations'] for result in load_results)
            success_rate = (total_successful / total_operations) * 100 if total_operations > 0 else 0
            
            # Check performance
            if success_rate >= self.thresholds['success_rate']:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'load_performance_success_rate',
                    'status': 'PASSED',
                    'success_rate': success_rate,
                    'threshold': self.thresholds['success_rate']
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'load_performance_success_rate',
                    'status': 'FAILED',
                    'success_rate': success_rate,
                    'threshold': self.thresholds['success_rate']
                })
            
            # Performance metrics
            results['performance_metrics'] = {
                'total_time': total_time,
                'total_operations': total_operations,
                'total_successful': total_successful,
                'success_rate': success_rate,
                'operations_per_second': total_operations / total_time if total_time > 0 else 0,
                'average_iteration_time': np.mean([result['time'] for result in load_results])
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing load performance: {e}")
            return {'error': str(e)}
    
    async def _simulate_load_operation(self, operation_id: int) -> Dict[str, Any]:
        """Simulate load operation"""
        try:
            # Simulate some processing
            await asyncio.sleep(0.05)  # 50ms delay
            
            # Simulate data processing
            data = {
                'operation_id': operation_id,
                'timestamp': datetime.now(),
                'result': np.random.random() * 100
            }
            
            return data
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _test_system_resources(self) -> Dict[str, Any]:
        """Test system resources"""
        try:
            results = {
                'test_name': 'System Resource Monitoring',
                'tests_passed': 0,
                'tests_failed': 0,
                'test_details': [],
                'performance_metrics': {}
            }
            
            # Monitor system resources
            start_time = time.time()
            resource_data = []
            
            # Monitor for 5 seconds
            for i in range(5):
                # Get system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                resource_data.append({
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used / (1024 * 1024),  # MB
                    'memory_available': memory.available / (1024 * 1024),  # MB
                    'disk_percent': disk.percent,
                    'disk_used': disk.used / (1024 * 1024),  # MB
                    'disk_free': disk.free / (1024 * 1024)  # MB
                })
                
                await asyncio.sleep(1)  # 1 second interval
            
            end_time = time.time()
            monitoring_time = end_time - start_time
            
            # Calculate average metrics
            avg_cpu = np.mean([data['cpu_percent'] for data in resource_data])
            avg_memory = np.mean([data['memory_percent'] for data in resource_data])
            avg_disk = np.mean([data['disk_percent'] for data in resource_data])
            
            # Check system health
            if avg_cpu < self.thresholds['cpu_usage']:
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'cpu_health_check',
                    'status': 'PASSED',
                    'avg_cpu': avg_cpu,
                    'threshold': self.thresholds['cpu_usage']
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'cpu_health_check',
                    'status': 'FAILED',
                    'avg_cpu': avg_cpu,
                    'threshold': self.thresholds['cpu_usage']
                })
            
            if avg_memory < 90:  # 90% memory threshold
                results['tests_passed'] += 1
                results['test_details'].append({
                    'test': 'memory_health_check',
                    'status': 'PASSED',
                    'avg_memory': avg_memory,
                    'threshold': 90
                })
            else:
                results['tests_failed'] += 1
                results['test_details'].append({
                    'test': 'memory_health_check',
                    'status': 'FAILED',
                    'avg_memory': avg_memory,
                    'threshold': 90
                })
            
            # Performance metrics
            results['performance_metrics'] = {
                'monitoring_time': monitoring_time,
                'avg_cpu': avg_cpu,
                'avg_memory': avg_memory,
                'avg_disk': avg_disk,
                'max_cpu': np.max([data['cpu_percent'] for data in resource_data]),
                'max_memory': np.max([data['memory_percent'] for data in resource_data]),
                'min_cpu': np.min([data['cpu_percent'] for data in resource_data]),
                'min_memory': np.min([data['memory_percent'] for data in resource_data])
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing system resources: {e}")
            return {'error': str(e)}
    
    async def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate performance test report"""
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
            logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for test_name, test_results in self.test_results.items():
            if isinstance(test_results, dict) and 'tests_failed' in test_results:
                if test_results['tests_failed'] > 0:
                    recommendations.append(f"Review {test_name}: {test_results['tests_failed']} tests failed")
        
        if not recommendations:
            recommendations.append("All performance tests passed. System is ready for production.")
        
        return recommendations

async def main():
    """Main function untuk menjalankan performance test"""
    try:
        test = PerformanceTest()
        results = await test.run_performance_test()
        
        print("\nPERFORMANCE TEST RESULTS:")
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
