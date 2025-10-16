#!/usr/bin/env python3
"""
Smart Tuning Analyzer
=====================

Sistem yang menganalisis data tuning dan memberikan rekomendasi optimasi
berdasarkan performa aktual dari sistem trading.

Author: AI Assistant
Date: 2025-01-17
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def load_performance_data():
    """Load performance data from JSON files"""
    performance_data = {}
    
    # List of possible performance files
    performance_files = [
        'module_testing/ultimate_trading_simulation_20251017_030858.json',
        'module_testing/optimized_trading_simulation_20251017_025642.json',
        'module_testing/fixed_trading_simulation_20251017_024808.json'
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

def analyze_performance_metrics(performance_data):
    """Analyze performance metrics from all systems"""
    print("\nANALYZING PERFORMANCE METRICS")
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

def identify_optimization_opportunities(analysis):
    """Identify optimization opportunities based on performance analysis"""
    print("\nIDENTIFYING OPTIMIZATION OPPORTUNITIES")
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
    
    opportunities = []
    
    for system_name, metrics in analysis.items():
        print(f"\n{system_name.upper()} ANALYSIS:")
        
        issues = []
        improvements = []
        
        # Check return
        if metrics['total_return'] < targets['target_return']:
            gap = targets['target_return'] - metrics['total_return']
            issues.append(f"Return {metrics['total_return']:.1f}% < {targets['target_return']:.1f}% (gap: {gap:.1f}%)")
            improvements.append(f"Improve signal quality and reduce risk per trade")
        
        # Check win rate
        if metrics['win_rate'] < targets['target_win_rate']:
            gap = targets['target_win_rate'] - metrics['win_rate']
            issues.append(f"Win rate {metrics['win_rate']:.1f}% < {targets['target_win_rate']:.1f}% (gap: {gap:.1f}%)")
            improvements.append(f"Add confirmation filters and improve signal validation")
        
        # Check sharpe ratio
        if metrics['sharpe_ratio'] < targets['target_sharpe']:
            gap = targets['target_sharpe'] - metrics['sharpe_ratio']
            issues.append(f"Sharpe {metrics['sharpe_ratio']:.2f} < {targets['target_sharpe']:.1f} (gap: {gap:.2f})")
            improvements.append(f"Improve risk management and position sizing")
        
        # Check trade frequency
        if metrics['total_trades'] > targets['target_trades']:
            excess = metrics['total_trades'] - targets['target_trades']
            issues.append(f"Trades {metrics['total_trades']} > {targets['target_trades']} (excess: {excess})")
            improvements.append(f"Increase signal thresholds and add market condition filters")
        
        # Check consistency
        if metrics['profitable_ratio'] < targets['target_consistency']:
            gap = targets['target_consistency'] - metrics['profitable_ratio']
            issues.append(f"Consistency {metrics['profitable_ratio']:.1%} < {targets['target_consistency']:.1%} (gap: {gap:.1%})")
            improvements.append(f"Add market regime detection and volatility filters")
        
        if issues:
            opportunities.append({
                'system': system_name,
                'performance_score': metrics['performance_score'],
                'issues': issues,
                'improvements': improvements,
                'priority': 'HIGH' if metrics['performance_score'] < 5 else 'MEDIUM' if metrics['performance_score'] < 7 else 'LOW'
            })
            
            print(f"  PRIORITY: {opportunities[-1]['priority']}")
            print(f"  ISSUES:")
            for issue in issues:
                print(f"    - {issue}")
            print(f"  IMPROVEMENTS:")
            for improvement in improvements:
                print(f"    - {improvement}")
        else:
            print(f"  PASS: All targets met")
    
    return opportunities

def generate_optimization_recommendations(opportunities):
    """Generate specific optimization recommendations"""
    print("\nGENERATING OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    for opp in opportunities:
        system_name = opp['system']
        score = opp['performance_score']
        priority = opp['priority']
        
        print(f"\n{system_name.upper()} RECOMMENDATIONS (Priority: {priority}):")
        
        rec = {
            'system': system_name,
            'priority': priority,
            'current_score': score,
            'parameter_optimizations': [],
            'module_enhancements': [],
            'module_replacements': [],
            'expected_improvement': 0
        }
        
        # Parameter optimizations based on issues
        for issue in opp['issues']:
            if "Return" in issue:
                rec['parameter_optimizations'].extend([
                    "Reduce risk per trade from 0.3% to 0.2%",
                    "Lower signal thresholds: BUY 0.8, STRONG_BUY 1.5",
                    "Increase position size for strong signals",
                    "Add momentum confirmation"
                ])
                rec['expected_improvement'] += 15
            
            if "Win rate" in issue:
                rec['parameter_optimizations'].extend([
                    "Increase signal thresholds: BUY 1.2, STRONG_BUY 2.0",
                    "Add volume confirmation requirement",
                    "Add trend confirmation requirement",
                    "Implement multi-timeframe validation"
                ])
                rec['expected_improvement'] += 20
            
            if "Sharpe" in issue:
                rec['parameter_optimizations'].extend([
                    "Reduce max position size to 1.5%",
                    "Tighten stop loss to 1.5%",
                    "Implement dynamic position sizing",
                    "Add correlation-based position limits"
                ])
                rec['expected_improvement'] += 25
            
            if "Trades" in issue:
                rec['parameter_optimizations'].extend([
                    "Increase signal thresholds significantly",
                    "Add market condition filters",
                    "Implement trade frequency limits",
                    "Add volatility-based trading pauses"
                ])
                rec['expected_improvement'] += 10
            
            if "Consistency" in issue:
                rec['parameter_optimizations'].extend([
                    "Add market regime detection",
                    "Implement volatility filters",
                    "Add correlation analysis",
                    "Implement drawdown protection"
                ])
                rec['expected_improvement'] += 30
        
        # Module enhancements for medium priority
        if priority == 'MEDIUM':
            rec['module_enhancements'].extend([
                "Enhance technical analysis with more indicators",
                "Improve fundamental analysis scoring",
                "Add sentiment analysis integration",
                "Implement portfolio optimization"
            ])
            rec['expected_improvement'] += 20
        
        # Module replacements for high priority
        if priority == 'HIGH':
            rec['module_replacements'].extend([
                "Replace signal generation with LSTM neural network",
                "Implement ensemble learning approach",
                "Add real-time market data integration",
                "Implement adaptive parameter tuning"
            ])
            rec['expected_improvement'] += 40
        
        recommendations.append(rec)
        
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

def create_optimized_configuration(recommendations):
    """Create optimized configuration based on recommendations"""
    print("\nCREATING OPTIMIZED CONFIGURATION")
    print("=" * 80)
    
    # Base configuration
    optimized_config = {
        "version": "2.0",
        "created_at": datetime.now().isoformat(),
        "modules": {
            "trading": {
                "risk_per_trade": 0.002,  # Reduced from 0.003
                "max_position_size": 0.015,  # Reduced from 0.02
                "stop_loss": 0.015,  # Reduced from 0.02
                "take_profit": 0.05,  # Reduced from 0.06
                "signal_threshold_buy": 1.2,  # Increased from 1.0
                "signal_threshold_strong_buy": 2.0,  # Increased from 2.0
                "signal_threshold_very_strong_buy": 3.0,
                "add_volume_confirmation": True,
                "add_trend_confirmation": True,
                "add_momentum_confirmation": True,
                "max_trades_per_month": 5
            },
            "risk_management": {
                "max_portfolio_risk": 0.08,  # Reduced from 0.1
                "correlation_threshold": 0.6,  # Reduced from 0.7
                "var_confidence": 0.99,  # Increased from 0.95
                "dynamic_position_sizing": True,
                "correlation_based_limits": True,
                "drawdown_protection": True
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
                "trend_confirmation": True
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
                "enhanced_scoring": True
            },
            "sentiment_analysis": {
                "sentiment_threshold": 0.3,
                "confidence_threshold": 0.7,
                "news_weight": 0.4,
                "social_weight": 0.3,
                "analyst_weight": 0.3,
                "real_time_integration": True
            },
            "market_analysis": {
                "regime_detection": True,
                "volatility_filter": True,
                "market_condition_filter": True,
                "correlation_analysis": True
            }
        },
        "system_performance": {
            "target_annual_return": 0.10,
            "target_win_rate": 0.60,
            "target_sharpe_ratio": 1.0,
            "target_trades_per_month": 5,
            "target_consistency": 0.6
        },
        "optimization_history": []
    }
    
    # Apply recommendations
    for rec in recommendations:
        if rec['priority'] == 'HIGH':
            # Apply aggressive optimizations
            optimized_config['modules']['trading']['risk_per_trade'] = 0.001
            optimized_config['modules']['trading']['max_position_size'] = 0.01
            optimized_config['modules']['trading']['signal_threshold_buy'] = 1.5
            optimized_config['modules']['trading']['signal_threshold_strong_buy'] = 2.5
        
        elif rec['priority'] == 'MEDIUM':
            # Apply moderate optimizations
            optimized_config['modules']['trading']['risk_per_trade'] = 0.002
            optimized_config['modules']['trading']['max_position_size'] = 0.015
            optimized_config['modules']['trading']['signal_threshold_buy'] = 1.2
            optimized_config['modules']['trading']['signal_threshold_strong_buy'] = 2.0
    
    # Save optimized configuration
    with open('modul/optimized_module_configuration.json', 'w') as f:
        json.dump(optimized_config, f, indent=4)
    
    print("Optimized configuration created with:")
    print(f"  Risk per trade: {optimized_config['modules']['trading']['risk_per_trade']:.3f}")
    print(f"  Max position size: {optimized_config['modules']['trading']['max_position_size']:.3f}")
    print(f"  Stop loss: {optimized_config['modules']['trading']['stop_loss']:.3f}")
    print(f"  Take profit: {optimized_config['modules']['trading']['take_profit']:.3f}")
    print(f"  BUY threshold: {optimized_config['modules']['trading']['signal_threshold_buy']:.1f}")
    print(f"  STRONG_BUY threshold: {optimized_config['modules']['trading']['signal_threshold_strong_buy']:.1f}")
    print(f"  Volume confirmation: {optimized_config['modules']['trading']['add_volume_confirmation']}")
    print(f"  Trend confirmation: {optimized_config['modules']['trading']['add_trend_confirmation']}")
    print(f"  Max trades per month: {optimized_config['modules']['trading']['max_trades_per_month']}")
    
    return optimized_config

def generate_implementation_roadmap(recommendations):
    """Generate implementation roadmap"""
    print("\nGENERATING IMPLEMENTATION ROADMAP")
    print("=" * 80)
    
    roadmap = {
        'phase_1_immediate': [],
        'phase_2_short_term': [],
        'phase_3_long_term': [],
        'expected_results': {}
    }
    
    # Phase 1: Immediate (parameter tuning)
    for rec in recommendations:
        if rec['priority'] == 'HIGH':
            roadmap['phase_1_immediate'].append({
                'action': 'Critical Parameter Optimization',
                'system': rec['system'],
                'changes': rec['parameter_optimizations'][:3],  # Top 3 changes
                'expected_improvement': f"+{rec['expected_improvement']:.0f}%",
                'effort': 'Low',
                'timeline': '1-2 days'
            })
    
    # Phase 2: Short term (module enhancements)
    for rec in recommendations:
        if rec['priority'] in ['HIGH', 'MEDIUM']:
            roadmap['phase_2_short_term'].append({
                'action': 'Module Enhancement',
                'system': rec['system'],
                'enhancements': rec['module_enhancements'],
                'expected_improvement': f"+{rec['expected_improvement'] * 0.5:.0f}%",
                'effort': 'Medium',
                'timeline': '1-2 weeks'
            })
    
    # Phase 3: Long term (module replacement)
    for rec in recommendations:
        if rec['priority'] == 'HIGH' and rec['module_replacements']:
            roadmap['phase_3_long_term'].append({
                'action': 'Module Replacement',
                'system': rec['system'],
                'replacements': rec['module_replacements'],
                'expected_improvement': f"+{rec['expected_improvement'] * 0.3:.0f}%",
                'effort': 'High',
                'timeline': '1-2 months'
            })
    
    # Calculate expected results
    total_improvement = sum(rec['expected_improvement'] for rec in recommendations)
    roadmap['expected_results'] = {
        'total_improvement': f"+{total_improvement:.0f}%",
        'target_return': f"{1.63 + (total_improvement/100 * 1.63):.1f}%",
        'target_win_rate': "65-75%",
        'target_sharpe': "1.2-1.5",
        'target_consistency': "70-80%"
    }
    
    # Display roadmap
    print("IMPLEMENTATION ROADMAP:")
    print(f"  Total Expected Improvement: {roadmap['expected_results']['total_improvement']}")
    print(f"  Target Return: {roadmap['expected_results']['target_return']}")
    print(f"  Target Win Rate: {roadmap['expected_results']['target_win_rate']}")
    print(f"  Target Sharpe: {roadmap['expected_results']['target_sharpe']}")
    print(f"  Target Consistency: {roadmap['expected_results']['target_consistency']}")
    
    print(f"\nPHASE 1 - IMMEDIATE ({len(roadmap['phase_1_immediate'])} items):")
    for i, item in enumerate(roadmap['phase_1_immediate'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    print(f"\nPHASE 2 - SHORT TERM ({len(roadmap['phase_2_short_term'])} items):")
    for i, item in enumerate(roadmap['phase_2_short_term'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    print(f"\nPHASE 3 - LONG TERM ({len(roadmap['phase_3_long_term'])} items):")
    for i, item in enumerate(roadmap['phase_3_long_term'], 1):
        print(f"  {i}. {item['action']} for {item['system']}")
        print(f"     Expected: {item['expected_improvement']}, Effort: {item['effort']}, Timeline: {item['timeline']}")
    
    return roadmap

def main():
    """Main function"""
    start_time = datetime.now()
    
    print("SMART TUNING ANALYZER")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Load performance data
        print("Loading performance data...")
        performance_data = load_performance_data()
        
        if not performance_data:
            print("[ERROR] No performance data found. Please run trading simulations first.")
            return
        
        # Analyze performance metrics
        analysis = analyze_performance_metrics(performance_data)
        
        # Identify optimization opportunities
        opportunities = identify_optimization_opportunities(analysis)
        
        # Generate optimization recommendations
        recommendations = generate_optimization_recommendations(opportunities)
        
        # Create optimized configuration
        optimized_config = create_optimized_configuration(recommendations)
        
        # Generate implementation roadmap
        roadmap = generate_implementation_roadmap(recommendations)
        
        # Save analysis results
        results = {
            'analysis': analysis,
            'opportunities': opportunities,
            'recommendations': recommendations,
            'optimized_config': optimized_config,
            'roadmap': roadmap,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save results
        end_time = datetime.now()
        file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"smart_tuning_analysis_{file_timestamp}.json"
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=4, default=str)
        
        print(f"\nAnalysis results saved to: {output_filename}")
        print(f"Optimization completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SMART TUNING ANALYZER SUMMARY")
        print("=" * 80)
        print(f"Systems Analyzed: {len(analysis)}")
        print(f"Optimization Opportunities: {len(opportunities)}")
        print(f"Recommendations Generated: {len(recommendations)}")
        print(f"Implementation Phases: 3")
        print(f"Expected Total Improvement: {roadmap['expected_results']['total_improvement']}")
        print(f"Target Return: {roadmap['expected_results']['target_return']}")
        print(f"Target Win Rate: {roadmap['expected_results']['target_win_rate']}")
        print(f"Target Sharpe: {roadmap['expected_results']['target_sharpe']}")
        print(f"Target Consistency: {roadmap['expected_results']['target_consistency']}")
        
    except Exception as err:
        print(f"[ERROR] {err}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
