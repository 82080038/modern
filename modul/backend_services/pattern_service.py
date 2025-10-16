"""
Pattern Recognition Service untuk Multi-timeframe Analysis
"""
from sqlalchemy.orm import Session
from app.services.data_service import DataService
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import linregress

logger = logging.getLogger(__name__)

class PatternRecognitionService:
    """Service untuk pattern recognition dan multi-timeframe analysis"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
        
        # Pattern definitions
        self.patterns = {
            'head_and_shoulders': {
                'name': 'Head and Shoulders',
                'description': 'Reversal pattern with three peaks',
                'timeframe_min': '1D',
                'confidence_threshold': 0.7
            },
            'double_top': {
                'name': 'Double Top',
                'description': 'Reversal pattern with two equal peaks',
                'timeframe_min': '1D',
                'confidence_threshold': 0.6
            },
            'double_bottom': {
                'name': 'Double Bottom',
                'description': 'Reversal pattern with two equal troughs',
                'timeframe_min': '1D',
                'confidence_threshold': 0.6
            },
            'triangle_ascending': {
                'name': 'Ascending Triangle',
                'description': 'Continuation pattern with horizontal resistance',
                'timeframe_min': '1D',
                'confidence_threshold': 0.6
            },
            'triangle_descending': {
                'name': 'Descending Triangle',
                'description': 'Continuation pattern with horizontal support',
                'timeframe_min': '1D',
                'confidence_threshold': 0.6
            },
            'flag_bullish': {
                'name': 'Bullish Flag',
                'description': 'Continuation pattern after uptrend',
                'timeframe_min': '1h',
                'confidence_threshold': 0.5
            },
            'flag_bearish': {
                'name': 'Bearish Flag',
                'description': 'Continuation pattern after downtrend',
                'timeframe_min': '1h',
                'confidence_threshold': 0.5
            },
            'wedge_rising': {
                'name': 'Rising Wedge',
                'description': 'Bearish reversal pattern',
                'timeframe_min': '1D',
                'confidence_threshold': 0.6
            },
            'wedge_falling': {
                'name': 'Falling Wedge',
                'description': 'Bullish reversal pattern',
                'timeframe_min': '1D',
                'confidence_threshold': 0.6
            }
        }
    
    def detect_patterns(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """Detect patterns across multiple timeframes"""
        try:
            if not timeframes:
                timeframes = ['1D', '1W', '1M']
            
            all_patterns = {}
            
            for timeframe in timeframes:
                # Get historical data
                historical_data = self.data_service.get_historical_candlestick_data(
                    symbol, timeframe, datetime.now() - timedelta(days=365), datetime.now()
                )
                
                if not historical_data or len(historical_data) < 50:
                    continue
                
                # Detect patterns for this timeframe
                patterns = self._detect_patterns_for_timeframe(historical_data, timeframe)
                all_patterns[timeframe] = patterns
            
            return {
                'symbol': symbol,
                'timeframes_analyzed': timeframes,
                'patterns_found': all_patterns,
                'total_patterns': sum(len(patterns) for patterns in all_patterns.values()),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {"error": str(e)}
    
    def _detect_patterns_for_timeframe(self, data: List[Dict], timeframe: str) -> List[Dict]:
        """Detect patterns for a specific timeframe"""
        try:
            patterns_found = []
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Detect each pattern type
            for pattern_type, pattern_info in self.patterns.items():
                if self._is_timeframe_suitable(timeframe, pattern_info['timeframe_min']):
                    pattern_result = self._detect_specific_pattern(df, pattern_type, pattern_info)
                    if pattern_result:
                        patterns_found.append(pattern_result)
            
            return patterns_found
            
        except Exception as e:
            logger.error(f"Error detecting patterns for timeframe {timeframe}: {e}")
            return []
    
    def _detect_specific_pattern(self, df: pd.DataFrame, pattern_type: str, pattern_info: Dict) -> Optional[Dict]:
        """Detect a specific pattern type"""
        try:
            if pattern_type == 'head_and_shoulders':
                return self._detect_head_and_shoulders(df, pattern_info)
            elif pattern_type == 'double_top':
                return self._detect_double_top(df, pattern_info)
            elif pattern_type == 'double_bottom':
                return self._detect_double_bottom(df, pattern_info)
            elif pattern_type == 'triangle_ascending':
                return self._detect_ascending_triangle(df, pattern_info)
            elif pattern_type == 'triangle_descending':
                return self._detect_descending_triangle(df, pattern_info)
            elif pattern_type == 'flag_bullish':
                return self._detect_bullish_flag(df, pattern_info)
            elif pattern_type == 'flag_bearish':
                return self._detect_bearish_flag(df, pattern_info)
            elif pattern_type == 'wedge_rising':
                return self._detect_rising_wedge(df, pattern_info)
            elif pattern_type == 'wedge_falling':
                return self._detect_falling_wedge(df, pattern_info)
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting {pattern_type}: {e}")
            return None
    
    def _detect_head_and_shoulders(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Head and Shoulders pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Find peaks
            peaks = self._find_peaks(df['high'].values)
            
            if len(peaks) < 3:
                return None
            
            # Look for H&S pattern in recent data
            recent_peaks = peaks[-10:]  # Last 10 peaks
            
            for i in range(len(recent_peaks) - 2):
                left_shoulder = recent_peaks[i]
                head = recent_peaks[i + 1]
                right_shoulder = recent_peaks[i + 2]
                
                # Check H&S conditions
                if (self._is_head_and_shoulders(left_shoulder, head, right_shoulder, df)):
                    confidence = self._calculate_hs_confidence(left_shoulder, head, right_shoulder, df)
                    
                    if confidence >= pattern_info['confidence_threshold']:
                        return {
                            'pattern_type': 'head_and_shoulders',
                            'name': pattern_info['name'],
                            'description': pattern_info['description'],
                            'confidence': confidence,
                            'left_shoulder': {
                                'index': left_shoulder,
                                'price': df.iloc[left_shoulder]['high'],
                                'date': df.index[left_shoulder].isoformat()
                            },
                            'head': {
                                'index': head,
                                'price': df.iloc[head]['high'],
                                'date': df.index[head].isoformat()
                            },
                            'right_shoulder': {
                                'index': right_shoulder,
                                'price': df.iloc[right_shoulder]['high'],
                                'date': df.index[right_shoulder].isoformat()
                            },
                            'neckline': self._calculate_neckline(df, left_shoulder, right_shoulder),
                            'target_price': self._calculate_hs_target(df, left_shoulder, head, right_shoulder)
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Head and Shoulders: {e}")
            return None
    
    def _detect_double_top(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Double Top pattern"""
        try:
            if len(df) < 20:
                return None
            
            peaks = self._find_peaks(df['high'].values)
            
            if len(peaks) < 2:
                return None
            
            # Look for double top in recent data
            recent_peaks = peaks[-5:]
            
            for i in range(len(recent_peaks) - 1):
                peak1 = recent_peaks[i]
                peak2 = recent_peaks[i + 1]
                
                if self._is_double_top(peak1, peak2, df):
                    confidence = self._calculate_double_top_confidence(peak1, peak2, df)
                    
                    if confidence >= pattern_info['confidence_threshold']:
                        return {
                            'pattern_type': 'double_top',
                            'name': pattern_info['name'],
                            'description': pattern_info['description'],
                            'confidence': confidence,
                            'peak1': {
                                'index': peak1,
                                'price': df.iloc[peak1]['high'],
                                'date': df.index[peak1].isoformat()
                            },
                            'peak2': {
                                'index': peak2,
                                'price': df.iloc[peak2]['high'],
                                'date': df.index[peak2].isoformat()
                            },
                            'trough': self._find_trough_between_peaks(df, peak1, peak2),
                            'target_price': self._calculate_double_top_target(df, peak1, peak2)
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Double Top: {e}")
            return None
    
    def _detect_double_bottom(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Double Bottom pattern"""
        try:
            if len(df) < 20:
                return None
            
            troughs = self._find_troughs(df['low'].values)
            
            if len(troughs) < 2:
                return None
            
            # Look for double bottom in recent data
            recent_troughs = troughs[-5:]
            
            for i in range(len(recent_troughs) - 1):
                trough1 = recent_troughs[i]
                trough2 = recent_troughs[i + 1]
                
                if self._is_double_bottom(trough1, trough2, df):
                    confidence = self._calculate_double_bottom_confidence(trough1, trough2, df)
                    
                    if confidence >= pattern_info['confidence_threshold']:
                        return {
                            'pattern_type': 'double_bottom',
                            'name': pattern_info['name'],
                            'description': pattern_info['description'],
                            'confidence': confidence,
                            'trough1': {
                                'index': trough1,
                                'price': df.iloc[trough1]['low'],
                                'date': df.index[trough1].isoformat()
                            },
                            'trough2': {
                                'index': trough2,
                                'price': df.iloc[trough2]['low'],
                                'date': df.index[trough2].isoformat()
                            },
                            'peak': self._find_peak_between_troughs(df, trough1, trough2),
                            'target_price': self._calculate_double_bottom_target(df, trough1, trough2)
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Double Bottom: {e}")
            return None
    
    def _detect_ascending_triangle(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Ascending Triangle pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Find resistance and support levels
            resistance = self._find_resistance_level(df)
            support_trend = self._find_support_trend(df)
            
            if resistance and support_trend and support_trend['slope'] > 0:
                confidence = self._calculate_triangle_confidence(df, resistance, support_trend)
                
                if confidence >= pattern_info['confidence_threshold']:
                    return {
                        'pattern_type': 'triangle_ascending',
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'confidence': confidence,
                        'resistance_level': resistance,
                        'support_trend': support_trend,
                        'breakout_target': self._calculate_triangle_breakout_target(df, resistance, support_trend)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Ascending Triangle: {e}")
            return None
    
    def _detect_descending_triangle(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Descending Triangle pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Find support and resistance levels
            support = self._find_support_level(df)
            resistance_trend = self._find_resistance_trend(df)
            
            if support and resistance_trend and resistance_trend['slope'] < 0:
                confidence = self._calculate_triangle_confidence(df, support, resistance_trend)
                
                if confidence >= pattern_info['confidence_threshold']:
                    return {
                        'pattern_type': 'triangle_descending',
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'confidence': confidence,
                        'support_level': support,
                        'resistance_trend': resistance_trend,
                        'breakout_target': self._calculate_triangle_breakout_target(df, support, resistance_trend)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Descending Triangle: {e}")
            return None
    
    def _detect_bullish_flag(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Bullish Flag pattern"""
        try:
            if len(df) < 10:
                return None
            
            # Look for flag pattern in recent data
            recent_data = df.tail(20)
            
            # Check for uptrend followed by consolidation
            uptrend = self._detect_uptrend(recent_data.head(10))
            consolidation = self._detect_consolidation(recent_data.tail(10))
            
            if uptrend and consolidation:
                confidence = self._calculate_flag_confidence(recent_data, uptrend, consolidation)
                
                if confidence >= pattern_info['confidence_threshold']:
                    return {
                        'pattern_type': 'flag_bullish',
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'confidence': confidence,
                        'uptrend': uptrend,
                        'consolidation': consolidation,
                        'target_price': self._calculate_flag_target(recent_data, uptrend, consolidation)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Bullish Flag: {e}")
            return None
    
    def _detect_bearish_flag(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Bearish Flag pattern"""
        try:
            if len(df) < 10:
                return None
            
            # Look for flag pattern in recent data
            recent_data = df.tail(20)
            
            # Check for downtrend followed by consolidation
            downtrend = self._detect_downtrend(recent_data.head(10))
            consolidation = self._detect_consolidation(recent_data.tail(10))
            
            if downtrend and consolidation:
                confidence = self._calculate_flag_confidence(recent_data, downtrend, consolidation)
                
                if confidence >= pattern_info['confidence_threshold']:
                    return {
                        'pattern_type': 'flag_bearish',
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'confidence': confidence,
                        'downtrend': downtrend,
                        'consolidation': consolidation,
                        'target_price': self._calculate_flag_target(recent_data, downtrend, consolidation)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Bearish Flag: {e}")
            return None
    
    def _detect_rising_wedge(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Rising Wedge pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Find support and resistance trends
            support_trend = self._find_support_trend(df)
            resistance_trend = self._find_resistance_trend(df)
            
            if (support_trend and resistance_trend and 
                support_trend['slope'] > 0 and resistance_trend['slope'] > 0 and
                support_trend['slope'] > resistance_trend['slope']):
                
                confidence = self._calculate_wedge_confidence(df, support_trend, resistance_trend)
                
                if confidence >= pattern_info['confidence_threshold']:
                    return {
                        'pattern_type': 'wedge_rising',
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'confidence': confidence,
                        'support_trend': support_trend,
                        'resistance_trend': resistance_trend,
                        'target_price': self._calculate_wedge_target(df, support_trend, resistance_trend)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Rising Wedge: {e}")
            return None
    
    def _detect_falling_wedge(self, df: pd.DataFrame, pattern_info: Dict) -> Optional[Dict]:
        """Detect Falling Wedge pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Find support and resistance trends
            support_trend = self._find_support_trend(df)
            resistance_trend = self._find_resistance_trend(df)
            
            if (support_trend and resistance_trend and 
                support_trend['slope'] < 0 and resistance_trend['slope'] < 0 and
                support_trend['slope'] < resistance_trend['slope']):
                
                confidence = self._calculate_wedge_confidence(df, support_trend, resistance_trend)
                
                if confidence >= pattern_info['confidence_threshold']:
                    return {
                        'pattern_type': 'wedge_falling',
                        'name': pattern_info['name'],
                        'description': pattern_info['description'],
                        'confidence': confidence,
                        'support_trend': support_trend,
                        'resistance_trend': resistance_trend,
                        'target_price': self._calculate_wedge_target(df, support_trend, resistance_trend)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting Falling Wedge: {e}")
            return None
    
    # Helper methods for pattern detection
    def _find_peaks(self, data: np.ndarray, prominence: float = 0.02) -> List[int]:
        """Find peaks in data"""
        try:
            peaks, _ = signal.find_peaks(data, prominence=prominence)
            return peaks.tolist()
        except:
            return []
    
    def _find_troughs(self, data: np.ndarray, prominence: float = 0.02) -> List[int]:
        """Find troughs in data"""
        try:
            troughs, _ = signal.find_peaks(-data, prominence=prominence)
            return troughs.tolist()
        except:
            return []
    
    def _is_head_and_shoulders(self, left_shoulder: int, head: int, right_shoulder: int, df: pd.DataFrame) -> bool:
        """Check if pattern is Head and Shoulders"""
        try:
            # Head should be higher than both shoulders
            head_price = df.iloc[head]['high']
            left_price = df.iloc[left_shoulder]['high']
            right_price = df.iloc[right_shoulder]['high']
            
            if head_price <= left_price or head_price <= right_price:
                return False
            
            # Shoulders should be roughly equal
            shoulder_diff = abs(left_price - right_price) / left_price
            if shoulder_diff > 0.05:  # 5% tolerance
                return False
            
            # Check timing (shoulders should be roughly equidistant from head)
            left_distance = head - left_shoulder
            right_distance = right_shoulder - head
            distance_diff = abs(left_distance - right_distance) / max(left_distance, right_distance)
            
            if distance_diff > 0.3:  # 30% tolerance
                return False
            
            return True
            
        except:
            return False
    
    def _is_double_top(self, peak1: int, peak2: int, df: pd.DataFrame) -> bool:
        """Check if pattern is Double Top"""
        try:
            peak1_price = df.iloc[peak1]['high']
            peak2_price = df.iloc[peak2]['high']
            
            # Peaks should be roughly equal
            price_diff = abs(peak1_price - peak2_price) / peak1_price
            if price_diff > 0.03:  # 3% tolerance
                return False
            
            # Check timing (peaks should be reasonably close)
            time_diff = peak2 - peak1
            if time_diff < 5 or time_diff > 50:  # Between 5 and 50 periods
                return False
            
            return True
            
        except:
            return False
    
    def _is_double_bottom(self, trough1: int, trough2: int, df: pd.DataFrame) -> bool:
        """Check if pattern is Double Bottom"""
        try:
            trough1_price = df.iloc[trough1]['low']
            trough2_price = df.iloc[trough2]['low']
            
            # Troughs should be roughly equal
            price_diff = abs(trough1_price - trough2_price) / trough1_price
            if price_diff > 0.03:  # 3% tolerance
                return False
            
            # Check timing (troughs should be reasonably close)
            time_diff = trough2 - trough1
            if time_diff < 5 or time_diff > 50:  # Between 5 and 50 periods
                return False
            
            return True
            
        except:
            return False
    
    def _is_timeframe_suitable(self, timeframe: str, min_timeframe: str) -> bool:
        """Check if timeframe is suitable for pattern detection"""
        timeframe_order = ['1m', '5m', '15m', '1h', '4h', '1D', '1W', '1M']
        
        try:
            current_index = timeframe_order.index(timeframe)
            min_index = timeframe_order.index(min_timeframe)
            return current_index >= min_index
        except:
            return False
    
    # Confidence calculation methods
    def _calculate_hs_confidence(self, left_shoulder: int, head: int, right_shoulder: int, df: pd.DataFrame) -> float:
        """Calculate Head and Shoulders confidence"""
        try:
            confidence = 0.5  # Base confidence
            
            # Head prominence
            head_price = df.iloc[head]['high']
            left_price = df.iloc[left_shoulder]['high']
            right_price = df.iloc[right_shoulder]['high']
            
            head_prominence = (head_price - max(left_price, right_price)) / max(left_price, right_price)
            confidence += min(head_prominence * 2, 0.3)
            
            # Shoulder symmetry
            shoulder_diff = abs(left_price - right_price) / left_price
            confidence += max(0, 0.2 - shoulder_diff * 4)
            
            return min(confidence, 1.0)
            
        except:
            return 0.0
    
    def _calculate_double_top_confidence(self, peak1: int, peak2: int, df: pd.DataFrame) -> float:
        """Calculate Double Top confidence"""
        try:
            confidence = 0.5  # Base confidence
            
            # Price similarity
            peak1_price = df.iloc[peak1]['high']
            peak2_price = df.iloc[peak2]['high']
            price_diff = abs(peak1_price - peak2_price) / peak1_price
            confidence += max(0, 0.3 - price_diff * 6)
            
            # Volume confirmation (if available)
            if 'volume' in df.columns:
                vol1 = df.iloc[peak1]['volume']
                vol2 = df.iloc[peak2]['volume']
                if vol1 > 0 and vol2 > 0:
                    vol_ratio = min(vol1, vol2) / max(vol1, vol2)
                    confidence += vol_ratio * 0.2
            
            return min(confidence, 1.0)
            
        except:
            return 0.0
    
    def _calculate_double_bottom_confidence(self, trough1: int, trough2: int, df: pd.DataFrame) -> float:
        """Calculate Double Bottom confidence"""
        try:
            confidence = 0.5  # Base confidence
            
            # Price similarity
            trough1_price = df.iloc[trough1]['low']
            trough2_price = df.iloc[trough2]['low']
            price_diff = abs(trough1_price - trough2_price) / trough1_price
            confidence += max(0, 0.3 - price_diff * 6)
            
            # Volume confirmation (if available)
            if 'volume' in df.columns:
                vol1 = df.iloc[trough1]['volume']
                vol2 = df.iloc[trough2]['volume']
                if vol1 > 0 and vol2 > 0:
                    vol_ratio = min(vol1, vol2) / max(vol1, vol2)
                    confidence += vol_ratio * 0.2
            
            return min(confidence, 1.0)
            
        except:
            return 0.0
    
    # Additional helper methods would be implemented here
    # (Support/resistance detection, trend analysis, etc.)
    
    def get_support_resistance_levels(self, symbol: str, timeframe: str = '1D') -> Dict:
        """Get support and resistance levels for a symbol"""
        try:
            # Get historical data
            historical_data = self.data_service.get_historical_candlestick_data(
                symbol, timeframe, datetime.now() - timedelta(days=365), datetime.now()
            )
            
            if not historical_data or len(historical_data) < 50:
                return {"error": "Insufficient data"}
            
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Find support and resistance levels
            support_levels = self._find_support_levels(df)
            resistance_levels = self._find_resistance_levels(df)
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting support/resistance levels: {e}")
            return {"error": str(e)}
    
    def _find_support_levels(self, df: pd.DataFrame) -> List[Dict]:
        """Find support levels"""
        try:
            # Find significant lows
            lows = self._find_troughs(df['low'].values)
            support_levels = []
            
            for low in lows:
                price = df.iloc[low]['low']
                date = df.index[low]
                
                # Check if this level has been tested multiple times
                touches = self._count_level_touches(df, price, 'support')
                
                if touches >= 2:  # At least 2 touches
                    support_levels.append({
                        'price': price,
                        'date': date.isoformat(),
                        'touches': touches,
                        'strength': min(touches / 5, 1.0)  # Strength based on touches
                    })
            
            # Sort by strength
            support_levels.sort(key=lambda x: x['strength'], reverse=True)
            return support_levels[:5]  # Top 5 support levels
            
        except Exception as e:
            logger.error(f"Error finding support levels: {e}")
            return []
    
    def _find_resistance_levels(self, df: pd.DataFrame) -> List[Dict]:
        """Find resistance levels"""
        try:
            # Find significant highs
            highs = self._find_peaks(df['high'].values)
            resistance_levels = []
            
            for high in highs:
                price = df.iloc[high]['high']
                date = df.index[high]
                
                # Check if this level has been tested multiple times
                touches = self._count_level_touches(df, price, 'resistance')
                
                if touches >= 2:  # At least 2 touches
                    resistance_levels.append({
                        'price': price,
                        'date': date.isoformat(),
                        'touches': touches,
                        'strength': min(touches / 5, 1.0)  # Strength based on touches
                    })
            
            # Sort by strength
            resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
            return resistance_levels[:5]  # Top 5 resistance levels
            
        except Exception as e:
            logger.error(f"Error finding resistance levels: {e}")
            return []
    
    def _count_level_touches(self, df: pd.DataFrame, level: float, level_type: str) -> int:
        """Count how many times a price level has been touched"""
        try:
            touches = 0
            tolerance = level * 0.02  # 2% tolerance
            
            if level_type == 'support':
                for low in df['low']:
                    if abs(low - level) <= tolerance:
                        touches += 1
            else:  # resistance
                for high in df['high']:
                    if abs(high - level) <= tolerance:
                        touches += 1
            
            return touches
            
        except:
            return 0
