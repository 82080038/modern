#!/usr/bin/env python3
"""
Run Scalper Testing - Script khusus untuk testing modul scalper
==============================================================

Script ini menjalankan testing framework khusus untuk aplikasi scalper:
1. Koneksi ke database scalper
2. Time lapse simulation dengan data historis
3. Validasi prediksi vs hasil aktual
4. Progress tracking untuk setiap modul
5. Analisis akurasi prediksi

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
    """Main function untuk menjalankan scalper testing"""
    
    print("SCALPER MODULE TESTING - Advanced Testing Framework")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Database configuration untuk scalper
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'scalper',
        'port': 3306
    }
    
    # Modules yang akan ditest (berdasarkan struktur aplikasi)
    modules = [
        "ai_ml",
        "algorithmic_trading", 
        "backtesting",
        "technical",
        "fundamental",
        "sentiment",
        "risk_management",
        "portfolio_optimization",
        "trading",
        "market_data",
        "earnings",
        "economic_calendar",
        "notifications",
        "watchlist"
    ]
    
    # Symbols untuk testing (dapat disesuaikan dengan data yang ada)
    symbols = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
        "NVDA", "META", "NFLX", "AMD", "INTC",
        "SPY", "QQQ", "IWM", "VTI", "VOO"
    ]
    
    # Testing period (last 30 days untuk testing)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Time ratio: 1 day = 1 second (sesuai permintaan)
    time_ratio = 1.0
    
    print(f"Testing Period: {start_date} to {end_date}")
    print(f"Modules: {len(modules)} modules")
    print(f"Symbols: {len(symbols)} symbols")
    print(f"Time Ratio: 1 day = {time_ratio} seconds")
    print(f"Database: {db_config['database']} on {db_config['host']}")
    print()
    
    # Initialize advanced tester
    tester = AdvancedModuleTester(db_config)
    
    # Setup testing
    tester.setup_testing(modules, symbols, start_date, end_date, time_ratio)
    
    # Run comprehensive testing
    try:
        print("Starting comprehensive scalper testing...")
        print("=" * 50)
        
        results = tester.run_comprehensive_testing()
        
        # Save results
        results_file = tester.save_results()
        
        # Print final summary
        print(f"\nSCALPER TESTING SUMMARY")
        print("=" * 50)
        print(f"Status: {results['status']}")
        print(f"Total Time: {results['total_time']}")
        print(f"Results File: {results_file}")
        
        if results['status'] == 'COMPLETED':
            print("\n✅ SCALPER TESTING COMPLETED SUCCESSFULLY!")
            
            # Print detailed module performance
            if 'comprehensive_report' in results:
                exec_summary = results['comprehensive_report']['executive_summary']
                print(f"\n📈 MODULE PERFORMANCE ANALYSIS")
                print("-" * 50)
                
                # Group modules by performance
                high_performers = []
                medium_performers = []
                low_performers = []
                
                for module, perf in exec_summary['module_performance'].items():
                    if perf['accuracy'] >= 80:
                        high_performers.append((module, perf['accuracy']))
                    elif perf['accuracy'] >= 60:
                        medium_performers.append((module, perf['accuracy']))
                    else:
                        low_performers.append((module, perf['accuracy']))
                
                # Print high performers
                if high_performers:
                    print("🏆 HIGH PERFORMERS (≥80% accuracy):")
                    for module, accuracy in sorted(high_performers, key=lambda x: x[1], reverse=True):
                        print(f"   ✅ {module}: {accuracy:.2f}%")
                
                # Print medium performers
                if medium_performers:
                    print("\n🔧 MEDIUM PERFORMERS (60-79% accuracy):")
                    for module, accuracy in sorted(medium_performers, key=lambda x: x[1], reverse=True):
                        print(f"   ⚠️  {module}: {accuracy:.2f}%")
                
                # Print low performers
                if low_performers:
                    print("\n❌ LOW PERFORMERS (<60% accuracy):")
                    for module, accuracy in sorted(low_performers, key=lambda x: x[1], reverse=True):
                        print(f"   ❌ {module}: {accuracy:.2f}%")
                
                print(f"\n🎯 Overall Assessment: {exec_summary['overall_assessment']}")
                
                # Print key findings
                if exec_summary['key_findings']:
                    print(f"\n🔍 KEY FINDINGS")
                    print("-" * 50)
                    for finding in exec_summary['key_findings']:
                        print(f"• {finding}")
                
                # Print recommendations
                if 'recommendations' in results['comprehensive_report']:
                    print(f"\n💡 RECOMMENDATIONS")
                    print("-" * 50)
                    for i, rec in enumerate(results['comprehensive_report']['recommendations'], 1):
                        print(f"{i}. {rec}")
                
                # Print action plan
                if 'action_plan' in results['comprehensive_report']:
                    print(f"\n📋 ACTION PLAN")
                    print("-" * 50)
                    
                    action_plan = results['comprehensive_report']['action_plan']
                    
                    if action_plan.get('immediate_actions'):
                        print("🚨 IMMEDIATE ACTIONS (This Week):")
                        for action in action_plan['immediate_actions']:
                            print(f"  • {action}")
                    
                    if action_plan.get('short_term_actions'):
                        print("\n📅 SHORT-TERM ACTIONS (Next 2-4 Weeks):")
                        for action in action_plan['short_term_actions']:
                            print(f"  • {action}")
                    
                    if action_plan.get('long_term_actions'):
                        print("\n🔮 LONG-TERM ACTIONS (Next 1-3 Months):")
                        for action in action_plan['long_term_actions']:
                            print(f"  • {action}")
                
                # Print module-specific recommendations
                print(f"\n🔧 MODULE-SPECIFIC RECOMMENDATIONS")
                print("-" * 50)
                
                for module, perf in exec_summary['module_performance'].items():
                    if perf['recommendation'] == 'KEEP':
                        print(f"✅ {module}: Keep and maintain")
                    elif perf['recommendation'] == 'IMPROVE':
                        print(f"🔧 {module}: Needs improvement")
                    elif perf['recommendation'] == 'REPLACE':
                        print(f"❌ {module}: Consider replacing")
        
        else:
            print(f"\n❌ SCALPER TESTING FAILED!")
            if 'error' in results:
                print(f"Error: {results['error']}")
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        print(f"⏱️  Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Print next steps
        print(f"\n📋 NEXT STEPS")
        print("-" * 50)
        print("1. Review the detailed results file")
        print("2. Implement immediate actions")
        print("3. Schedule short-term improvements")
        print("4. Plan long-term enhancements")
        print("5. Set up continuous monitoring")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Testing interrupted by user")
        print(f"⏱️  Testing stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ SCALPER TESTING ERROR: {str(e)}")
        print(f"⏱️  Testing failed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💡 Please check database connection and configuration")

if __name__ == "__main__":
    main()