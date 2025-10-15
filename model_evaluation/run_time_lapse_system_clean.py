"""
Clean Time Lapse System Runner
Sistem yang tidak berjalan otomatis dan hanya update ketika simulasi aktif
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from time_lapse_web_interface import create_app

if __name__ == '__main__':
    print("Starting Time Lapse Simulator...")
    print("System will NOT run simulation automatically")
    print("Use the web interface to start simulation manually")
    print("Web interface: http://localhost:5001")
    print("Press Ctrl+C to stop")
    
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=False)
