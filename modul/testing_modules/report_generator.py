#!/usr/bin/env python3
"""
Report Generator - Generator laporan evaluasi modul
==================================================

Script ini menghasilkan laporan komprehensif dari hasil evaluasi modul:
1. Executive Summary
2. Detailed Analysis
3. Recommendations
4. Action Plan
5. Risk Assessment

Author: AI Assistant
Date: 2025-01-16
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd

class ReportGenerator:
    """Generator untuk laporan evaluasi modul"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates')
        
        # Create templates directory if not exists
        os.makedirs(self.template_path, exist_ok=True)
    
    def generate_executive_summary(self, evaluation_results: Dict[str, Any], 
                                 test_results: Dict[str, Any] = None) -> str:
        """Generate executive summary"""
        
        summary = []
        summary.append("# EXECUTIVE SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Module statistics
        total_modules = len(evaluation_results)
        keep_count = sum(1 for r in evaluation_results.values() if r['recommendation'] == 'KEEP')
        fix_count = sum(1 for r in evaluation_results.values() if r['recommendation'] == 'FIX')
        remove_count = sum(1 for r in evaluation_results.values() if r['recommendation'] == 'REMOVE')
        
        summary.append("## MODULE OVERVIEW")
        summary.append(f"- **Total Modules Evaluated**: {total_modules}")
        summary.append(f"- **Modules to Keep**: {keep_count} ({keep_count/total_modules*100:.1f}%)")
        summary.append(f"- **Modules to Fix**: {fix_count} ({fix_count/total_modules*100:.1f}%)")
        summary.append(f"- **Modules to Remove**: {remove_count} ({remove_count/total_modules*100:.1f}%)")
        summary.append("")
        
        # Priority analysis
        high_priority = sum(1 for r in evaluation_results.values() if r['priority'] == 'HIGH')
        medium_priority = sum(1 for r in evaluation_results.values() if r['priority'] == 'MEDIUM')
        low_priority = sum(1 for r in evaluation_results.values() if r['priority'] == 'LOW')
        
        summary.append("## PRIORITY DISTRIBUTION")
        summary.append(f"- **High Priority**: {high_priority} modules")
        summary.append(f"- **Medium Priority**: {medium_priority} modules")
        summary.append(f"- **Low Priority**: {low_priority} modules")
        summary.append("")
        
        # Test results summary (if available)
        if test_results:
            total_tests = sum(r.get('summary', {}).get('total_tests', 0) for r in test_results.values())
            total_passed = sum(r.get('summary', {}).get('total_passed', 0) for r in test_results.values())
            test_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            summary.append("## TESTING RESULTS")
            summary.append(f"- **Total Tests Run**: {total_tests}")
            summary.append(f"- **Tests Passed**: {total_passed}")
            summary.append(f"- **Success Rate**: {test_success_rate:.1f}%")
            summary.append("")
        
        # Key findings
        summary.append("## KEY FINDINGS")
        
        # Find modules with most errors
        error_modules = [(name, r) for name, r in evaluation_results.items() 
                        if len(r.get('error_messages', [])) > 0]
        error_modules.sort(key=lambda x: len(x[1].get('error_messages', [])), reverse=True)
        
        if error_modules:
            summary.append(f"- **Most Problematic Module**: {error_modules[0][0]} ({len(error_modules[0][1].get('error_messages', []))} errors)")
        
        # Find modules with highest complexity
        complex_modules = [(name, r) for name, r in evaluation_results.items() 
                          if r.get('complexity_score', 0) > 30]
        complex_modules.sort(key=lambda x: x[1].get('complexity_score', 0), reverse=True)
        
        if complex_modules:
            summary.append(f"- **Most Complex Module**: {complex_modules[0][0]} (complexity: {complex_modules[0][1].get('complexity_score', 0)})")
        
        # Find modules to remove
        remove_modules = [name for name, r in evaluation_results.items() 
                         if r.get('recommendation') == 'REMOVE']
        if remove_modules:
            summary.append(f"- **Modules to Remove**: {', '.join(remove_modules[:5])}{'...' if len(remove_modules) > 5 else ''}")
        
        summary.append("")
        
        return "\n".join(summary)
    
    def generate_detailed_analysis(self, evaluation_results: Dict[str, Any]) -> str:
        """Generate detailed analysis"""
        
        analysis = []
        analysis.append("# DETAILED ANALYSIS")
        analysis.append("=" * 50)
        analysis.append("")
        
        # Group modules by recommendation
        keep_modules = {name: r for name, r in evaluation_results.items() 
                       if r.get('recommendation') == 'KEEP'}
        fix_modules = {name: r for name, r in evaluation_results.items() 
                      if r.get('recommendation') == 'FIX'}
        remove_modules = {name: r for name, r in evaluation_results.items() 
                         if r.get('recommendation') == 'REMOVE'}
        
        # Modules to Keep
        if keep_modules:
            analysis.append("## MODULES TO KEEP")
            analysis.append("")
            for name, result in keep_modules.items():
                analysis.append(f"### {name}")
                analysis.append(f"- **Status**: ✅ Keep")
                analysis.append(f"- **Priority**: {result.get('priority', 'UNKNOWN')}")
                analysis.append(f"- **File Size**: {result.get('file_size', 0)} bytes")
                analysis.append(f"- **Line Count**: {result.get('line_count', 0)}")
                analysis.append(f"- **Function Count**: {result.get('function_count', 0)}")
                analysis.append(f"- **Class Count**: {result.get('class_count', 0)}")
                analysis.append(f"- **Complexity Score**: {result.get('complexity_score', 0)}")
                analysis.append("")
        
        # Modules to Fix
        if fix_modules:
            analysis.append("## MODULES TO FIX")
            analysis.append("")
            for name, result in fix_modules.items():
                analysis.append(f"### {name}")
                analysis.append(f"- **Status**: 🔧 Fix Required")
                analysis.append(f"- **Priority**: {result.get('priority', 'UNKNOWN')}")
                analysis.append(f"- **Issues Found**: {len(result.get('error_messages', []))}")
                
                if result.get('error_messages'):
                    analysis.append("- **Errors**:")
                    for error in result['error_messages']:
                        analysis.append(f"  - {error}")
                
                if result.get('warnings'):
                    analysis.append("- **Warnings**:")
                    for warning in result['warnings']:
                        analysis.append(f"  - {warning}")
                
                analysis.append("")
        
        # Modules to Remove
        if remove_modules:
            analysis.append("## MODULES TO REMOVE")
            analysis.append("")
            for name, result in remove_modules.items():
                analysis.append(f"### {name}")
                analysis.append(f"- **Status**: ❌ Remove")
                analysis.append(f"- **Reason**: {self._get_remove_reason(result)}")
                analysis.append(f"- **File Size**: {result.get('file_size', 0)} bytes")
                analysis.append(f"- **Line Count**: {result.get('line_count', 0)}")
                analysis.append("")
        
        return "\n".join(analysis)
    
    def _get_remove_reason(self, result: Dict[str, Any]) -> str:
        """Get reason for removal recommendation"""
        
        if not result.get('file_exists'):
            return "File does not exist"
        
        if not result.get('syntax_valid'):
            return "Syntax errors"
        
        if not result.get('import_success'):
            return "Import failures"
        
        if result.get('line_count', 0) < 10:
            return "File too small/empty"
        
        if not result.get('has_functions') and not result.get('has_classes'):
            return "No functions or classes"
        
        return "Multiple issues detected"
    
    def generate_recommendations(self, evaluation_results: Dict[str, Any]) -> str:
        """Generate recommendations"""
        
        recommendations = []
        recommendations.append("# RECOMMENDATIONS")
        recommendations.append("=" * 50)
        recommendations.append("")
        
        # Immediate actions
        recommendations.append("## IMMEDIATE ACTIONS")
        recommendations.append("")
        
        # High priority fixes
        high_priority_fixes = [name for name, r in evaluation_results.items() 
                             if r.get('recommendation') == 'FIX' and r.get('priority') == 'HIGH']
        
        if high_priority_fixes:
            recommendations.append("### High Priority Fixes Required")
            recommendations.append("These modules need immediate attention:")
            for module in high_priority_fixes:
                recommendations.append(f"- **{module}**: Fix critical errors")
            recommendations.append("")
        
        # Modules to remove immediately
        remove_modules = [name for name, r in evaluation_results.items() 
                         if r.get('recommendation') == 'REMOVE']
        
        if remove_modules:
            recommendations.append("### Modules to Remove")
            recommendations.append("These modules should be removed immediately:")
            for module in remove_modules:
                recommendations.append(f"- **{module}**: No longer needed")
            recommendations.append("")
        
        # Medium-term improvements
        recommendations.append("## MEDIUM-TERM IMPROVEMENTS")
        recommendations.append("")
        
        # Code quality improvements
        complex_modules = [(name, r) for name, r in evaluation_results.items() 
                         if r.get('complexity_score', 0) > 30 and r.get('recommendation') == 'KEEP']
        
        if complex_modules:
            recommendations.append("### Code Refactoring")
            recommendations.append("These modules have high complexity and should be refactored:")
            for name, result in complex_modules:
                recommendations.append(f"- **{name}**: Complexity score {result.get('complexity_score', 0)}")
            recommendations.append("")
        
        # Documentation improvements
        modules_without_docstrings = [name for name, r in evaluation_results.items() 
                                    if not r.get('has_docstring') and r.get('recommendation') == 'KEEP']
        
        if modules_without_docstrings:
            recommendations.append("### Documentation Improvements")
            recommendations.append("These modules need better documentation:")
            for module in modules_without_docstrings:
                recommendations.append(f"- **{module}**: Add docstrings and comments")
            recommendations.append("")
        
        # Long-term strategy
        recommendations.append("## LONG-TERM STRATEGY")
        recommendations.append("")
        recommendations.append("### Architecture Improvements")
        recommendations.append("- Implement consistent error handling patterns")
        recommendations.append("- Add comprehensive logging")
        recommendations.append("- Implement automated testing")
        recommendations.append("- Add performance monitoring")
        recommendations.append("- Implement code quality gates")
        recommendations.append("")
        
        return "\n".join(recommendations)
    
    def generate_action_plan(self, evaluation_results: Dict[str, Any]) -> str:
        """Generate action plan"""
        
        action_plan = []
        action_plan.append("# ACTION PLAN")
        action_plan.append("=" * 50)
        action_plan.append("")
        
        # Phase 1: Immediate (Week 1)
        action_plan.append("## PHASE 1: IMMEDIATE ACTIONS (Week 1)")
        action_plan.append("")
        
        remove_modules = [name for name, r in evaluation_results.items() 
                         if r.get('recommendation') == 'REMOVE']
        high_priority_fixes = [name for name, r in evaluation_results.items() 
                             if r.get('recommendation') == 'FIX' and r.get('priority') == 'HIGH']
        
        action_plan.append("### Remove Unnecessary Modules")
        for module in remove_modules:
            action_plan.append(f"- [ ] Delete {module}")
        action_plan.append("")
        
        action_plan.append("### Fix Critical Issues")
        for module in high_priority_fixes:
            action_plan.append(f"- [ ] Fix {module}")
        action_plan.append("")
        
        # Phase 2: Short-term (Weeks 2-4)
        action_plan.append("## PHASE 2: SHORT-TERM IMPROVEMENTS (Weeks 2-4)")
        action_plan.append("")
        
        medium_priority_fixes = [name for name, r in evaluation_results.items() 
                               if r.get('recommendation') == 'FIX' and r.get('priority') == 'MEDIUM']
        
        action_plan.append("### Fix Medium Priority Issues")
        for module in medium_priority_fixes:
            action_plan.append(f"- [ ] Fix {module}")
        action_plan.append("")
        
        # Phase 3: Long-term (Months 2-6)
        action_plan.append("## PHASE 3: LONG-TERM IMPROVEMENTS (Months 2-6)")
        action_plan.append("")
        
        action_plan.append("### Code Quality Improvements")
        action_plan.append("- [ ] Implement code quality standards")
        action_plan.append("- [ ] Add automated testing")
        action_plan.append("- [ ] Improve documentation")
        action_plan.append("- [ ] Refactor complex modules")
        action_plan.append("")
        
        action_plan.append("### Architecture Improvements")
        action_plan.append("- [ ] Implement consistent error handling")
        action_plan.append("- [ ] Add comprehensive logging")
        action_plan.append("- [ ] Implement performance monitoring")
        action_plan.append("- [ ] Add security measures")
        action_plan.append("")
        
        return "\n".join(action_plan)
    
    def generate_risk_assessment(self, evaluation_results: Dict[str, Any]) -> str:
        """Generate risk assessment"""
        
        risk_assessment = []
        risk_assessment.append("# RISK ASSESSMENT")
        risk_assessment.append("=" * 50)
        risk_assessment.append("")
        
        # High risk modules
        high_risk_modules = [name for name, r in evaluation_results.items() 
                           if r.get('priority') == 'HIGH' and r.get('recommendation') == 'FIX']
        
        if high_risk_modules:
            risk_assessment.append("## HIGH RISK MODULES")
            risk_assessment.append("These modules pose significant risks to the system:")
            risk_assessment.append("")
            for module in high_risk_modules:
                risk_assessment.append(f"### {module}")
                risk_assessment.append("- **Risk Level**: HIGH")
                risk_assessment.append("- **Impact**: System instability, data loss, security vulnerabilities")
                risk_assessment.append("- **Mitigation**: Immediate fixes required")
                risk_assessment.append("")
        
        # Medium risk modules
        medium_risk_modules = [name for name, r in evaluation_results.items() 
                             if r.get('priority') == 'MEDIUM' and r.get('recommendation') == 'FIX']
        
        if medium_risk_modules:
            risk_assessment.append("## MEDIUM RISK MODULES")
            risk_assessment.append("These modules pose moderate risks:")
            risk_assessment.append("")
            for module in medium_risk_modules:
                risk_assessment.append(f"### {module}")
                risk_assessment.append("- **Risk Level**: MEDIUM")
                risk_assessment.append("- **Impact**: Performance issues, maintenance difficulties")
                risk_assessment.append("- **Mitigation**: Schedule fixes within 2-4 weeks")
                risk_assessment.append("")
        
        # Risk mitigation strategies
        risk_assessment.append("## RISK MITIGATION STRATEGIES")
        risk_assessment.append("")
        risk_assessment.append("### Immediate Actions")
        risk_assessment.append("- Prioritize fixing high-risk modules")
        risk_assessment.append("- Implement backup procedures")
        risk_assessment.append("- Add monitoring for critical modules")
        risk_assessment.append("")
        
        risk_assessment.append("### Long-term Strategies")
        risk_assessment.append("- Implement automated testing")
        risk_assessment.append("- Add code quality gates")
        risk_assessment.append("- Regular code reviews")
        risk_assessment.append("- Performance monitoring")
        risk_assessment.append("")
        
        return "\n".join(risk_assessment)
    
    def generate_complete_report(self, evaluation_results: Dict[str, Any], 
                               test_results: Dict[str, Any] = None) -> str:
        """Generate complete report"""
        
        report = []
        report.append("# COMPLETE MODULE EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Add all sections
        report.append(self.generate_executive_summary(evaluation_results, test_results))
        report.append("")
        report.append(self.generate_detailed_analysis(evaluation_results))
        report.append("")
        report.append(self.generate_recommendations(evaluation_results))
        report.append("")
        report.append(self.generate_action_plan(evaluation_results))
        report.append("")
        report.append(self.generate_risk_assessment(evaluation_results))
        
        return "\n".join(report)
    
    def save_report(self, report: str, filename: str = None) -> str:
        """Save report to file"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"complete_evaluation_report_{timestamp}.md"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Complete report saved to: {filepath}")
        return filepath

def main():
    """Main function untuk generate report"""
    
    print("📊 REPORT GENERATOR - Module Evaluation Report")
    print("=" * 50)
    
    # Initialize report generator
    generator = ReportGenerator()
    
    # Load evaluation results (if available)
    evaluation_file = None
    test_file = None
    
    # Look for latest evaluation results
    base_dir = os.path.dirname(__file__)
    for file in os.listdir(base_dir):
        if file.startswith('module_evaluation_results_') and file.endswith('.json'):
            evaluation_file = os.path.join(base_dir, file)
        elif file.startswith('test_results_') and file.endswith('.json'):
            test_file = os.path.join(base_dir, file)
    
    evaluation_results = {}
    test_results = {}
    
    if evaluation_file and os.path.exists(evaluation_file):
        print(f"📋 Loading evaluation results from: {evaluation_file}")
        with open(evaluation_file, 'r', encoding='utf-8') as f:
            evaluation_results = json.load(f)
    
    if test_file and os.path.exists(test_file):
        print(f"🧪 Loading test results from: {test_file}")
        with open(test_file, 'r', encoding='utf-8') as f:
            test_results = json.load(f)
    
    if not evaluation_results:
        print("❌ No evaluation results found. Please run module_evaluator.py first.")
        return
    
    # Generate complete report
    print("📝 Generating complete report...")
    report = generator.generate_complete_report(evaluation_results, test_results)
    
    # Save report
    report_file = generator.save_report(report)
    
    print(f"\n✅ Report generation completed!")
    print(f"📄 Report saved to: {report_file}")

if __name__ == "__main__":
    main()
