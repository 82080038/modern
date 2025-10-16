#!/usr/bin/env python3
"""
Run All Tests - Script utama untuk menjalankan semua testing
============================================================

Script ini menjalankan semua komponen testing framework:
1. Module Evaluator
2. Test Runner
3. Decision Framework
4. Report Generator

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from typing import Dict, Any

class TestOrchestrator:
    """Orchestrator untuk menjalankan semua testing"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.testing_dir = os.path.dirname(__file__)
        
    def run_module_evaluator(self) -> bool:
        """Jalankan module evaluator"""
        
        print("🔍 STEP 1: Running Module Evaluator")
        print("=" * 50)
        
        try:
            evaluator_script = os.path.join(self.testing_dir, 'module_evaluator.py')
            result = subprocess.run([sys.executable, evaluator_script], 
                                  capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("✅ Module Evaluator completed successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Module Evaluator failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error running Module Evaluator: {str(e)}")
            return False
    
    def run_test_runner(self) -> bool:
        """Jalankan test runner"""
        
        print("\n🧪 STEP 2: Running Test Runner")
        print("=" * 50)
        
        try:
            test_script = os.path.join(self.testing_dir, 'test_runner.py')
            result = subprocess.run([sys.executable, test_script], 
                                  capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("✅ Test Runner completed successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Test Runner failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error running Test Runner: {str(e)}")
            return False
    
    def run_decision_framework(self) -> bool:
        """Jalankan decision framework"""
        
        print("\n🤔 STEP 3: Running Decision Framework")
        print("=" * 50)
        
        try:
            decision_script = os.path.join(self.testing_dir, 'decision_framework.py')
            result = subprocess.run([sys.executable, decision_script], 
                                  capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("✅ Decision Framework completed successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Decision Framework failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error running Decision Framework: {str(e)}")
            return False
    
    def run_report_generator(self) -> bool:
        """Jalankan report generator"""
        
        print("\n📊 STEP 4: Running Report Generator")
        print("=" * 50)
        
        try:
            report_script = os.path.join(self.testing_dir, 'report_generator.py')
            result = subprocess.run([sys.executable, report_script], 
                                  capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("✅ Report Generator completed successfully")
                print(result.stdout)
                return True
            else:
                print("❌ Report Generator failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error running Report Generator: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Jalankan semua testing"""
        
        print("🚀 COMPLETE MODULE TESTING FRAMEWORK")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        
        results = {
            'start_time': datetime.now().isoformat(),
            'steps_completed': [],
            'steps_failed': [],
            'overall_success': False,
            'end_time': None
        }
        
        # Step 1: Module Evaluator
        if self.run_module_evaluator():
            results['steps_completed'].append('module_evaluator')
        else:
            results['steps_failed'].append('module_evaluator')
        
        # Step 2: Test Runner
        if self.run_test_runner():
            results['steps_completed'].append('test_runner')
        else:
            results['steps_failed'].append('test_runner')
        
        # Step 3: Decision Framework
        if self.run_decision_framework():
            results['steps_completed'].append('decision_framework')
        else:
            results['steps_failed'].append('decision_framework')
        
        # Step 4: Report Generator
        if self.run_report_generator():
            results['steps_completed'].append('report_generator')
        else:
            results['steps_failed'].append('report_generator')
        
        # Determine overall success
        results['overall_success'] = len(results['steps_failed']) == 0
        results['end_time'] = datetime.now().isoformat()
        
        # Print final results
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        
        print(f"✅ Steps Completed: {len(results['steps_completed'])}")
        for step in results['steps_completed']:
            print(f"   - {step}")
        
        if results['steps_failed']:
            print(f"❌ Steps Failed: {len(results['steps_failed'])}")
            for step in results['steps_failed']:
                print(f"   - {step}")
        
        print(f"\n🎯 Overall Success: {'✅ YES' if results['overall_success'] else '❌ NO'}")
        
        # List generated files
        print("\n📄 Generated Files:")
        self._list_generated_files()
        
        return results
    
    def _list_generated_files(self):
        """List semua file yang dihasilkan"""
        
        testing_dir = self.testing_dir
        
        # Look for generated files
        file_patterns = [
            'module_evaluation_results_*.json',
            'module_evaluation_report_*.md',
            'test_results_*.json',
            'module_decisions_*.json',
            'decision_summary_*.md',
            'action_plan_*.md',
            'complete_evaluation_report_*.md'
        ]
        
        import glob
        generated_files = []
        
        for pattern in file_patterns:
            files = glob.glob(os.path.join(testing_dir, pattern))
            generated_files.extend(files)
        
        if generated_files:
            for file in sorted(generated_files):
                filename = os.path.basename(file)
                file_size = os.path.getsize(file)
                print(f"   📄 {filename} ({file_size} bytes)")
        else:
            print("   No files generated")
    
    def cleanup_old_files(self, days_old: int = 7):
        """Bersihkan file lama"""
        
        print(f"\n🧹 Cleaning up files older than {days_old} days...")
        
        import time
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        testing_dir = self.testing_dir
        cleaned_count = 0
        
        for file in os.listdir(testing_dir):
            file_path = os.path.join(testing_dir, file)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                        print(f"   🗑️  Removed: {file}")
                    except Exception as e:
                        print(f"   ❌ Error removing {file}: {str(e)}")
        
        print(f"✅ Cleaned up {cleaned_count} old files")

def main():
    """Main function"""
    
    print("🚀 MODULE TESTING FRAMEWORK - Complete Test Suite")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = TestOrchestrator()
    
    # Run all tests
    results = orchestrator.run_all_tests()
    
    # Cleanup old files (optional)
    try:
        orchestrator.cleanup_old_files(days_old=7)
    except Exception as e:
        print(f"⚠️  Cleanup warning: {str(e)}")
    
    # Final message
    if results['overall_success']:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("📋 Check the generated reports for detailed analysis.")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("📋 Check the error messages above for details.")
    
    print(f"\n⏱️  Total execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
