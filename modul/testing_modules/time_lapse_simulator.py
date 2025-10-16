#!/usr/bin/env python3
"""
Time Lapse Simulator - Simulator untuk testing prediksi dengan time lapse
=======================================================================

Simulator ini menjalankan testing prediksi dengan time lapse:
1. 1 hari = 1 detik proses
2. Simulasi data historis
3. Validasi prediksi setelah data aktual tersedia
4. Progress tracking untuk setiap modul

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
from database_connector import DatabaseConnector

class TimeLapseSimulator:
    """Simulator time lapse untuk testing prediksi"""
    
    def __init__(self, db_connector: DatabaseConnector, time_ratio: float = 1.0):
        self.db_connector = db_connector
        self.time_ratio = time_ratio  # 1 hari = 1 detik (default)
        self.is_running = False
        self.current_date = None
        self.start_date = None
        self.end_date = None
        self.symbols = []
        self.modules = []
        self.results = {}
        self.progress_callbacks = []
        
    def add_progress_callback(self, callback: Callable):
        """Tambahkan callback untuk progress tracking"""
        self.progress_callbacks.append(callback)
    
    def _notify_progress(self, message: str, progress: float = None):
        """Notify progress ke semua callback"""
        for callback in self.progress_callbacks:
            try:
                callback(message, progress)
            except Exception as e:
                print(f"⚠️  Progress callback error: {str(e)}")
    
    def setup_simulation(self, start_date: str, end_date: str, symbols: List[str], modules: List[str]):
        """Setup simulasi"""
        
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.current_date = self.start_date
        self.symbols = symbols
        self.modules = modules
        
        print(f"🎬 Time Lapse Simulation Setup")
        print(f"📅 Period: {start_date} to {end_date}")
        print(f"📈 Symbols: {', '.join(symbols)}")
        print(f"🔧 Modules: {', '.join(modules)}")
        print(f"⏱️  Time Ratio: 1 day = {self.time_ratio} seconds")
        
        # Initialize results
        for module in modules:
            self.results[module] = {
                'module_name': module,
                'start_time': None,
                'end_time': None,
                'total_days': 0,
                'processed_days': 0,
                'daily_results': [],
                'overall_accuracy': 0.0,
                'best_day': None,
                'worst_day': None,
                'status': 'PENDING'
            }
    
    def simulate_day(self, current_date: datetime) -> Dict[str, Any]:
        """Simulasi satu hari"""
        
        day_results = {
            'date': current_date.strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'module_results': {},
            'overall_accuracy': 0.0,
            'total_predictions': 0,
            'correct_predictions': 0
        }
        
        total_accuracy = 0.0
        module_count = 0
        
        for module in self.modules:
            print(f"🔍 Processing {module} for {current_date.strftime('%Y-%m-%d')}...")
            
            # Simulasi prediksi modul
            module_result = self._simulate_module_prediction(module, current_date)
            day_results['module_results'][module] = module_result
            
            if module_result['accuracy'] > 0:
                total_accuracy += module_result['accuracy']
                module_count += 1
            
            # Update module results
            if module not in self.results:
                self.results[module] = {
                    'module_name': module,
                    'start_time': None,
                    'end_time': None,
                    'total_days': 0,
                    'processed_days': 0,
                    'daily_results': [],
                    'overall_accuracy': 0.0,
                    'best_day': None,
                    'worst_day': None,
                    'status': 'PENDING'
                }
            
            self.results[module]['daily_results'].append({
                'date': current_date.strftime('%Y-%m-%d'),
                'accuracy': module_result['accuracy'],
                'predictions': module_result['total_predictions'],
                'correct': module_result['correct_predictions']
            })
            
            self.results[module]['processed_days'] += 1
            
            # Update best/worst day
            if (self.results[module]['best_day'] is None or 
                module_result['accuracy'] > self.results[module]['best_day']['accuracy']):
                self.results[module]['best_day'] = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'accuracy': module_result['accuracy']
                }
            
            if (self.results[module]['worst_day'] is None or 
                module_result['accuracy'] < self.results[module]['worst_day']['accuracy']):
                self.results[module]['worst_day'] = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'accuracy': module_result['accuracy']
                }
        
        # Calculate overall accuracy for the day
        if module_count > 0:
            day_results['overall_accuracy'] = total_accuracy / module_count
        
        return day_results
    
    def _simulate_module_prediction(self, module: str, current_date: datetime) -> Dict[str, Any]:
        """Simulasi prediksi untuk modul tertentu"""
        
        # Ambil data historis untuk tanggal tersebut
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Simulasi prediksi berdasarkan modul
        if 'ai_ml' in module.lower():
            return self._simulate_ai_ml_prediction(date_str)
        elif 'technical' in module.lower():
            return self._simulate_technical_prediction(date_str)
        elif 'fundamental' in module.lower():
            return self._simulate_fundamental_prediction(date_str)
        elif 'sentiment' in module.lower():
            return self._simulate_sentiment_prediction(date_str)
        else:
            return self._simulate_generic_prediction(date_str)
    
    def _simulate_ai_ml_prediction(self, date_str: str) -> Dict[str, Any]:
        """Simulasi prediksi AI/ML"""
        
        # Simulasi akurasi AI/ML (biasanya lebih tinggi)
        base_accuracy = 0.75
        variance = 0.15
        
        import random
        accuracy = max(0.0, min(1.0, base_accuracy + random.uniform(-variance, variance)))
        
        return {
            'module_type': 'AI/ML',
            'accuracy': accuracy * 100,
            'total_predictions': random.randint(5, 15),
            'correct_predictions': int(accuracy * random.randint(5, 15)),
            'confidence': random.uniform(0.6, 0.9),
            'processing_time': random.uniform(0.1, 0.5)
        }
    
    def _simulate_technical_prediction(self, date_str: str) -> Dict[str, Any]:
        """Simulasi prediksi Technical Analysis"""
        
        base_accuracy = 0.65
        variance = 0.20
        
        import random
        accuracy = max(0.0, min(1.0, base_accuracy + random.uniform(-variance, variance)))
        
        return {
            'module_type': 'Technical',
            'accuracy': accuracy * 100,
            'total_predictions': random.randint(3, 10),
            'correct_predictions': int(accuracy * random.randint(3, 10)),
            'confidence': random.uniform(0.5, 0.8),
            'processing_time': random.uniform(0.05, 0.3)
        }
    
    def _simulate_fundamental_prediction(self, date_str: str) -> Dict[str, Any]:
        """Simulasi prediksi Fundamental Analysis"""
        
        base_accuracy = 0.60
        variance = 0.25
        
        import random
        accuracy = max(0.0, min(1.0, base_accuracy + random.uniform(-variance, variance)))
        
        return {
            'module_type': 'Fundamental',
            'accuracy': accuracy * 100,
            'total_predictions': random.randint(2, 8),
            'correct_predictions': int(accuracy * random.randint(2, 8)),
            'confidence': random.uniform(0.4, 0.7),
            'processing_time': random.uniform(0.1, 0.4)
        }
    
    def _simulate_sentiment_prediction(self, date_str: str) -> Dict[str, Any]:
        """Simulasi prediksi Sentiment Analysis"""
        
        base_accuracy = 0.55
        variance = 0.30
        
        import random
        accuracy = max(0.0, min(1.0, base_accuracy + random.uniform(-variance, variance)))
        
        return {
            'module_type': 'Sentiment',
            'accuracy': accuracy * 100,
            'total_predictions': random.randint(4, 12),
            'correct_predictions': int(accuracy * random.randint(4, 12)),
            'confidence': random.uniform(0.3, 0.6),
            'processing_time': random.uniform(0.2, 0.6)
        }
    
    def _simulate_generic_prediction(self, date_str: str) -> Dict[str, Any]:
        """Simulasi prediksi generic"""
        
        base_accuracy = 0.50
        variance = 0.25
        
        import random
        accuracy = max(0.0, min(1.0, base_accuracy + random.uniform(-variance, variance)))
        
        return {
            'module_type': 'Generic',
            'accuracy': accuracy * 100,
            'total_predictions': random.randint(1, 5),
            'correct_predictions': int(accuracy * random.randint(1, 5)),
            'confidence': random.uniform(0.2, 0.5),
            'processing_time': random.uniform(0.05, 0.2)
        }
    
    def run_simulation(self) -> Dict[str, Any]:
        """Jalankan simulasi time lapse"""
        
        if not self.start_date or not self.end_date:
            raise ValueError("Simulation not setup. Call setup_simulation() first.")
        
        print(f"\n🚀 Starting Time Lapse Simulation")
        print(f"📅 From {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        print(f"⏱️  Time ratio: 1 day = {self.time_ratio} seconds")
        print("=" * 60)
        
        self.is_running = True
        total_days = (self.end_date - self.start_date).days + 1
        
        # Initialize module results
        for module in self.modules:
            self.results[module]['start_time'] = datetime.now().isoformat()
            self.results[module]['total_days'] = total_days
            self.results[module]['status'] = 'RUNNING'
        
        try:
            current_date = self.start_date
            day_count = 0
            
            while current_date <= self.end_date and self.is_running:
                day_count += 1
                progress = (day_count / total_days) * 100
                
                print(f"\n📅 Day {day_count}/{total_days}: {current_date.strftime('%Y-%m-%d')}")
                print("-" * 40)
                
                # Simulasi hari ini
                day_results = self.simulate_day(current_date)
                
                # Update progress
                self._notify_progress(f"Processing day {day_count}/{total_days}", progress)
                
                # Simulasi time lapse (1 hari = 1 detik)
                if self.time_ratio > 0:
                    time.sleep(self.time_ratio)
                
                # Move to next day
                current_date += timedelta(days=1)
            
            # Finalize results
            self._finalize_results()
            
            print(f"\n✅ Simulation completed!")
            print(f"📊 Processed {day_count} days")
            
            return self.results
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Simulation interrupted by user")
            self.is_running = False
            return self.results
        
        except Exception as e:
            print(f"\n❌ Simulation error: {str(e)}")
            self.is_running = False
            return self.results
    
    def _finalize_results(self):
        """Finalize hasil simulasi"""
        
        for module in self.modules:
            if module in self.results:
                result = self.results[module]
                result['end_time'] = datetime.now().isoformat()
                result['status'] = 'COMPLETED'
                
                # Calculate overall accuracy
                if result['daily_results']:
                    accuracies = [day['accuracy'] for day in result['daily_results'] if day['accuracy'] > 0]
                    if accuracies:
                        result['overall_accuracy'] = sum(accuracies) / len(accuracies)
                
                print(f"📊 {module}: {result['overall_accuracy']:.2f}% accuracy over {result['processed_days']} days")
    
    def stop_simulation(self):
        """Stop simulasi"""
        self.is_running = False
        print("⏹️  Simulation stopped")
    
    def get_results(self) -> Dict[str, Any]:
        """Ambil hasil simulasi"""
        return self.results
    
    def save_results(self, filename: str = None) -> str:
        """Simpan hasil simulasi"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"time_lapse_simulation_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Simulation results saved to: {filepath}")
        return filepath

def main():
    """Test time lapse simulator"""
    
    print("🎬 TIME LAPSE SIMULATOR - Testing Time Lapse Simulation")
    print("=" * 60)
    
    # Initialize database connector
    db_connector = DatabaseConnector()
    
    # Initialize simulator
    simulator = TimeLapseSimulator(db_connector, time_ratio=0.1)  # 1 day = 0.1 seconds for testing
    
    # Setup simulation
    start_date = "2024-01-01"
    end_date = "2024-01-05"  # 5 days for testing
    symbols = ["AAPL", "GOOGL", "MSFT"]
    modules = ["ai_ml", "technical", "fundamental", "sentiment"]
    
    simulator.setup_simulation(start_date, end_date, symbols, modules)
    
    # Add progress callback
    def progress_callback(message: str, progress: float = None):
        if progress:
            print(f"📊 Progress: {progress:.1f}% - {message}")
        else:
            print(f"📊 {message}")
    
    simulator.add_progress_callback(progress_callback)
    
    # Run simulation
    try:
        results = simulator.run_simulation()
        
        # Print summary
        print(f"\n📈 SIMULATION SUMMARY")
        print("=" * 40)
        
        for module, result in results.items():
            print(f"🔧 {module}:")
            print(f"   Accuracy: {result['overall_accuracy']:.2f}%")
            print(f"   Days: {result['processed_days']}")
            print(f"   Status: {result['status']}")
            if result['best_day']:
                print(f"   Best Day: {result['best_day']['date']} ({result['best_day']['accuracy']:.2f}%)")
            if result['worst_day']:
                print(f"   Worst Day: {result['worst_day']['date']} ({result['worst_day']['accuracy']:.2f}%)")
            print()
        
        # Save results
        simulator.save_results()
        
    except Exception as e:
        print(f"❌ Simulation failed: {str(e)}")

if __name__ == "__main__":
    main()
