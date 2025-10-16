#!/usr/bin/env python3
"""
Prediction Validator - Validator untuk membandingkan prediksi vs hasil aktual
=======================================================================

Validator ini membandingkan prediksi dengan hasil aktual:
1. Validasi prediksi setelah data aktual tersedia
2. Hitung akurasi prediksi
3. Analisis performa modul
4. Generate laporan validasi

Author: AI Assistant
Date: 2025-01-16
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from database_connector import DatabaseConnector

class PredictionValidator:
    """Validator untuk prediksi vs hasil aktual"""
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
        self.validation_results = {}
        
    def validate_predictions(self, symbol: str, start_date: str, end_date: str, 
                           module_name: str = None) -> Dict[str, Any]:
        """Validasi prediksi untuk symbol dan periode tertentu"""
        
        print(f"🔍 Validating predictions for {symbol} from {start_date} to {end_date}")
        
        # Ambil data historis
        historical_data = self.db_connector.get_historical_data(symbol, start_date, end_date)
        
        # Ambil data prediksi
        predictions = self.db_connector.get_predictions(symbol, start_date, end_date)
        
        if not historical_data or not predictions:
            return {
                'symbol': symbol,
                'period': f"{start_date} to {end_date}",
                'module': module_name,
                'status': 'NO_DATA',
                'message': 'No historical data or predictions found',
                'accuracy': 0.0,
                'total_predictions': 0,
                'correct_predictions': 0
            }
        
        # Buat dictionary untuk lookup data historis
        hist_dict = {row['date']: row for row in historical_data}
        
        # Validasi setiap prediksi
        validation_details = []
        correct_predictions = 0
        total_predictions = 0
        
        for pred in predictions:
            pred_date = pred['prediction_date']
            prediction_date_str = pred_date.strftime('%Y-%m-%d') if hasattr(pred_date, 'strftime') else str(pred_date)
            
            # Cari data aktual untuk hari berikutnya
            next_day = pred_date + timedelta(days=1)
            next_day_str = next_day.strftime('%Y-%m-%d')
            
            if next_day_str in hist_dict:
                actual_data = hist_dict[next_day_str]
                current_data = hist_dict.get(prediction_date_str, {})
                
                if current_data and actual_data:
                    # Validasi prediksi
                    validation_result = self._validate_single_prediction(pred, current_data, actual_data)
                    validation_details.append(validation_result)
                    
                    if validation_result['is_correct']:
                        correct_predictions += 1
                    
                    total_predictions += 1
        
        # Hitung akurasi
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        # Analisis detail
        analysis = self._analyze_validation_details(validation_details)
        
        result = {
            'symbol': symbol,
            'period': f"{start_date} to {end_date}",
            'module': module_name,
            'status': 'COMPLETED',
            'accuracy': accuracy,
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'validation_details': validation_details,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Validation completed: {accuracy:.2f}% accuracy ({correct_predictions}/{total_predictions})")
        
        return result
    
    def _validate_single_prediction(self, prediction: Dict[str, Any], 
                                  current_data: Dict[str, Any], 
                                  actual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validasi satu prediksi"""
        
        # Ambil data prediksi
        predicted_direction = prediction.get('predicted_direction', 'up')
        predicted_price = prediction.get('predicted_price', 0)
        confidence = prediction.get('confidence', 0.5)
        
        # Ambil data aktual
        current_price = current_data.get('close_price', 0)
        actual_price = actual_data.get('close_price', 0)
        
        # Tentukan arah aktual
        if actual_price > current_price:
            actual_direction = 'up'
        elif actual_price < current_price:
            actual_direction = 'down'
        else:
            actual_direction = 'neutral'
        
        # Validasi arah
        direction_correct = predicted_direction == actual_direction
        
        # Validasi harga (jika ada)
        price_accuracy = 0.0
        if predicted_price > 0 and actual_price > 0:
            price_error = abs(predicted_price - actual_price) / actual_price
            price_accuracy = max(0.0, 1.0 - price_error)
        
        # Hitung skor validasi
        validation_score = 0.0
        if direction_correct:
            validation_score += 0.7  # 70% untuk arah yang benar
        if price_accuracy > 0:
            validation_score += price_accuracy * 0.3  # 30% untuk akurasi harga
        
        return {
            'prediction_date': prediction.get('prediction_date', ''),
            'predicted_direction': predicted_direction,
            'predicted_price': predicted_price,
            'actual_direction': actual_direction,
            'actual_price': actual_price,
            'current_price': current_price,
            'direction_correct': direction_correct,
            'price_accuracy': price_accuracy,
            'validation_score': validation_score,
            'is_correct': direction_correct,
            'confidence': confidence
        }
    
    def _analyze_validation_details(self, validation_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisis detail validasi"""
        
        if not validation_details:
            return {
                'total_validations': 0,
                'average_accuracy': 0.0,
                'best_prediction': None,
                'worst_prediction': None,
                'confidence_analysis': {},
                'direction_analysis': {},
                'price_analysis': {}
            }
        
        # Hitung statistik
        total_validations = len(validation_details)
        correct_predictions = sum(1 for v in validation_details if v['is_correct'])
        average_accuracy = (correct_predictions / total_validations * 100) if total_validations > 0 else 0
        
        # Analisis confidence
        confidences = [v['confidence'] for v in validation_details if v['confidence'] > 0]
        confidence_analysis = {
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'high_confidence_count': sum(1 for c in confidences if c > 0.7),
            'low_confidence_count': sum(1 for c in confidences if c < 0.3)
        }
        
        # Analisis arah
        direction_analysis = {
            'up_predictions': sum(1 for v in validation_details if v['predicted_direction'] == 'up'),
            'down_predictions': sum(1 for v in validation_details if v['predicted_direction'] == 'down'),
            'up_correct': sum(1 for v in validation_details if v['predicted_direction'] == 'up' and v['is_correct']),
            'down_correct': sum(1 for v in validation_details if v['predicted_direction'] == 'down' and v['is_correct'])
        }
        
        # Analisis harga
        price_accuracies = [v['price_accuracy'] for v in validation_details if v['price_accuracy'] > 0]
        price_analysis = {
            'average_price_accuracy': sum(price_accuracies) / len(price_accuracies) if price_accuracies else 0,
            'high_price_accuracy_count': sum(1 for p in price_accuracies if p > 0.8),
            'low_price_accuracy_count': sum(1 for p in price_accuracies if p < 0.2)
        }
        
        # Best dan worst prediction
        best_prediction = max(validation_details, key=lambda x: x['validation_score']) if validation_details else None
        worst_prediction = min(validation_details, key=lambda x: x['validation_score']) if validation_details else None
        
        return {
            'total_validations': total_validations,
            'average_accuracy': average_accuracy,
            'best_prediction': {
                'date': best_prediction['prediction_date'],
                'score': best_prediction['validation_score'],
                'direction': best_prediction['predicted_direction'],
                'confidence': best_prediction['confidence']
            } if best_prediction else None,
            'worst_prediction': {
                'date': worst_prediction['prediction_date'],
                'score': worst_prediction['validation_score'],
                'direction': worst_prediction['predicted_direction'],
                'confidence': worst_prediction['confidence']
            } if worst_prediction else None,
            'confidence_analysis': confidence_analysis,
            'direction_analysis': direction_analysis,
            'price_analysis': price_analysis
        }
    
    def validate_module_performance(self, module_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Validasi performa modul"""
        
        print(f"🔧 Validating module performance: {module_name}")
        
        # Ambil semua symbol
        symbols = self.db_connector.get_available_symbols()
        
        module_performance = {
            'module_name': module_name,
            'period': f"{start_date} to {end_date}",
            'total_symbols': len(symbols),
            'symbols_analyzed': 0,
            'overall_accuracy': 0.0,
            'symbol_performance': [],
            'best_symbol': None,
            'worst_symbol': None,
            'average_accuracy': 0.0,
            'validation_details': []
        }
        
        symbol_accuracies = []
        
        for symbol in symbols:
            print(f"📊 Validating {symbol}...")
            
            # Validasi prediksi untuk symbol ini
            validation_result = self.validate_predictions(symbol, start_date, end_date, module_name)
            
            if validation_result['status'] == 'COMPLETED' and validation_result['total_predictions'] > 0:
                module_performance['symbols_analyzed'] += 1
                symbol_accuracies.append(validation_result['accuracy'])
                
                module_performance['symbol_performance'].append({
                    'symbol': symbol,
                    'accuracy': validation_result['accuracy'],
                    'total_predictions': validation_result['total_predictions'],
                    'correct_predictions': validation_result['correct_predictions'],
                    'analysis': validation_result['analysis']
                })
                
                module_performance['validation_details'].append(validation_result)
        
        # Hitung statistik overall
        if symbol_accuracies:
            module_performance['average_accuracy'] = sum(symbol_accuracies) / len(symbol_accuracies)
            module_performance['overall_accuracy'] = module_performance['average_accuracy']
            
            # Find best and worst performing symbols
            best_perf = max(module_performance['symbol_performance'], key=lambda x: x['accuracy'])
            worst_perf = min(module_performance['symbol_performance'], key=lambda x: x['accuracy'])
            
            module_performance['best_symbol'] = {
                'symbol': best_perf['symbol'],
                'accuracy': best_perf['accuracy'],
                'total_predictions': best_perf['total_predictions']
            }
            
            module_performance['worst_symbol'] = {
                'symbol': worst_perf['symbol'],
                'accuracy': worst_perf['accuracy'],
                'total_predictions': worst_perf['total_predictions']
            }
        
        print(f"✅ Module validation completed: {module_performance['overall_accuracy']:.2f}% accuracy")
        
        return module_performance
    
    def compare_modules(self, modules: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """Bandingkan performa beberapa modul"""
        
        print(f"🔄 Comparing modules: {', '.join(modules)}")
        
        comparison_results = {
            'period': f"{start_date} to {end_date}",
            'modules_compared': len(modules),
            'module_performance': {},
            'ranking': [],
            'best_module': None,
            'worst_module': None,
            'average_accuracy': 0.0
        }
        
        module_accuracies = []
        
        for module in modules:
            print(f"🔍 Analyzing {module}...")
            
            # Validasi performa modul
            module_perf = self.validate_module_performance(module, start_date, end_date)
            comparison_results['module_performance'][module] = module_perf
            
            if module_perf['overall_accuracy'] > 0:
                module_accuracies.append(module_perf['overall_accuracy'])
                comparison_results['ranking'].append({
                    'module': module,
                    'accuracy': module_perf['overall_accuracy'],
                    'symbols_analyzed': module_perf['symbols_analyzed']
                })
        
        # Sort ranking
        comparison_results['ranking'].sort(key=lambda x: x['accuracy'], reverse=True)
        
        # Find best and worst modules
        if comparison_results['ranking']:
            comparison_results['best_module'] = comparison_results['ranking'][0]
            comparison_results['worst_module'] = comparison_results['ranking'][-1]
            comparison_results['average_accuracy'] = sum(module_accuracies) / len(module_accuracies)
        
        print(f"✅ Module comparison completed")
        
        return comparison_results
    
    def save_validation_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """Simpan hasil validasi"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prediction_validation_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Validation results saved to: {filepath}")
        return filepath

def main():
    """Test prediction validator"""
    
    print("🔍 PREDICTION VALIDATOR - Testing Prediction Validation")
    print("=" * 60)
    
    # Initialize database connector
    db_connector = DatabaseConnector()
    
    # Initialize validator
    validator = PredictionValidator(db_connector)
    
    # Test validation
    try:
        # Test single symbol validation
        print("🔍 Testing single symbol validation...")
        result = validator.validate_predictions("AAPL", "2024-01-01", "2024-01-31")
        print(f"✅ Single validation: {result['accuracy']:.2f}% accuracy")
        
        # Test module performance
        print("\n🔧 Testing module performance validation...")
        module_perf = validator.validate_module_performance("ai_ml", "2024-01-01", "2024-01-31")
        print(f"✅ Module performance: {module_perf['overall_accuracy']:.2f}% accuracy")
        
        # Test module comparison
        print("\n🔄 Testing module comparison...")
        comparison = validator.compare_modules(["ai_ml", "technical", "fundamental"], "2024-01-01", "2024-01-31")
        print(f"✅ Module comparison completed")
        
        # Save results
        validator.save_validation_results(comparison)
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")

if __name__ == "__main__":
    main()
