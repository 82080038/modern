#!/usr/bin/env python3
"""
Decision Framework - Framework untuk keputusan modul
===================================================

Framework ini membantu dalam mengambil keputusan untuk setiap modul:
1. KEEP - Pertahankan modul
2. FIX - Perbaiki modul
3. REMOVE - Hapus modul

Author: AI Assistant
Date: 2025-01-16
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
import pandas as pd

class DecisionFramework:
    """Framework untuk mengambil keputusan modul"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Decision criteria weights
        self.criteria_weights = {
            'file_exists': 0.15,
            'syntax_valid': 0.20,
            'import_success': 0.20,
            'has_functions': 0.15,
            'has_classes': 0.10,
            'complexity_score': 0.10,
            'error_count': 0.10
        }
        
        # Decision thresholds
        self.thresholds = {
            'KEEP': {
                'min_score': 0.7,
                'max_errors': 0,
                'min_functions': 1,
                'max_complexity': 50
            },
            'FIX': {
                'min_score': 0.3,
                'max_errors': 5,
                'min_functions': 0,
                'max_complexity': 100
            },
            'REMOVE': {
                'max_score': 0.3,
                'max_errors': 10,
                'max_functions': 0,
                'max_complexity': 200
            }
        }
    
    def calculate_module_score(self, module_result: Dict[str, Any]) -> float:
        """Hitung skor modul berdasarkan kriteria"""
        
        score = 0.0
        
        # File exists
        if module_result.get('file_exists', False):
            score += self.criteria_weights['file_exists']
        
        # Syntax valid
        if module_result.get('syntax_valid', False):
            score += self.criteria_weights['syntax_valid']
        
        # Import success
        if module_result.get('import_success', False):
            score += self.criteria_weights['import_success']
        
        # Has functions
        if module_result.get('has_functions', False):
            score += self.criteria_weights['has_functions']
        
        # Has classes
        if module_result.get('has_classes', False):
            score += self.criteria_weights['has_classes']
        
        # Complexity score (inverted - lower is better)
        complexity = module_result.get('complexity_score', 0)
        if complexity <= 20:
            score += self.criteria_weights['complexity_score']
        elif complexity <= 50:
            score += self.criteria_weights['complexity_score'] * 0.5
        
        # Error count (inverted - fewer errors is better)
        error_count = len(module_result.get('error_messages', []))
        if error_count == 0:
            score += self.criteria_weights['error_count']
        elif error_count <= 2:
            score += self.criteria_weights['error_count'] * 0.5
        
        return min(score, 1.0)  # Cap at 1.0
    
    def make_decision(self, module_result: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Buat keputusan untuk modul"""
        
        module_name = module_result.get('module_name', 'unknown')
        score = self.calculate_module_score(module_result)
        
        # Get module metrics
        file_exists = module_result.get('file_exists', False)
        syntax_valid = module_result.get('syntax_valid', False)
        import_success = module_result.get('import_success', False)
        has_functions = module_result.get('has_functions', False)
        has_classes = module_result.get('has_classes', False)
        function_count = module_result.get('function_count', 0)
        class_count = module_result.get('class_count', 0)
        complexity_score = module_result.get('complexity_score', 0)
        error_count = len(module_result.get('error_messages', []))
        line_count = module_result.get('line_count', 0)
        
        # Decision logic
        decision = 'UNKNOWN'
        priority = 'LOW'
        reasoning = []
        
        # Check for immediate removal
        if not file_exists:
            decision = 'REMOVE'
            priority = 'HIGH'
            reasoning.append("File does not exist")
        elif line_count < 5:
            decision = 'REMOVE'
            priority = 'HIGH'
            reasoning.append("File is too small or empty")
        elif not syntax_valid:
            decision = 'REMOVE'
            priority = 'HIGH'
            reasoning.append("Syntax errors cannot be fixed")
        elif error_count > 10:
            decision = 'REMOVE'
            priority = 'HIGH'
            reasoning.append("Too many errors to fix")
        elif complexity_score > 100:
            decision = 'REMOVE'
            priority = 'HIGH'
            reasoning.append("Extremely high complexity")
        
        # Check for fix requirements
        elif not import_success:
            decision = 'FIX'
            priority = 'HIGH'
            reasoning.append("Import failures")
        elif error_count > 0:
            decision = 'FIX'
            priority = 'HIGH' if error_count > 3 else 'MEDIUM'
            reasoning.append(f"{error_count} errors found")
        elif complexity_score > 50:
            decision = 'FIX'
            priority = 'MEDIUM'
            reasoning.append("High complexity needs refactoring")
        elif not has_functions and not has_classes:
            decision = 'FIX'
            priority = 'MEDIUM'
            reasoning.append("No functions or classes found")
        
        # Check for keep
        elif score >= 0.7 and error_count == 0 and complexity_score <= 30:
            decision = 'KEEP'
            priority = 'LOW'
            reasoning.append("Module is in good condition")
        elif score >= 0.5 and error_count <= 2:
            decision = 'KEEP'
            priority = 'LOW'
            reasoning.append("Module is acceptable with minor issues")
        
        # Default to fix if uncertain
        else:
            decision = 'FIX'
            priority = 'MEDIUM'
            reasoning.append("Module needs improvement")
        
        # Create decision details
        decision_details = {
            'module_name': module_name,
            'decision': decision,
            'priority': priority,
            'score': score,
            'reasoning': reasoning,
            'metrics': {
                'file_exists': file_exists,
                'syntax_valid': syntax_valid,
                'import_success': import_success,
                'has_functions': has_functions,
                'has_classes': has_classes,
                'function_count': function_count,
                'class_count': class_count,
                'complexity_score': complexity_score,
                'error_count': error_count,
                'line_count': line_count
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return decision, priority, decision_details
    
    def analyze_all_modules(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analisis semua modul dan buat keputusan"""
        
        print("🤔 Analyzing modules and making decisions...")
        print("=" * 50)
        
        all_decisions = {}
        
        for module_name, module_result in evaluation_results.items():
            print(f"📋 Analyzing: {module_name}")
            
            decision, priority, details = self.make_decision(module_result)
            all_decisions[module_name] = details
            
            # Print decision
            decision_emoji = {
                'KEEP': '✅',
                'FIX': '🔧',
                'REMOVE': '❌'
            }
            
            priority_emoji = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            
            emoji = decision_emoji.get(decision, '❓')
            priority_icon = priority_emoji.get(priority, '⚪')
            
            print(f"   {emoji} {decision} {priority_icon} {priority}")
            print(f"   📊 Score: {details['score']:.2f}")
            print(f"   💭 Reasoning: {', '.join(details['reasoning'])}")
            print()
        
        return all_decisions
    
    def generate_decision_summary(self, decisions: Dict[str, Any]) -> str:
        """Generate summary dari keputusan"""
        
        summary = []
        summary.append("# DECISION SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Count decisions
        total_modules = len(decisions)
        keep_count = sum(1 for d in decisions.values() if d['decision'] == 'KEEP')
        fix_count = sum(1 for d in decisions.values() if d['decision'] == 'FIX')
        remove_count = sum(1 for d in decisions.values() if d['decision'] == 'REMOVE')
        
        # Count priorities
        high_priority = sum(1 for d in decisions.values() if d['priority'] == 'HIGH')
        medium_priority = sum(1 for d in decisions.values() if d['priority'] == 'MEDIUM')
        low_priority = sum(1 for d in decisions.values() if d['priority'] == 'LOW')
        
        summary.append("## OVERVIEW")
        summary.append(f"- **Total Modules**: {total_modules}")
        summary.append(f"- **Keep**: {keep_count} ({keep_count/total_modules*100:.1f}%)")
        summary.append(f"- **Fix**: {fix_count} ({fix_count/total_modules*100:.1f}%)")
        summary.append(f"- **Remove**: {remove_count} ({remove_count/total_modules*100:.1f}%)")
        summary.append("")
        
        summary.append("## PRIORITY DISTRIBUTION")
        summary.append(f"- **High Priority**: {high_priority}")
        summary.append(f"- **Medium Priority**: {medium_priority}")
        summary.append(f"- **Low Priority**: {low_priority}")
        summary.append("")
        
        # Detailed breakdown
        summary.append("## DETAILED BREAKDOWN")
        summary.append("")
        
        # Keep modules
        keep_modules = [d for d in decisions.values() if d['decision'] == 'KEEP']
        if keep_modules:
            summary.append("### Modules to Keep")
            for decision in keep_modules:
                summary.append(f"- **{decision['module_name']}**: Score {decision['score']:.2f}")
            summary.append("")
        
        # Fix modules
        fix_modules = [d for d in decisions.values() if d['decision'] == 'FIX']
        if fix_modules:
            summary.append("### Modules to Fix")
            for decision in fix_modules:
                summary.append(f"- **{decision['module_name']}**: {decision['priority']} priority")
                summary.append(f"  - Score: {decision['score']:.2f}")
                summary.append(f"  - Issues: {', '.join(decision['reasoning'])}")
            summary.append("")
        
        # Remove modules
        remove_modules = [d for d in decisions.values() if d['decision'] == 'REMOVE']
        if remove_modules:
            summary.append("### Modules to Remove")
            for decision in remove_modules:
                summary.append(f"- **{decision['module_name']}**: {decision['priority']} priority")
                summary.append(f"  - Score: {decision['score']:.2f}")
                summary.append(f"  - Reasons: {', '.join(decision['reasoning'])}")
            summary.append("")
        
        return "\n".join(summary)
    
    def generate_action_plan(self, decisions: Dict[str, Any]) -> str:
        """Generate action plan berdasarkan keputusan"""
        
        action_plan = []
        action_plan.append("# ACTION PLAN")
        action_plan.append("=" * 50)
        action_plan.append("")
        
        # Group by priority
        high_priority = [d for d in decisions.values() if d['priority'] == 'HIGH']
        medium_priority = [d for d in decisions.values() if d['priority'] == 'MEDIUM']
        low_priority = [d for d in decisions.values() if d['priority'] == 'LOW']
        
        # Immediate actions (High priority)
        if high_priority:
            action_plan.append("## IMMEDIATE ACTIONS (This Week)")
            action_plan.append("")
            
            high_remove = [d for d in high_priority if d['decision'] == 'REMOVE']
            high_fix = [d for d in high_priority if d['decision'] == 'FIX']
            
            if high_remove:
                action_plan.append("### Remove High Priority Modules")
                for decision in high_remove:
                    action_plan.append(f"- [ ] Delete {decision['module_name']}")
                action_plan.append("")
            
            if high_fix:
                action_plan.append("### Fix High Priority Modules")
                for decision in high_fix:
                    action_plan.append(f"- [ ] Fix {decision['module_name']}")
                    action_plan.append(f"  - Issues: {', '.join(decision['reasoning'])}")
                action_plan.append("")
        
        # Short-term actions (Medium priority)
        if medium_priority:
            action_plan.append("## SHORT-TERM ACTIONS (Next 2-4 Weeks)")
            action_plan.append("")
            
            medium_fix = [d for d in medium_priority if d['decision'] == 'FIX']
            medium_remove = [d for d in medium_priority if d['decision'] == 'REMOVE']
            
            if medium_remove:
                action_plan.append("### Remove Medium Priority Modules")
                for decision in medium_remove:
                    action_plan.append(f"- [ ] Delete {decision['module_name']}")
                action_plan.append("")
            
            if medium_fix:
                action_plan.append("### Fix Medium Priority Modules")
                for decision in medium_fix:
                    action_plan.append(f"- [ ] Fix {decision['module_name']}")
                    action_plan.append(f"  - Issues: {', '.join(decision['reasoning'])}")
                action_plan.append("")
        
        # Long-term actions (Low priority)
        if low_priority:
            action_plan.append("## LONG-TERM ACTIONS (Next 1-3 Months)")
            action_plan.append("")
            
            low_keep = [d for d in low_priority if d['decision'] == 'KEEP']
            low_fix = [d for d in low_priority if d['decision'] == 'FIX']
            
            if low_keep:
                action_plan.append("### Maintain Low Priority Modules")
                for decision in low_keep:
                    action_plan.append(f"- [ ] Review {decision['module_name']} for improvements")
                action_plan.append("")
            
            if low_fix:
                action_plan.append("### Improve Low Priority Modules")
                for decision in low_fix:
                    action_plan.append(f"- [ ] Improve {decision['module_name']}")
                    action_plan.append(f"  - Issues: {', '.join(decision['reasoning'])}")
                action_plan.append("")
        
        return "\n".join(action_plan)
    
    def save_decisions(self, decisions: Dict[str, Any], filename: str = None) -> str:
        """Simpan keputusan ke file"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"module_decisions_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(decisions, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Decisions saved to: {filepath}")
        return filepath

def main():
    """Main function untuk menjalankan decision framework"""
    
    print("🤔 DECISION FRAMEWORK - Module Decision Maker")
    print("=" * 50)
    
    # Initialize decision framework
    framework = DecisionFramework()
    
    # Load evaluation results
    evaluation_file = None
    base_dir = os.path.dirname(__file__)
    
    # Look for latest evaluation results
    for file in os.listdir(base_dir):
        if file.startswith('module_evaluation_results_') and file.endswith('.json'):
            evaluation_file = os.path.join(base_dir, file)
            break
    
    if not evaluation_file or not os.path.exists(evaluation_file):
        print("❌ No evaluation results found. Please run module_evaluator.py first.")
        return
    
    print(f"📋 Loading evaluation results from: {evaluation_file}")
    with open(evaluation_file, 'r', encoding='utf-8') as f:
        evaluation_results = json.load(f)
    
    # Analyze all modules
    decisions = framework.analyze_all_modules(evaluation_results)
    
    # Generate summary
    summary = framework.generate_decision_summary(decisions)
    
    # Generate action plan
    action_plan = framework.generate_action_plan(decisions)
    
    # Save decisions
    decisions_file = framework.save_decisions(decisions)
    
    # Save summary
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_file = f"decision_summary_{timestamp}.md"
    summary_path = os.path.join(os.path.dirname(__file__), summary_file)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # Save action plan
    action_file = f"action_plan_{timestamp}.md"
    action_path = os.path.join(os.path.dirname(__file__), action_file)
    
    with open(action_path, 'w', encoding='utf-8') as f:
        f.write(action_plan)
    
    print(f"\n✅ Decision analysis completed!")
    print(f"📄 Decisions: {decisions_file}")
    print(f"📄 Summary: {summary_path}")
    print(f"📄 Action Plan: {action_path}")
    
    # Print final summary
    total = len(decisions)
    keep = sum(1 for d in decisions.values() if d['decision'] == 'KEEP')
    fix = sum(1 for d in decisions.values() if d['decision'] == 'FIX')
    remove = sum(1 for d in decisions.values() if d['decision'] == 'REMOVE')
    
    print(f"\n📈 FINAL DECISIONS:")
    print(f"   Total Modules: {total}")
    print(f"   ✅ Keep: {keep}")
    print(f"   🔧 Fix: {fix}")
    print(f"   ❌ Remove: {remove}")

if __name__ == "__main__":
    main()
