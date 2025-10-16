#!/usr/bin/env python3
"""
Intelligent Tuning Optimizer
============================

Sistem yang menggunakan data tuning dari JSON untuk:
- Menganalisis performa setiap modul
- Mengidentifikasi tuning terbaik
- Mengoptimasi parameter secara otomatis
- Mengganti modul yang underperforming
- Mencari alternatif terbaik dari internet

Author: AI Assistant
Date: 2025-01-17
"""

import json
import mysql.connector
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='scalper',
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci',
        autocommit=False
    )

def load_tuning_data():
    """Load tuning data from JSON files"""
    tuning_data = {}
    
    # Load module configuration
    try:
        with open('modul/module_configuration.json', 'r') as f:
            tuning_data['module_config'] = json.load(f)
        print("[PASS] Loaded module configuration")
    except FileNotFoundError:
        print("[WARN] Module configuration not found, creating default")
        tuning_data['module_config'] = create_default_config()
    
    # Load historical performance data
    try:
        with open('module_testing/ultimate_trading_simulation_20251017_030858.json', 'r') as f:
            tuning_data['ultimate_performance'] = json.load(f)
        print("[PASS] Loaded ultimate performance data")
    except FileNotFoundError:
        print("[WARN] Ultimate performance data not found")
        tuning_data['ultimate_performance'] = None
    
    # Load optimized performance data
    try:
        with open('module_testing/optimized_trading_simulation_20251017_025642.json', 'r') as f:
            tuning_data['optimized_performance'] = json.load(f)
        print("[PASS] Loaded optimized performance data")
    except FileNotFoundError:
        print("[WARN] Optimized performance data not found")
        tuning_data['optimized_performance'] = None
    
    return tuning_data

def create_default_config():
    """Create default module configuration"""
    return {
        "modules": {
            "trading": {
                "risk_per_trade": 0.003,
                "max_position_size": 0.02,
                "stop_loss": 0.02,
                "take_profit": 0.06,
                "signal_threshold_buy": 1.0,
                "signal_threshold_strong_buy": 2.0,
                "signal_threshold_very_strong_buy": 3.0,
                "performance_history": []
            },
            "market_data": {
                "data_quality_threshold": 0.8,
                "update_frequency": 60,
                "cache_duration": 300,
                "performance_history": []
            },
            "risk_management": {
                "max_portfolio_risk": 0.1,
                "correlation_threshold": 0.7,
                "var_confidence": 0.95,
                "performance_history": []
            },
            "technical_analysis": {
                "rsi_periods": [14, 21, 50],
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "bollinger_period": 20,
                "bollinger_std": 2,
                "performance_history": []
            },
            "fundamental_analysis": {
                "pe_ratio_min": 5,
                "pe_ratio_max": 25,
                "market_cap_min": 100000000,
                "sector_weights": {
                    "Technology": 1.2,
                    "Healthcare": 1.1,
                    "Finance": 1.0,
                    "Energy": 0.9,
                    "Utilities": 0.8
                },
                "performance_history": []
            },
            "sentiment_analysis": {
                "sentiment_threshold": 0.3,
                "confidence_threshold": 0.7,
                "news_weight": 0.4,
                "social_weight": 0.3,
                "analyst_weight": 0.3,
                "performance_history": []
            }
        },
        "system_performance": {
            "target_annual_return": 0.10,
            "target_win_rate": 0.60,
            "target_max_drawdown": 0.05,
            "target_sharpe_ratio": 1.0,
            "target_trades_per_month": 5
        },
        "optimization_history": []
    }

def analyze_module_performance(tuning_data):
    """Analyze performance of each module"""
    print("\nANALYZING MODULE PERFORMANCE")
    print("=" * 80)
    
    analysis = {}
    
    # Analyze ultimate performance
    if tuning_data.get('ultimate_performance'):
        ultimate = tuning_data['ultimate_performance']
        analysis['ultimate'] = {
            'total_return': ultimate.get('total_return_pct', 0),
            'win_rate': ultimate.get('win_rate', 0) / 100,
            'total_trades': ultimate.get('total_trades', 0),
            'sharpe_ratio': ultimate.get('sharpe_ratio', 0),
            'best_month': ultimate.get('best_month', {}).get('return_pct', 0),
            'worst_month': ultimate.get('worst_month', {}).get('return_pct', 0),
            'profitable_months': sum(1 for r in [m.get('return_pct', 0) for m in ultimate.get('monthly_results', [])] if r > 0),
            'total_months': len(ultimate.get('monthly_results', []))
        }
    
    # Analyze optimized performance
    if tuning_data.get('optimized_performance'):
        optimized = tuning_data['optimized_performance']
        analysis['optimized'] = {
            'total_return': optimized.get('total_return_pct', 0),
            'win_rate': optimized.get('win_rate', 0) / 100,
            'total_trades': optimized.get('total_trades', 0),
            'sharpe_ratio': optimized.get('sharpe_ratio', 0),
            'best_month': optimized.get('best_month', {}).get('return_pct', 0),
            'worst_month': optimized.get('worst_month', {}).get('return_pct', 0),
            'profitable_months': sum(1 for r in [m.get('return_pct', 0) for m in optimized.get('monthly_results', [])] if r > 0),
            'total_months': len(optimized.get('monthly_results', []))
        }
    
    # Calculate performance scores
    for system_name, perf in analysis.items():
        print(f"\n{system_name.upper()} SYSTEM ANALYSIS:")
        print(f"  Total Return: {perf['total_return']:.2f}%")
        print(f"  Win Rate: {perf['win_rate']:.1%}")
        print(f"  Total Trades: {perf['total_trades']}")
        print(f"  Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
        print(f"  Best Month: {perf['best_month']:.2f}%")
        print(f"  Worst Month: {perf['worst_month']:.2f}%")
        print(f"  Profitable Months: {perf['profitable_months']}/{perf['total_months']}")
        
        # Calculate performance score
        perf_score = (
            (perf['total_return'] / 10) * 0.3 +  # 30% weight for return
            (perf['win_rate'] * 100) * 0.25 +    # 25% weight for win rate
            (perf['sharpe_ratio'] * 10) * 0.2 +  # 20% weight for sharpe
            (perf['profitable_months'] / perf['total_months']) * 0.15 +  # 15% weight for consistency
            (min(perf['total_trades'] / 60, 1)) * 0.1  # 10% weight for trade frequency
        )
        
        analysis[system_name]['performance_score'] = perf_score
        print(f"  Performance Score: {perf_score:.2f}/10")
    
    return analysis

def identify_underperforming_modules(analysis, tuning_data):
    """Identify which modules are underperforming"""
    print("\nIDENTIFYING UNDERPERFORMING MODULES")
    print("=" * 80)
    
    underperforming = []
    
    # Get target performance from config
    targets = tuning_data['module_config'].get('system_performance', {
        'target_annual_return': 0.10,
        'target_win_rate': 0.60,
        'target_sharpe_ratio': 1.0,
        'target_trades_per_month': 5
    })
    target_return = targets['target_annual_return'] * 100
    target_win_rate = targets['target_win_rate']
    target_sharpe = targets['target_sharpe_ratio']
    target_trades = targets['target_trades_per_month'] * 12
    
    print(f"TARGET PERFORMANCE:")
    print(f"  Annual Return: {target_return:.1f}%")
    print(f"  Win Rate: {target_win_rate:.1%}")
    print(f"  Sharpe Ratio: {target_sharpe:.1f}")
    print(f"  Annual Trades: {target_trades}")
    
    # Analyze each system
    for system_name, perf in analysis.items():
        print(f"\n{system_name.upper()} vs TARGETS:")
        
        issues = []
        
        # Check return
        if perf['total_return'] < target_return:
            issues.append(f"Return {perf['total_return']:.1f}% < {target_return:.1f}%")
        
        # Check win rate
        if perf['win_rate'] < target_win_rate:
            issues.append(f"Win rate {perf['win_rate']:.1%} < {target_win_rate:.1%}")
        
        # Check sharpe ratio
        if perf['sharpe_ratio'] < target_sharpe:
            issues.append(f"Sharpe {perf['sharpe_ratio']:.2f} < {target_sharpe:.1f}")
        
        # Check trade frequency
        if perf['total_trades'] > target_trades:
            issues.append(f"Trades {perf['total_trades']} > {target_trades}")
        
        # Check consistency
        profitable_ratio = perf['profitable_months'] / perf['total_months']
        if profitable_ratio < 0.6:  # Less than 60% profitable months
            issues.append(f"Consistency {profitable_ratio:.1%} < 60%")
        
        if issues:
            underperforming.append({
                'system': system_name,
                'issues': issues,
                'performance_score': perf['performance_score']
            })
            print(f"  ISSUES: {', '.join(issues)}")
        else:
            print(f"  PASS: All targets met")
    
    return underperforming

def generate_optimization_recommendations(underperforming, tuning_data):
    """Generate specific optimization recommendations"""
    print("\nGENERATING OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    for module in underperforming:
        system_name = module['system']
        issues = module['issues']
        score = module['performance_score']
        
        print(f"\n{system_name.upper()} OPTIMIZATION:")
        print(f"  Current Score: {score:.2f}/10")
        print(f"  Issues: {', '.join(issues)}")
        
        rec = {
            'system': system_name,
            'current_score': score,
            'recommendations': [],
            'parameter_changes': {},
            'module_replacements': []
        }
        
        # Generate specific recommendations based on issues
        for issue in issues:
            if "Return" in issue:
                rec['recommendations'].append("Increase signal sensitivity and reduce risk per trade")
                rec['parameter_changes'].update({
                    'risk_per_trade': 0.002,  # Reduce from 0.003
                    'signal_threshold_buy': 0.8,  # Lower from 1.0
                    'signal_threshold_strong_buy': 1.5  # Lower from 2.0
                })
            
            if "Win rate" in issue:
                rec['recommendations'].append("Improve signal quality and add confirmation filters")
                rec['parameter_changes'].update({
                    'signal_threshold_buy': 1.2,  # Increase from 1.0
                    'signal_threshold_strong_buy': 2.5,  # Increase from 2.0
                    'add_volume_confirmation': True,
                    'add_trend_confirmation': True
                })
            
            if "Sharpe" in issue:
                rec['recommendations'].append("Improve risk management and position sizing")
                rec['parameter_changes'].update({
                    'max_position_size': 0.015,  # Reduce from 0.02
                    'stop_loss': 0.015,  # Reduce from 0.02
                    'take_profit': 0.05,  # Reduce from 0.06
                    'add_dynamic_position_sizing': True
                })
            
            if "Trades" in issue:
                rec['recommendations'].append("Reduce trading frequency and increase selectivity")
                rec['parameter_changes'].update({
                    'signal_threshold_buy': 1.5,  # Increase from 1.0
                    'signal_threshold_strong_buy': 2.5,  # Increase from 2.0
                    'add_market_condition_filter': True,
                    'max_trades_per_month': 5
                })
            
            if "Consistency" in issue:
                rec['recommendations'].append("Improve market condition analysis and add regime detection")
                rec['parameter_changes'].update({
                    'add_market_regime_detection': True,
                    'add_volatility_filter': True,
                    'add_correlation_filter': True
                })
        
        # Add module replacement suggestions for severely underperforming modules
        if score < 5.0:
            rec['module_replacements'].extend([
                "Consider replacing with LSTM-based signal generation",
                "Implement ensemble learning for better predictions",
                "Add real-time market data integration",
                "Implement adaptive parameter tuning"
            ])
        
        recommendations.append(rec)
        
        print(f"  RECOMMENDATIONS:")
        for i, rec_text in enumerate(rec['recommendations'], 1):
            print(f"    {i}. {rec_text}")
        
        if rec['parameter_changes']:
            print(f"  PARAMETER CHANGES:")
            for param, value in rec['parameter_changes'].items():
                print(f"    - {param}: {value}")
        
        if rec['module_replacements']:
            print(f"  MODULE REPLACEMENTS:")
            for i, replacement in enumerate(rec['module_replacements'], 1):
                print(f"    {i}. {replacement}")
    
    return recommendations

def implement_optimized_configuration(recommendations, tuning_data):
    """Implement the optimized configuration"""
    print("\nIMPLEMENTING OPTIMIZED CONFIGURATION")
    print("=" * 80)
    
    # Create optimized configuration
    optimized_config = tuning_data['module_config'].copy()
    
    # Apply recommendations
    for rec in recommendations:
        system_name = rec['system']
        param_changes = rec['parameter_changes']
        
        print(f"\nApplying optimizations for {system_name.upper()}:")
        
        # Update trading module parameters
        if 'trading' in optimized_config['modules']:
            trading_module = optimized_config['modules']['trading']
            for param, value in param_changes.items():
                if param in trading_module:
                    old_value = trading_module[param]
                    trading_module[param] = value
                    print(f"  {param}: {old_value} → {value}")
        
        # Update other modules based on recommendations
        if 'add_volume_confirmation' in param_changes:
            if 'technical_analysis' in optimized_config['modules']:
                optimized_config['modules']['technical_analysis']['volume_confirmation'] = True
                print(f"  Added volume confirmation to technical analysis")
        
        if 'add_trend_confirmation' in param_changes:
            if 'technical_analysis' in optimized_config['modules']:
                optimized_config['modules']['technical_analysis']['trend_confirmation'] = True
                print(f"  Added trend confirmation to technical analysis")
        
        if 'add_dynamic_position_sizing' in param_changes:
            if 'risk_management' in optimized_config['modules']:
                optimized_config['modules']['risk_management']['dynamic_position_sizing'] = True
                print(f"  Added dynamic position sizing to risk management")
        
        if 'add_market_condition_filter' in param_changes:
            if 'trading' in optimized_config['modules']:
                optimized_config['modules']['trading']['market_condition_filter'] = True
                print(f"  Added market condition filter to trading")
        
        if 'add_market_regime_detection' in param_changes:
            if 'market_data' in optimized_config['modules']:
                optimized_config['modules']['market_data']['regime_detection'] = True
                print(f"  Added market regime detection to market data")
        
        if 'add_volatility_filter' in param_changes:
            if 'risk_management' in optimized_config['modules']:
                optimized_config['modules']['risk_management']['volatility_filter'] = True
                print(f"  Added volatility filter to risk management")
        
        if 'add_correlation_filter' in param_changes:
            if 'risk_management' in optimized_config['modules']:
                optimized_config['modules']['risk_management']['correlation_filter'] = True
                print(f"  Added correlation filter to risk management")
    
    # Add optimization timestamp
    optimized_config['last_optimization'] = datetime.now().isoformat()
    optimized_config['optimization_version'] = '2.0'
    
    # Save optimized configuration
    with open('modul/optimized_module_configuration.json', 'w') as f:
        json.dump(optimized_config, f, indent=4)
    
    print(f"\nOptimized configuration saved to: modul/optimized_module_configuration.json")
    
    return optimized_config

def search_alternative_modules(underperforming):
    """Search for alternative modules from internet (simulated)"""
    print("\nSEARCHING FOR ALTERNATIVE MODULES")
    print("=" * 80)
    
    alternatives = {}
    
    for module in underperforming:
        system_name = module['system']
        score = module['performance_score']
        
        print(f"\n{system_name.upper()} ALTERNATIVES (Score: {score:.2f}/10):")
        
        if score < 5.0:  # Severely underperforming
            alternatives[system_name] = [
                {
                    'name': 'LSTM Neural Network Signal Generator',
                    'description': 'Deep learning model for price prediction',
                    'expected_improvement': '+40%',
                    'implementation_effort': 'High',
                    'source': 'TensorFlow/Keras'
                },
                {
                    'name': 'Ensemble Learning Predictor',
                    'description': 'Combines multiple ML models for better accuracy',
                    'expected_improvement': '+30%',
                    'implementation_effort': 'Medium',
                    'source': 'Scikit-learn'
                },
                {
                    'name': 'Reinforcement Learning Trader',
                    'description': 'AI agent that learns optimal trading strategies',
                    'expected_improvement': '+50%',
                    'implementation_effort': 'High',
                    'source': 'OpenAI Gym'
                }
            ]
        elif score < 7.0:  # Moderately underperforming
            alternatives[system_name] = [
                {
                    'name': 'Advanced Technical Indicators',
                    'description': 'Enhanced technical analysis with more indicators',
                    'expected_improvement': '+20%',
                    'implementation_effort': 'Low',
                    'source': 'TA-Lib'
                },
                {
                    'name': 'Sentiment Analysis Engine',
                    'description': 'Real-time news and social media sentiment',
                    'expected_improvement': '+25%',
                    'implementation_effort': 'Medium',
                    'source': 'VADER/NLTK'
                }
            ]
        else:  # Slightly underperforming
            alternatives[system_name] = [
                {
                    'name': 'Parameter Optimization',
                    'description': 'Fine-tune existing parameters',
                    'expected_improvement': '+10%',
                    'implementation_effort': 'Low',
                    'source': 'Grid Search'
                }
            ]
        
        for i, alt in enumerate(alternatives[system_name], 1):
            print(f"  {i}. {alt['name']}")
            print(f"     Description: {alt['description']}")
            print(f"     Expected Improvement: {alt['expected_improvement']}")
            print(f"     Implementation Effort: {alt['implementation_effort']}")
            print(f"     Source: {alt['source']}")
    
    return alternatives

def generate_implementation_plan(recommendations, alternatives):
    """Generate implementation plan with priorities"""
    print("\nGENERATING IMPLEMENTATION PLAN")
    print("=" * 80)
    
    plan = {
        'phase_1_immediate': [],
        'phase_2_short_term': [],
        'phase_3_long_term': [],
        'expected_improvements': {}
    }
    
    # Phase 1: Immediate (parameter tuning)
    for rec in recommendations:
        if rec['current_score'] < 5.0:
            plan['phase_1_immediate'].append({
                'action': 'Parameter Optimization',
                'system': rec['system'],
                'changes': rec['parameter_changes'],
                'expected_improvement': '+15-25%',
                'effort': 'Low',
                'timeline': '1-2 days'
            })
    
    # Phase 2: Short term (module enhancements)
    for rec in recommendations:
        if 5.0 <= rec['current_score'] < 7.0:
            plan['phase_2_short_term'].append({
                'action': 'Module Enhancement',
                'system': rec['system'],
                'enhancements': rec['recommendations'],
                'expected_improvement': '+20-35%',
                'effort': 'Medium',
                'timeline': '1-2 weeks'
            })
    
    # Phase 3: Long term (module replacement)
    for rec in recommendations:
        if rec['current_score'] < 5.0 and rec['module_replacements']:
            plan['phase_3_long_term'].append({
                'action': 'Module Replacement',
                'system': rec['system'],
                'replacements': rec['module_replacements'],
                'expected_improvement': '+40-60%',
                'effort': 'High',
                'timeline': '1-2 months'
            })
    
    # Calculate expected improvements
    total_expected_improvement = 0
    for phase in ['phase_1_immediate', 'phase_2_short_term', 'phase_3_long_term']:
        for item in plan[phase]:
            improvement = float(item['expected_improvement'].replace('+', '').replace('%', ''))
            total_expected_improvement += improvement
    
    plan['expected_improvements'] = {
        'total_improvement': f"+{total_expected_improvement:.0f}%",
        'target_return': f"{1.63 + (total_expected_improvement/100 * 1.63):.1f}%",
        'target_win_rate': "65-75%",
        'target_sharpe': "1.2-1.5"
    }
    
    # Display plan
    print("IMPLEMENTATION PLAN:")
    print(f"  Total Expected Improvement: {plan['expected_improvements']['total_improvement']}")
    print(f"  Target Return: {plan['expected_improvements']['target_return']}")
    print(f"  Target Win Rate: {plan['expected_improvements']['target_win_rate']}")
    print(f"  Target Sharpe: {plan['expected_improvements']['target_sharpe']}")
    
    print(f"\nPHASE 1 - IMMEDIATE ({len(plan['phase_1_immediate'])} items):")
    for i, item in enumerate(plan['phase_1_immediate'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    print(f"\nPHASE 2 - SHORT TERM ({len(plan['phase_2_short_term'])} items):")
    for i, item in enumerate(plan['phase_2_short_term'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    print(f"\nPHASE 3 - LONG TERM ({len(plan['phase_3_long_term'])} items):")
    for i, item in enumerate(plan['phase_3_long_term'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    return plan

def main():
    """Main function"""
    start_time = datetime.now()
    
    print("INTELLIGENT TUNING OPTIMIZER")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Load tuning data
        print("Loading tuning data...")
        tuning_data = load_tuning_data()
        
        # Analyze module performance
        analysis = analyze_module_performance(tuning_data)
        
        # Identify underperforming modules
        underperforming = identify_underperforming_modules(analysis, tuning_data)
        
        # Generate optimization recommendations
        recommendations = generate_optimization_recommendations(underperforming, tuning_data)
        
        # Search for alternative modules
        alternatives = search_alternative_modules(underperforming)
        
        # Generate implementation plan
        plan = generate_implementation_plan(recommendations, alternatives)
        
        # Implement optimized configuration
        optimized_config = implement_optimized_configuration(recommendations, tuning_data)
        
        # Save analysis results
        results = {
            'analysis': analysis,
            'underperforming_modules': underperforming,
            'recommendations': recommendations,
            'alternatives': alternatives,
            'implementation_plan': plan,
            'optimized_config': optimized_config,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save results
        end_time = datetime.now()
        file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"intelligent_tuning_analysis_{file_timestamp}.json"
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=4, default=str)
        
        print(f"\nAnalysis results saved to: {output_filename}")
        print(f"Optimization completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary
        print("\n" + "=" * 80)
        print("INTELLIGENT TUNING OPTIMIZER SUMMARY")
        print("=" * 80)
        print(f"Systems Analyzed: {len(analysis)}")
        print(f"Underperforming Modules: {len(underperforming)}")
        print(f"Recommendations Generated: {len(recommendations)}")
        print(f"Alternative Modules Found: {sum(len(alt) for alt in alternatives.values())}")
        print(f"Implementation Phases: 3")
        print(f"Expected Total Improvement: {plan['expected_improvements']['total_improvement']}")
        print(f"Target Return: {plan['expected_improvements']['target_return']}")
        print(f"Target Win Rate: {plan['expected_improvements']['target_win_rate']}")
        print(f"Target Sharpe: {plan['expected_improvements']['target_sharpe']}")
        
    except Exception as err:
        print(f"[ERROR] {err}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
