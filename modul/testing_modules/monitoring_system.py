#!/usr/bin/env python3
"""
Continuous Monitoring System
============================

Sistem monitoring berkelanjutan untuk memantau performa modul trading
dan memberikan alert ketika ada masalah.

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import schedule

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModuleMonitor:
    """Monitor untuk memantau performa modul trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.monitoring_active = False
        self.alert_thresholds = {
            'accuracy': 70.0,  # Alert jika accuracy < 70%
            'response_time': 5.0,  # Alert jika response time > 5 detik
            'error_rate': 5.0,  # Alert jika error rate > 5%
            'memory_usage': 80.0,  # Alert jika memory usage > 80%
            'cpu_usage': 80.0  # Alert jika CPU usage > 80%
        }
        self.monitoring_data = {}
        self.alerts = []
        
    def start_monitoring(self):
        """Mulai monitoring berkelanjutan"""
        logger.info("Starting continuous monitoring system...")
        self.monitoring_active = True
        
        # Schedule monitoring tasks
        schedule.every(1).minutes.do(self.check_module_performance)
        schedule.every(5).minutes.do(self.check_system_health)
        schedule.every(15).minutes.do(self.generate_performance_report)
        schedule.every(1).hours.do(self.cleanup_old_data)
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        logger.info("Monitoring system started successfully")
        
    def stop_monitoring(self):
        """Hentikan monitoring"""
        logger.info("Stopping monitoring system...")
        self.monitoring_active = False
        logger.info("Monitoring system stopped")
        
    def _monitoring_loop(self):
        """Loop monitoring utama"""
        while self.monitoring_active:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
                
    def check_module_performance(self):
        """Cek performa setiap modul"""
        logger.info("Checking module performance...")
        
        modules = [
            "ai_ml", "algorithmic_trading", "backtesting",
            "technical", "fundamental", "sentiment",
            "risk_management", "portfolio_optimization",
            "trading", "market_data", "earnings",
            "economic_calendar", "notifications", "watchlist"
        ]
        
        for module in modules:
            try:
                # Simulate performance check
                performance_data = self._check_module_health(module)
                self.monitoring_data[module] = performance_data
                
                # Check for alerts
                self._check_alerts(module, performance_data)
                
            except Exception as e:
                logger.error(f"Error checking module {module}: {e}")
                self._create_alert(module, "ERROR", f"Failed to check module: {e}")
                
    def _check_module_health(self, module: str) -> Dict[str, Any]:
        """Cek kesehatan modul individual"""
        # Simulate health check
        import random
        
        return {
            'timestamp': datetime.now().isoformat(),
            'accuracy': round(random.uniform(40, 90), 2),
            'response_time': round(random.uniform(0.5, 10), 2),
            'error_rate': round(random.uniform(0, 15), 2),
            'memory_usage': round(random.uniform(20, 95), 2),
            'cpu_usage': round(random.uniform(10, 90), 2),
            'status': 'healthy' if random.random() > 0.1 else 'degraded'
        }
        
    def _check_alerts(self, module: str, data: Dict[str, Any]):
        """Cek apakah perlu alert"""
        alerts = []
        
        if data['accuracy'] < self.alert_thresholds['accuracy']:
            alerts.append(f"LOW_ACCURACY: {data['accuracy']:.2f}% < {self.alert_thresholds['accuracy']}%")
            
        if data['response_time'] > self.alert_thresholds['response_time']:
            alerts.append(f"SLOW_RESPONSE: {data['response_time']:.2f}s > {self.alert_thresholds['response_time']}s")
            
        if data['error_rate'] > self.alert_thresholds['error_rate']:
            alerts.append(f"HIGH_ERROR_RATE: {data['error_rate']:.2f}% > {self.alert_thresholds['error_rate']}%")
            
        if data['memory_usage'] > self.alert_thresholds['memory_usage']:
            alerts.append(f"HIGH_MEMORY: {data['memory_usage']:.2f}% > {self.alert_thresholds['memory_usage']}%")
            
        if data['cpu_usage'] > self.alert_thresholds['cpu_usage']:
            alerts.append(f"HIGH_CPU: {data['cpu_usage']:.2f}% > {self.alert_thresholds['cpu_usage']}%")
            
        if data['status'] == 'degraded':
            alerts.append("DEGRADED_STATUS: Module performance degraded")
            
        for alert in alerts:
            self._create_alert(module, "WARNING", alert)
            
    def _create_alert(self, module: str, level: str, message: str):
        """Buat alert baru"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'module': module,
            'level': level,
            'message': message,
            'resolved': False
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT [{level}] {module}: {message}")
        
    def check_system_health(self):
        """Cek kesehatan sistem keseluruhan"""
        logger.info("Checking system health...")
        
        # Check database connection
        try:
            # Simulate database check
            db_status = "connected"
            logger.info("Database: connected")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self._create_alert("SYSTEM", "CRITICAL", f"Database connection failed: {e}")
            
        # Check disk space
        try:
            disk_usage = self._check_disk_usage()
            if disk_usage > 90:
                self._create_alert("SYSTEM", "WARNING", f"Disk usage high: {disk_usage}%")
        except Exception as e:
            logger.error(f"Error checking disk usage: {e}")
            
        # Check memory usage
        try:
            memory_usage = self._check_memory_usage()
            if memory_usage > 90:
                self._create_alert("SYSTEM", "WARNING", f"Memory usage high: {memory_usage}%")
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
            
    def _check_disk_usage(self) -> float:
        """Cek penggunaan disk"""
        # Simulate disk usage check
        import random
        return round(random.uniform(30, 95), 2)
        
    def _check_memory_usage(self) -> float:
        """Cek penggunaan memory"""
        # Simulate memory usage check
        import random
        return round(random.uniform(40, 90), 2)
        
    def generate_performance_report(self):
        """Generate laporan performa"""
        logger.info("Generating performance report...")
        
        if not self.monitoring_data:
            logger.warning("No monitoring data available")
            return
            
        # Calculate averages
        total_modules = len(self.monitoring_data)
        avg_accuracy = sum(data['accuracy'] for data in self.monitoring_data.values()) / total_modules
        avg_response_time = sum(data['response_time'] for data in self.monitoring_data.values()) / total_modules
        avg_error_rate = sum(data['error_rate'] for data in self.monitoring_data.values()) / total_modules
        
        # Count healthy modules
        healthy_modules = sum(1 for data in self.monitoring_data.values() if data['status'] == 'healthy')
        degraded_modules = total_modules - healthy_modules
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_modules': total_modules,
            'healthy_modules': healthy_modules,
            'degraded_modules': degraded_modules,
            'average_accuracy': round(avg_accuracy, 2),
            'average_response_time': round(avg_response_time, 2),
            'average_error_rate': round(avg_error_rate, 2),
            'active_alerts': len([a for a in self.alerts if not a['resolved']]),
            'system_status': 'healthy' if degraded_modules == 0 else 'degraded'
        }
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"performance_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Performance report saved: {report_file}")
        logger.info(f"System Status: {report['system_status']}")
        logger.info(f"Healthy Modules: {healthy_modules}/{total_modules}")
        logger.info(f"Active Alerts: {report['active_alerts']}")
        
    def cleanup_old_data(self):
        """Bersihkan data lama"""
        logger.info("Cleaning up old data...")
        
        # Keep only last 24 hours of monitoring data
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Clean up old alerts
        self.alerts = [alert for alert in self.alerts 
                      if datetime.fromisoformat(alert['timestamp']) > cutoff_time]
        
        logger.info("Old data cleanup completed")
        
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Dapatkan status monitoring saat ini"""
        return {
            'monitoring_active': self.monitoring_active,
            'total_modules': len(self.monitoring_data),
            'active_alerts': len([a for a in self.alerts if not a['resolved']]),
            'last_check': datetime.now().isoformat(),
            'monitoring_data': self.monitoring_data,
            'recent_alerts': self.alerts[-10:] if self.alerts else []
        }

def main():
    """Main function untuk menjalankan monitoring system"""
    print("CONTINUOUS MONITORING SYSTEM")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Configuration
    config = {
        'monitoring_interval': 60,  # seconds
        'alert_thresholds': {
            'accuracy': 70.0,
            'response_time': 5.0,
            'error_rate': 5.0,
            'memory_usage': 80.0,
            'cpu_usage': 80.0
        },
        'cleanup_interval': 3600,  # seconds
        'report_interval': 900  # seconds
    }
    
    # Initialize monitor
    monitor = ModuleMonitor(config)
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        print("Monitoring system is running...")
        print("Press Ctrl+C to stop")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping monitoring system...")
        monitor.stop_monitoring()
        print("Monitoring system stopped")
        
    except Exception as e:
        logger.error(f"Error in monitoring system: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
