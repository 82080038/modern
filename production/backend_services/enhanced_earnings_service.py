"""
Enhanced Earnings Service
=========================

Service untuk earnings analysis dengan implementasi algoritma terbukti
menggunakan earnings forecasting, surprise analysis, dan quality assessment.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import json
from app.models.earnings import EarningsData, EarningsForecast, EarningsSurprise
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class EnhancedEarningsService:
    """
    Enhanced Earnings Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = CacheService(db)
        
        # Earnings quality thresholds
        self.quality_thresholds = {
            'earnings_growth': {'excellent': 0.20, 'good': 0.10, 'poor': 0.05},
            'revenue_growth': {'excellent': 0.15, 'good': 0.08, 'poor': 0.03},
            'earnings_consistency': {'excellent': 0.80, 'good': 0.60, 'poor': 0.40},
            'surprise_consistency': {'excellent': 0.70, 'good': 0.50, 'poor': 0.30}
        }
        
        # Earnings surprise thresholds
        self.surprise_thresholds = {
            'positive_surprise': 0.05,  # 5% positive surprise
            'negative_surprise': -0.05,  # 5% negative surprise
            'significant_surprise': 0.20  # 20% significant surprise
        }
    
    async def analyze_earnings(
        self, 
        symbol: str, 
        analysis_type: str = 'comprehensive',
        include_forecasting: bool = True,
        include_quality_assessment: bool = True
    ) -> Dict[str, Any]:
        """Analyze earnings untuk symbol"""
        try:
            # Get earnings data
            earnings_data = await self._get_earnings_data(symbol)
            if not earnings_data:
                return {'error': f'No earnings data available for {symbol}'}
            
            # Calculate earnings metrics
            earnings_metrics = await self._calculate_earnings_metrics(earnings_data)
            
            # Analyze earnings surprises
            surprise_analysis = await self._analyze_earnings_surprises(symbol, earnings_data)
            
            # Assess earnings quality
            quality_assessment = None
            if include_quality_assessment:
                quality_assessment = await self._assess_earnings_quality(earnings_data, earnings_metrics)
            
            # Generate earnings forecast
            earnings_forecast = None
            if include_forecasting:
                earnings_forecast = await self._generate_earnings_forecast(symbol, earnings_data)
            
            # Calculate earnings trends
            earnings_trends = await self._calculate_earnings_trends(earnings_data)
            
            # Generate earnings recommendation
            earnings_recommendation = await self._generate_earnings_recommendation(
                symbol, earnings_metrics, surprise_analysis, quality_assessment
            )
            
            return {
                'success': True,
                'symbol': symbol,
                'analysis_type': analysis_type,
                'earnings_data': earnings_data,
                'earnings_metrics': earnings_metrics,
                'surprise_analysis': surprise_analysis,
                'quality_assessment': quality_assessment,
                'earnings_forecast': earnings_forecast,
                'earnings_trends': earnings_trends,
                'earnings_recommendation': earnings_recommendation,
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing earnings: {e}")
            return {'error': str(e)}
    
    async def _get_earnings_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get earnings data untuk symbol"""
        try:
            # Try to get from database first
            earnings_data = self.db.query(EarningsData).filter(
                EarningsData.symbol == symbol
            ).order_by(EarningsData.earnings_date.desc()).all()
            
            if earnings_data:
                return {
                    'historical_earnings': [
                        {
                            'earnings_date': ed.earnings_date,
                            'eps_actual': ed.eps_actual,
                            'eps_estimate': ed.eps_estimate,
                            'revenue_actual': ed.revenue_actual,
                            'revenue_estimate': ed.revenue_estimate,
                            'surprise_percentage': ed.surprise_percentage
                        }
                        for ed in earnings_data
                    ]
                }
            
            # If not in database, get from Yahoo Finance
            ticker = yf.Ticker(symbol)
            
            # Get earnings data
            earnings_calendar = ticker.calendar
            earnings_history = ticker.earnings_history
            
            if earnings_calendar is None and earnings_history is None:
                return None
            
            earnings_data = {
                'earnings_calendar': earnings_calendar.to_dict() if earnings_calendar is not None else {},
                'earnings_history': earnings_history.to_dict() if earnings_history is not None else {}
            }
            
            # Store in database
            await self._store_earnings_data(symbol, earnings_data)
            
            return earnings_data
            
        except Exception as e:
            logger.error(f"Error getting earnings data: {e}")
            return None
    
    async def _calculate_earnings_metrics(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive earnings metrics"""
        try:
            metrics = {}
            
            # Get historical earnings
            historical_earnings = earnings_data.get('historical_earnings', [])
            if not historical_earnings:
                return {}
            
            # Calculate basic metrics
            eps_values = [e['eps_actual'] for e in historical_earnings if e['eps_actual'] is not None]
            revenue_values = [e['revenue_actual'] for e in historical_earnings if e['revenue_actual'] is not None]
            
            if not eps_values:
                return {}
            
            # Earnings growth
            if len(eps_values) >= 2:
                eps_growth = (eps_values[0] - eps_values[1]) / abs(eps_values[1]) if eps_values[1] != 0 else 0
                metrics['eps_growth'] = eps_growth
            
            # Revenue growth
            if len(revenue_values) >= 2:
                revenue_growth = (revenue_values[0] - revenue_values[1]) / abs(revenue_values[1]) if revenue_values[1] != 0 else 0
                metrics['revenue_growth'] = revenue_growth
            
            # Earnings consistency
            eps_changes = []
            for i in range(1, len(eps_values)):
                if eps_values[i-1] != 0:
                    change = (eps_values[i] - eps_values[i-1]) / abs(eps_values[i-1])
                    eps_changes.append(change)
            
            if eps_changes:
                eps_volatility = np.std(eps_changes)
                metrics['eps_volatility'] = eps_volatility
                
                # Consistency score (lower volatility = higher consistency)
                metrics['earnings_consistency'] = max(0, 1 - eps_volatility)
            
            # Average earnings
            metrics['average_eps'] = np.mean(eps_values)
            metrics['average_revenue'] = np.mean(revenue_values) if revenue_values else 0
            
            # Earnings quality score
            quality_score = await self._calculate_earnings_quality_score(eps_values, revenue_values)
            metrics['quality_score'] = quality_score
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating earnings metrics: {e}")
            return {}
    
    async def _calculate_earnings_quality_score(self, eps_values: List[float], revenue_values: List[float]) -> float:
        """Calculate earnings quality score"""
        try:
            if not eps_values:
                return 0.0
            
            score = 0.0
            
            # Growth consistency
            if len(eps_values) >= 2:
                eps_growth = (eps_values[0] - eps_values[1]) / abs(eps_values[1]) if eps_values[1] != 0 else 0
                if eps_growth > 0.1:
                    score += 0.3
                elif eps_growth > 0.05:
                    score += 0.2
                elif eps_growth > 0:
                    score += 0.1
            
            # Revenue growth alignment
            if len(revenue_values) >= 2 and len(eps_values) >= 2:
                revenue_growth = (revenue_values[0] - revenue_values[1]) / abs(revenue_values[1]) if revenue_values[1] != 0 else 0
                eps_growth = (eps_values[0] - eps_values[1]) / abs(eps_values[1]) if eps_values[1] != 0 else 0
                
                if revenue_growth > 0 and eps_growth > 0:
                    score += 0.3
                elif revenue_growth > 0 or eps_growth > 0:
                    score += 0.2
            
            # Earnings stability
            if len(eps_values) >= 3:
                eps_volatility = np.std(eps_values)
                if eps_volatility < 0.1:
                    score += 0.2
                elif eps_volatility < 0.2:
                    score += 0.1
            
            # Positive earnings
            positive_earnings = sum(1 for eps in eps_values if eps > 0)
            if positive_earnings == len(eps_values):
                score += 0.2
            elif positive_earnings >= len(eps_values) * 0.8:
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating earnings quality score: {e}")
            return 0.0
    
    async def _analyze_earnings_surprises(self, symbol: str, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze earnings surprises"""
        try:
            historical_earnings = earnings_data.get('historical_earnings', [])
            if not historical_earnings:
                return {}
            
            surprises = []
            surprise_percentages = []
            
            for earnings in historical_earnings:
                if earnings['eps_actual'] is not None and earnings['eps_estimate'] is not None:
                    surprise = (earnings['eps_actual'] - earnings['eps_estimate']) / abs(earnings['eps_estimate']) if earnings['eps_estimate'] != 0 else 0
                    surprises.append(surprise)
                    surprise_percentages.append(surprise)
            
            if not surprises:
                return {}
            
            # Calculate surprise metrics
            average_surprise = np.mean(surprises)
            surprise_volatility = np.std(surprises)
            positive_surprises = sum(1 for s in surprises if s > 0)
            negative_surprises = sum(1 for s in surprises if s < 0)
            
            # Categorize surprises
            surprise_categories = []
            for surprise in surprises:
                if surprise > self.surprise_thresholds['significant_surprise']:
                    surprise_categories.append('significant_positive')
                elif surprise > self.surprise_thresholds['positive_surprise']:
                    surprise_categories.append('positive')
                elif surprise < -self.surprise_thresholds['significant_surprise']:
                    surprise_categories.append('significant_negative')
                elif surprise < self.surprise_thresholds['negative_surprise']:
                    surprise_categories.append('negative')
                else:
                    surprise_categories.append('in_line')
            
            # Calculate surprise consistency
            surprise_consistency = positive_surprises / len(surprises) if surprises else 0
            
            return {
                'average_surprise': average_surprise,
                'surprise_volatility': surprise_volatility,
                'positive_surprises': positive_surprises,
                'negative_surprises': negative_surprises,
                'surprise_consistency': surprise_consistency,
                'surprise_categories': surprise_categories,
                'recent_surprises': surprises[:4] if len(surprises) >= 4 else surprises
            }
            
        except Exception as e:
            logger.error(f"Error analyzing earnings surprises: {e}")
            return {}
    
    async def _assess_earnings_quality(self, earnings_data: Dict[str, Any], earnings_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess earnings quality"""
        try:
            quality_assessment = {
                'overall_quality': 'medium',
                'quality_factors': [],
                'quality_score': 0.0
            }
            
            score = 0.0
            
            # Growth quality
            eps_growth = earnings_metrics.get('eps_growth', 0)
            revenue_growth = earnings_metrics.get('revenue_growth', 0)
            
            if eps_growth > self.quality_thresholds['earnings_growth']['excellent']:
                quality_assessment['quality_factors'].append('Excellent earnings growth')
                score += 0.3
            elif eps_growth > self.quality_thresholds['earnings_growth']['good']:
                quality_assessment['quality_factors'].append('Good earnings growth')
                score += 0.2
            elif eps_growth < self.quality_thresholds['earnings_growth']['poor']:
                quality_assessment['quality_factors'].append('Poor earnings growth')
                score -= 0.2
            
            if revenue_growth > self.quality_thresholds['revenue_growth']['excellent']:
                quality_assessment['quality_factors'].append('Excellent revenue growth')
                score += 0.2
            elif revenue_growth > self.quality_thresholds['revenue_growth']['good']:
                quality_assessment['quality_factors'].append('Good revenue growth')
                score += 0.1
            elif revenue_growth < self.quality_thresholds['revenue_growth']['poor']:
                quality_assessment['quality_factors'].append('Poor revenue growth')
                score -= 0.1
            
            # Consistency quality
            earnings_consistency = earnings_metrics.get('earnings_consistency', 0)
            if earnings_consistency > self.quality_thresholds['earnings_consistency']['excellent']:
                quality_assessment['quality_factors'].append('Excellent earnings consistency')
                score += 0.2
            elif earnings_consistency > self.quality_thresholds['earnings_consistency']['good']:
                quality_assessment['quality_factors'].append('Good earnings consistency')
                score += 0.1
            elif earnings_consistency < self.quality_thresholds['earnings_consistency']['poor']:
                quality_assessment['quality_factors'].append('Poor earnings consistency')
                score -= 0.1
            
            # Overall quality assessment
            if score >= 0.6:
                quality_assessment['overall_quality'] = 'high'
            elif score >= 0.3:
                quality_assessment['overall_quality'] = 'medium'
            else:
                quality_assessment['overall_quality'] = 'low'
            
            quality_assessment['quality_score'] = score
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Error assessing earnings quality: {e}")
            return {'overall_quality': 'unknown', 'quality_factors': [], 'quality_score': 0.0}
    
    async def _generate_earnings_forecast(self, symbol: str, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate earnings forecast"""
        try:
            historical_earnings = earnings_data.get('historical_earnings', [])
            if not historical_earnings:
                return {}
            
            # Get recent earnings data
            recent_earnings = historical_earnings[:4] if len(historical_earnings) >= 4 else historical_earnings
            
            # Calculate growth trends
            eps_values = [e['eps_actual'] for e in recent_earnings if e['eps_actual'] is not None]
            revenue_values = [e['revenue_actual'] for e in recent_earnings if e['revenue_actual'] is not None]
            
            if not eps_values:
                return {}
            
            # Simple linear trend forecasting
            eps_trend = np.polyfit(range(len(eps_values)), eps_values, 1)[0] if len(eps_values) > 1 else 0
            revenue_trend = np.polyfit(range(len(revenue_values)), revenue_values, 1)[0] if len(revenue_values) > 1 else 0
            
            # Forecast next quarter
            next_eps = eps_values[0] + eps_trend if eps_values else 0
            next_revenue = revenue_values[0] + revenue_trend if revenue_values else 0
            
            # Calculate confidence based on historical accuracy
            confidence = await self._calculate_forecast_confidence(historical_earnings)
            
            return {
                'next_quarter_eps': next_eps,
                'next_quarter_revenue': next_revenue,
                'eps_trend': eps_trend,
                'revenue_trend': revenue_trend,
                'confidence': confidence,
                'forecast_method': 'linear_trend'
            }
            
        except Exception as e:
            logger.error(f"Error generating earnings forecast: {e}")
            return {}
    
    async def _calculate_forecast_confidence(self, historical_earnings: List[Dict[str, Any]]) -> float:
        """Calculate forecast confidence based on historical accuracy"""
        try:
            if len(historical_earnings) < 2:
                return 0.5
            
            # Calculate historical forecast accuracy
            accuracies = []
            for i in range(1, len(historical_earnings)):
                actual = historical_earnings[i-1]['eps_actual']
                estimate = historical_earnings[i]['eps_estimate']
                
                if actual is not None and estimate is not None and estimate != 0:
                    accuracy = 1 - abs(actual - estimate) / abs(estimate)
                    accuracies.append(accuracy)
            
            if not accuracies:
                return 0.5
            
            # Average accuracy
            average_accuracy = np.mean(accuracies)
            
            # Adjust confidence based on data quality
            confidence = average_accuracy * 0.8 + 0.2  # Base confidence of 20%
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating forecast confidence: {e}")
            return 0.5
    
    async def _calculate_earnings_trends(self, earnings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate earnings trends"""
        try:
            historical_earnings = earnings_data.get('historical_earnings', [])
            if not historical_earnings:
                return {}
            
            # Get earnings data
            eps_values = [e['eps_actual'] for e in historical_earnings if e['eps_actual'] is not None]
            revenue_values = [e['revenue_actual'] for e in historical_earnings if e['revenue_actual'] is not None]
            
            if not eps_values:
                return {}
            
            # Calculate trends
            trends = {}
            
            # EPS trend
            if len(eps_values) >= 2:
                eps_trend = (eps_values[0] - eps_values[-1]) / abs(eps_values[-1]) if eps_values[-1] != 0 else 0
                trends['eps_trend'] = eps_trend
                trends['eps_trend_direction'] = 'increasing' if eps_trend > 0 else 'decreasing' if eps_trend < 0 else 'stable'
            
            # Revenue trend
            if len(revenue_values) >= 2:
                revenue_trend = (revenue_values[0] - revenue_values[-1]) / abs(revenue_values[-1]) if revenue_values[-1] != 0 else 0
                trends['revenue_trend'] = revenue_trend
                trends['revenue_trend_direction'] = 'increasing' if revenue_trend > 0 else 'decreasing' if revenue_trend < 0 else 'stable'
            
            # Volatility trend
            if len(eps_values) >= 3:
                eps_volatility = np.std(eps_values)
                trends['eps_volatility'] = eps_volatility
                trends['volatility_trend'] = 'high' if eps_volatility > 0.2 else 'medium' if eps_volatility > 0.1 else 'low'
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating earnings trends: {e}")
            return {}
    
    async def _generate_earnings_recommendation(
        self, 
        symbol: str, 
        earnings_metrics: Dict[str, Any], 
        surprise_analysis: Dict[str, Any], 
        quality_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate earnings-based investment recommendation"""
        try:
            recommendation = {
                'action': 'hold',
                'confidence': 'medium',
                'reasons': [],
                'risks': [],
                'score': 0
            }
            
            score = 0
            
            # Earnings growth assessment
            eps_growth = earnings_metrics.get('eps_growth', 0)
            if eps_growth > 0.1:
                recommendation['reasons'].append('Strong earnings growth')
                score += 2
            elif eps_growth > 0.05:
                recommendation['reasons'].append('Moderate earnings growth')
                score += 1
            elif eps_growth < -0.05:
                recommendation['risks'].append('Declining earnings')
                score -= 2
            
            # Revenue growth assessment
            revenue_growth = earnings_metrics.get('revenue_growth', 0)
            if revenue_growth > 0.1:
                recommendation['reasons'].append('Strong revenue growth')
                score += 1
            elif revenue_growth < -0.05:
                recommendation['risks'].append('Declining revenue')
                score -= 1
            
            # Earnings quality assessment
            quality_score = earnings_metrics.get('quality_score', 0)
            if quality_score > 0.7:
                recommendation['reasons'].append('High earnings quality')
                score += 1
            elif quality_score < 0.3:
                recommendation['risks'].append('Low earnings quality')
                score -= 1
            
            # Surprise analysis
            surprise_consistency = surprise_analysis.get('surprise_consistency', 0)
            if surprise_consistency > 0.7:
                recommendation['reasons'].append('Consistent positive surprises')
                score += 1
            elif surprise_consistency < 0.3:
                recommendation['risks'].append('Frequent negative surprises')
                score -= 1
            
            # Overall quality assessment
            overall_quality = quality_assessment.get('overall_quality', 'medium')
            if overall_quality == 'high':
                recommendation['reasons'].append('High overall earnings quality')
                score += 1
            elif overall_quality == 'low':
                recommendation['risks'].append('Low overall earnings quality')
                score -= 1
            
            # Determine action
            if score >= 4:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = 'high'
            elif score >= 2:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = 'medium'
            elif score <= -4:
                recommendation['action'] = 'sell'
                recommendation['confidence'] = 'high'
            elif score <= -2:
                recommendation['action'] = 'sell'
                recommendation['confidence'] = 'medium'
            else:
                recommendation['action'] = 'hold'
                recommendation['confidence'] = 'medium'
            
            recommendation['score'] = score
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating earnings recommendation: {e}")
            return {'action': 'hold', 'confidence': 'low', 'reasons': [], 'risks': [], 'score': 0}
    
    async def _store_earnings_data(self, symbol: str, earnings_data: Dict[str, Any]):
        """Store earnings data in database"""
        try:
            # This would implement storing earnings data
            # For now, just log
            logger.info(f"Storing earnings data for {symbol}")
            
        except Exception as e:
            logger.error(f"Error storing earnings data: {e}")
    
    async def get_earnings_calendar(self, symbol: str) -> Dict[str, Any]:
        """Get earnings calendar untuk symbol"""
        try:
            ticker = yf.Ticker(symbol)
            calendar = ticker.calendar
            
            if calendar is None:
                return {'error': 'No earnings calendar data available'}
            
            return {
                'success': True,
                'earnings_calendar': calendar.to_dict(),
                'next_earnings_date': calendar.index[0] if len(calendar.index) > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings calendar: {e}")
            return {'error': str(e)}
    
    async def get_earnings_surprises(self, symbol: str) -> Dict[str, Any]:
        """Get earnings surprises untuk symbol"""
        try:
            ticker = yf.Ticker(symbol)
            earnings_history = ticker.earnings_history
            
            if earnings_history is None:
                return {'error': 'No earnings history data available'}
            
            # Calculate surprise statistics
            surprises = []
            for date, row in earnings_history.iterrows():
                if 'Surprise' in row and pd.notna(row['Surprise']):
                    surprises.append(row['Surprise'])
            
            if not surprises:
                return {'error': 'No surprise data available'}
            
            surprise_stats = {
                'average_surprise': np.mean(surprises),
                'surprise_volatility': np.std(surprises),
                'positive_surprises': sum(1 for s in surprises if s > 0),
                'negative_surprises': sum(1 for s in surprises if s < 0),
                'total_surprises': len(surprises)
            }
            
            return {
                'success': True,
                'surprise_stats': surprise_stats,
                'recent_surprises': surprises[:4] if len(surprises) >= 4 else surprises
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings surprises: {e}")
            return {'error': str(e)}
