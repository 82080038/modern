"""
Test script untuk Model Evaluation System
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_monitor import ModelEvaluator
from data_integration import DataIntegrator

def test_model_evaluator():
    """Test model evaluator functionality"""
    print("Testing Model Evaluator...")
    
    evaluator = ModelEvaluator()
    
    # Add test model
    evaluator.add_model(
        model_id="test_model_1",
        model_name="Test Model 1",
        initial_performance={
            'accuracy': 0.75,
            'precision': 0.72,
            'recall': 0.78,
            'f1_score': 0.75,
            'profit_loss': 0.15,
            'win_rate': 0.68,
            'max_drawdown': 0.08,
            'sharpe_ratio': 1.8
        }
    )
    
    # Update performance
    evaluator.update_model_performance("test_model_1", {
        'accuracy': 0.80,
        'profit_loss': 0.20
    })
    
    # Get summary
    summary = evaluator.get_model_summary()
    print(f"Model Summary: {summary['total_models']} models")
    print(f"   - Active: {summary['active_models']}")
    print(f"   - Status: {summary['models'][0]['status']}")
    
    return True

def test_data_integrator():
    """Test data integrator functionality"""
    print("Testing Data Integrator...")
    
    integrator = DataIntegrator()
    
    # Test data flow
    flow_id = integrator.start_data_flow(
        source_module="market_data",
        target_module="technical_analysis",
        data_type="price_data",
        data_size=1000
    )
    
    print(f"Started data flow: {flow_id}")
    
    # Simulate processing
    time.sleep(0.1)
    
    # Complete flow
    flow = integrator.complete_data_flow(flow_id, success=True)
    print(f"Completed data flow: {flow.processing_time:.3f}s")
    
    # Get integration status
    status = integrator.get_integration_status()
    print(f"Integration Status: {status['overall_status']['total_flows']} flows")
    
    return True

def test_web_interface():
    """Test web interface (basic import)"""
    print("Testing Web Interface...")
    
    try:
        from web_interface import ModelEvaluationWebApp
        app = ModelEvaluationWebApp()
        print("Web Interface created successfully")
        return True
    except Exception as e:
        print(f"Web Interface error: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Model Evaluation System Tests...")
    print("="*60)
    
    tests = [
        ("Model Evaluator", test_model_evaluator),
        ("Data Integrator", test_data_integrator),
        ("Web Interface", test_web_interface)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning {test_name} test...")
            if test_func():
                print(f"{test_name} test PASSED")
                passed += 1
            else:
                print(f"{test_name} test FAILED")
        except Exception as e:
            print(f"{test_name} test ERROR: {e}")
    
    print("\n" + "="*60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests PASSED! System is ready to run.")
        print("\nTo start the full system, run:")
        print("   python run_evaluation_system.py")
        print("\nThen open: Request ID: 9cf48613-f294-4ebf-b501-c45cb4d2ad03
ConnectError: [aborted] read ECONNRESET
    at ZWl.$endAiConnectTransportReportError (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:7349:371721)
    at wMr._doInvokeHandler (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:489:35946)
    at wMr._invokeHandler (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:489:35688)
    at wMr._receiveRequest (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:489:34453)
    at wMr._receiveOneMessage (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:489:33275)
    at cEt.value (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:489:31369)
    at _e._deliver (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:49:2962)
    at _e.fire (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:49:3283)
    at ddt.fire (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:7334:12154)
    at MessagePort.<anonymous> (vscode-file://vscode-app/c:/Users/indon/AppData/Local/Programs/cursor/resources/app/out/vs/workbench/workbench.desktop.main.js:9402:18292)
    http://localhost:5000")
    else:
        print("Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    main()
