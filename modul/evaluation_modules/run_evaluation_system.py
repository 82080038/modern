"""
Main runner untuk Model Evaluation System
Menjalankan sistem evaluasi model dengan web interface
"""

import sys
import os
import time
import threading
from datetime import datetime
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_monitor import ModelEvaluator
from web_interface import ModelEvaluationWebApp
from data_integration import DataIntegrator, get_integrator

class ModelEvaluationSystem:
    """Main system untuk model evaluation"""
    
    def __init__(self):
        self.evaluator = ModelEvaluator()
        self.integrator = get_integrator()
        self.web_app = ModelEvaluationWebApp()
        self.running = False
        
    def initialize_test_models(self):
        """Initialize beberapa test model untuk demo"""
        print("Initializing test models...")
        
        # Add beberapa test models
        test_models = [
            {
                'model_id': 'technical_analysis_model',
                'model_name': 'Technical Analysis Model',
                'initial_performance': {
                    'accuracy': 0.75,
                    'precision': 0.72,
                    'recall': 0.78,
                    'f1_score': 0.75,
                    'profit_loss': 0.15,
                    'win_rate': 0.68,
                    'max_drawdown': 0.08,
                    'sharpe_ratio': 1.8
                }
            },
            {
                'model_id': 'fundamental_analysis_model',
                'model_name': 'Fundamental Analysis Model',
                'initial_performance': {
                    'accuracy': 0.82,
                    'precision': 0.85,
                    'recall': 0.79,
                    'f1_score': 0.82,
                    'profit_loss': 0.22,
                    'win_rate': 0.74,
                    'max_drawdown': 0.06,
                    'sharpe_ratio': 2.1
                }
            },
            {
                'model_id': 'sentiment_analysis_model',
                'model_name': 'Sentiment Analysis Model',
                'initial_performance': {
                    'accuracy': 0.68,
                    'precision': 0.65,
                    'recall': 0.71,
                    'f1_score': 0.68,
                    'profit_loss': 0.05,
                    'win_rate': 0.62,
                    'max_drawdown': 0.12,
                    'sharpe_ratio': 1.2
                }
            },
            {
                'model_id': 'ensemble_model',
                'model_name': 'Ensemble Model',
                'initial_performance': {
                    'accuracy': 0.88,
                    'precision': 0.86,
                    'recall': 0.90,
                    'f1_score': 0.88,
                    'profit_loss': 0.28,
                    'win_rate': 0.82,
                    'max_drawdown': 0.04,
                    'sharpe_ratio': 2.8
                }
            }
        ]
        
        for model_data in test_models:
            self.evaluator.add_model(
                model_data['model_id'],
                model_data['model_name'],
                model_data['initial_performance']
            )
            print(f"Added model: {model_data['model_name']}")
    
    def simulate_data_flows(self):
        """Simulate data flows antar modul"""
        print("Simulating data flows...")
        
        # Define module connections based on the documentation
        module_connections = [
            ('market_data', 'technical_analysis', 'price_data'),
            ('market_data', 'fundamental_analysis', 'price_data'),
            ('market_data', 'sentiment_analysis', 'price_data'),
            ('technical_analysis', 'strategy_builder', 'technical_signals'),
            ('fundamental_analysis', 'strategy_builder', 'fundamental_metrics'),
            ('sentiment_analysis', 'strategy_builder', 'sentiment_scores'),
            ('strategy_builder', 'algorithmic_trading', 'trading_strategy'),
            ('algorithmic_trading', 'risk_management', 'trade_signals'),
            ('risk_management', 'trading', 'risk_assessment'),
            ('trading', 'performance_analytics', 'trade_results'),
            ('performance_analytics', 'portfolio_heatmap', 'performance_metrics'),
            ('portfolio_heatmap', 'notifications', 'portfolio_alerts')
        ]
        
        for source, target, data_type in module_connections:
            # Simulate data flow
            flow_id = self.integrator.start_data_flow(source, target, data_type)
            
            # Simulate processing time
            processing_time = np.random.exponential(0.3)
            time.sleep(processing_time)
            
            # Simulate success/failure (95% success rate)
            success = np.random.random() > 0.05
            error_message = None if success else f"Error in {source} -> {target}"
            
            self.integrator.complete_data_flow(flow_id, success, error_message)
            print(f"Data flow: {source} -> {target} ({'SUCCESS' if success else 'FAILED'})")
    
    def start_model_monitoring(self):
        """Start model monitoring in background"""
        print("Starting model monitoring...")
        self.evaluator.start_monitoring()
        
        # Start data flow simulation in background
        def simulate_continuous_flows():
            while self.running:
                try:
                    # Simulate random data flows
                    modules = ['market_data', 'technical_analysis', 'fundamental_analysis', 
                             'sentiment_analysis', 'strategy_builder', 'algorithmic_trading',
                             'risk_management', 'trading', 'performance_analytics']
                    
                    source = np.random.choice(modules)
                    target = np.random.choice([m for m in modules if m != source])
                    data_type = np.random.choice(['price_data', 'signals', 'metrics', 'alerts'])
                    
                    flow_id = self.integrator.start_data_flow(source, target, data_type)
                    
                    # Simulate processing
                    processing_time = np.random.exponential(0.2)
                    time.sleep(processing_time)
                    
                    # Complete flow
                    success = np.random.random() > 0.1  # 90% success rate
                    error_message = None if success else f"Simulated error in {source} -> {target}"
                    self.integrator.complete_data_flow(flow_id, success, error_message)
                    
                    time.sleep(10)  # Wait 10 seconds between flows
                    
                except Exception as e:
                    print(f"Error in data flow simulation: {e}")
                    time.sleep(30)
        
        # Start simulation thread
        simulation_thread = threading.Thread(target=simulate_continuous_flows)
        simulation_thread.daemon = True
        simulation_thread.start()
    
    def print_system_status(self):
        """Print current system status"""
        print("\n" + "="*60)
        print("MODEL EVALUATION SYSTEM STATUS")
        print("="*60)
        
        # Model status
        model_summary = self.evaluator.get_model_summary()
        print(f"Models: {model_summary['total_models']} total")
        print(f"   - Active: {model_summary['active_models']}")
        print(f"   - Tuning: {model_summary['tuning_models']}")
        print(f"   - Replaced: {model_summary['replaced_models']}")
        print(f"   - Maintained: {model_summary['maintained_models']}")
        
        # Data flow status
        integration_status = self.integrator.get_integration_status()
        overall_status = integration_status['overall_status']
        print(f"\nData Flows: {overall_status['total_flows']} total")
        print(f"   - Success Rate: {overall_status['success_rate']:.1f}%")
        print(f"   - Avg Processing Time: {overall_status['avg_processing_time']:.3f}s")
        print(f"   - Active Flows: {integration_status['active_flows']}")
        
        # Module connections
        connections = integration_status['module_connections']
        if connections:
            print(f"\nTop Module Connections:")
            for conn in connections[:5]:  # Show top 5
                print(f"   - {conn['source']} -> {conn['target']}: {conn['connection_count']} flows")
        
        print("="*60)
    
    def run(self):
        """Run the complete system"""
        print("Starting Model Evaluation System...")
        
        try:
            # Initialize system
            self.initialize_test_models()
            self.simulate_data_flows()
            
            # Start monitoring
            self.running = True
            self.start_model_monitoring()
            
            # Print initial status
            self.print_system_status()
            
            print("\nStarting Web Interface...")
            print("Dashboard will be available at: http://localhost:5000")
            print("System is running... Press Ctrl+C to stop")
            
            # Start web interface
            self.web_app.run(host='0.0.0.0', port=5000, debug=False)
            
        except KeyboardInterrupt:
            print("\nStopping Model Evaluation System...")
            self.running = False
            self.evaluator.stop_monitoring()
            print("System stopped successfully")
            
        except Exception as e:
            print(f"Error running system: {e}")
            self.running = False

if __name__ == '__main__':
    # Create and run the system
    system = ModelEvaluationSystem()
    system.run()
