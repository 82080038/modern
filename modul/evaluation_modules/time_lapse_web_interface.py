"""
Web Interface untuk Time Lapse Simulator
Visualisasi real-time flow modul dengan time-lapse
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
from time_lapse_simulator import TimeLapseSimulator, get_simulator

class TimeLapseWebApp:
    """Web application untuk time lapse simulator"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'time_lapse_simulator_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.simulator = get_simulator()
        self.simulation_running = False
        self.setup_routes()
        self.setup_socketio()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main time lapse dashboard"""
            return render_template('time_lapse_dashboard.html')
        
        @self.app.route('/api/modules')
        def get_modules():
            """Get all modules information"""
            return jsonify(self.simulator.modules)
        
        @self.app.route('/api/sessions')
        def get_sessions():
            """Get all trading sessions"""
            sessions_data = []
            for session in self.simulator.sessions:
                sessions_data.append({
                    'session_id': session.session_id,
                    'date': session.date.isoformat(),
                    'overall_performance': session.overall_performance,
                    'recommendations': session.recommendations,
                    'modules_count': len(session.modules_status)
                })
            return jsonify(sessions_data)
        
        @self.app.route('/api/session/<session_id>')
        def get_session_details(session_id):
            """Get specific session details"""
            for session in self.simulator.sessions:
                if session.session_id == session_id:
                    modules_data = {}
                    for module_name, status in session.modules_status.items():
                        modules_data[module_name] = {
                            'name': self.simulator.modules[module_name]['name'],
                            'status': status.status,
                            'start_time': status.start_time.isoformat(),
                            'end_time': status.end_time.isoformat() if status.end_time else None,
                            'processing_time': status.processing_time,
                            'performance_metrics': status.performance_metrics,
                            'error_message': status.error_message
                        }
                    
                    # Convert trading decisions to dict
                    trading_decisions = []
                    for decision in session.trading_decisions:
                        trading_decisions.append({
                            'symbol': decision.symbol,
                            'action': decision.action,
                            'quantity': decision.quantity,
                            'price': decision.price,
                            'timestamp': decision.timestamp.isoformat(),
                            'reason': decision.reason,
                            'confidence': decision.confidence
                        })
                    
                    # Convert trading history to dict
                    trading_history = {
                        'total_capital': session.trading_history.total_capital,
                        'current_capital': session.trading_history.current_capital,
                        'total_pnl': session.trading_history.total_pnl,
                        'daily_pnl': session.trading_history.daily_pnl,
                        'win_rate': session.trading_history.win_rate,
                        'total_trades': session.trading_history.total_trades,
                        'winning_trades': session.trading_history.winning_trades,
                        'losing_trades': session.trading_history.losing_trades
                    }
                    
                    return jsonify({
                        'session_id': session.session_id,
                        'date': session.date.isoformat(),
                        'overall_performance': session.overall_performance,
                        'recommendations': session.recommendations,
                        'modules': modules_data,
                        'trading_decisions': trading_decisions,
                        'trading_history': trading_history
                    })
            return jsonify({'error': 'Session not found'}), 404
        
        @self.app.route('/api/start-simulation', methods=['POST'])
        def start_simulation():
            """Start time lapse simulation"""
            data = request.get_json()
            start_date_str = data.get('start_date', '2024-01-01')
            days = data.get('days', 30)
            time_multiplier = data.get('time_multiplier', 2)
            
            try:
                start_date = datetime.fromisoformat(start_date_str)
                
                # Set simulation parameters
                self.simulator.simulation_running = True
                self.simulator.time_multiplier = time_multiplier
                
                print(f"Starting simulation with:")
                print(f"  Start Date: {start_date_str}")
                print(f"  Days: {days}")
                print(f"  Time Multiplier: {time_multiplier}")
                
                # Start simulation in background thread
                def run_simulation():
                    try:
                        self.simulator.run_time_lapse_simulation(start_date, days)
                    except Exception as e:
                        print(f"Simulation error: {e}")
                    finally:
                        self.simulator.simulation_running = False
                
                simulation_thread = threading.Thread(target=run_simulation)
                simulation_thread.daemon = True
                simulation_thread.start()
                
                return jsonify({'success': True, 'message': 'Simulation started'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400
        
        @self.app.route('/api/stop-simulation', methods=['POST'])
        def stop_simulation():
            """Stop time lapse simulation"""
            self.simulator.simulation_running = False
            return jsonify({'success': True, 'message': 'Simulation stopped'})
        
        @self.app.route('/favicon.ico')
        def favicon():
            """Favicon handler"""
            return '', 204  # No content
        
        @self.app.route('/api/simulation-status')
        def get_simulation_status():
            """Get current simulation status"""
            return jsonify({
                'running': self.simulator.simulation_running,
                'sessions_count': len(self.simulator.sessions),
                'current_session': self.simulator.current_session.session_id if self.simulator.current_session else None,
                'start_date': self.simulator.start_date.isoformat() if self.simulator.start_date else None,
                'end_date': self.simulator.end_date.isoformat() if self.simulator.end_date else None,
                'current_date': self.simulator.current_date.isoformat() if self.simulator.current_date else None,
                'initial_capital': self.simulator.initial_capital,
                'current_capital': self.simulator.current_capital,
                'total_pnl': self.simulator.total_pnl
            })
        
        @self.app.route('/api/trading-history')
        def get_trading_history():
            """Get complete trading history"""
            all_trades = []
            for session in self.simulator.sessions:
                for decision in session.trading_decisions:
                    all_trades.append({
                        'session_id': session.session_id,
                        'date': session.date.isoformat(),
                        'symbol': decision.symbol,
                        'action': decision.action,
                        'quantity': decision.quantity,
                        'price': decision.price,
                        'timestamp': decision.timestamp.isoformat(),
                        'reason': decision.reason,
                        'confidence': decision.confidence
                    })
            
            return jsonify({
                'trades': all_trades,
                'total_trades': len(all_trades),
                'initial_capital': self.simulator.initial_capital,
                'current_capital': self.simulator.current_capital,
                'total_pnl': self.simulator.total_pnl,
                'return_percentage': (self.simulator.total_pnl / self.simulator.initial_capital * 100) if self.simulator.initial_capital > 0 else 0
            })
    
    def setup_socketio(self):
        """Setup SocketIO for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            # print(f"Client connected to time lapse simulator: {request.sid}")
            emit('status', {'message': 'Connected to time lapse simulator'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            # print(f"Client disconnected from time lapse simulator: {request.sid}")
            pass
        
        @self.socketio.on('request_modules')
        def handle_modules_request():
            """Handle modules data request"""
            emit('modules_data', self.simulator.modules)
        
        @self.socketio.on('request_sessions')
        def handle_sessions_request():
            """Handle sessions data request"""
            sessions_data = []
            for session in self.simulator.sessions:
                sessions_data.append({
                    'session_id': session.session_id,
                    'date': session.date.isoformat(),
                    'overall_performance': session.overall_performance,
                    'recommendations': session.recommendations,
                    'modules_count': len(session.modules_status)
                })
            emit('sessions_data', sessions_data)
    
    def start_real_time_updates(self):
        """Start real-time updates thread"""
        def update_loop():
            while True:
                try:
                    # Only send updates if simulation is running
                    if self.simulator.simulation_running:
                        # Send simulation status updates
                        status = {
                            'running': True,
                            'sessions_count': len(self.simulator.sessions),
                            'current_session': self.simulator.current_session.session_id if self.simulator.current_session else None,
                            'start_date': self.simulator.start_date.isoformat() if self.simulator.start_date else None,
                            'end_date': self.simulator.end_date.isoformat() if self.simulator.end_date else None,
                            'current_date': self.simulator.current_date.isoformat() if self.simulator.current_date else None,
                            'initial_capital': self.simulator.initial_capital,
                            'current_capital': self.simulator.current_capital,
                            'total_pnl': self.simulator.total_pnl
                        }
                        self.socketio.emit('simulation_update', status)
                        
                        # Send sessions updates only if there are new sessions
                        if self.simulator.sessions:
                            latest_session = self.simulator.sessions[-1]
                            session_data = {
                                'session_id': latest_session.session_id,
                                'date': latest_session.date.isoformat(),
                                'overall_performance': latest_session.overall_performance,
                                'recommendations': latest_session.recommendations,
                                'trading_decisions': [
                                    {
                                        'symbol': decision.symbol,
                                        'action': decision.action,
                                        'quantity': decision.quantity,
                                        'price': decision.price,
                                        'timestamp': decision.timestamp.isoformat(),
                                        'reason': decision.reason,
                                        'confidence': decision.confidence
                                    } for decision in latest_session.trading_decisions
                                ],
                                'trading_history': {
                                    'total_capital': latest_session.trading_history.total_capital,
                                    'current_capital': latest_session.trading_history.current_capital,
                                    'total_pnl': latest_session.trading_history.total_pnl,
                                    'daily_pnl': latest_session.trading_history.daily_pnl,
                                    'win_rate': latest_session.trading_history.win_rate,
                                    'total_trades': latest_session.trading_history.total_trades,
                                    'winning_trades': latest_session.trading_history.winning_trades,
                                    'losing_trades': latest_session.trading_history.losing_trades
                                },
                                'modules': {}
                            }
                            
                            for module_name, status in latest_session.modules_status.items():
                                session_data['modules'][module_name] = {
                                    'name': self.simulator.modules[module_name]['name'],
                                    'status': status.status,
                                    'performance_metrics': status.performance_metrics,
                                    'processing_time': status.processing_time
                                }
                            
                            self.socketio.emit('session_update', session_data)
                    
                    time.sleep(10)  # Update setiap 10 detik (lebih lambat)
                    
                except Exception as e:
                    print(f"Error in time lapse update loop: {e}")
                    time.sleep(10)
        
        update_thread = threading.Thread(target=update_loop)
        update_thread.daemon = True
        update_thread.start()
    
    def run(self, host='0.0.0.0', port=5001, debug=True):
        """Run the time lapse web application"""
        # Start real-time updates
        self.start_real_time_updates()
        
        # Start the app
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# Global app instance
app_instance = None

def create_app():
    """Create and return the time lapse app instance"""
    global app_instance
    if app_instance is None:
        app_instance = TimeLapseWebApp()
    return app_instance

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
