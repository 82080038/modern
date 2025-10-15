"""
Test script untuk memverifikasi tombol stop berfungsi
"""

import time
import requests
import threading
from time_lapse_simulator import get_simulator

def test_stop_functionality():
    """Test apakah tombol stop berfungsi dengan baik"""
    print("Testing Stop Button Functionality...")
    
    # Get simulator instance
    simulator = get_simulator()
    
    # Start simulation in background
    def start_simulation():
        print("Starting simulation...")
        simulator.run_time_lapse_simulation('2024-01-01', 10)  # 10 days
    
    # Start simulation thread
    sim_thread = threading.Thread(target=start_simulation)
    sim_thread.daemon = True
    sim_thread.start()
    
    # Wait a bit for simulation to start
    time.sleep(2)
    
    # Check if simulation is running
    print(f"Simulation running: {simulator.simulation_running}")
    
    # Stop simulation
    print("Stopping simulation...")
    simulator.simulation_running = False
    
    # Wait a bit
    time.sleep(1)
    
    # Check if simulation stopped
    print(f"Simulation running after stop: {simulator.simulation_running}")
    
    # Test API endpoint
    try:
        response = requests.post('http://localhost:5001/api/stop-simulation')
        print(f"API Stop response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"API test failed: {e}")
    
    print("Stop button test completed!")

if __name__ == '__main__':
    test_stop_functionality()
