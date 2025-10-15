"""
Model Monitoring System
Sistem monitoring performa model real-time
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
import sqlite3
import threading
from pathlib import Path

@dataclass
class ModelPerformance:
    """Data class untuk menyimpan performa model"""
    model_id: str
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    profit_loss: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    last_updated: datetime
    status: str  # 'active', 'tuning', 'replaced', 'maintained'
    recommendations: List[str]

class ModelEvaluator:
    """Kelas utama untuk evaluasi model"""
    
    def __init__(self, db_path: str = "model_evaluation/models.db"):
        self.db_path = db_path
        self.models = {}
        self.performance_history = []
        self.setup_database()
        self.monitoring_active = False
        
    def setup_database(self):
        """Setup database untuk menyimpan data model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel untuk model performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                profit_loss REAL,
                win_rate REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                status TEXT,
                recommendations TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk model decisions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk data flow tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_flow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_module TEXT NOT NULL,
                target_module TEXT NOT NULL,
                data_type TEXT NOT NULL,
                status TEXT,
                processing_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_model(self, model_id: str, model_name: str, initial_performance: Dict[str, float]):
        """Tambahkan model baru ke sistem monitoring"""
        performance = ModelPerformance(
            model_id=model_id,
            model_name=model_name,
            accuracy=initial_performance.get('accuracy', 0.0),
            precision=initial_performance.get('precision', 0.0),
            recall=initial_performance.get('recall', 0.0),
            f1_score=initial_performance.get('f1_score', 0.0),
            profit_loss=initial_performance.get('profit_loss', 0.0),
            win_rate=initial_performance.get('win_rate', 0.0),
            max_drawdown=initial_performance.get('max_drawdown', 0.0),
            sharpe_ratio=initial_performance.get('sharpe_ratio', 0.0),
            last_updated=datetime.now(),
            status='active',
            recommendations=[]
        )
        
        self.models[model_id] = performance
        self.save_performance_to_db(performance)
        
    def update_model_performance(self, model_id: str, new_performance: Dict[str, float]):
        """Update performa model"""
        if model_id in self.models:
            model = self.models[model_id]
            
            # Update metrics
            model.accuracy = new_performance.get('accuracy', model.accuracy)
            model.precision = new_performance.get('precision', model.precision)
            model.recall = new_performance.get('recall', model.recall)
            model.f1_score = new_performance.get('f1_score', model.f1_score)
            model.profit_loss = new_performance.get('profit_loss', model.profit_loss)
            model.win_rate = new_performance.get('win_rate', model.win_rate)
            model.max_drawdown = new_performance.get('max_drawdown', model.max_drawdown)
            model.sharpe_ratio = new_performance.get('sharpe_ratio', model.sharpe_ratio)
            model.last_updated = datetime.now()
            
            # Generate recommendations
            model.recommendations = self.generate_recommendations(model)
            
            # Update status based on performance
            model.status = self.determine_model_status(model)
            
            self.save_performance_to_db(model)
            
    def generate_recommendations(self, model: ModelPerformance) -> List[str]:
        """Generate rekomendasi berdasarkan performa model"""
        recommendations = []
        
        # Accuracy recommendations
        if model.accuracy < 0.6:
            recommendations.append("Accuracy rendah - pertimbangkan tuning atau replacement")
        elif model.accuracy > 0.8:
            recommendations.append("Accuracy baik - pertahankan model")
            
        # Profit/Loss recommendations
        if model.profit_loss < -0.1:
            recommendations.append("Loss tinggi - segera evaluasi dan pertimbangkan stop")
        elif model.profit_loss > 0.2:
            recommendations.append("Profit baik - pertahankan dan monitor")
            
        # Sharpe ratio recommendations
        if model.sharpe_ratio < 1.0:
            recommendations.append("Sharpe ratio rendah - pertimbangkan optimasi")
        elif model.sharpe_ratio > 2.0:
            recommendations.append("Sharpe ratio excellent - pertahankan")
            
        # Win rate recommendations
        if model.win_rate < 0.4:
            recommendations.append("Win rate rendah - model perlu improvement")
        elif model.win_rate > 0.7:
            recommendations.append("Win rate tinggi - performa bagus")
            
        return recommendations
    
    def determine_model_status(self, model: ModelPerformance) -> str:
        """Tentukan status model berdasarkan performa"""
        if model.accuracy < 0.5 or model.profit_loss < -0.2:
            return "replaced"
        elif model.accuracy < 0.7 or model.profit_loss < -0.1:
            return "tuning"
        else:
            return "maintained"
    
    def save_performance_to_db(self, model: ModelPerformance):
        """Simpan performa model ke database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_performance 
            (model_id, model_name, accuracy, precision, recall, f1_score, 
             profit_loss, win_rate, max_drawdown, sharpe_ratio, status, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model.model_id, model.model_name, model.accuracy, model.precision,
            model.recall, model.f1_score, model.profit_loss, model.win_rate,
            model.max_drawdown, model.sharpe_ratio, model.status,
            json.dumps(model.recommendations)
        ))
        
        conn.commit()
        conn.close()
    
    def track_data_flow(self, source_module: str, target_module: str, 
                       data_type: str, status: str, processing_time: float):
        """Track data flow antar modul"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_flow (source_module, target_module, data_type, status, processing_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_module, target_module, data_type, status, processing_time))
        
        conn.commit()
        conn.close()
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Dapatkan ringkasan semua model"""
        summary = {
            'total_models': len(self.models),
            'active_models': len([m for m in self.models.values() if m.status == 'active']),
            'tuning_models': len([m for m in self.models.values() if m.status == 'tuning']),
            'replaced_models': len([m for m in self.models.values() if m.status == 'replaced']),
            'maintained_models': len([m for m in self.models.values() if m.status == 'maintained']),
            'models': []
        }
        
        for model in self.models.values():
            summary['models'].append({
                'model_id': model.model_id,
                'model_name': model.model_name,
                'accuracy': model.accuracy,
                'profit_loss': model.profit_loss,
                'status': model.status,
                'recommendations': model.recommendations,
                'last_updated': model.last_updated.isoformat()
            })
            
        return summary
    
    def get_data_flow_summary(self) -> Dict[str, Any]:
        """Dapatkan ringkasan data flow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent data flow
        cursor.execute('''
            SELECT source_module, target_module, data_type, status, processing_time, timestamp
            FROM data_flow 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        
        flows = cursor.fetchall()
        conn.close()
        
        return {
            'total_flows': len(flows),
            'recent_flows': [
                {
                    'source': flow[0],
                    'target': flow[1],
                    'data_type': flow[2],
                    'status': flow[3],
                    'processing_time': flow[4],
                    'timestamp': flow[5]
                } for flow in flows
            ]
        }
    
    def start_monitoring(self):
        """Mulai monitoring real-time"""
        self.monitoring_active = True
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
    
    def _monitoring_loop(self):
        """Loop monitoring real-time"""
        while self.monitoring_active:
            # Simulate model performance updates
            for model_id in self.models:
                # Simulate performance changes
                performance_change = np.random.normal(0, 0.05)
                current_performance = {
                    'accuracy': max(0, min(1, self.models[model_id].accuracy + performance_change)),
                    'profit_loss': self.models[model_id].profit_loss + np.random.normal(0, 0.02),
                    'win_rate': max(0, min(1, self.models[model_id].win_rate + np.random.normal(0, 0.03)))
                }
                
                self.update_model_performance(model_id, current_performance)
            
            time.sleep(30)  # Update setiap 30 detik
