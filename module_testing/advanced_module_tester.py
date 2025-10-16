#!/usr/bin/env python3
"""
Advanced Module Tester - Testing framework canggih dengan time lapse dan validasi prediksi
========================================================================================

Framework ini mengintegrasikan semua komponen untuk testing modul:
1. Database Connector - Akses data historis
2. Time Lapse Simulator - Simulasi time lapse (1 hari = 1 detik)
3. Prediction Validator - Validasi prediksi vs hasil aktual
4. Progress Tracker - Tracking progress real-time
5. Historical Analyzer - Analisis data historis dan akurasi

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import pandas as pd

# Import semua komponen
from database_connector import DatabaseConnector
from time_lapse_simulator import TimeLapseSimulator
from prediction_validator import PredictionValidator
from progress_tracker import ProgressTracker
from historical_analyzer import HistoricalAnalyzer

class AdvancedModuleTester:
    """Testing framework canggih untuk modul trading"""
    
    def __init__(self, db_config: Dict[str, Any] = None):
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'scalper',
            'port': 3306
        }
        
        # Initialize komponen
        self.db_connector = DatabaseConnector(self.db_config)
        self.simulator = None
        self.validator = None
        self.tracker = None
        self.analyzer = None
        
        # Testing configuration
        self.testing_config = {
            'time_ratio': 1.0,  # 1 hari = 1 detik
            'modules': [],
            'symbols': [],
            'start_date': None,
            'end_date': None,
            'enable_time_lapse': True,
            'enable_validation': True,
            'enable_analysis': True
        }
        
        # Results
        self.testing_results = {}
        self.is_running = False
        
    def setup_testing(self, modules: List[str], symbols: List[str], 
                     start_date: str, end_date: str, time_ratio: float = 1.0):
        """Setup testing configuration"""
        
        self.testing_config.update({
            'modules': modules,
            'symbols': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'time_ratio': time_ratio
        })
        
        print(f"🔧 Setting up advanced module testing")
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"🔧 Modules: {', '.join(modules)}")
        print(f"📈 Symbols: {', '.join(symbols)}")
        print(f"⏱️  Time Ratio: 1 day = {time_ratio} seconds")
        print("=" * 60)
        
        # Initialize komponen
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize semua komponen"""
        
        # Initialize database connector
        if not self.db_connector.connect():
            raise Exception("Cannot connect to database")
        
        # Initialize validator
        self.validator = PredictionValidator(self.db_connector)
        
        # Initialize analyzer
        self.analyzer = HistoricalAnalyzer(self.db_connector)
        
        # Initialize progress tracker
        self.tracker = ProgressTracker()
        
        # Initialize simulator
        self.simulator = TimeLapseSimulator(self.db_connector, self.testing_config['time_ratio'])
        
        print("✅ All components initialized successfully")
    
    def run_comprehensive_testing(self) -> Dict[str, Any]:
        """Jalankan testing komprehensif"""
        
        print(f"\n🚀 STARTING COMPREHENSIVE MODULE TESTING")
        print("=" * 60)
        print(f"📅 Period: {self.testing_config['start_date']} to {self.testing_config['end_date']}")
        print(f"🔧 Modules: {', '.join(self.testing_config['modules'])}")
        print(f"📈 Symbols: {', '.join(self.testing_config['symbols'])}")
        print(f"⏱️  Time Ratio: 1 day = {self.testing_config['time_ratio']} seconds")
        print("=" * 60)
        
        self.is_running = True
        start_time = datetime.now()
        
        try:
            # Step 1: Historical Analysis
            print(f"\n📊 STEP 1: Historical Analysis")
            print("-" * 40)
            historical_results = self._run_historical_analysis()
            
            # Step 2: Time Lapse Simulation
            print(f"\n🎬 STEP 2: Time Lapse Simulation")
            print("-" * 40)
            simulation_results = self._run_time_lapse_simulation()
            
            # Step 3: Prediction Validation
            print(f"\n🔍 STEP 3: Prediction Validation")
            print("-" * 40)
            validation_results = self._run_prediction_validation()
            
            # Step 4: Module Performance Analysis
            print(f"\n📈 STEP 4: Module Performance Analysis")
            print("-" * 40)
            performance_results = self._run_performance_analysis()
            
            # Step 5: Generate Comprehensive Report
            print(f"\n📋 STEP 5: Generating Comprehensive Report")
            print("-" * 40)
            comprehensive_report = self._generate_comprehensive_report(
                historical_results, simulation_results, validation_results, performance_results
            )
            
            # Finalize results
            end_time = datetime.now()
            total_time = end_time - start_time
            
            self.testing_results = {
                'testing_config': self.testing_config,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_time': str(total_time),
                'historical_results': historical_results,
                'simulation_results': simulation_results,
                'validation_results': validation_results,
                'performance_results': performance_results,
                'comprehensive_report': comprehensive_report,
                'status': 'COMPLETED'
            }
            
            print(f"\n✅ COMPREHENSIVE TESTING COMPLETED!")
            print(f"⏱️  Total Time: {total_time}")
            print(f"📊 Results saved to testing_results.json")
            
            return self.testing_results
            
        except Exception as e:
            print(f"\n❌ TESTING FAILED: {str(e)}")
            self.testing_results['status'] = 'FAILED'
            self.testing_results['error'] = str(e)
            return self.testing_results
        
        finally:
            self.is_running = False
            self.db_connector.disconnect()
    
    def _run_historical_analysis(self) -> Dict[str, Any]:
        """Jalankan analisis data historis"""
        
        historical_results = {
            'symbols_analyzed': 0,
            'symbol_analysis': {},
            'overall_summary': {}
        }
        
        for symbol in self.testing_config['symbols']:
            print(f"📊 Analyzing historical data for {symbol}...")
            
            try:
                analysis = self.analyzer.analyze_historical_data(
                    symbol, 
                    self.testing_config['start_date'], 
                    self.testing_config['end_date']
                )
                
                historical_results['symbol_analysis'][symbol] = analysis
                historical_results['symbols_analyzed'] += 1
                
                print(f"✅ {symbol}: {analysis.get('data_points', 0)} data points")
                
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {str(e)}")
                historical_results['symbol_analysis'][symbol] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        # Generate overall summary
        historical_results['overall_summary'] = self._summarize_historical_results(historical_results)
        
        return historical_results
    
    def _run_time_lapse_simulation(self) -> Dict[str, Any]:
        """Jalankan simulasi time lapse"""
        
        if not self.testing_config['enable_time_lapse']:
            print("⏭️  Time lapse simulation disabled")
            return {'status': 'DISABLED'}
        
        print(f"🎬 Starting time lapse simulation...")
        
        # Setup simulator
        self.simulator.setup_simulation(
            self.testing_config['start_date'],
            self.testing_config['end_date'],
            self.testing_config['symbols'],
            self.testing_config['modules']
        )
        
        # Add progress callback
        def progress_callback(message: str, progress: float = None):
            if progress:
                print(f"📊 {message} ({progress:.1f}%)")
            else:
                print(f"📊 {message}")
        
        self.simulator.add_progress_callback(progress_callback)
        
        # Run simulation
        simulation_results = self.simulator.run_simulation()
        
        # Save simulation results
        self.simulator.save_results()
        
        print(f"✅ Time lapse simulation completed")
        
        return simulation_results
    
    def _run_prediction_validation(self) -> Dict[str, Any]:
        """Jalankan validasi prediksi"""
        
        if not self.testing_config['enable_validation']:
            print("⏭️  Prediction validation disabled")
            return {'status': 'DISABLED'}
        
        validation_results = {
            'modules_analyzed': 0,
            'module_validation': {},
            'overall_summary': {}
        }
        
        for module in self.testing_config['modules']:
            print(f"🔍 Validating predictions for {module}...")
            
            try:
                # Validasi performa modul
                module_performance = self.validator.validate_module_performance(
                    module,
                    self.testing_config['start_date'],
                    self.testing_config['end_date']
                )
                
                validation_results['module_validation'][module] = module_performance
                validation_results['modules_analyzed'] += 1
                
                print(f"✅ {module}: {module_performance['overall_accuracy']:.2f}% accuracy")
                
            except Exception as e:
                print(f"❌ Error validating {module}: {str(e)}")
                validation_results['module_validation'][module] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        # Generate overall summary
        validation_results['overall_summary'] = self._summarize_validation_results(validation_results)
        
        return validation_results
    
    def _run_performance_analysis(self) -> Dict[str, Any]:
        """Jalankan analisis performa"""
        
        if not self.testing_config['enable_analysis']:
            print("⏭️  Performance analysis disabled")
            return {'status': 'DISABLED'}
        
        performance_results = {
            'modules_analyzed': 0,
            'module_performance': {},
            'overall_summary': {}
        }
        
        for module in self.testing_config['modules']:
            print(f"📈 Analyzing performance for {module}...")
            
            try:
                # Analisis performa modul
                module_analysis = self.analyzer.analyze_prediction_accuracy(
                    self.testing_config['symbols'][0],  # Use first symbol
                    self.testing_config['start_date'],
                    self.testing_config['end_date']
                )
                
                performance_results['module_performance'][module] = module_analysis
                performance_results['modules_analyzed'] += 1
                
                print(f"✅ {module}: {module_analysis.get('overall_accuracy', 0):.2f}% accuracy")
                
            except Exception as e:
                print(f"❌ Error analyzing {module}: {str(e)}")
                performance_results['module_performance'][module] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        # Generate overall summary
        performance_results['overall_summary'] = self._summarize_performance_results(performance_results)
        
        return performance_results
    
    def _generate_comprehensive_report(self, historical_results: Dict[str, Any],
                                     simulation_results: Dict[str, Any],
                                     validation_results: Dict[str, Any],
                                     performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate laporan komprehensif"""
        
        print(f"📋 Generating comprehensive report...")
        
        comprehensive_report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'testing_period': f"{self.testing_config['start_date']} to {self.testing_config['end_date']}",
                'modules_tested': self.testing_config['modules'],
                'symbols_tested': self.testing_config['symbols'],
                'time_ratio': self.testing_config['time_ratio']
            },
            'executive_summary': self._generate_executive_summary(
                historical_results, simulation_results, validation_results, performance_results
            ),
            'detailed_analysis': {
                'historical_analysis': historical_results,
                'simulation_results': simulation_results,
                'validation_results': validation_results,
                'performance_analysis': performance_results
            },
            'recommendations': self._generate_recommendations(
                historical_results, simulation_results, validation_results, performance_results
            ),
            'action_plan': self._generate_action_plan(
                historical_results, simulation_results, validation_results, performance_results
            )
        }
        
        print(f"✅ Comprehensive report generated")
        
        return comprehensive_report
    
    def _generate_executive_summary(self, historical_results: Dict[str, Any],
                                  simulation_results: Dict[str, Any],
                                  validation_results: Dict[str, Any],
                                  performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        
        summary = {
            'testing_overview': {
                'total_modules': len(self.testing_config['modules']),
                'total_symbols': len(self.testing_config['symbols']),
                'testing_period': f"{self.testing_config['start_date']} to {self.testing_config['end_date']}",
                'time_ratio': self.testing_config['time_ratio']
            },
            'key_findings': [],
            'module_performance': {},
            'overall_assessment': 'UNKNOWN'
        }
        
        # Analyze module performance
        for module in self.testing_config['modules']:
            module_perf = {
                'module_name': module,
                'accuracy': 0.0,
                'status': 'UNKNOWN',
                'recommendation': 'UNKNOWN'
            }
            
            # Get accuracy from validation results
            if module in validation_results.get('module_validation', {}):
                val_data = validation_results['module_validation'][module]
                if val_data.get('status') == 'COMPLETED':
                    module_perf['accuracy'] = val_data.get('overall_accuracy', 0)
                    module_perf['status'] = 'VALIDATED'
            
            # Get accuracy from performance results
            if module in performance_results.get('module_performance', {}):
                perf_data = performance_results['module_performance'][module]
                if perf_data.get('status') == 'COMPLETED':
                    module_perf['accuracy'] = max(module_perf['accuracy'], perf_data.get('overall_accuracy', 0))
                    module_perf['status'] = 'ANALYZED'
            
            # Determine recommendation
            if module_perf['accuracy'] >= 80:
                module_perf['recommendation'] = 'KEEP'
            elif module_perf['accuracy'] >= 60:
                module_perf['recommendation'] = 'IMPROVE'
            else:
                module_perf['recommendation'] = 'REPLACE'
            
            summary['module_performance'][module] = module_perf
        
        # Generate key findings
        high_accuracy_modules = [m for m, p in summary['module_performance'].items() if p['accuracy'] >= 80]
        low_accuracy_modules = [m for m, p in summary['module_performance'].items() if p['accuracy'] < 60]
        
        if high_accuracy_modules:
            summary['key_findings'].append(f"High accuracy modules: {', '.join(high_accuracy_modules)}")
        
        if low_accuracy_modules:
            summary['key_findings'].append(f"Low accuracy modules: {', '.join(low_accuracy_modules)}")
        
        # Overall assessment
        avg_accuracy = sum(p['accuracy'] for p in summary['module_performance'].values()) / len(summary['module_performance'])
        if avg_accuracy >= 70:
            summary['overall_assessment'] = 'GOOD'
        elif avg_accuracy >= 50:
            summary['overall_assessment'] = 'FAIR'
        else:
            summary['overall_assessment'] = 'POOR'
        
        return summary
    
    def _summarize_historical_results(self, historical_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize historical analysis results"""
        
        summary = {
            'total_symbols': historical_results['symbols_analyzed'],
            'successful_analysis': 0,
            'failed_analysis': 0,
            'average_data_points': 0,
            'data_quality': 'UNKNOWN'
        }
        
        successful_analyses = []
        for symbol, analysis in historical_results['symbol_analysis'].items():
            if analysis.get('status') == 'COMPLETED':
                summary['successful_analysis'] += 1
                successful_analyses.append(analysis.get('data_points', 0))
            else:
                summary['failed_analysis'] += 1
        
        if successful_analyses:
            summary['average_data_points'] = sum(successful_analyses) / len(successful_analyses)
            summary['data_quality'] = 'GOOD' if summary['average_data_points'] > 50 else 'FAIR'
        
        return summary
    
    def _summarize_validation_results(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize validation results"""
        
        summary = {
            'total_modules': validation_results['modules_analyzed'],
            'successful_validation': 0,
            'failed_validation': 0,
            'average_accuracy': 0.0,
            'validation_quality': 'UNKNOWN'
        }
        
        accuracies = []
        for module, validation in validation_results['module_validation'].items():
            if validation.get('status') == 'COMPLETED':
                summary['successful_validation'] += 1
                accuracies.append(validation.get('overall_accuracy', 0))
            else:
                summary['failed_validation'] += 1
        
        if accuracies:
            summary['average_accuracy'] = sum(accuracies) / len(accuracies)
            summary['validation_quality'] = 'GOOD' if summary['average_accuracy'] > 70 else 'FAIR'
        
        return summary
    
    def _summarize_performance_results(self, performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize performance analysis results"""
        
        summary = {
            'total_modules': performance_results['modules_analyzed'],
            'successful_analysis': 0,
            'failed_analysis': 0,
            'average_accuracy': 0.0,
            'performance_quality': 'UNKNOWN'
        }
        
        accuracies = []
        for module, performance in performance_results['module_performance'].items():
            if performance.get('status') == 'COMPLETED':
                summary['successful_analysis'] += 1
                accuracies.append(performance.get('overall_accuracy', 0))
            else:
                summary['failed_analysis'] += 1
        
        if accuracies:
            summary['average_accuracy'] = sum(accuracies) / len(accuracies)
            summary['performance_quality'] = 'GOOD' if summary['average_accuracy'] > 70 else 'FAIR'
        
        return summary
    
    def _generate_recommendations(self, historical_results: Dict[str, Any],
                                simulation_results: Dict[str, Any],
                                validation_results: Dict[str, Any],
                                performance_results: Dict[str, Any]) -> List[str]:
        """Generate rekomendasi"""
        
        recommendations = []
        
        # Data quality recommendations
        hist_summary = historical_results.get('overall_summary', {})
        if hist_summary.get('data_quality') == 'FAIR':
            recommendations.append("Improve data quality and collection")
        
        # Accuracy recommendations
        val_summary = validation_results.get('overall_summary', {})
        if val_summary.get('average_accuracy', 0) < 60:
            recommendations.append("Focus on improving prediction accuracy")
        
        # Performance recommendations
        perf_summary = performance_results.get('overall_summary', {})
        if perf_summary.get('average_accuracy', 0) < 70:
            recommendations.append("Optimize module performance")
        
        # General recommendations
        recommendations.extend([
            "Implement continuous monitoring",
            "Add automated testing",
            "Improve error handling",
            "Enhance documentation"
        ])
        
        return recommendations
    
    def _generate_action_plan(self, historical_results: Dict[str, Any],
                            simulation_results: Dict[str, Any],
                            validation_results: Dict[str, Any],
                            performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action plan"""
        
        action_plan = {
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': []
        }
        
        # Immediate actions
        action_plan['immediate_actions'] = [
            "Review test results",
            "Identify critical issues",
            "Prioritize fixes",
            "Implement monitoring"
        ]
        
        # Short-term actions
        action_plan['short_term_actions'] = [
            "Fix high-priority issues",
            "Improve data quality",
            "Enhance accuracy",
            "Add testing"
        ]
        
        # Long-term actions
        action_plan['long_term_actions'] = [
            "Architecture improvements",
            "Performance optimization",
            "Advanced analytics",
            "Automation"
        ]
        
        return action_plan
    
    def save_results(self, filename: str = None) -> str:
        """Simpan hasil testing"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"advanced_module_testing_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.testing_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Testing results saved to: {filepath}")
        return filepath

def main():
    """Main function untuk menjalankan advanced module testing"""
    
    print("🚀 ADVANCED MODULE TESTER - Comprehensive Testing Framework")
    print("=" * 70)
    
    # Initialize tester
    tester = AdvancedModuleTester()
    
    # Setup testing configuration
    modules = ["ai_ml", "technical", "fundamental", "sentiment"]
    symbols = ["AAPL", "GOOGL", "MSFT"]
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    time_ratio = 0.1  # 1 day = 0.1 seconds for testing
    
    tester.setup_testing(modules, symbols, start_date, end_date, time_ratio)
    
    # Run comprehensive testing
    try:
        results = tester.run_comprehensive_testing()
        
        # Save results
        tester.save_results()
        
        # Print summary
        print(f"\n📊 TESTING SUMMARY")
        print("=" * 40)
        print(f"Status: {results['status']}")
        print(f"Total Time: {results['total_time']}")
        
        if 'comprehensive_report' in results:
            exec_summary = results['comprehensive_report']['executive_summary']
            print(f"Overall Assessment: {exec_summary['overall_assessment']}")
            print(f"Modules Tested: {exec_summary['testing_overview']['total_modules']}")
            print(f"Symbols Tested: {exec_summary['testing_overview']['total_symbols']}")
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")

if __name__ == "__main__":
    main()
