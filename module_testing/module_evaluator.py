#!/usr/bin/env python3
"""
Module Evaluator - Testing Framework untuk Evaluasi Modul
==========================================================

Script ini digunakan untuk mengevaluasi setiap modul dalam aplikasi trading
dan menentukan apakah modul tersebut perlu:
1. Dipertahankan (Keep)
2. Dihapus (Remove) 
3. Diperbaiki (Fix)

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import importlib
import traceback
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
import inspect

class ModuleEvaluator:
    """Evaluator untuk testing dan analisis modul"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.results = {}
        self.errors = {}
        self.recommendations = {}
        
    def evaluate_module(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """
        Evaluasi satu modul berdasarkan berbagai kriteria
        
        Args:
            module_path: Path ke file modul
            module_name: Nama modul
            
        Returns:
            Dict berisi hasil evaluasi
        """
        result = {
            'module_name': module_name,
            'module_path': module_path,
            'file_exists': os.path.exists(module_path),
            'file_size': 0,
            'last_modified': None,
            'import_success': False,
            'syntax_valid': False,
            'has_docstring': False,
            'has_functions': False,
            'has_classes': False,
            'function_count': 0,
            'class_count': 0,
            'line_count': 0,
            'complexity_score': 0,
            'error_messages': [],
            'warnings': [],
            'recommendation': 'UNKNOWN',
            'priority': 'LOW',
            'evaluation_time': datetime.now().isoformat()
        }
        
        try:
            # File information
            if result['file_exists']:
                stat = os.stat(module_path)
                result['file_size'] = stat.st_size
                result['last_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # Count lines
                with open(module_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    result['line_count'] = len(lines)
                    
                    # Check for docstring
                    for line in lines[:10]:  # Check first 10 lines
                        if '"""' in line or "'''" in line:
                            result['has_docstring'] = True
                            break
                
                # Syntax validation
                try:
                    with open(module_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), module_path, 'exec')
                    result['syntax_valid'] = True
                except SyntaxError as e:
                    result['syntax_valid'] = False
                    result['error_messages'].append(f"Syntax Error: {str(e)}")
                
                # Import test
                try:
                    # Add parent directory to path
                    parent_dir = os.path.dirname(module_path)
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)
                    
                    # Try to import module
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        result['import_success'] = True
                        
                        # Analyze module content
                        members = inspect.getmembers(module)
                        functions = [name for name, obj in members if inspect.isfunction(obj)]
                        classes = [name for name, obj in members if inspect.isclass(obj)]
                        
                        result['has_functions'] = len(functions) > 0
                        result['has_classes'] = len(classes) > 0
                        result['function_count'] = len(functions)
                        result['class_count'] = len(classes)
                        
                        # Calculate complexity score
                        result['complexity_score'] = self._calculate_complexity(module_path)
                        
                except Exception as e:
                    result['import_success'] = False
                    result['error_messages'].append(f"Import Error: {str(e)}")
            
            # Generate recommendation
            result['recommendation'] = self._generate_recommendation(result)
            result['priority'] = self._calculate_priority(result)
            
        except Exception as e:
            result['error_messages'].append(f"Evaluation Error: {str(e)}")
            result['recommendation'] = 'REMOVE'
            result['priority'] = 'HIGH'
        
        return result
    
    def _calculate_complexity(self, file_path: str) -> int:
        """Hitung skor kompleksitas sederhana"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple complexity metrics
            complexity = 0
            complexity += content.count('if ') * 2
            complexity += content.count('for ') * 3
            complexity += content.count('while ') * 4
            complexity += content.count('try:') * 2
            complexity += content.count('except') * 2
            complexity += content.count('def ') * 1
            complexity += content.count('class ') * 2
            
            return complexity
        except:
            return 0
    
    def _generate_recommendation(self, result: Dict[str, Any]) -> str:
        """Generate recommendation berdasarkan hasil evaluasi"""
        
        # Jika file tidak ada
        if not result['file_exists']:
            return 'REMOVE'
        
        # Jika syntax error
        if not result['syntax_valid']:
            return 'FIX'
        
        # Jika tidak bisa diimport
        if not result['import_success']:
            return 'FIX'
        
        # Jika file kosong atau terlalu kecil
        if result['line_count'] < 10:
            return 'REMOVE'
        
        # Jika tidak ada fungsi atau class
        if not result['has_functions'] and not result['has_classes']:
            return 'REMOVE'
        
        # Jika ada error messages
        if len(result['error_messages']) > 0:
            return 'FIX'
        
        # Jika kompleksitas terlalu tinggi
        if result['complexity_score'] > 50:
            return 'FIX'
        
        # Default: pertahankan
        return 'KEEP'
    
    def _calculate_priority(self, result: Dict[str, Any]) -> str:
        """Hitung prioritas berdasarkan kriteria"""
        
        if result['recommendation'] == 'REMOVE':
            return 'LOW'
        
        if result['recommendation'] == 'FIX':
            if len(result['error_messages']) > 0:
                return 'HIGH'
            elif result['complexity_score'] > 30:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        if result['recommendation'] == 'KEEP':
            if result['complexity_score'] > 20:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        return 'LOW'
    
    def evaluate_all_modules(self) -> Dict[str, Any]:
        """Evaluasi semua modul dalam proyek"""
        
        modules_to_evaluate = [
            # Backend API modules
            ('backend/app/api/ai_ml.py', 'ai_ml'),
            ('backend/app/api/algorithmic_trading.py', 'algorithmic_trading'),
            ('backend/app/api/backtesting.py', 'backtesting'),
            ('backend/app/api/backup.py', 'backup'),
            ('backend/app/api/cache.py', 'cache'),
            ('backend/app/api/dashboard.py', 'dashboard'),
            ('backend/app/api/earnings.py', 'earnings'),
            ('backend/app/api/economic_calendar.py', 'economic_calendar'),
            ('backend/app/api/educational.py', 'educational'),
            ('backend/app/api/fundamental.py', 'fundamental'),
            ('backend/app/api/market_data.py', 'market_data'),
            ('backend/app/api/notifications.py', 'notifications'),
            ('backend/app/api/pattern.py', 'pattern'),
            ('backend/app/api/performance_analytics.py', 'performance_analytics'),
            ('backend/app/api/portfolio_heatmap.py', 'portfolio_heatmap'),
            ('backend/app/api/portfolio_optimization.py', 'portfolio_optimization'),
            ('backend/app/api/risk_management.py', 'risk_management'),
            ('backend/app/api/security.py', 'security'),
            ('backend/app/api/sentiment_scraping.py', 'sentiment_scraping'),
            ('backend/app/api/sentiment.py', 'sentiment'),
            ('backend/app/api/strategy_builder.py', 'strategy_builder'),
            ('backend/app/api/tax.py', 'tax'),
            ('backend/app/api/technical.py', 'technical'),
            ('backend/app/api/trading.py', 'trading'),
            ('backend/app/api/two_factor.py', 'two_factor'),
            ('backend/app/api/watchlist.py', 'watchlist'),
            ('backend/app/api/web_scraping.py', 'web_scraping'),
            
            # Core modules
            ('backend/app/core/fundamental.py', 'core_fundamental'),
            ('backend/app/core/sentiment.py', 'core_sentiment'),
            
            # Model modules
            ('backend/app/models/backtesting.py', 'model_backtesting'),
            ('backend/app/models/dashboard.py', 'model_dashboard'),
            ('backend/app/models/earnings.py', 'model_earnings'),
            ('backend/app/models/educational.py', 'model_educational'),
            ('backend/app/models/fundamental.py', 'model_fundamental'),
            ('backend/app/models/market_data.py', 'model_market_data'),
            ('backend/app/models/notifications.py', 'model_notifications'),
            ('backend/app/models/security.py', 'model_security'),
            ('backend/app/models/sentiment.py', 'model_sentiment'),
            ('backend/app/models/trading.py', 'model_trading'),
            ('backend/app/models/watchlist.py', 'model_watchlist'),
            
            # Main files
            ('backend/main.py', 'main'),
            ('backend/run_server.py', 'run_server'),
        ]
        
        print("🔍 Memulai evaluasi semua modul...")
        print("=" * 60)
        
        all_results = {}
        
        for module_path, module_name in modules_to_evaluate:
            full_path = os.path.join(self.base_path, module_path)
            print(f"📋 Mengevaluasi: {module_name}")
            
            result = self.evaluate_module(full_path, module_name)
            all_results[module_name] = result
            
            # Print summary
            status_emoji = {
                'KEEP': '✅',
                'FIX': '🔧', 
                'REMOVE': '❌'
            }
            
            priority_emoji = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            
            emoji = status_emoji.get(result['recommendation'], '❓')
            priority = priority_emoji.get(result['priority'], '⚪')
            
            print(f"   {emoji} {result['recommendation']} {priority} {result['priority']}")
            
            if result['error_messages']:
                print(f"   ⚠️  Errors: {len(result['error_messages'])}")
            
            print()
        
        return all_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate laporan evaluasi"""
        
        report = []
        report.append("# MODULE EVALUATION REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        total_modules = len(results)
        keep_count = sum(1 for r in results.values() if r['recommendation'] == 'KEEP')
        fix_count = sum(1 for r in results.values() if r['recommendation'] == 'FIX')
        remove_count = sum(1 for r in results.values() if r['recommendation'] == 'REMOVE')
        
        report.append("## SUMMARY")
        report.append(f"- Total Modules: {total_modules}")
        report.append(f"- Keep: {keep_count}")
        report.append(f"- Fix: {fix_count}")
        report.append(f"- Remove: {remove_count}")
        report.append("")
        
        # Detailed results
        report.append("## DETAILED RESULTS")
        report.append("")
        
        for module_name, result in results.items():
            report.append(f"### {module_name}")
            report.append(f"- **Recommendation**: {result['recommendation']}")
            report.append(f"- **Priority**: {result['priority']}")
            report.append(f"- **File Exists**: {result['file_exists']}")
            report.append(f"- **Import Success**: {result['import_success']}")
            report.append(f"- **Syntax Valid**: {result['syntax_valid']}")
            report.append(f"- **Line Count**: {result['line_count']}")
            report.append(f"- **Function Count**: {result['function_count']}")
            report.append(f"- **Class Count**: {result['class_count']}")
            report.append(f"- **Complexity Score**: {result['complexity_score']}")
            
            if result['error_messages']:
                report.append("- **Errors**:")
                for error in result['error_messages']:
                    report.append(f"  - {error}")
            
            if result['warnings']:
                report.append("- **Warnings**:")
                for warning in result['warnings']:
                    report.append(f"  - {warning}")
            
            report.append("")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Simpan hasil evaluasi ke file"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"module_evaluation_results_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Hasil evaluasi disimpan ke: {filepath}")
        return filepath

def main():
    """Main function untuk menjalankan evaluasi"""
    
    print("🚀 MODULE EVALUATOR - Testing Framework")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = ModuleEvaluator()
    
    # Run evaluation
    results = evaluator.evaluate_all_modules()
    
    # Generate and save report
    report = evaluator.generate_report(results)
    
    # Save report to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"module_evaluation_report_{timestamp}.md"
    report_path = os.path.join(os.path.dirname(__file__), report_file)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save JSON results
    json_file = evaluator.save_results(results)
    
    print("\n" + "=" * 60)
    print("📊 EVALUATION COMPLETED")
    print("=" * 60)
    print(f"📄 Report: {report_path}")
    print(f"📄 JSON: {json_file}")
    
    # Print summary
    total = len(results)
    keep = sum(1 for r in results.values() if r['recommendation'] == 'KEEP')
    fix = sum(1 for r in results.values() if r['recommendation'] == 'FIX')
    remove = sum(1 for r in results.values() if r['recommendation'] == 'REMOVE')
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Modules: {total}")
    print(f"   ✅ Keep: {keep}")
    print(f"   🔧 Fix: {fix}")
    print(f"   ❌ Remove: {remove}")

if __name__ == "__main__":
    main()
