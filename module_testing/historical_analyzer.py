#!/usr/bin/env python3
"""
Historical Analyzer - Analyzer untuk data historis dan akurasi prediksi
====================================================================

Analyzer ini menganalisis data historis dan akurasi prediksi:
1. Analisis data historis
2. Analisis akurasi prediksi
3. Analisis performa modul
4. Generate laporan analisis
5. Rekomendasi perbaikan

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
import numpy as np
from database_connector import DatabaseConnector
from prediction_validator import PredictionValidator

class HistoricalAnalyzer:
    """Analyzer untuk data historis dan akurasi prediksi"""
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
        self.validator = PredictionValidator(db_connector)
        self.analysis_results = {}
        
    def analyze_historical_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analisis data historis untuk symbol tertentu"""
        
        print(f"📊 Analyzing historical data for {symbol} from {start_date} to {end_date}")
        
        # Ambil data historis
        historical_data = self.db_connector.get_historical_data(symbol, start_date, end_date)
        
        if not historical_data:
            return {
                'symbol': symbol,
                'period': f"{start_date} to {end_date}",
                'status': 'NO_DATA',
                'message': 'No historical data found',
                'analysis': {}
            }
        
        # Convert to DataFrame untuk analisis
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Analisis statistik
        analysis = {
            'symbol': symbol,
            'period': f"{start_date} to {end_date}",
            'status': 'COMPLETED',
            'data_points': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d'),
                'total_days': (df['date'].max() - df['date'].min()).days + 1
            },
            'price_analysis': self._analyze_price_data(df),
            'volume_analysis': self._analyze_volume_data(df),
            'volatility_analysis': self._analyze_volatility(df),
            'trend_analysis': self._analyze_trends(df),
            'pattern_analysis': self._analyze_patterns(df),
            'correlation_analysis': self._analyze_correlations(df)
        }
        
        print(f"✅ Historical analysis completed: {analysis['data_points']} data points")
        
        return analysis
    
    def _analyze_price_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis data harga"""
        
        price_analysis = {
            'open_price': {
                'min': df['open_price'].min(),
                'max': df['open_price'].max(),
                'mean': df['open_price'].mean(),
                'std': df['open_price'].std()
            },
            'close_price': {
                'min': df['close_price'].min(),
                'max': df['close_price'].max(),
                'mean': df['close_price'].mean(),
                'std': df['close_price'].std()
            },
            'high_price': {
                'min': df['high_price'].min(),
                'max': df['high_price'].max(),
                'mean': df['high_price'].mean(),
                'std': df['high_price'].std()
            },
            'low_price': {
                'min': df['low_price'].min(),
                'max': df['low_price'].max(),
                'mean': df['low_price'].mean(),
                'std': df['low_price'].std()
            },
            'price_changes': {
                'daily_returns': df['close_price'].pct_change().dropna(),
                'total_return': (df['close_price'].iloc[-1] / df['close_price'].iloc[0] - 1) * 100,
                'positive_days': (df['close_price'].pct_change() > 0).sum(),
                'negative_days': (df['close_price'].pct_change() < 0).sum(),
                'neutral_days': (df['close_price'].pct_change() == 0).sum()
            }
        }
        
        # Calculate additional metrics
        daily_returns = price_analysis['price_changes']['daily_returns']
        price_analysis['price_changes']['avg_daily_return'] = daily_returns.mean()
        price_analysis['price_changes']['volatility'] = daily_returns.std()
        price_analysis['price_changes']['sharpe_ratio'] = (
            daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        ) if daily_returns.std() > 0 else 0
        
        return price_analysis
    
    def _analyze_volume_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis data volume"""
        
        volume_analysis = {
            'volume_stats': {
                'min': df['volume'].min(),
                'max': df['volume'].max(),
                'mean': df['volume'].mean(),
                'std': df['volume'].std(),
                'median': df['volume'].median()
            },
            'volume_trends': {
                'increasing_volume_days': (df['volume'].pct_change() > 0).sum(),
                'decreasing_volume_days': (df['volume'].pct_change() < 0).sum(),
                'avg_volume_change': df['volume'].pct_change().mean()
            },
            'volume_price_correlation': df['volume'].corr(df['close_price'])
        }
        
        return volume_analysis
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis volatilitas"""
        
        # Calculate daily returns
        daily_returns = df['close_price'].pct_change().dropna()
        
        volatility_analysis = {
            'daily_volatility': daily_returns.std(),
            'annualized_volatility': daily_returns.std() * np.sqrt(252),
            'volatility_percentiles': {
                '25th': daily_returns.quantile(0.25),
                '50th': daily_returns.quantile(0.50),
                '75th': daily_returns.quantile(0.75),
                '95th': daily_returns.quantile(0.95)
            },
            'volatility_trends': {
                'high_volatility_days': (abs(daily_returns) > daily_returns.std() * 2).sum(),
                'low_volatility_days': (abs(daily_returns) < daily_returns.std() * 0.5).sum()
            }
        }
        
        return volatility_analysis
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis tren"""
        
        # Calculate moving averages
        df['ma_5'] = df['close_price'].rolling(window=5).mean()
        df['ma_20'] = df['close_price'].rolling(window=20).mean()
        df['ma_50'] = df['close_price'].rolling(window=50).mean()
        
        trend_analysis = {
            'moving_averages': {
                'ma_5': df['ma_5'].iloc[-1] if not df['ma_5'].isna().iloc[-1] else None,
                'ma_20': df['ma_20'].iloc[-1] if not df['ma_20'].isna().iloc[-1] else None,
                'ma_50': df['ma_50'].iloc[-1] if not df['ma_50'].isna().iloc[-1] else None
            },
            'trend_direction': self._determine_trend_direction(df),
            'trend_strength': self._calculate_trend_strength(df),
            'support_resistance': self._find_support_resistance(df)
        }
        
        return trend_analysis
    
    def _determine_trend_direction(self, df: pd.DataFrame) -> str:
        """Tentukan arah tren"""
        
        if len(df) < 20:
            return 'INSUFFICIENT_DATA'
        
        # Compare current price with moving averages
        current_price = df['close_price'].iloc[-1]
        ma_20 = df['ma_20'].iloc[-1]
        ma_50 = df['ma_50'].iloc[-1]
        
        if current_price > ma_20 > ma_50:
            return 'UPTREND'
        elif current_price < ma_20 < ma_50:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Hitung kekuatan tren"""
        
        if len(df) < 20:
            return 0.0
        
        # Calculate trend strength based on price momentum
        price_momentum = (df['close_price'].iloc[-1] / df['close_price'].iloc[-20] - 1) * 100
        return abs(price_momentum)
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Temukan support dan resistance levels"""
        
        if len(df) < 20:
            return {'support': None, 'resistance': None}
        
        # Find recent highs and lows
        recent_data = df.tail(20)
        resistance = recent_data['high_price'].max()
        support = recent_data['low_price'].min()
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': df['close_price'].iloc[-1],
            'distance_to_support': ((df['close_price'].iloc[-1] - support) / support) * 100,
            'distance_to_resistance': ((resistance - df['close_price'].iloc[-1]) / df['close_price'].iloc[-1]) * 100
        }
    
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis pola harga"""
        
        pattern_analysis = {
            'price_patterns': self._detect_price_patterns(df),
            'volume_patterns': self._detect_volume_patterns(df),
            'candlestick_patterns': self._detect_candlestick_patterns(df)
        }
        
        return pattern_analysis
    
    def _detect_price_patterns(self, df: pd.DataFrame) -> List[str]:
        """Deteksi pola harga"""
        
        patterns = []
        
        if len(df) < 10:
            return patterns
        
        # Simple pattern detection
        recent_prices = df['close_price'].tail(10).values
        
        # Check for ascending pattern
        if all(recent_prices[i] < recent_prices[i+1] for i in range(len(recent_prices)-1)):
            patterns.append('ASCENDING')
        
        # Check for descending pattern
        if all(recent_prices[i] > recent_prices[i+1] for i in range(len(recent_prices)-1)):
            patterns.append('DESCENDING')
        
        # Check for consolidation
        price_range = max(recent_prices) - min(recent_prices)
        avg_price = np.mean(recent_prices)
        if price_range / avg_price < 0.05:  # Less than 5% range
            patterns.append('CONSOLIDATION')
        
        return patterns
    
    def _detect_volume_patterns(self, df: pd.DataFrame) -> List[str]:
        """Deteksi pola volume"""
        
        patterns = []
        
        if len(df) < 10:
            return patterns
        
        recent_volumes = df['volume'].tail(10).values
        avg_volume = df['volume'].mean()
        
        # Check for increasing volume
        if all(recent_volumes[i] < recent_volumes[i+1] for i in range(len(recent_volumes)-1)):
            patterns.append('INCREASING_VOLUME')
        
        # Check for decreasing volume
        if all(recent_volumes[i] > recent_volumes[i+1] for i in range(len(recent_volumes)-1)):
            patterns.append('DECREASING_VOLUME')
        
        # Check for high volume
        if all(vol > avg_volume * 1.5 for vol in recent_volumes):
            patterns.append('HIGH_VOLUME')
        
        return patterns
    
    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> List[str]:
        """Deteksi pola candlestick"""
        
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        # Simple candlestick pattern detection
        recent_data = df.tail(3)
        
        # Check for doji pattern
        for _, row in recent_data.iterrows():
            body_size = abs(row['close_price'] - row['open_price'])
            total_range = row['high_price'] - row['low_price']
            
            if total_range > 0 and body_size / total_range < 0.1:
                patterns.append('DOJI')
        
        return patterns
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis korelasi"""
        
        correlation_analysis = {
            'price_volume_correlation': df['close_price'].corr(df['volume']),
            'open_close_correlation': df['open_price'].corr(df['close_price']),
            'high_low_correlation': df['high_price'].corr(df['low_price']),
            'volume_volatility_correlation': df['volume'].corr(df['close_price'].pct_change().abs())
        }
        
        return correlation_analysis
    
    def analyze_prediction_accuracy(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analisis akurasi prediksi"""
        
        print(f"🎯 Analyzing prediction accuracy for {symbol} from {start_date} to {end_date}")
        
        # Validasi prediksi
        validation_result = self.validator.validate_predictions(symbol, start_date, end_date)
        
        if validation_result['status'] != 'COMPLETED':
            return {
                'symbol': symbol,
                'period': f"{start_date} to {end_date}",
                'status': 'NO_DATA',
                'message': 'No prediction data available',
                'analysis': {}
            }
        
        # Analisis akurasi
        accuracy_analysis = {
            'symbol': symbol,
            'period': f"{start_date} to {end_date}",
            'status': 'COMPLETED',
            'overall_accuracy': validation_result['accuracy'],
            'total_predictions': validation_result['total_predictions'],
            'correct_predictions': validation_result['correct_predictions'],
            'accuracy_analysis': self._analyze_accuracy_details(validation_result['validation_details']),
            'performance_metrics': self._calculate_performance_metrics(validation_result),
            'recommendations': self._generate_recommendations(validation_result)
        }
        
        print(f"✅ Accuracy analysis completed: {accuracy_analysis['overall_accuracy']:.2f}% accuracy")
        
        return accuracy_analysis
    
    def _analyze_accuracy_details(self, validation_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisis detail akurasi"""
        
        if not validation_details:
            return {}
        
        # Calculate accuracy by confidence level
        confidence_levels = {
            'high': [v for v in validation_details if v['confidence'] > 0.7],
            'medium': [v for v in validation_details if 0.4 <= v['confidence'] <= 0.7],
            'low': [v for v in validation_details if v['confidence'] < 0.4]
        }
        
        accuracy_by_confidence = {}
        for level, predictions in confidence_levels.items():
            if predictions:
                correct = sum(1 for p in predictions if p['is_correct'])
                accuracy_by_confidence[level] = (correct / len(predictions)) * 100
        
        # Calculate accuracy by direction
        up_predictions = [v for v in validation_details if v['predicted_direction'] == 'up']
        down_predictions = [v for v in validation_details if v['predicted_direction'] == 'down']
        
        accuracy_by_direction = {}
        if up_predictions:
            correct_up = sum(1 for p in up_predictions if p['is_correct'])
            accuracy_by_direction['up'] = (correct_up / len(up_predictions)) * 100
        
        if down_predictions:
            correct_down = sum(1 for p in down_predictions if p['is_correct'])
            accuracy_by_direction['down'] = (correct_down / len(down_predictions)) * 100
        
        return {
            'accuracy_by_confidence': accuracy_by_confidence,
            'accuracy_by_direction': accuracy_by_direction,
            'average_confidence': sum(v['confidence'] for v in validation_details) / len(validation_details),
            'confidence_distribution': {
                'high': len(confidence_levels['high']),
                'medium': len(confidence_levels['medium']),
                'low': len(confidence_levels['low'])
            }
        }
    
    def _calculate_performance_metrics(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Hitung metrik performa"""
        
        total_predictions = validation_result['total_predictions']
        correct_predictions = validation_result['correct_predictions']
        accuracy = validation_result['accuracy']
        
        # Calculate additional metrics
        validation_details = validation_result.get('validation_details', [])
        
        if validation_details:
            # Calculate average confidence
            avg_confidence = sum(v['confidence'] for v in validation_details) / len(validation_details)
            
            # Calculate prediction consistency
            daily_accuracies = []
            current_date = None
            daily_correct = 0
            daily_total = 0
            
            for detail in validation_details:
                pred_date = detail['prediction_date']
                if current_date != pred_date:
                    if current_date and daily_total > 0:
                        daily_accuracies.append(daily_correct / daily_total)
                    current_date = pred_date
                    daily_correct = 0
                    daily_total = 0
                
                daily_total += 1
                if detail['is_correct']:
                    daily_correct += 1
            
            # Add last day
            if daily_total > 0:
                daily_accuracies.append(daily_correct / daily_total)
            
            consistency = np.std(daily_accuracies) if daily_accuracies else 0
            
            return {
                'accuracy': accuracy,
                'average_confidence': avg_confidence,
                'consistency': consistency,
                'total_predictions': total_predictions,
                'correct_predictions': correct_predictions,
                'prediction_frequency': len(validation_details),
                'daily_consistency': daily_accuracies
            }
        
        return {
            'accuracy': accuracy,
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions
        }
    
    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate rekomendasi berdasarkan analisis"""
        
        recommendations = []
        accuracy = validation_result['accuracy']
        total_predictions = validation_result['total_predictions']
        
        # Accuracy-based recommendations
        if accuracy < 50:
            recommendations.append("Accuracy is below 50%. Consider improving prediction model.")
        elif accuracy < 70:
            recommendations.append("Accuracy is moderate. Fine-tune model parameters.")
        else:
            recommendations.append("Accuracy is good. Consider expanding prediction scope.")
        
        # Volume-based recommendations
        if total_predictions < 10:
            recommendations.append("Low prediction volume. Increase prediction frequency.")
        elif total_predictions > 100:
            recommendations.append("High prediction volume. Consider quality over quantity.")
        
        # Confidence-based recommendations
        validation_details = validation_result.get('validation_details', [])
        if validation_details:
            avg_confidence = sum(v['confidence'] for v in validation_details) / len(validation_details)
            
            if avg_confidence < 0.3:
                recommendations.append("Low confidence predictions. Improve model training.")
            elif avg_confidence > 0.8:
                recommendations.append("High confidence predictions. Consider risk management.")
        
        return recommendations
    
    def generate_comprehensive_report(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate laporan komprehensif"""
        
        print(f"📊 Generating comprehensive report for {symbol} from {start_date} to {end_date}")
        
        # Analisis data historis
        historical_analysis = self.analyze_historical_data(symbol, start_date, end_date)
        
        # Analisis akurasi prediksi
        accuracy_analysis = self.analyze_prediction_accuracy(symbol, start_date, end_date)
        
        # Gabungkan hasil
        comprehensive_report = {
            'symbol': symbol,
            'period': f"{start_date} to {end_date}",
            'generated_at': datetime.now().isoformat(),
            'historical_analysis': historical_analysis,
            'accuracy_analysis': accuracy_analysis,
            'summary': self._generate_summary(historical_analysis, accuracy_analysis),
            'recommendations': self._generate_overall_recommendations(historical_analysis, accuracy_analysis)
        }
        
        print(f"✅ Comprehensive report generated")
        
        return comprehensive_report
    
    def _generate_summary(self, historical_analysis: Dict[str, Any], 
                         accuracy_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ringkasan"""
        
        summary = {
            'data_quality': 'GOOD' if historical_analysis['status'] == 'COMPLETED' else 'POOR',
            'prediction_accuracy': accuracy_analysis.get('overall_accuracy', 0),
            'data_points': historical_analysis.get('data_points', 0),
            'prediction_volume': accuracy_analysis.get('total_predictions', 0),
            'trend_direction': historical_analysis.get('trend_analysis', {}).get('trend_direction', 'UNKNOWN'),
            'volatility_level': self._assess_volatility_level(historical_analysis),
            'recommendation_priority': self._assess_priority(historical_analysis, accuracy_analysis)
        }
        
        return summary
    
    def _assess_volatility_level(self, historical_analysis: Dict[str, Any]) -> str:
        """Assess level volatilitas"""
        
        volatility = historical_analysis.get('volatility_analysis', {}).get('daily_volatility', 0)
        
        if volatility < 0.01:
            return 'LOW'
        elif volatility < 0.03:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _assess_priority(self, historical_analysis: Dict[str, Any], 
                        accuracy_analysis: Dict[str, Any]) -> str:
        """Assess prioritas rekomendasi"""
        
        accuracy = accuracy_analysis.get('overall_accuracy', 0)
        data_points = historical_analysis.get('data_points', 0)
        
        if accuracy < 50 or data_points < 10:
            return 'HIGH'
        elif accuracy < 70 or data_points < 50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_overall_recommendations(self, historical_analysis: Dict[str, Any], 
                                       accuracy_analysis: Dict[str, Any]) -> List[str]:
        """Generate rekomendasi overall"""
        
        recommendations = []
        
        # Data quality recommendations
        if historical_analysis['status'] != 'COMPLETED':
            recommendations.append("Improve data quality and availability")
        
        # Accuracy recommendations
        accuracy = accuracy_analysis.get('overall_accuracy', 0)
        if accuracy < 60:
            recommendations.append("Focus on improving prediction accuracy")
        elif accuracy > 80:
            recommendations.append("Consider expanding prediction scope")
        
        # Data volume recommendations
        data_points = historical_analysis.get('data_points', 0)
        if data_points < 30:
            recommendations.append("Increase historical data collection")
        
        # Volatility recommendations
        volatility = historical_analysis.get('volatility_analysis', {}).get('daily_volatility', 0)
        if volatility > 0.05:
            recommendations.append("Implement volatility-based risk management")
        
        return recommendations
    
    def save_analysis_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """Simpan hasil analisis"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"historical_analysis_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Analysis results saved to: {filepath}")
        return filepath

def main():
    """Test historical analyzer"""
    
    print("📊 HISTORICAL ANALYZER - Testing Historical Analysis")
    print("=" * 60)
    
    # Initialize database connector
    db_connector = DatabaseConnector()
    
    # Initialize analyzer
    analyzer = HistoricalAnalyzer(db_connector)
    
    # Test analysis
    try:
        # Test historical analysis
        print("🔍 Testing historical analysis...")
        hist_analysis = analyzer.analyze_historical_data("AAPL", "2024-01-01", "2024-01-31")
        print(f"✅ Historical analysis: {hist_analysis['data_points']} data points")
        
        # Test accuracy analysis
        print("\n🎯 Testing accuracy analysis...")
        acc_analysis = analyzer.analyze_prediction_accuracy("AAPL", "2024-01-01", "2024-01-31")
        print(f"✅ Accuracy analysis: {acc_analysis['overall_accuracy']:.2f}% accuracy")
        
        # Test comprehensive report
        print("\n📊 Testing comprehensive report...")
        comprehensive_report = analyzer.generate_comprehensive_report("AAPL", "2024-01-01", "2024-01-31")
        print(f"✅ Comprehensive report generated")
        
        # Save results
        analyzer.save_analysis_results(comprehensive_report)
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")

if __name__ == "__main__":
    main()
