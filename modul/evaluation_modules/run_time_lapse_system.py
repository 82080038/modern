"""
Main runner untuk Time Lapse Model Simulator
Menjalankan sistem simulasi time-lapse dengan web interface
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from time_lapse_simulator import TimeLapseSimulator
from time_lapse_web_interface import TimeLapseWebApp

class TimeLapseSystem:
    """Main system untuk time lapse simulation"""
    
    def __init__(self):
        self.simulator = TimeLapseSimulator()
        self.web_app = TimeLapseWebApp()
        self.running = False
        
    def run_demo_simulation(self):
        """Run demo simulation untuk testing"""
        print("="*60)
        print("TIME LAPSE MODEL SIMULATOR - DEMO")
        print("="*60)
        print("Running demo simulation...")
        print("1 day = 2 seconds")
        print("Simulating 7 days...")
        print("="*60)
        
        # Run 7-day simulation
        start_date = datetime(2024, 1, 1)
        self.simulator.run_time_lapse_simulation(start_date, 7)
        
        print("\nDemo simulation completed!")
        print("Web interface available at: http://localhost:5001")
    
    def run_web_interface(self):
        """Run web interface untuk time lapse simulator"""
        print("="*60)
        print("TIME LAPSE MODEL SIMULATOR - WEB INTERFACE")
        print("="*60)
        print("Starting web interface...")
        print("Dashboard available at: http://localhost:5001")
        print("Press Ctrl+C to stop")
        print("="*60)
        
        try:
            self.web_app.run(host='0.0.0.0', port=5001, debug=False)
        except KeyboardInterrupt:
            print("\nStopping Time Lapse Simulator...")
            print("System stopped successfully")
        except Exception as e:
            print(f"Error running system: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        # Run demo simulation
        system = TimeLapseSystem()
        system.run_demo_simulation()
    else:
        # Run web interface
        system = TimeLapseSystem()
        system.run_web_interface()

if __name__ == '__main__':
    main()
