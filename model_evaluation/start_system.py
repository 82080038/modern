"""
Simple script to start the Model Evaluation System
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

def start_system():
    """Start the model evaluation system"""
    print("="*60)
    print("MODEL EVALUATION SYSTEM LAUNCHER")
    print("="*60)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "model_evaluation").exists():
        print("Error: Please run this script from the project root directory")
        print("Current directory:", current_dir)
        return False
    
    print("Starting Model Evaluation System...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the system")
    print("="*60)
    
    try:
        # Start the system
        os.chdir("model_evaluation")
        subprocess.run([sys.executable, "run_evaluation_system.py"])
    except KeyboardInterrupt:
        print("\nSystem stopped by user")
    except Exception as e:
        print(f"Error starting system: {e}")
        return False
    
    return True

if __name__ == '__main__':
    start_system()
