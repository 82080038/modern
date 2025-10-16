#!/usr/bin/env python3
"""
Progress Tracker - Tracker untuk menampilkan proses setiap modul
==============================================================

Tracker ini menampilkan progress real-time untuk setiap modul:
1. Progress bar untuk setiap modul
2. Status real-time
3. Performance metrics
4. Error tracking
5. Time estimation

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import pandas as pd

class ProgressTracker:
    """Tracker untuk progress real-time"""
    
    def __init__(self):
        self.tracking_data = {}
        self.callbacks = []
        self.is_tracking = False
        self.start_time = None
        self.end_time = None
        
    def add_callback(self, callback: Callable):
        """Tambahkan callback untuk progress updates"""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, message: str, data: Dict[str, Any] = None):
        """Notify semua callback"""
        for callback in self.callbacks:
            try:
                callback(message, data)
            except Exception as e:
                print(f"⚠️  Callback error: {str(e)}")
    
    def start_tracking(self, modules: List[str], total_days: int):
        """Mulai tracking"""
        
        self.is_tracking = True
        self.start_time = datetime.now()
        
        # Initialize tracking data untuk setiap modul
        for module in modules:
            self.tracking_data[module] = {
                'module_name': module,
                'status': 'PENDING',
                'start_time': None,
                'end_time': None,
                'total_days': total_days,
                'processed_days': 0,
                'current_day': 0,
                'progress_percentage': 0.0,
                'daily_results': [],
                'errors': [],
                'warnings': [],
                'performance_metrics': {
                    'average_accuracy': 0.0,
                    'best_day': None,
                    'worst_day': None,
                    'processing_speed': 0.0
                },
                'estimated_completion': None
            }
        
        print(f"🚀 Progress tracking started for {len(modules)} modules")
        print(f"📅 Total days to process: {total_days}")
        print("=" * 60)
    
    def update_module_progress(self, module: str, current_day: int, total_days: int, 
                              day_result: Dict[str, Any] = None):
        """Update progress untuk modul tertentu"""
        
        if module not in self.tracking_data:
            return
        
        tracking = self.tracking_data[module]
        
        # Update progress
        tracking['current_day'] = current_day
        tracking['processed_days'] = current_day
        tracking['progress_percentage'] = (current_day / total_days) * 100
        
        # Update status
        if current_day == 0:
            tracking['status'] = 'STARTING'
            tracking['start_time'] = datetime.now().isoformat()
        elif current_day < total_days:
            tracking['status'] = 'RUNNING'
        else:
            tracking['status'] = 'COMPLETED'
            tracking['end_time'] = datetime.now().isoformat()
        
        # Add day result
        if day_result:
            tracking['daily_results'].append({
                'day': current_day,
                'date': day_result.get('date', ''),
                'accuracy': day_result.get('accuracy', 0.0),
                'predictions': day_result.get('total_predictions', 0),
                'correct': day_result.get('correct_predictions', 0),
                'processing_time': day_result.get('processing_time', 0.0),
                'timestamp': datetime.now().isoformat()
            })
            
            # Update performance metrics
            self._update_performance_metrics(module)
        
        # Estimate completion time
        self._estimate_completion(module)
        
        # Notify callbacks
        self._notify_callbacks(f"Module {module} progress updated", {
            'module': module,
            'progress': tracking['progress_percentage'],
            'status': tracking['status'],
            'current_day': current_day,
            'total_days': total_days
        })
    
    def _update_performance_metrics(self, module: str):
        """Update performance metrics untuk modul"""
        
        if module not in self.tracking_data:
            return
        
        tracking = self.tracking_data[module]
        daily_results = tracking['daily_results']
        
        if not daily_results:
            return
        
        # Calculate average accuracy
        accuracies = [day['accuracy'] for day in daily_results if day['accuracy'] > 0]
        if accuracies:
            tracking['performance_metrics']['average_accuracy'] = sum(accuracies) / len(accuracies)
        
        # Find best and worst days
        if daily_results:
            best_day = max(daily_results, key=lambda x: x['accuracy'])
            worst_day = min(daily_results, key=lambda x: x['accuracy'])
            
            tracking['performance_metrics']['best_day'] = {
                'day': best_day['day'],
                'date': best_day['date'],
                'accuracy': best_day['accuracy']
            }
            
            tracking['performance_metrics']['worst_day'] = {
                'day': worst_day['day'],
                'date': worst_day['date'],
                'accuracy': worst_day['accuracy']
            }
        
        # Calculate processing speed
        if tracking['start_time']:
            start_time = datetime.fromisoformat(tracking['start_time'])
            current_time = datetime.now()
            elapsed_time = (current_time - start_time).total_seconds()
            
            if elapsed_time > 0:
                tracking['performance_metrics']['processing_speed'] = tracking['processed_days'] / elapsed_time
    
    def _estimate_completion(self, module: str):
        """Estimate waktu penyelesaian untuk modul"""
        
        if module not in self.tracking_data:
            return
        
        tracking = self.tracking_data[module]
        
        if tracking['status'] == 'COMPLETED':
            tracking['estimated_completion'] = 'COMPLETED'
            return
        
        if tracking['processed_days'] == 0:
            return
        
        # Calculate average time per day
        if tracking['start_time']:
            start_time = datetime.fromisoformat(tracking['start_time'])
            current_time = datetime.now()
            elapsed_time = (current_time - start_time).total_seconds()
            
            if elapsed_time > 0 and tracking['processed_days'] > 0:
                avg_time_per_day = elapsed_time / tracking['processed_days']
                remaining_days = tracking['total_days'] - tracking['processed_days']
                estimated_remaining_time = remaining_days * avg_time_per_day
                
                estimated_completion = current_time + timedelta(seconds=estimated_remaining_time)
                tracking['estimated_completion'] = estimated_completion.isoformat()
    
    def add_error(self, module: str, error_message: str, error_type: str = 'ERROR'):
        """Tambahkan error untuk modul"""
        
        if module not in self.tracking_data:
            return
        
        error = {
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'type': error_type
        }
        
        self.tracking_data[module]['errors'].append(error)
        
        # Update status
        if error_type == 'ERROR':
            self.tracking_data[module]['status'] = 'ERROR'
        elif error_type == 'WARNING':
            self.tracking_data[module]['status'] = 'WARNING'
        
        self._notify_callbacks(f"Error in {module}: {error_message}", {
            'module': module,
            'error': error
        })
    
    def add_warning(self, module: str, warning_message: str):
        """Tambahkan warning untuk modul"""
        
        if module not in self.tracking_data:
            return
        
        warning = {
            'timestamp': datetime.now().isoformat(),
            'message': warning_message,
            'type': 'WARNING'
        }
        
        self.tracking_data[module]['warnings'].append(warning)
        
        self._notify_callbacks(f"Warning in {module}: {warning_message}", {
            'module': module,
            'warning': warning
        })
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Ambil ringkasan progress"""
        
        if not self.tracking_data:
            return {}
        
        summary = {
            'total_modules': len(self.tracking_data),
            'completed_modules': 0,
            'running_modules': 0,
            'error_modules': 0,
            'pending_modules': 0,
            'overall_progress': 0.0,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'current_time': datetime.now().isoformat(),
            'module_details': {}
        }
        
        total_progress = 0.0
        
        for module, data in self.tracking_data.items():
            # Count by status
            if data['status'] == 'COMPLETED':
                summary['completed_modules'] += 1
            elif data['status'] == 'RUNNING':
                summary['running_modules'] += 1
            elif data['status'] == 'ERROR':
                summary['error_modules'] += 1
            else:
                summary['pending_modules'] += 1
            
            # Calculate overall progress
            total_progress += data['progress_percentage']
            
            # Module details
            summary['module_details'][module] = {
                'status': data['status'],
                'progress': data['progress_percentage'],
                'processed_days': data['processed_days'],
                'total_days': data['total_days'],
                'average_accuracy': data['performance_metrics']['average_accuracy'],
                'errors': len(data['errors']),
                'warnings': len(data['warnings']),
                'estimated_completion': data['estimated_completion']
            }
        
        # Calculate overall progress
        if self.tracking_data:
            summary['overall_progress'] = total_progress / len(self.tracking_data)
        
        return summary
    
    def print_progress_summary(self):
        """Print ringkasan progress"""
        
        summary = self.get_progress_summary()
        
        if not summary:
            print("📊 No progress data available")
            return
        
        print(f"\n📊 PROGRESS SUMMARY")
        print("=" * 50)
        print(f"🕐 Time: {summary['current_time']}")
        print(f"📈 Overall Progress: {summary['overall_progress']:.1f}%")
        print(f"✅ Completed: {summary['completed_modules']}")
        print(f"🔄 Running: {summary['running_modules']}")
        print(f"❌ Errors: {summary['error_modules']}")
        print(f"⏳ Pending: {summary['pending_modules']}")
        print()
        
        # Print module details
        for module, details in summary['module_details'].items():
            status_emoji = {
                'COMPLETED': '✅',
                'RUNNING': '🔄',
                'ERROR': '❌',
                'WARNING': '⚠️',
                'PENDING': '⏳'
            }
            
            emoji = status_emoji.get(details['status'], '❓')
            
            print(f"{emoji} {module}: {details['progress']:.1f}% ({details['processed_days']}/{details['total_days']})")
            print(f"   Accuracy: {details['average_accuracy']:.2f}%")
            print(f"   Errors: {details['errors']}, Warnings: {details['warnings']}")
            
            if details['estimated_completion'] and details['estimated_completion'] != 'COMPLETED':
                try:
                    est_time = datetime.fromisoformat(details['estimated_completion'])
                    remaining = est_time - datetime.now()
                    print(f"   ETA: {remaining}")
                except:
                    pass
            
            print()
    
    def stop_tracking(self):
        """Stop tracking"""
        
        self.is_tracking = False
        self.end_time = datetime.now()
        
        print(f"⏹️  Progress tracking stopped")
        print(f"🕐 Total time: {self.end_time - self.start_time}")
    
    def save_tracking_data(self, filename: str = None) -> str:
        """Simpan data tracking"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"progress_tracking_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.tracking_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Progress tracking data saved to: {filepath}")
        return filepath

def main():
    """Test progress tracker"""
    
    print("📊 PROGRESS TRACKER - Testing Progress Tracking")
    print("=" * 60)
    
    # Initialize tracker
    tracker = ProgressTracker()
    
    # Add callback
    def progress_callback(message: str, data: Dict[str, Any] = None):
        print(f"📊 {message}")
        if data:
            print(f"   Data: {data}")
    
    tracker.add_callback(progress_callback)
    
    # Start tracking
    modules = ["ai_ml", "technical", "fundamental", "sentiment"]
    total_days = 30
    
    tracker.start_tracking(modules, total_days)
    
    # Simulate progress
    try:
        for day in range(1, total_days + 1):
            print(f"\n📅 Processing day {day}/{total_days}")
            
            for module in modules:
                # Simulate day result
                day_result = {
                    'date': f"2024-01-{day:02d}",
                    'accuracy': 70 + (day % 30),  # Simulate accuracy
                    'total_predictions': 10,
                    'correct_predictions': 7,
                    'processing_time': 0.5
                }
                
                # Update progress
                tracker.update_module_progress(module, day, total_days, day_result)
                
                # Simulate some errors
                if day == 5 and module == "technical":
                    tracker.add_error(module, "Connection timeout", "ERROR")
                elif day == 10 and module == "fundamental":
                    tracker.add_warning(module, "Low confidence prediction")
            
            # Print progress summary
            tracker.print_progress_summary()
            
            # Simulate time delay
            time.sleep(0.1)
        
        # Stop tracking
        tracker.stop_tracking()
        
        # Save data
        tracker.save_tracking_data()
        
    except KeyboardInterrupt:
        print("\n⏹️  Tracking interrupted by user")
        tracker.stop_tracking()

if __name__ == "__main__":
    main()
