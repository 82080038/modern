"""
Web Interface untuk Model Evaluation System
Web interface yang terhubung langsung dengan Python tanpa API
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
from model_monitor import ModelEvaluator, ModelPerformance

class ModelEvaluationWebApp:
    """Web application untuk model evaluation"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'model_evaluation_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.evaluator = ModelEvaluator()
        self.setup_routes()
        self.setup_socketio()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard"""
            return render_template('model_dashboard.html')
        
        @self.app.route('/favicon.ico')
        def favicon():
            """Favicon handler"""
            return '', 204  # No content
        
        @self.app.route('/api/models')
        def get_models():
            """Get all models data"""
            return jsonify(self.evaluator.get_model_summary())
        
        @self.app.route('/api/data-flow')
        def get_data_flow():
            """Get data flow information"""
            return jsonify(self.evaluator.get_data_flow_summary())
        
        @self.app.route('/api/model/<model_id>')
        def get_model_details(model_id):
            """Get specific model details"""
            if model_id in self.evaluator.models:
                model = self.evaluator.models[model_id]
                return jsonify({
                    'model_id': model.model_id,
                    'model_name': model.model_name,
                    'accuracy': model.accuracy,
                    'precision': model.precision,
                    'recall': model.recall,
                    'f1_score': model.f1_score,
                    'profit_loss': model.profit_loss,
                    'win_rate': model.win_rate,
                    'max_drawdown': model.max_drawdown,
                    'sharpe_ratio': model.sharpe_ratio,
                    'status': model.status,
                    'recommendations': model.recommendations,
                    'last_updated': model.last_updated.isoformat()
                })
            return jsonify({'error': 'Model not found'}), 404
        
        @self.app.route('/api/add-model', methods=['POST'])
        def add_model():
            """Add new model"""
            data = request.get_json()
            model_id = data.get('model_id')
            model_name = data.get('model_name')
            initial_performance = data.get('initial_performance', {})
            
            if not model_id or not model_name:
                return jsonify({'error': 'Model ID and name required'}), 400
            
            self.evaluator.add_model(model_id, model_name, initial_performance)
            return jsonify({'success': True, 'message': 'Model added successfully'})
        
        @self.app.route('/api/update-model/<model_id>', methods=['POST'])
        def update_model(model_id):
            """Update model performance"""
            data = request.get_json()
            new_performance = data.get('performance', {})
            
            if model_id not in self.evaluator.models:
                return jsonify({'error': 'Model not found'}), 404
            
            self.evaluator.update_model_performance(model_id, new_performance)
            return jsonify({'success': True, 'message': 'Model updated successfully'})
        
        @self.app.route('/api/start-monitoring', methods=['POST'])
        def start_monitoring():
            """Start model monitoring"""
            self.evaluator.start_monitoring()
            return jsonify({'success': True, 'message': 'Monitoring started'})
        
        @self.app.route('/api/stop-monitoring', methods=['POST'])
        def stop_monitoring():
            """Stop model monitoring"""
            self.evaluator.stop_monitoring()
            return jsonify({'success': True, 'message': 'Monitoring stopped'})
    
    def setup_socketio(self):
        """Setup SocketIO for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            print(f"Client connected: {request.sid}")
            emit('status', {'message': 'Connected to model evaluation system'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('request_model_data')
        def handle_model_data_request():
            """Handle model data request"""
            model_summary = self.evaluator.get_model_summary()
            emit('model_data', model_summary)
        
        @self.socketio.on('request_data_flow')
        def handle_data_flow_request():
            """Handle data flow request"""
            data_flow = self.evaluator.get_data_flow_summary()
            emit('data_flow', data_flow)
    
    def start_real_time_updates(self):
        """Start real-time updates thread"""
        def update_loop():
            while True:
                try:
                    # Send model updates
                    model_summary = self.evaluator.get_model_summary()
                    self.socketio.emit('model_update', model_summary)
                    
                    # Send data flow updates
                    data_flow = self.evaluator.get_data_flow_summary()
                    self.socketio.emit('data_flow_update', data_flow)
                    
                    time.sleep(5)  # Update setiap 5 detik
                except Exception as e:
                    print(f"Error in update loop: {e}")
                    time.sleep(10)
        
        update_thread = threading.Thread(target=update_loop)
        update_thread.daemon = True
        update_thread.start()
    
    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Run the web application"""
        # Start real-time updates
        self.start_real_time_updates()
        
        # Start the app
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# Global app instance
app_instance = None

def create_app():
    """Create and return the app instance"""
    global app_instance
    if app_instance is None:
        app_instance = ModelEvaluationWebApp()
    return app_instance

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
