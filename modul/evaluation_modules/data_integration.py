"""
Data Integration System
Sistem integrasi data antar modul dengan tracking dan monitoring
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
import sqlite3
import threading
from pathlib import Path

@dataclass
class DataFlow:
    """Data class untuk tracking data flow"""
    source_module: str
    target_module: str
    data_type: str
    status: str
    processing_time: float
    timestamp: datetime
    data_size: int
    success: bool

class DataIntegrator:
    """Kelas utama untuk integrasi data antar modul"""
    
    def __init__(self, db_path: str = "data_integration.db"):
        self.db_path = db_path
        self.active_flows = {}
        self.flow_history = []
        self.setup_database()
        
    def setup_database(self):
        """Setup database untuk tracking data flow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel untuk data flow tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_module TEXT NOT NULL,
                target_module TEXT NOT NULL,
                data_type TEXT NOT NULL,
                status TEXT NOT NULL,
                processing_time REAL,
                data_size INTEGER,
                success BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        ''')
        
        # Tabel untuk module performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_name TEXT NOT NULL,
                total_requests INTEGER,
                successful_requests INTEGER,
                failed_requests INTEGER,
                avg_processing_time REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_data_flow(self, source_module: str, target_module: str, 
                       data_type: str, data_size: int = 0) -> str:
        """Mulai tracking data flow"""
        flow_id = f"{source_module}_{target_module}_{int(time.time())}"
        
        flow = DataFlow(
            source_module=source_module,
            target_module=target_module,
            data_type=data_type,
            status="processing",
            processing_time=0.0,
            timestamp=datetime.now(),
            data_size=data_size,
            success=False
        )
        
        self.active_flows[flow_id] = flow
        return flow_id
    
    def complete_data_flow(self, flow_id: str, success: bool = True, 
                          error_message: str = None):
        """Selesaikan tracking data flow"""
        if flow_id in self.active_flows:
            flow = self.active_flows[flow_id]
            flow.status = "completed" if success else "failed"
            flow.success = success
            flow.processing_time = (datetime.now() - flow.timestamp).total_seconds()
            
            # Simpan ke database
            self.save_flow_to_db(flow, error_message)
            
            # Pindahkan ke history
            self.flow_history.append(flow)
            del self.active_flows[flow_id]
            
            return flow
    
    def save_flow_to_db(self, flow: DataFlow, error_message: str = None):
        """Simpan data flow ke database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_flows 
            (source_module, target_module, data_type, status, processing_time, 
             data_size, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flow.source_module, flow.target_module, flow.data_type, flow.status,
            flow.processing_time, flow.data_size, flow.success, error_message
        ))
        
        conn.commit()
        conn.close()
    
    def get_module_performance(self, module_name: str) -> Dict[str, Any]:
        """Dapatkan performa modul"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get module statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests,
                AVG(processing_time) as avg_processing_time
            FROM data_flows 
            WHERE source_module = ? OR target_module = ?
        ''', (module_name, module_name))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            total, successful, failed, avg_time = result
            return {
                'module_name': module_name,
                'total_requests': total or 0,
                'successful_requests': successful or 0,
                'failed_requests': failed or 0,
                'success_rate': (successful / total * 100) if total > 0 else 0,
                'avg_processing_time': avg_time or 0,
                'last_updated': datetime.now().isoformat()
            }
        
        return {
            'module_name': module_name,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'success_rate': 0,
            'avg_processing_time': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_data_flow_summary(self) -> Dict[str, Any]:
        """Dapatkan ringkasan data flow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent flows
        cursor.execute('''
            SELECT source_module, target_module, data_type, status, 
                   processing_time, data_size, success, timestamp
            FROM data_flows 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        
        flows = cursor.fetchall()
        
        # Get module performance
        cursor.execute('''
            SELECT source_module, COUNT(*) as flow_count, 
                   AVG(processing_time) as avg_time,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
            FROM data_flows 
            GROUP BY source_module
        ''')
        
        module_stats = cursor.fetchall()
        
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
                    'data_size': flow[5],
                    'success': bool(flow[6]),
                    'timestamp': flow[7]
                } for flow in flows
            ],
            'module_performance': [
                {
                    'module': stat[0],
                    'flow_count': stat[1],
                    'avg_processing_time': stat[2],
                    'success_count': stat[3]
                } for stat in module_stats
            ]
        }
    
    def simulate_data_flow(self, source_module: str, target_module: str, 
                          data_type: str, processing_time: float = None):
        """Simulasi data flow untuk testing"""
        data_size = np.random.randint(100, 10000)
        flow_id = self.start_data_flow(source_module, target_module, data_type, data_size)
        
        # Simulate processing time
        if processing_time is None:
            processing_time = np.random.exponential(0.5)  # Exponential distribution
        
        time.sleep(processing_time)
        
        # Simulate success/failure
        success = np.random.random() > 0.1  # 90% success rate
        error_message = None if success else "Simulated error"
        
        return self.complete_data_flow(flow_id, success, error_message)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Dapatkan status integrasi sistem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get overall statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_flows,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_flows,
                AVG(processing_time) as avg_processing_time,
                MAX(timestamp) as last_flow_time
            FROM data_flows
        ''')
        
        overall_stats = cursor.fetchone()
        
        # Get module connectivity
        cursor.execute('''
            SELECT source_module, target_module, COUNT(*) as connection_count
            FROM data_flows 
            GROUP BY source_module, target_module
            ORDER BY connection_count DESC
        ''')
        
        connections = cursor.fetchall()
        
        conn.close()
        
        if overall_stats:
            total, successful, avg_time, last_flow = overall_stats
            success_rate = (successful / total * 100) if total > 0 else 0
            
            return {
                'overall_status': {
                    'total_flows': total or 0,
                    'successful_flows': successful or 0,
                    'success_rate': success_rate,
                    'avg_processing_time': avg_time or 0,
                    'last_flow_time': last_flow
                },
                'module_connections': [
                    {
                        'source': conn[0],
                        'target': conn[1],
                        'connection_count': conn[2]
                    } for conn in connections
                ],
                'active_flows': len(self.active_flows),
                'flow_history_count': len(self.flow_history)
            }
        
        return {
            'overall_status': {
                'total_flows': 0,
                'successful_flows': 0,
                'success_rate': 0,
                'avg_processing_time': 0,
                'last_flow_time': None
            },
            'module_connections': [],
            'active_flows': 0,
            'flow_history_count': 0
        }

# Global integrator instance
integrator = None

def get_integrator():
    """Get or create integrator instance"""
    global integrator
    if integrator is None:
        integrator = DataIntegrator()
    return integrator

def track_data_flow(source_module: str, target_module: str, data_type: str, 
                   data_size: int = 0) -> str:
    """Track data flow between modules"""
    integrator = get_integrator()
    return integrator.start_data_flow(source_module, target_module, data_type, data_size)

def complete_data_flow(flow_id: str, success: bool = True, error_message: str = None):
    """Complete data flow tracking"""
    integrator = get_integrator()
    return integrator.complete_data_flow(flow_id, success, error_message)

def get_module_performance(module_name: str) -> Dict[str, Any]:
    """Get module performance"""
    integrator = get_integrator()
    return integrator.get_module_performance(module_name)

def get_integration_status() -> Dict[str, Any]:
    """Get overall integration status"""
    integrator = get_integrator()
    return integrator.get_integration_status()
