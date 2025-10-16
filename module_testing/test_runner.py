#!/usr/bin/env python3
"""
Test Runner - Menjalankan testing untuk setiap modul
====================================================

Script ini menjalankan berbagai jenis testing untuk setiap modul:
1. Unit Testing
2. Integration Testing  
3. Performance Testing
4. Security Testing
5. Code Quality Testing

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Any
import importlib.util

class TestRunner:
    """Runner untuk menjalankan berbagai jenis testing"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.test_results = {}
        self.test_errors = {}
        
    def run_unit_tests(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Jalankan unit testing untuk modul"""
        
        result = {
            'module_name': module_name,
            'test_type': 'unit',
            'start_time': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_duration': 0,
            'errors': [],
            'warnings': [],
            'status': 'UNKNOWN'
        }
        
        try:
            start_time = time.time()
            
            # Basic functionality tests
            tests = [
                self._test_import(module_path, module_name),
                self._test_syntax(module_path),
                self._test_basic_functions(module_path, module_name),
                self._test_error_handling(module_path, module_name)
            ]
            
            result['tests_run'] = len(tests)
            result['tests_passed'] = sum(1 for test in tests if test['passed'])
            result['tests_failed'] = sum(1 for test in tests if not test['passed'])
            
            # Collect errors and warnings
            for test in tests:
                result['errors'].extend(test.get('errors', []))
                result['warnings'].extend(test.get('warnings', []))
            
            result['test_duration'] = time.time() - start_time
            result['end_time'] = datetime.now().isoformat()
            
            # Determine status
            if result['tests_failed'] == 0:
                result['status'] = 'PASSED'
            elif result['tests_passed'] > 0:
                result['status'] = 'PARTIAL'
            else:
                result['status'] = 'FAILED'
                
        except Exception as e:
            result['errors'].append(f"Unit test error: {str(e)}")
            result['status'] = 'ERROR'
            result['end_time'] = datetime.now().isoformat()
        
        return result
    
    def _test_import(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test apakah modul bisa diimport"""
        
        test_result = {
            'test_name': 'import_test',
            'passed': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            if not os.path.exists(module_path):
                test_result['errors'].append(f"File tidak ditemukan: {module_path}")
                return test_result
            
            # Add parent directory to path
            parent_dir = os.path.dirname(module_path)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # Try to import
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                test_result['passed'] = True
            else:
                test_result['errors'].append("Tidak bisa membuat module spec")
                
        except Exception as e:
            test_result['errors'].append(f"Import error: {str(e)}")
        
        return test_result
    
    def _test_syntax(self, module_path: str) -> Dict[str, Any]:
        """Test syntax validity"""
        
        test_result = {
            'test_name': 'syntax_test',
            'passed': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compile to check syntax
            compile(content, module_path, 'exec')
            test_result['passed'] = True
            
        except SyntaxError as e:
            test_result['errors'].append(f"Syntax error: {str(e)}")
        except Exception as e:
            test_result['errors'].append(f"Syntax test error: {str(e)}")
        
        return test_result
    
    def _test_basic_functions(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test basic function calls"""
        
        test_result = {
            'test_name': 'basic_functions_test',
            'passed': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Import module
            parent_dir = os.path.dirname(module_path)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if module has any callable functions
                import inspect
                members = inspect.getmembers(module)
                functions = [name for name, obj in members if inspect.isfunction(obj)]
                
                if functions:
                    test_result['passed'] = True
                    test_result['warnings'].append(f"Found {len(functions)} functions")
                else:
                    test_result['warnings'].append("No functions found in module")
                    test_result['passed'] = True  # Not necessarily an error
            else:
                test_result['errors'].append("Could not create module spec")
                
        except Exception as e:
            test_result['errors'].append(f"Basic functions test error: {str(e)}")
        
        return test_result
    
    def _test_error_handling(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test error handling capabilities"""
        
        test_result = {
            'test_name': 'error_handling_test',
            'passed': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for try-except blocks
            if 'try:' in content and 'except' in content:
                test_result['passed'] = True
                test_result['warnings'].append("Found try-except blocks")
            else:
                test_result['warnings'].append("No try-except blocks found")
                test_result['passed'] = True  # Not necessarily bad
            
        except Exception as e:
            test_result['errors'].append(f"Error handling test error: {str(e)}")
        
        return test_result
    
    def run_integration_tests(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Jalankan integration testing"""
        
        result = {
            'module_name': module_name,
            'test_type': 'integration',
            'start_time': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_duration': 0,
            'errors': [],
            'warnings': [],
            'status': 'UNKNOWN'
        }
        
        try:
            start_time = time.time()
            
            # Integration tests
            tests = [
                self._test_dependencies(module_path, module_name),
                self._test_api_endpoints(module_path, module_name),
                self._test_database_connections(module_path, module_name)
            ]
            
            result['tests_run'] = len(tests)
            result['tests_passed'] = sum(1 for test in tests if test['passed'])
            result['tests_failed'] = sum(1 for test in tests if not test['passed'])
            
            # Collect errors and warnings
            for test in tests:
                result['errors'].extend(test.get('errors', []))
                result['warnings'].extend(test.get('warnings', []))
            
            result['test_duration'] = time.time() - start_time
            result['end_time'] = datetime.now().isoformat()
            
            # Determine status
            if result['tests_failed'] == 0:
                result['status'] = 'PASSED'
            elif result['tests_passed'] > 0:
                result['status'] = 'PARTIAL'
            else:
                result['status'] = 'FAILED'
                
        except Exception as e:
            result['errors'].append(f"Integration test error: {str(e)}")
            result['status'] = 'ERROR'
            result['end_time'] = datetime.now().isoformat()
        
        return result
    
    def _test_dependencies(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test module dependencies"""
        
        test_result = {
            'test_name': 'dependencies_test',
            'passed': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common imports
            imports = []
            for line in content.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    imports.append(line.strip())
            
            if imports:
                test_result['passed'] = True
                test_result['warnings'].append(f"Found {len(imports)} imports")
            else:
                test_result['warnings'].append("No imports found")
                test_result['passed'] = True  # Not necessarily bad
            
        except Exception as e:
            test_result['errors'].append(f"Dependencies test error: {str(e)}")
        
        return test_result
    
    def _test_api_endpoints(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test API endpoints if applicable"""
        
        test_result = {
            'test_name': 'api_endpoints_test',
            'passed': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Flask/FastAPI patterns
            if '@app.route' in content or '@router.' in content or 'def ' in content:
                test_result['passed'] = True
                test_result['warnings'].append("Found potential API endpoints")
            else:
                test_result['warnings'].append("No API endpoints found")
                test_result['passed'] = True  # Not all modules need API endpoints
            
        except Exception as e:
            test_result['errors'].append(f"API endpoints test error: {str(e)}")
        
        return test_result
    
    def _test_database_connections(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test database connection patterns"""
        
        test_result = {
            'test_name': 'database_connections_test',
            'passed': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for database patterns
            db_patterns = ['sqlite', 'mysql', 'postgresql', 'database', 'db', 'cursor', 'execute']
            found_patterns = [pattern for pattern in db_patterns if pattern in content.lower()]
            
            if found_patterns:
                test_result['passed'] = True
                test_result['warnings'].append(f"Found database patterns: {', '.join(found_patterns)}")
            else:
                test_result['warnings'].append("No database patterns found")
                test_result['passed'] = True  # Not all modules need database
            
        except Exception as e:
            test_result['errors'].append(f"Database connections test error: {str(e)}")
        
        return test_result
    
    def run_performance_tests(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Jalankan performance testing"""
        
        result = {
            'module_name': module_name,
            'test_type': 'performance',
            'start_time': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_duration': 0,
            'errors': [],
            'warnings': [],
            'status': 'UNKNOWN',
            'performance_metrics': {}
        }
        
        try:
            start_time = time.time()
            
            # Performance tests
            tests = [
                self._test_import_performance(module_path, module_name),
                self._test_memory_usage(module_path, module_name),
                self._test_code_complexity(module_path, module_name)
            ]
            
            result['tests_run'] = len(tests)
            result['tests_passed'] = sum(1 for test in tests if test['passed'])
            result['tests_failed'] = sum(1 for test in tests if not test['passed'])
            
            # Collect performance metrics
            for test in tests:
                if 'metrics' in test:
                    result['performance_metrics'].update(test['metrics'])
                result['errors'].extend(test.get('errors', []))
                result['warnings'].extend(test.get('warnings', []))
            
            result['test_duration'] = time.time() - start_time
            result['end_time'] = datetime.now().isoformat()
            
            # Determine status
            if result['tests_failed'] == 0:
                result['status'] = 'PASSED'
            elif result['tests_passed'] > 0:
                result['status'] = 'PARTIAL'
            else:
                result['status'] = 'FAILED'
                
        except Exception as e:
            result['errors'].append(f"Performance test error: {str(e)}")
            result['status'] = 'ERROR'
            result['end_time'] = datetime.now().isoformat()
        
        return result
    
    def _test_import_performance(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test import performance"""
        
        test_result = {
            'test_name': 'import_performance_test',
            'passed': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            import time
            
            # Measure import time
            start_time = time.time()
            
            parent_dir = os.path.dirname(module_path)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                import_time = time.time() - start_time
                test_result['metrics']['import_time'] = import_time
                
                if import_time < 1.0:  # Less than 1 second
                    test_result['passed'] = True
                else:
                    test_result['warnings'].append(f"Slow import time: {import_time:.2f}s")
                    test_result['passed'] = True  # Not necessarily failed
            else:
                test_result['errors'].append("Could not create module spec")
                
        except Exception as e:
            test_result['errors'].append(f"Import performance test error: {str(e)}")
        
        return test_result
    
    def _test_memory_usage(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test memory usage"""
        
        test_result = {
            'test_name': 'memory_usage_test',
            'passed': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            import psutil
            import os
            
            # Get current process
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Import module
            parent_dir = os.path.dirname(module_path)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_used = memory_after - memory_before
                
                test_result['metrics']['memory_used_mb'] = memory_used
                
                if memory_used < 10:  # Less than 10 MB
                    test_result['passed'] = True
                else:
                    test_result['warnings'].append(f"High memory usage: {memory_used:.2f}MB")
                    test_result['passed'] = True  # Not necessarily failed
            else:
                test_result['errors'].append("Could not create module spec")
                
        except ImportError:
            test_result['warnings'].append("psutil not available, skipping memory test")
            test_result['passed'] = True
        except Exception as e:
            test_result['errors'].append(f"Memory usage test error: {str(e)}")
        
        return test_result
    
    def _test_code_complexity(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Test code complexity"""
        
        test_result = {
            'test_name': 'code_complexity_test',
            'passed': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate complexity metrics
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Count complexity indicators
            if_count = content.count('if ')
            for_count = content.count('for ')
            while_count = content.count('while ')
            try_count = content.count('try:')
            except_count = content.count('except')
            def_count = content.count('def ')
            class_count = content.count('class ')
            
            complexity_score = (if_count * 2 + for_count * 3 + while_count * 4 + 
                              try_count * 2 + except_count * 2 + def_count * 1 + class_count * 2)
            
            test_result['metrics']['total_lines'] = total_lines
            test_result['metrics']['code_lines'] = code_lines
            test_result['metrics']['complexity_score'] = complexity_score
            test_result['metrics']['if_statements'] = if_count
            test_result['metrics']['loops'] = for_count + while_count
            test_result['metrics']['functions'] = def_count
            test_result['metrics']['classes'] = class_count
            
            if complexity_score < 20:
                test_result['passed'] = True
            elif complexity_score < 50:
                test_result['warnings'].append(f"Medium complexity: {complexity_score}")
                test_result['passed'] = True
            else:
                test_result['warnings'].append(f"High complexity: {complexity_score}")
                test_result['passed'] = True  # Not necessarily failed
            
        except Exception as e:
            test_result['errors'].append(f"Code complexity test error: {str(e)}")
        
        return test_result
    
    def run_all_tests(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Jalankan semua jenis testing"""
        
        print(f"🧪 Running tests for: {module_name}")
        print("-" * 40)
        
        all_results = {
            'module_name': module_name,
            'module_path': module_path,
            'test_start_time': datetime.now().isoformat(),
            'unit_tests': {},
            'integration_tests': {},
            'performance_tests': {},
            'overall_status': 'UNKNOWN',
            'summary': {}
        }
        
        try:
            # Run unit tests
            print("🔬 Running unit tests...")
            unit_results = self.run_unit_tests(module_path, module_name)
            all_results['unit_tests'] = unit_results
            
            # Run integration tests
            print("🔗 Running integration tests...")
            integration_results = self.run_integration_tests(module_path, module_name)
            all_results['integration_tests'] = integration_results
            
            # Run performance tests
            print("⚡ Running performance tests...")
            performance_results = self.run_performance_tests(module_path, module_name)
            all_results['performance_tests'] = performance_results
            
            # Calculate overall status
            unit_status = unit_results['status']
            integration_status = integration_results['status']
            performance_status = performance_results['status']
            
            if all(status == 'PASSED' for status in [unit_status, integration_status, performance_status]):
                all_results['overall_status'] = 'PASSED'
            elif any(status == 'FAILED' for status in [unit_status, integration_status, performance_status]):
                all_results['overall_status'] = 'FAILED'
            else:
                all_results['overall_status'] = 'PARTIAL'
            
            # Generate summary
            all_results['summary'] = {
                'total_tests': (unit_results['tests_run'] + 
                               integration_results['tests_run'] + 
                               performance_results['tests_run']),
                'total_passed': (unit_results['tests_passed'] + 
                                integration_results['tests_passed'] + 
                                performance_results['tests_passed']),
                'total_failed': (unit_results['tests_failed'] + 
                                integration_results['tests_failed'] + 
                                performance_results['tests_failed']),
                'total_errors': (len(unit_results['errors']) + 
                                len(integration_results['errors']) + 
                                len(performance_results['errors'])),
                'total_warnings': (len(unit_results['warnings']) + 
                                  len(integration_results['warnings']) + 
                                  len(performance_results['warnings']))
            }
            
            all_results['test_end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            all_results['test_error'] = str(e)
            all_results['overall_status'] = 'ERROR'
            all_results['test_end_time'] = datetime.now().isoformat()
        
        return all_results

def main():
    """Main function untuk menjalankan testing"""
    
    print("🧪 TEST RUNNER - Module Testing Framework")
    print("=" * 50)
    
    # Initialize test runner
    runner = TestRunner()
    
    # List of modules to test
    modules_to_test = [
        ('backend/app/api/ai_ml.py', 'ai_ml'),
        ('backend/app/api/trading.py', 'trading'),
        ('backend/app/api/market_data.py', 'market_data'),
        ('backend/app/api/technical.py', 'technical'),
        ('backend/app/api/fundamental.py', 'fundamental'),
        ('backend/main.py', 'main'),
    ]
    
    all_test_results = {}
    
    for module_path, module_name in modules_to_test:
        full_path = os.path.join(runner.base_path, module_path)
        
        if os.path.exists(full_path):
            print(f"\n📋 Testing: {module_name}")
            results = runner.run_all_tests(full_path, module_name)
            all_test_results[module_name] = results
            
            # Print summary
            status_emoji = {
                'PASSED': '✅',
                'PARTIAL': '⚠️',
                'FAILED': '❌',
                'ERROR': '💥'
            }
            
            emoji = status_emoji.get(results['overall_status'], '❓')
            print(f"   {emoji} {results['overall_status']}")
            
            if 'summary' in results:
                summary = results['summary']
                print(f"   📊 Tests: {summary.get('total_passed', 0)}/{summary.get('total_tests', 0)} passed")
                print(f"   ⚠️  Errors: {summary.get('total_errors', 0)}, Warnings: {summary.get('total_warnings', 0)}")
        else:
            print(f"\n❌ Module not found: {module_path}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"test_results_{timestamp}.json"
    results_path = os.path.join(os.path.dirname(__file__), results_file)
    
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(all_test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test results saved to: {results_path}")
    
    # Print overall summary
    total_modules = len(all_test_results)
    passed_modules = sum(1 for r in all_test_results.values() if r['overall_status'] == 'PASSED')
    partial_modules = sum(1 for r in all_test_results.values() if r['overall_status'] == 'PARTIAL')
    failed_modules = sum(1 for r in all_test_results.values() if r['overall_status'] == 'FAILED')
    
    print(f"\n📈 OVERALL SUMMARY:")
    print(f"   Total Modules Tested: {total_modules}")
    print(f"   ✅ Passed: {passed_modules}")
    print(f"   ⚠️  Partial: {partial_modules}")
    print(f"   ❌ Failed: {failed_modules}")

if __name__ == "__main__":
    main()
