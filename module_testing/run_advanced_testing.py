#!/usr/bin/env python3
"""
Run Advanced Testing - Script utama untuk menjalankan advanced module testing
=======================================================================

Script ini menjalankan testing framework canggih dengan:
1. Koneksi ke database scalper
2. Time lapse simulation (1 hari = 1 detik)
3. Validasi prediksi vs hasil aktual
4. Progress tracking real-time
5. Analisis komprehensif

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import advanced tester
from advanced_module_tester import AdvancedModuleTester

def main():
    """Main function untuk menjalankan advanced testing"""
    
    print("🚀 ADVANCED MODULE TESTING - Comprehensive Testing Framework")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'scalper',
        'port': 3306
    }
    
    # Testing configuration
    modules = [
        "ai_ml",
        "technical", 
        "fundamental",
        "sentiment",
        "algorithmic_trading",
        "risk_management",
        "portfolio_optimization",
        "backtesting"
    ]
    
    symbols = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
        "NVDA", "META", "NFLX", "AMD", "INTC"
    ]
    
    # Testing period (last 30 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Time ratio: 1 day = 1 second
    time_ratio = 1.0
    
    print(f"📅 Testing Period: {start_date} to {end_date}")
    print(f"🔧 Modules: {len(modules)} modules")
    print(f"📈 Symbols: {len(symbols)} symbols")
    print(f"⏱️  Time Ratio: 1 day = {time_ratio} seconds")
    print()
    
    # Initialize advanced tester
    tester = AdvancedModuleTester(db_config)
    
    # Setup testing
    tester.setup_testing(modules, symbols, start_date, end_date, time_ratio)
    
    # Run comprehensive testing
    try:
        print("🚀 Starting comprehensive testing...")
        results = tester.run_comprehensive_testing()
        
        # Save results
        results_file = tester.save_results()
        
        # Print final summary
        print(f"\n📊 FINAL TESTING SUMMARY")
        print("=" * 50)
        print(f"Status: {results['status']}")
        print(f"Total Time: {results['total_time']}")
        print(f"Results File: {results_file}")
        
        if results['status'] == 'COMPLETED':
            print("\n✅ TESTING COMPLETED SUCCESSFULLY!")
            
            # Print module performance summary
            if 'comprehensive_report' in results:
                exec_summary = results['comprehensive_report']['executive_summary']
                print(f"\n📈 MODULE PERFORMANCE SUMMARY")
                print("-" * 40)
                
                for module, perf in exec_summary['module_performance'].items():
                    status_emoji = {
                        'VALIDATED': '✅',
                        'ANALYZED': '📊',
                        'ERROR': '❌'
                    }
                    emoji = status_emoji.get(perf['status'], '❓')
                    
                    rec_emoji = {
                        'KEEP': '✅',
                        'IMPROVE': '🔧',
                        'REPLACE': '❌'
                    }
                    rec_icon = rec_emoji.get(perf['recommendation'], '❓')
                    
                    print(f"{emoji} {module}: {perf['accuracy']:.2f}% {rec_icon} {perf['recommendation']}")
                
                print(f"\n🎯 Overall Assessment: {exec_summary['overall_assessment']}")
                
                # Print key findings
                if exec_summary['key_findings']:
                    print(f"\n🔍 KEY FINDINGS")
                    print("-" * 40)
                    for finding in exec_summary['key_findings']:
                        print(f"• {finding}")
                
                # Print recommendations
                if 'recommendations' in results['comprehensive_report']:
                    print(f"\n💡 RECOMMENDATIONS")
                    print("-" * 40)
                    for i, rec in enumerate(results['comprehensive_report']['recommendations'], 1):
                        print(f"{i}. {rec}")
                
                # Print action plan
                if 'action_plan' in results['comprehensive_report']:
                    print(f"\n📋 ACTION PLAN")
                    print("-" * 40)
                    
                    action_plan = results['comprehensive_report']['action_plan']
                    
                    if action_plan.get('immediate_actions'):
                        print("🚨 IMMEDIATE ACTIONS:")
                        for action in action_plan['immediate_actions']:
                            print(f"  • {action}")
                    
                    if action_plan.get('short_term_actions'):
                        print("\n📅 SHORT-TERM ACTIONS:")
                        for action in action_plan['short_term_actions']:
                            print(f"  • {action}")
                    
                    if action_plan.get('long_term_actions'):
                        print("\n🔮 LONG-TERM ACTIONS:")
                        for action in action_plan['long_term_actions']:
                            print(f"  • {action}")
        
        else:
            print(f"\n❌ TESTING FAILED!")
            if 'error' in results:
                print(f"Error: {results['error']}")
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        print(f"⏱️  Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Testing interrupted by user")
        print(f"⏱️  Testing stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ TESTING ERROR: {str(e)}")
        print(f"⏱️  Testing failed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
