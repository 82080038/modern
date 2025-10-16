#!/usr/bin/env python3
"""
Comprehensive Tuning Analyzer
=============================

Sistem yang menganalisis semua data tuning yang ada dan memberikan
rekomendasi optimasi berdasarkan performa aktual dari sistem trading.

Author: AI Assistant
Date: 2025-01-17
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def load_all_performance_data():
    """Load all available performance data from JSON files"""
    performance_data = {}
    
    # List of performance files to analyze
    performance_files = [
        'module_testing/ultimate_trading_simulation_20251017_030858.json',
        'module_testing/optimized_trading_simulation_20251017_025642.json',
        'module_testing/fixed_trading_simulation_20251017_024808.json',
        'module_testing/improved_trading_simulation_20251017_022032.json',
        'module_testing/time_lapse_simulation_20251017_020737.json'
    ]
    
    for file_path in performance_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    system_name = data.get('simulation_period', 'unknown').split(' - ')[-1].lower()
                    performance_data[system_name] = data
                print(f"[PASS] Loaded {system_name} performance data")
            except Exception as e:
                print(f"[WARN] Could not load {file_path}: {e}")
    
    return performance_data

def analyze_comprehensive_performance(performance_data):
    """Analyze comprehensive performance metrics from all systems"""
    print("\nCOMPREHENSIVE PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    analysis = {}
    
    for system_name, data in performance_data.items():
        print(f"\n{system_name.upper()} SYSTEM:")
        
        # Extract key metrics
        total_return = data.get('total_return_pct', 0)
        win_rate = data.get('win_rate', 0)
        total_trades = data.get('total_trades', 0)
        sharpe_ratio = data.get('sharpe_ratio', 0)
        best_month = data.get('best_month', {}).get('return_pct', 0)
        worst_month = data.get('worst_month', {}).get('return_pct', 0)
        
        # Calculate profitable months
        monthly_results = data.get('monthly_results', [])
        profitable_months = sum(1 for month in monthly_results if month.get('return_pct', 0) > 0)
        total_months = len(monthly_results)
        profitable_ratio = profitable_months / total_months if total_months > 0 else 0
        
        # Calculate performance score
        performance_score = (
            (total_return / 10) * 0.3 +  # 30% weight for return
            (win_rate / 100) * 0.25 +   # 25% weight for win rate
            (sharpe_ratio * 10) * 0.2 + # 20% weight for sharpe
            profitable_ratio * 0.15 +     # 15% weight for consistency
            (min(total_trades / 60, 1)) * 0.1  # 10% weight for trade frequency
        )
        
        analysis[system_name] = {
            'total_return': total_return,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'sharpe_ratio': sharpe_ratio,
            'best_month': best_month,
            'worst_month': worst_month,
            'profitable_months': profitable_months,
            'total_months': total_months,
            'profitable_ratio': profitable_ratio,
            'performance_score': performance_score
        }
        
        print(f"  Total Return: {total_return:.2f}%")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Total Trades: {total_trades}")
        print(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"  Best Month: {best_month:.2f}%")
        print(f"  Worst Month: {worst_month:.2f}%")
        print(f"  Profitable Months: {profitable_months}/{total_months} ({profitable_ratio:.1%})")
        print(f"  Performance Score: {performance_score:.2f}/10")
    
    return analysis

def identify_critical_issues(analysis):
    """Identify critical issues that need immediate attention"""
    print("\nIDENTIFYING CRITICAL ISSUES")
    print("=" * 80)
    
    # Define target performance
    targets = {
        'target_return': 10.0,  # 10% annual return
        'target_win_rate': 60.0,  # 60% win rate
        'target_sharpe': 1.0,  # 1.0 sharpe ratio
        'target_trades': 60,  # 60 trades per year
        'target_consistency': 0.6  # 60% profitable months
    }
    
    print("TARGET PERFORMANCE:")
    print(f"  Annual Return: {targets['target_return']:.1f}%")
    print(f"  Win Rate: {targets['target_win_rate']:.1f}%")
    print(f"  Sharpe Ratio: {targets['target_sharpe']:.1f}")
    print(f"  Annual Trades: {targets['target_trades']}")
    print(f"  Consistency: {targets['target_consistency']:.1%}")
    
    critical_issues = []
    
    for system_name, metrics in analysis.items():
        print(f"\n{system_name.upper()} CRITICAL ISSUES:")
        
        issues = []
        severity = "LOW"
        
        # Check return
        if metrics['total_return'] < targets['target_return']:
            gap = targets['target_return'] - metrics['total_return']
            issues.append(f"Return {metrics['total_return']:.1f}% < {targets['target_return']:.1f}% (gap: {gap:.1f}%)")
            if gap > 5:
                severity = "HIGH"
        
        # Check win rate
        if metrics['win_rate'] < targets['target_win_rate']:
            gap = targets['target_win_rate'] - metrics['win_rate']
            issues.append(f"Win rate {metrics['win_rate']:.1f}% < {targets['target_win_rate']:.1f}% (gap: {gap:.1f}%)")
            if gap > 20:
                severity = "HIGH"
        
        # Check sharpe ratio
        if metrics['sharpe_ratio'] < targets['target_sharpe']:
            gap = targets['target_sharpe'] - metrics['sharpe_ratio']
            issues.append(f"Sharpe {metrics['sharpe_ratio']:.2f} < {targets['target_sharpe']:.1f} (gap: {gap:.2f})")
            if gap > 0.5:
                severity = "HIGH"
        
        # Check trade frequency
        if metrics['total_trades'] > targets['target_trades']:
            excess = metrics['total_trades'] - targets['target_trades']
            issues.append(f"Trades {metrics['total_trades']} > {targets['target_trades']} (excess: {excess})")
            if excess > 20:
                severity = "HIGH"
        
        # Check consistency
        if metrics['profitable_ratio'] < targets['target_consistency']:
            gap = targets['target_consistency'] - metrics['profitable_ratio']
            issues.append(f"Consistency {metrics['profitable_ratio']:.1%} < {targets['target_consistency']:.1%} (gap: {gap:.1%})")
            if gap > 0.2:
                severity = "HIGH"
        
        if issues:
            critical_issues.append({
                'system': system_name,
                'severity': severity,
                'performance_score': metrics['performance_score'],
                'issues': issues,
                'priority': 'CRITICAL' if severity == 'HIGH' else 'MEDIUM' if severity == 'MEDIUM' else 'LOW'
            })
            
            print(f"  SEVERITY: {severity}")
            print(f"  PRIORITY: {critical_issues[-1]['priority']}")
            print(f"  ISSUES:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  PASS: All targets met")
    
    return critical_issues

def generate_smart_recommendations(critical_issues):
    """Generate smart recommendations based on critical issues"""
    print("\nGENERATING SMART RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    for issue in critical_issues:
        system_name = issue['system']
        severity = issue['severity']
        priority = issue['priority']
        score = issue['performance_score']
        
        print(f"\n{system_name.upper()} RECOMMENDATIONS (Priority: {priority}):")
        
        rec = {
            'system': system_name,
            'priority': priority,
            'severity': severity,
            'current_score': score,
            'immediate_actions': [],
            'parameter_optimizations': [],
            'module_enhancements': [],
            'module_replacements': [],
            'expected_improvement': 0
        }
        
        # Immediate actions for critical issues
        if priority == 'CRITICAL':
            rec['immediate_actions'].extend([
                "STOP trading immediately and review all parameters",
                "Reduce risk per trade to 0.1% (emergency mode)",
                "Increase signal thresholds by 50%",
                "Implement strict position size limits",
                "Add mandatory confirmation filters"
            ])
            rec['expected_improvement'] += 30
        
        # Parameter optimizations based on specific issues
        for issue_text in issue['issues']:
            if "Return" in issue_text:
                rec['parameter_optimizations'].extend([
                    "Reduce risk per trade from 0.3% to 0.2%",
                    "Lower signal thresholds: BUY 0.8, STRONG_BUY 1.5",
                    "Increase position size for strong signals only",
                    "Add momentum confirmation requirement"
                ])
                rec['expected_improvement'] += 15
            
            if "Win rate" in issue_text:
                rec['parameter_optimizations'].extend([
                    "Increase signal thresholds: BUY 1.2, STRONG_BUY 2.0",
                    "Add volume confirmation requirement",
                    "Add trend confirmation requirement",
                    "Implement multi-timeframe validation"
                ])
                rec['expected_improvement'] += 20
            
            if "Sharpe" in issue_text:
                rec['parameter_optimizations'].extend([
                    "Reduce max position size to 1.5%",
                    "Tighten stop loss to 1.5%",
                    "Implement dynamic position sizing",
                    "Add correlation-based position limits"
                ])
                rec['expected_improvement'] += 25
            
            if "Trades" in issue_text:
                rec['parameter_optimizations'].extend([
                    "Increase signal thresholds significantly",
                    "Add market condition filters",
                    "Implement trade frequency limits",
                    "Add volatility-based trading pauses"
                ])
                rec['expected_improvement'] += 10
            
            if "Consistency" in issue_text:
                rec['parameter_optimizations'].extend([
                    "Add market regime detection",
                    "Implement volatility filters",
                    "Add correlation analysis",
                    "Implement drawdown protection"
                ])
                rec['expected_improvement'] += 30
        
        # Module enhancements for medium priority
        if priority in ['MEDIUM', 'CRITICAL']:
            rec['module_enhancements'].extend([
                "Enhance technical analysis with more indicators",
                "Improve fundamental analysis scoring",
                "Add sentiment analysis integration",
                "Implement portfolio optimization"
            ])
            rec['expected_improvement'] += 20
        
        # Module replacements for critical issues
        if priority == 'CRITICAL':
            rec['module_replacements'].extend([
                "Replace signal generation with LSTM neural network",
                "Implement ensemble learning approach",
                "Add real-time market data integration",
                "Implement adaptive parameter tuning"
            ])
            rec['expected_improvement'] += 40
        
        recommendations.append(rec)
        
        print(f"  IMMEDIATE ACTIONS:")
        for i, action in enumerate(rec['immediate_actions'], 1):
            print(f"    {i}. {action}")
        
        print(f"  PARAMETER OPTIMIZATIONS:")
        for i, opt in enumerate(rec['parameter_optimizations'], 1):
            print(f"    {i}. {opt}")
        
        if rec['module_enhancements']:
            print(f"  MODULE ENHANCEMENTS:")
            for i, enh in enumerate(rec['module_enhancements'], 1):
                print(f"    {i}. {enh}")
        
        if rec['module_replacements']:
            print(f"  MODULE REPLACEMENTS:")
            for i, rep in enumerate(rec['module_replacements'], 1):
                print(f"    {i}. {rep}")
        
        print(f"  EXPECTED IMPROVEMENT: +{rec['expected_improvement']:.0f}%")
    
    return recommendations

def create_emergency_configuration(recommendations):
    """Create emergency configuration for critical issues"""
    print("\nCREATING EMERGENCY CONFIGURATION")
    print("=" * 80)
    
    # Emergency configuration for critical issues
    emergency_config = {
        "version": "EMERGENCY_1.0",
        "created_at": datetime.now().isoformat(),
        "status": "EMERGENCY_MODE",
        "modules": {
            "trading": {
                "risk_per_trade": 0.001,  # Ultra-conservative
                "max_position_size": 0.01,  # 1% max position
                "stop_loss": 0.01,  # 1% stop loss
                "take_profit": 0.03,  # 3% take profit
                "signal_threshold_buy": 2.0,  # Very high threshold
                "signal_threshold_strong_buy": 3.0,
                "signal_threshold_very_strong_buy": 4.0,
                "add_volume_confirmation": True,
                "add_trend_confirmation": True,
                "add_momentum_confirmation": True,
                "add_correlation_confirmation": True,
                "max_trades_per_month": 3,  # Very limited trading
                "emergency_mode": True
            },
            "risk_management": {
                "max_portfolio_risk": 0.05,  # 5% max portfolio risk
                "correlation_threshold": 0.5,  # Very strict correlation
                "var_confidence": 0.99,
                "dynamic_position_sizing": True,
                "correlation_based_limits": True,
                "drawdown_protection": True,
                "emergency_stop_loss": True
            },
            "technical_analysis": {
                "rsi_periods": [14, 21, 50],
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "bollinger_period": 20,
                "bollinger_std": 2,
                "multi_timeframe_validation": True,
                "volume_confirmation": True,
                "trend_confirmation": True,
                "momentum_confirmation": True
            },
            "fundamental_analysis": {
                "pe_ratio_min": 8,  # Stricter PE ratio
                "pe_ratio_max": 20,  # Stricter PE ratio
                "market_cap_min": 500000000,  # Higher market cap requirement
                "sector_weights": {
                    "Technology": 1.0,  # Neutral weights
                    "Healthcare": 1.0,
                    "Finance": 1.0,
                    "Energy": 1.0,
                    "Utilities": 1.0
                },
                "enhanced_scoring": True,
                "strict_fundamental_filter": True
            },
            "sentiment_analysis": {
                "sentiment_threshold": 0.5,  # Higher sentiment threshold
                "confidence_threshold": 0.8,  # Higher confidence threshold
                "news_weight": 0.5,
                "social_weight": 0.3,
                "analyst_weight": 0.2,
                "real_time_integration": True,
                "strict_sentiment_filter": True
            },
            "market_analysis": {
                "regime_detection": True,
                "volatility_filter": True,
                "market_condition_filter": True,
                "correlation_analysis": True,
                "emergency_market_filter": True
            }
        },
        "system_performance": {
            "target_annual_return": 0.05,  # Lower target for safety
            "target_win_rate": 0.70,  # Higher win rate target
            "target_sharpe_ratio": 1.5,  # Higher sharpe target
            "target_trades_per_month": 3,  # Very limited trading
            "target_consistency": 0.80  # High consistency target
        },
        "emergency_protocols": {
            "auto_stop_trading": True,
            "max_daily_loss": 0.02,  # 2% max daily loss
            "max_weekly_loss": 0.05,  # 5% max weekly loss
            "emergency_contact": True
        }
    }
    
    # Save emergency configuration
    with open('modul/emergency_module_configuration.json', 'w') as f:
        json.dump(emergency_config, f, indent=4)
    
    print("Emergency configuration created with:")
    print(f"  Risk per trade: {emergency_config['modules']['trading']['risk_per_trade']:.3f}")
    print(f"  Max position size: {emergency_config['modules']['trading']['max_position_size']:.3f}")
    print(f"  Stop loss: {emergency_config['modules']['trading']['stop_loss']:.3f}")
    print(f"  Take profit: {emergency_config['modules']['trading']['take_profit']:.3f}")
    print(f"  BUY threshold: {emergency_config['modules']['trading']['signal_threshold_buy']:.1f}")
    print(f"  STRONG_BUY threshold: {emergency_config['modules']['trading']['signal_threshold_strong_buy']:.1f}")
    print(f"  Max trades per month: {emergency_config['modules']['trading']['max_trades_per_month']}")
    print(f"  Emergency mode: {emergency_config['modules']['trading']['emergency_mode']}")
    
    return emergency_config

def generate_implementation_roadmap(recommendations):
    """Generate implementation roadmap with priorities"""
    print("\nGENERATING IMPLEMENTATION ROADMAP")
    print("=" * 80)
    
    roadmap = {
        'phase_1_emergency': [],
        'phase_2_immediate': [],
        'phase_3_short_term': [],
        'phase_4_long_term': [],
        'expected_results': {}
    }
    
    # Phase 1: Emergency (critical issues)
    for rec in recommendations:
        if rec['priority'] == 'CRITICAL':
            roadmap['phase_1_emergency'].append({
                'action': 'Emergency Configuration',
                'system': rec['system'],
                'actions': rec['immediate_actions'],
                'expected_improvement': f"+{rec['expected_improvement']:.0f}%",
                'effort': 'Low',
                'timeline': 'Immediate'
            })
    
    # Phase 2: Immediate (parameter optimization)
    for rec in recommendations:
        if rec['priority'] in ['CRITICAL', 'MEDIUM']:
            roadmap['phase_2_immediate'].append({
                'action': 'Parameter Optimization',
                'system': rec['system'],
                'changes': rec['parameter_optimizations'][:3],  # Top 3 changes
                'expected_improvement': f"+{rec['expected_improvement'] * 0.6:.0f}%",
                'effort': 'Low',
                'timeline': '1-2 days'
            })
    
    # Phase 3: Short term (module enhancements)
    for rec in recommendations:
        if rec['module_enhancements']:
            roadmap['phase_3_short_term'].append({
                'action': 'Module Enhancement',
                'system': rec['system'],
                'enhancements': rec['module_enhancements'],
                'expected_improvement': f"+{rec['expected_improvement'] * 0.3:.0f}%",
                'effort': 'Medium',
                'timeline': '1-2 weeks'
            })
    
    # Phase 4: Long term (module replacement)
    for rec in recommendations:
        if rec['module_replacements']:
            roadmap['phase_4_long_term'].append({
                'action': 'Module Replacement',
                'system': rec['system'],
                'replacements': rec['module_replacements'],
                'expected_improvement': f"+{rec['expected_improvement'] * 0.1:.0f}%",
                'effort': 'High',
                'timeline': '1-2 months'
            })
    
    # Calculate expected results
    total_improvement = sum(rec['expected_improvement'] for rec in recommendations)
    roadmap['expected_results'] = {
        'total_improvement': f"+{total_improvement:.0f}%",
        'target_return': f"{1.63 + (total_improvement/100 * 1.63):.1f}%",
        'target_win_rate': "70-80%",
        'target_sharpe': "1.5-2.0",
        'target_consistency': "80-90%"
    }
    
    # Display roadmap
    print("IMPLEMENTATION ROADMAP:")
    print(f"  Total Expected Improvement: {roadmap['expected_results']['total_improvement']}")
    print(f"  Target Return: {roadmap['expected_results']['target_return']}")
    print(f"  Target Win Rate: {roadmap['expected_results']['target_win_rate']}")
    print(f"  Target Sharpe: {roadmap['expected_results']['target_sharpe']}")
    print(f"  Target Consistency: {roadmap['expected_results']['target_consistency']}")
    
    print(f"\nPHASE 1 - EMERGENCY ({len(roadmap['phase_1_emergency'])} items):")
    for i, item in enumerate(roadmap['phase_1_emergency'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    print(f"\nPHASE 2 - IMMEDIATE ({len(roadmap['phase_2_immediate'])} items):")
    for i, item in enumerate(roadmap['phase_2_immediate'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    print(f"\nPHASE 3 - SHORT TERM ({len(roadmap['phase_3_short_term'])} items):")
    for i, item in enumerate(roadmap['phase_3_short_term'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    print(f"\nPHASE 4 - LONG TERM ({len(roadmap['phase_4_long_term'])} items):")
    for i, item in enumerate(roadmap['phase_4_long_term'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    return roadmap

def main():
    """Main function"""
    start_time = datetime.now()
    
    print("COMPREHENSIVE TUNING ANALYZER")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Load all performance data
        print("Loading all performance data...")
        performance_data = load_all_performance_data()
        
        if not performance_data:
            print("[ERROR] No performance data found. Please run trading simulations first.")
            return
        
        # Analyze comprehensive performance
        analysis = analyze_comprehensive_performance(performance_data)
        
        # Identify critical issues
        critical_issues = identify_critical_issues(analysis)
        
        # Generate smart recommendations
        recommendations = generate_smart_recommendations(critical_issues)
        
        # Create emergency configuration
        emergency_config = create_emergency_configuration(recommendations)
        
        # Generate implementation roadmap
        roadmap = generate_implementation_roadmap(recommendations)
        
        # Save analysis results
        results = {
            'analysis': analysis,
            'critical_issues': critical_issues,
            'recommendations': recommendations,
            'emergency_config': emergency_config,
            'roadmap': roadmap,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save results
        end_time = datetime.now()
        file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"comprehensive_tuning_analysis_{file_timestamp}.json"
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=4, default=str)
        
        print(f"\nAnalysis results saved to: {output_filename}")
        print(f"Optimization completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TUNING ANALYZER SUMMARY")
        print("=" * 80)
        print(f"Systems Analyzed: {len(analysis)}")
        print(f"Critical Issues Found: {len(critical_issues)}")
        print(f"Recommendations Generated: {len(recommendations)}")
        print(f"Implementation Phases: 4")
        print(f"Expected Total Improvement: {roadmap['expected_results']['total_improvement']}")
        print(f"Target Return: {roadmap['expected_results']['target_return']}")
        print(f"Target Win Rate: {roadmap['expected_results']['target_win_rate']}")
        print(f"Target Sharpe: {roadmap['expected_results']['target_sharpe']}")
        print(f"Target Consistency: {roadmap['expected_results']['target_consistency']}")
        
        # Critical alerts
        critical_count = sum(1 for issue in critical_issues if issue['priority'] == 'CRITICAL')
        if critical_count > 0:
            print(f"\n🚨 CRITICAL ALERT: {critical_count} systems need immediate attention!")
            print("Emergency configuration has been created.")
            print("Please review and implement emergency protocols immediately.")
        
    except Exception as err:
        print(f"[ERROR] {err}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
