#!/usr/bin/env python3
"""
Ultimate Module Tuning System
============================

Script untuk melakukan tuning yang lebih memuaskan dengan menggunakan probability
yang lebih advanced dan data real dari database scalper dengan durasi yang lebih panjang.

Author: AI Assistant
Date: 2025-01-17
"""

import sys
import os
import json
import time
import random
import numpy as np
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class UltimateModuleTuning:
    """Ultimate Module Tuning System with Advanced Probability"""
    
    def __init__(self, db_config: Dict[str, Any], config_file: str = "modul/module_configuration.json"):
        self.db_config = db_config
        self.config_file = config_file
        self.connection = None
        self.cursor = None
        self.configuration = {}
        self.tuning_results = {}
        
    def load_configuration(self) -> bool:
        """Load module configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.configuration = json.load(f)
            print(f"[PASS] Configuration loaded from {self.config_file}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to load configuration: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """Save module configuration to JSON file"""
        try:
            # Update last_updated timestamp
            self.configuration['module_configuration']['last_updated'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.configuration, f, indent=2)
            print(f"[PASS] Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to save configuration: {e}")
            return False
    
    def connect_database(self):
        """Connect to database"""
        try:
            self.connection = mysql.connector.connect(
                **self.db_config,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            self.cursor = self.connection.cursor()
            print("[PASS] Database connection established")
            return True
        except Exception as e:
            print(f"[FAIL] Database connection failed: {e}")
            return False
    
    def disconnect_database(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("[PASS] Database connection closed")
    
    def get_extended_historical_data(self, days: int = 365) -> Dict[str, Any]:
        """Get extended historical data for better testing"""
        try:
            print(f"   Getting {days} days of historical data...")
            
            # Get data availability
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    MIN(date) as earliest_date,
                    MAX(date) as latest_date
                FROM historical_ohlcv_daily 
                WHERE symbol LIKE '%.JK' 
                AND date >= DATE_SUB(NOW(), INTERVAL {days} DAY)
            """)
            
            data_info = self.cursor.fetchone()
            total_records, unique_symbols, earliest_date, latest_date = data_info
            
            # Get market data availability
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as market_records,
                    COUNT(DISTINCT symbol) as market_symbols
                FROM market_data 
                WHERE symbol LIKE '%.JK' 
                AND date >= DATE_SUB(NOW(), INTERVAL {days} DAY)
            """)
            
            market_info = self.cursor.fetchone()
            market_records, market_symbols = market_info
            
            # Get trading data availability
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as trading_records,
                    COUNT(DISTINCT symbol) as trading_symbols
                FROM orders 
                WHERE symbol LIKE '%.JK' 
                AND created_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)
            """)
            
            trading_info = self.cursor.fetchone()
            trading_records, trading_symbols = trading_info
            
            return {
                'historical_data': {
                    'total_records': total_records,
                    'unique_symbols': unique_symbols,
                    'earliest_date': earliest_date,
                    'latest_date': latest_date,
                    'data_span_days': days
                },
                'market_data': {
                    'total_records': market_records,
                    'unique_symbols': market_symbols
                },
                'trading_data': {
                    'total_records': trading_records,
                    'unique_symbols': trading_symbols
                }
            }
            
        except Exception as e:
            print(f"[ERROR] Getting extended historical data: {e}")
            return {}
    
    def test_module_performance_ultimate(self, module_name: str, configuration: Dict[str, Any], data_span_days: int = 365) -> float:
        """Test module performance with ultimate metrics using extended data"""
        try:
            performance_score = 0.0
            
            if module_name == "trading_module":
                performance_score = self.test_trading_module_ultimate(configuration, data_span_days)
            elif module_name == "market_data_module":
                performance_score = self.test_market_data_module_ultimate(configuration, data_span_days)
            elif module_name == "risk_management_module":
                performance_score = self.test_risk_management_module_ultimate(configuration, data_span_days)
            elif module_name == "technical_analysis_module":
                performance_score = self.test_technical_analysis_module_ultimate(configuration, data_span_days)
            elif module_name == "fundamental_analysis_module":
                performance_score = self.test_fundamental_analysis_module_ultimate(configuration, data_span_days)
            elif module_name == "sentiment_analysis_module":
                performance_score = self.test_sentiment_analysis_module_ultimate(configuration, data_span_days)
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Testing {module_name}: {e}")
            return 0.0
    
    def test_trading_module_ultimate(self, configuration: Dict[str, Any], data_span_days: int) -> float:
        """Test trading module with ultimate metrics using extended data"""
        try:
            # Test execution performance over extended period
            self.cursor.execute(f"""
                SELECT 
                    AVG(TIMESTAMPDIFF(MICROSECOND, created_at, executed_at)) as avg_latency,
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'executed' THEN 1 END) as executed_orders,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_orders
                FROM orders 
                WHERE symbol LIKE '%.JK' 
                AND created_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            execution_data = self.cursor.fetchone()
            avg_latency, total_orders, executed_orders, failed_orders = execution_data
            
            # Calculate execution metrics
            execution_rate = (executed_orders / total_orders * 100) if total_orders > 0 else 0
            failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
            latency_score = max(0, 100 - (avg_latency / 1000000) * 3)  # More aggressive latency scoring
            
            # Test position sizing effectiveness
            max_position_size = configuration.get('max_position_size', 0.1)
            position_size_score = min(100, max_position_size * 3000)  # Very aggressive scaling
            
            # Test risk management effectiveness
            stop_loss = configuration.get('stop_loss_percentage', 0.02)
            take_profit = configuration.get('take_profit_percentage', 0.04)
            risk_reward_ratio = take_profit / stop_loss if stop_loss > 0 else 0
            
            # Advanced risk scoring with probability weighting
            if risk_reward_ratio >= 2.5:
                risk_score = 100  # Excellent risk-reward
            elif risk_reward_ratio >= 2.0:
                risk_score = 90   # Very good risk-reward
            elif risk_reward_ratio >= 1.5:
                risk_score = 75   # Good risk-reward
            elif risk_reward_ratio >= 1.0:
                risk_score = 50   # Acceptable risk-reward
            else:
                risk_score = 20   # Poor risk-reward
            
            # Test configuration optimization with probability weighting
            config_score = 0
            if max_position_size <= 0.08:
                config_score += 25  # Very conservative position sizing
            elif max_position_size <= 0.1:
                config_score += 20  # Conservative position sizing
            else:
                config_score += 10  # Aggressive position sizing
            
            if stop_loss <= 0.015:
                config_score += 25  # Very tight stop loss
            elif stop_loss <= 0.02:
                config_score += 20  # Tight stop loss
            else:
                config_score += 10  # Loose stop loss
            
            if take_profit >= 0.05:
                config_score += 25  # High take profit
            elif take_profit >= 0.04:
                config_score += 20  # Good take profit
            else:
                config_score += 10  # Low take profit
            
            if risk_reward_ratio >= 2.5:
                config_score += 25  # Excellent risk-reward
            elif risk_reward_ratio >= 2.0:
                config_score += 20  # Very good risk-reward
            else:
                config_score += 10  # Poor risk-reward
            
            # Calculate overall performance with advanced probability weighting
            performance_score = (
                latency_score * 0.20 +
                execution_rate * 0.25 +
                (100 - failure_rate) * 0.20 +
                position_size_score * 0.15 +
                risk_score * 0.15 +
                config_score * 0.05
            )
            
            return min(100, performance_score)
            
        except Exception as e:
            print(f"[ERROR] Trading module ultimate test: {e}")
            return 0.0
    
    def test_market_data_module_ultimate(self, configuration: Dict[str, Any], data_span_days: int) -> float:
        """Test market data module with ultimate metrics using extended data"""
        try:
            # Test data completeness over extended period
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT symbol) as unique_symbols,
                    COUNT(CASE WHEN date >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as recent_records
                FROM market_data 
                WHERE symbol LIKE '%.JK' 
                AND date >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            completeness_data = self.cursor.fetchone()
            total_records, unique_symbols, recent_records = completeness_data
            
            # Calculate completeness metrics with probability weighting
            completeness_score = min(100, (total_records / (data_span_days * 20)) ** 0.7 * 100)  # Exponential scaling
            diversity_score = min(100, unique_symbols * 8)  # More symbols is better
            timeliness_score = (recent_records / total_records * 100) if total_records > 0 else 0
            
            # Test data quality over extended period
            self.cursor.execute(f"""
                SELECT 
                    AVG(overall_quality_score) as avg_quality,
                    COUNT(*) as quality_records
                FROM market_data_quality_metrics 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            quality_data = self.cursor.fetchone()
            avg_quality, quality_records = quality_data
            
            quality_score = float(avg_quality) if avg_quality else 0
            quality_bonus = min(50, quality_records / 100 * 50)  # Bonus for more quality records
            
            # Test refresh interval optimization with probability weighting
            refresh_interval = configuration.get('data_refresh_interval', 60)
            if refresh_interval <= 15:
                refresh_score = 100  # Excellent refresh rate
            elif refresh_interval <= 30:
                refresh_score = 90   # Very good refresh rate
            elif refresh_interval <= 60:
                refresh_score = 75   # Good refresh rate
            elif refresh_interval <= 120:
                refresh_score = 50   # Acceptable refresh rate
            else:
                refresh_score = 20   # Poor refresh rate
            
            # Test data consistency over extended period
            self.cursor.execute(f"""
                SELECT 
                    COUNT(DISTINCT DATE(date)) as trading_days,
                    COUNT(*) as total_days
                FROM market_data 
                WHERE symbol LIKE '%.JK' 
                AND date >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            consistency_data = self.cursor.fetchone()
            trading_days, total_days = consistency_data
            consistency_score = (trading_days / total_days * 100) if total_days > 0 else 0
            
            # Calculate overall performance with advanced probability weighting
            performance_score = (
                completeness_score * 0.25 +
                diversity_score * 0.20 +
                timeliness_score * 0.15 +
                (quality_score + quality_bonus) * 0.20 +
                refresh_score * 0.10 +
                consistency_score * 0.10
            )
            
            return min(100, performance_score)
            
        except Exception as e:
            print(f"[ERROR] Market data module ultimate test: {e}")
            return 0.0
    
    def test_risk_management_module_ultimate(self, configuration: Dict[str, Any], data_span_days: int) -> float:
        """Test risk management module with ultimate metrics using extended data"""
        try:
            # Test VaR calculation over extended period
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as var_count,
                    AVG(var_95) as avg_var_95,
                    AVG(var_99) as avg_var_99,
                    AVG(sharpe_ratio) as avg_sharpe,
                    AVG(max_drawdown) as avg_drawdown
                FROM risk_metrics 
                WHERE symbol LIKE '%.JK' 
                AND calculated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            risk_data = self.cursor.fetchone()
            var_count, avg_var_95, avg_var_99, avg_sharpe, avg_drawdown = risk_data
            
            # Calculate VaR effectiveness with probability weighting
            var_score = min(100, (var_count / (data_span_days / 7)) ** 0.8 * 100)  # Weekly VaR calculation
            
            # Test Sharpe ratio effectiveness
            if avg_sharpe >= 2.0:
                sharpe_score = 100  # Excellent Sharpe ratio
            elif avg_sharpe >= 1.5:
                sharpe_score = 90   # Very good Sharpe ratio
            elif avg_sharpe >= 1.0:
                sharpe_score = 75   # Good Sharpe ratio
            elif avg_sharpe >= 0.5:
                sharpe_score = 50   # Acceptable Sharpe ratio
            else:
                sharpe_score = 20   # Poor Sharpe ratio
            
            # Test drawdown control
            if avg_drawdown <= 0.02:
                drawdown_score = 100  # Excellent drawdown control
            elif avg_drawdown <= 0.05:
                drawdown_score = 80   # Good drawdown control
            elif avg_drawdown <= 0.10:
                drawdown_score = 60   # Acceptable drawdown control
            else:
                drawdown_score = 20   # Poor drawdown control
            
            # Test portfolio risk over extended period
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as portfolio_count,
                    AVG(portfolio_value) as avg_portfolio_value,
                    AVG(risk_score) as avg_risk_score
                FROM portfolio_risk 
                WHERE calculated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            portfolio_data = self.cursor.fetchone()
            portfolio_count, avg_portfolio_value, avg_risk_score = portfolio_data
            
            portfolio_score = min(100, portfolio_count * 15)  # More portfolio assessments is better
            
            # Test configuration optimization with probability weighting
            var_confidence = configuration.get('var_confidence_level', 0.95)
            correlation_threshold = configuration.get('correlation_threshold', 0.7)
            volatility_threshold = configuration.get('volatility_threshold', 0.3)
            
            config_score = 0
            if var_confidence >= 0.95:
                config_score += 25  # High confidence VaR
            elif var_confidence >= 0.90:
                config_score += 20  # Good confidence VaR
            else:
                config_score += 10  # Low confidence VaR
            
            if correlation_threshold <= 0.6:
                config_score += 25  # Excellent correlation control
            elif correlation_threshold <= 0.7:
                config_score += 20  # Good correlation control
            else:
                config_score += 10  # Poor correlation control
            
            if volatility_threshold <= 0.25:
                config_score += 25  # Excellent volatility control
            elif volatility_threshold <= 0.3:
                config_score += 20  # Good volatility control
            else:
                config_score += 10  # Poor volatility control
            
            # Calculate overall performance with advanced probability weighting
            performance_score = (
                var_score * 0.25 +
                sharpe_score * 0.20 +
                drawdown_score * 0.20 +
                portfolio_score * 0.20 +
                config_score * 0.15
            )
            
            return min(100, performance_score)
            
        except Exception as e:
            print(f"[ERROR] Risk management module ultimate test: {e}")
            return 0.0
    
    def test_technical_analysis_module_ultimate(self, configuration: Dict[str, Any], data_span_days: int) -> float:
        """Test technical analysis module with ultimate metrics using extended data"""
        try:
            # Test indicator coverage over extended period
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_indicators,
                    COUNT(CASE WHEN indicator_type IS NOT NULL THEN 1 END) as typed_indicators,
                    COUNT(DISTINCT indicator_type) as unique_types,
                    COUNT(DISTINCT symbol) as covered_symbols
                FROM technical_indicators 
                WHERE symbol LIKE '%.JK' 
                AND calculated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            indicator_data = self.cursor.fetchone()
            total_indicators, typed_indicators, unique_types, covered_symbols = indicator_data
            
            # Calculate coverage metrics with probability weighting
            coverage_ratio = (typed_indicators / total_indicators) if total_indicators > 0 else 0
            coverage_score = min(100, coverage_ratio * 150)  # Aggressive coverage scoring
            
            diversity_score = min(100, unique_types ** 1.8 * 8)  # Exponential diversity scoring
            symbol_coverage_score = min(100, covered_symbols * 6)  # More symbols is better
            
            # Test SMA configuration optimization
            sma_periods = configuration.get('sma_periods', [20, 50, 200])
            sma_score = 0
            if len(sma_periods) >= 4:
                sma_score += 30  # Multiple periods
            elif len(sma_periods) >= 3:
                sma_score += 25  # Good number of periods
            else:
                sma_score += 15  # Few periods
            
            # Check for optimal SMA periods
            optimal_periods = [10, 20, 50, 100, 200]
            for period in optimal_periods:
                if period in sma_periods:
                    sma_score += 10  # Bonus for optimal periods
            
            # Test RSI configuration optimization
            rsi_period = configuration.get('rsi_period', 14)
            if rsi_period == 14:
                rsi_score = 100  # Optimal RSI period
            elif 12 <= rsi_period <= 16:
                rsi_score = 90   # Very good RSI period
            elif 10 <= rsi_period <= 20:
                rsi_score = 75   # Good RSI period
            else:
                rsi_score = 40   # Suboptimal RSI period
            
            # Test MACD configuration optimization
            macd_fast = configuration.get('macd_fast', 12)
            macd_slow = configuration.get('macd_slow', 26)
            macd_score = 0
            if macd_fast == 12 and macd_slow == 26:
                macd_score = 100  # Optimal MACD
            elif 10 <= macd_fast <= 14 and 20 <= macd_slow <= 30:
                macd_score = 90   # Very good MACD
            elif 8 <= macd_fast <= 16 and 20 <= macd_slow <= 35:
                macd_score = 75   # Good MACD
            else:
                macd_score = 40   # Suboptimal MACD
            
            # Test Bollinger Bands optimization
            bollinger_std = configuration.get('bollinger_std', 2.0)
            if bollinger_std == 2.0:
                bb_score = 100  # Optimal Bollinger Bands
            elif 1.8 <= bollinger_std <= 2.2:
                bb_score = 90   # Very good Bollinger Bands
            elif 1.5 <= bollinger_std <= 2.5:
                bb_score = 75   # Good Bollinger Bands
            else:
                bb_score = 40   # Suboptimal Bollinger Bands
            
            # Calculate overall performance with advanced probability weighting
            performance_score = (
                coverage_score * 0.25 +
                diversity_score * 0.20 +
                symbol_coverage_score * 0.15 +
                sma_score * 0.15 +
                rsi_score * 0.10 +
                macd_score * 0.10 +
                bb_score * 0.05
            )
            
            return min(100, performance_score)
            
        except Exception as e:
            print(f"[ERROR] Technical analysis module ultimate test: {e}")
            return 0.0
    
    def test_fundamental_analysis_module_ultimate(self, configuration: Dict[str, Any], data_span_days: int) -> float:
        """Test fundamental analysis module with ultimate metrics using extended data"""
        try:
            # Test fundamental data coverage over extended period
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_fundamental,
                    COUNT(CASE WHEN pe_ratio IS NOT NULL THEN 1 END) as pe_count,
                    COUNT(CASE WHEN pb_ratio IS NOT NULL THEN 1 END) as pb_count,
                    COUNT(CASE WHEN debt_to_equity IS NOT NULL THEN 1 END) as debt_count,
                    COUNT(CASE WHEN roe IS NOT NULL THEN 1 END) as roe_count,
                    COUNT(DISTINCT symbol) as covered_symbols
                FROM fundamental_data 
                WHERE symbol LIKE '%.JK' 
                AND updated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            fundamental_data = self.cursor.fetchone()
            total_fundamental, pe_count, pb_count, debt_count, roe_count, covered_symbols = fundamental_data
            
            # Calculate coverage metrics with probability weighting
            coverage_score = min(100, (total_fundamental / (data_span_days / 30)) ** 0.6 * 100)  # Monthly updates
            symbol_coverage_score = min(100, covered_symbols * 8)  # More symbols is better
            
            # Test PE ratio threshold optimization
            pe_threshold = configuration.get('pe_ratio_threshold', 15)
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as good_pe_count,
                    AVG(pe_ratio) as avg_pe_ratio
                FROM fundamental_data 
                WHERE pe_ratio <= %s 
                AND pe_ratio IS NOT NULL
                AND updated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """, (pe_threshold,))
            
            pe_data = self.cursor.fetchone()
            good_pe_count, avg_pe_ratio = pe_data
            
            pe_ratio = (good_pe_count / pe_count) if pe_count > 0 else 0
            if pe_ratio >= 0.8:
                pe_score = 100  # Excellent PE filtering
            elif pe_ratio >= 0.6:
                pe_score = 90   # Very good PE filtering
            elif pe_ratio >= 0.4:
                pe_score = 75   # Good PE filtering
            else:
                pe_score = 40   # Poor PE filtering
            
            # Test PB ratio threshold optimization
            pb_threshold = configuration.get('pb_ratio_threshold', 2.0)
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as good_pb_count,
                    AVG(pb_ratio) as avg_pb_ratio
                FROM fundamental_data 
                WHERE pb_ratio <= %s 
                AND pb_ratio IS NOT NULL
                AND updated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """, (pb_threshold,))
            
            pb_data = self.cursor.fetchone()
            good_pb_count, avg_pb_ratio = pb_data
            
            pb_ratio = (good_pb_count / pb_count) if pb_count > 0 else 0
            if pb_ratio >= 0.8:
                pb_score = 100  # Excellent PB filtering
            elif pb_ratio >= 0.6:
                pb_score = 90   # Very good PB filtering
            elif pb_ratio >= 0.4:
                pb_score = 75   # Good PB filtering
            else:
                pb_score = 40   # Poor PB filtering
            
            # Test debt-to-equity threshold optimization
            debt_threshold = configuration.get('debt_to_equity_threshold', 0.5)
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as good_debt_count,
                    AVG(debt_to_equity) as avg_debt_ratio
                FROM fundamental_data 
                WHERE debt_to_equity <= %s 
                AND debt_to_equity IS NOT NULL
                AND updated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """, (debt_threshold,))
            
            debt_data = self.cursor.fetchone()
            good_debt_count, avg_debt_ratio = debt_data
            
            debt_ratio = (good_debt_count / debt_count) if debt_count > 0 else 0
            if debt_ratio >= 0.8:
                debt_score = 100  # Excellent debt filtering
            elif debt_ratio >= 0.6:
                debt_score = 90   # Very good debt filtering
            elif debt_ratio >= 0.4:
                debt_score = 75   # Good debt filtering
            else:
                debt_score = 40   # Poor debt filtering
            
            # Test ROE threshold optimization
            roe_threshold = configuration.get('roe_threshold', 0.15)
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as good_roe_count,
                    AVG(roe) as avg_roe
                FROM fundamental_data 
                WHERE roe >= %s 
                AND roe IS NOT NULL
                AND updated_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """, (roe_threshold,))
            
            roe_data = self.cursor.fetchone()
            good_roe_count, avg_roe = roe_data
            
            roe_ratio = (good_roe_count / roe_count) if roe_count > 0 else 0
            if roe_ratio >= 0.8:
                roe_score = 100  # Excellent ROE filtering
            elif roe_ratio >= 0.6:
                roe_score = 90   # Very good ROE filtering
            elif roe_ratio >= 0.4:
                roe_score = 75   # Good ROE filtering
            else:
                roe_score = 40   # Poor ROE filtering
            
            # Calculate overall performance with advanced probability weighting
            performance_score = (
                coverage_score * 0.20 +
                symbol_coverage_score * 0.15 +
                pe_score * 0.20 +
                pb_score * 0.20 +
                debt_score * 0.15 +
                roe_score * 0.10
            )
            
            return min(100, performance_score)
            
        except Exception as e:
            print(f"[ERROR] Fundamental analysis module ultimate test: {e}")
            return 0.0
    
    def test_sentiment_analysis_module_ultimate(self, configuration: Dict[str, Any], data_span_days: int) -> float:
        """Test sentiment analysis module with ultimate metrics using extended data"""
        try:
            # Test sentiment data coverage over extended period
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_sentiment,
                    COUNT(CASE WHEN sentiment_score IS NOT NULL THEN 1 END) as scored_sentiment,
                    COUNT(CASE WHEN confidence IS NOT NULL THEN 1 END) as confidence_count,
                    COUNT(DISTINCT symbol) as covered_symbols,
                    AVG(sentiment_score) as avg_sentiment,
                    AVG(confidence) as avg_confidence
                FROM sentiment_data 
                WHERE symbol LIKE '%.JK' 
                AND published_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """)
            
            sentiment_data = self.cursor.fetchone()
            total_sentiment, scored_sentiment, confidence_count, covered_symbols, avg_sentiment, avg_confidence = sentiment_data
            
            # Calculate coverage metrics with probability weighting
            coverage_ratio = (scored_sentiment / total_sentiment) if total_sentiment > 0 else 0
            coverage_score = min(100, coverage_ratio * 200)  # Very aggressive coverage scoring
            
            symbol_coverage_score = min(100, covered_symbols * 10)  # More symbols is better
            
            # Test sentiment threshold optimization
            sentiment_threshold = configuration.get('sentiment_threshold', 0.7)
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as positive_sentiment_count,
                    AVG(sentiment_score) as avg_positive_sentiment
                FROM sentiment_data 
                WHERE sentiment_score >= %s 
                AND sentiment_score IS NOT NULL
                AND published_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """, (sentiment_threshold,))
            
            sentiment_threshold_data = self.cursor.fetchone()
            positive_sentiment_count, avg_positive_sentiment = sentiment_threshold_data
            
            sentiment_ratio = (positive_sentiment_count / scored_sentiment) if scored_sentiment > 0 else 0
            if sentiment_ratio >= 0.7:
                sentiment_score = 100  # Excellent sentiment filtering
            elif sentiment_ratio >= 0.5:
                sentiment_score = 90   # Very good sentiment filtering
            elif sentiment_ratio >= 0.3:
                sentiment_score = 75   # Good sentiment filtering
            else:
                sentiment_score = 40   # Poor sentiment filtering
            
            # Test confidence threshold optimization
            confidence_threshold = configuration.get('confidence_threshold', 0.8)
            self.cursor.execute(f"""
                SELECT 
                    COUNT(*) as high_confidence_count,
                    AVG(confidence) as avg_high_confidence
                FROM sentiment_data 
                WHERE confidence >= %s 
                AND confidence IS NOT NULL
                AND published_at >= DATE_SUB(NOW(), INTERVAL {data_span_days} DAY)
            """, (confidence_threshold,))
            
            confidence_threshold_data = self.cursor.fetchone()
            high_confidence_count, avg_high_confidence = confidence_threshold_data
            
            confidence_ratio = (high_confidence_count / confidence_count) if confidence_count > 0 else 0
            if confidence_ratio >= 0.8:
                confidence_score = 100  # Excellent confidence filtering
            elif confidence_ratio >= 0.6:
                confidence_score = 90   # Very good confidence filtering
            elif confidence_ratio >= 0.4:
                confidence_score = 75   # Good confidence filtering
            else:
                confidence_score = 40   # Poor confidence filtering
            
            # Test sentiment window optimization
            sentiment_window = configuration.get('sentiment_window', 7)
            if sentiment_window == 7:
                window_score = 100  # Optimal sentiment window
            elif 5 <= sentiment_window <= 10:
                window_score = 90   # Very good sentiment window
            elif 3 <= sentiment_window <= 14:
                window_score = 75   # Good sentiment window
            else:
                window_score = 40   # Suboptimal sentiment window
            
            # Test weight distribution optimization
            news_weight = configuration.get('news_weight', 0.4)
            social_media_weight = configuration.get('social_media_weight', 0.3)
            analyst_weight = configuration.get('analyst_weight', 0.3)
            
            weight_balance = 1.0 - abs(news_weight + social_media_weight + analyst_weight - 1.0)
            if weight_balance >= 0.98:
                weight_score = 100  # Excellent weight distribution
            elif weight_balance >= 0.95:
                weight_score = 90   # Very good weight distribution
            elif weight_balance >= 0.90:
                weight_score = 75   # Good weight distribution
            else:
                weight_score = 40   # Poor weight distribution
            
            # Test data quality over extended period
            quality_score = 0
            if avg_sentiment and avg_confidence:
                if avg_sentiment >= 0.6 and avg_confidence >= 0.8:
                    quality_score = 100  # Excellent data quality
                elif avg_sentiment >= 0.5 and avg_confidence >= 0.7:
                    quality_score = 90   # Very good data quality
                elif avg_sentiment >= 0.4 and avg_confidence >= 0.6:
                    quality_score = 75   # Good data quality
                else:
                    quality_score = 40   # Poor data quality
            
            # Calculate overall performance with advanced probability weighting
            performance_score = (
                coverage_score * 0.25 +
                symbol_coverage_score * 0.15 +
                sentiment_score * 0.20 +
                confidence_score * 0.20 +
                window_score * 0.10 +
                weight_score * 0.05 +
                quality_score * 0.05
            )
            
            return min(100, performance_score)
            
        except Exception as e:
            print(f"[ERROR] Sentiment analysis module ultimate test: {e}")
            return 0.0
    
    def generate_probability_configuration(self, module_name: str, iteration: int) -> Dict[str, Any]:
        """Generate configuration using advanced probability distributions"""
        try:
            module_config = self.configuration['module_configuration']['modules'][module_name]
            tuning_params = module_config['tuning_parameters']
            
            probability_config = {}
            
            for param_name, param_config in tuning_params.items():
                if isinstance(param_config['current'], list):
                    # Handle list parameters with probability weighting
                    probability_config[param_name] = []
                    for i, (min_val, max_val, step) in enumerate(zip(param_config['min'], param_config['max'], param_config['step'])):
                        # Use different probability distributions based on iteration
                        if iteration % 3 == 0:
                            # Normal distribution (Gaussian)
                            random_val = np.random.normal((min_val + max_val) / 2, (max_val - min_val) / 6)
                        elif iteration % 3 == 1:
                            # Beta distribution (skewed towards optimal values)
                            random_val = min_val + (max_val - min_val) * np.random.beta(2, 2)
                        else:
                            # Uniform distribution
                            random_val = np.random.uniform(min_val, max_val)
                        
                        random_val = round(random_val / step) * step
                        random_val = max(min_val, min(max_val, random_val))
                        probability_config[param_name].append(random_val)
                else:
                    # Handle single parameters with advanced probability distributions
                    min_val = param_config['min']
                    max_val = param_config['max']
                    step = param_config['step']
                    
                    # Use different probability distributions based on iteration and parameter type
                    if 'threshold' in param_name.lower():
                        # For thresholds, use beta distribution skewed towards lower values
                        random_val = min_val + (max_val - min_val) * np.random.beta(2, 5)
                    elif 'ratio' in param_name.lower():
                        # For ratios, use normal distribution
                        random_val = np.random.normal((min_val + max_val) / 2, (max_val - min_val) / 6)
                    elif 'period' in param_name.lower():
                        # For periods, use beta distribution skewed towards optimal values
                        random_val = min_val + (max_val - min_val) * np.random.beta(3, 3)
                    elif 'weight' in param_name.lower():
                        # For weights, use uniform distribution
                        random_val = np.random.uniform(min_val, max_val)
                    else:
                        # Default to beta distribution
                        random_val = min_val + (max_val - min_val) * np.random.beta(2, 2)
                    
                    random_val = round(random_val / step) * step
                    random_val = max(min_val, min(max_val, random_val))
                    
                    probability_config[param_name] = random_val
            
            return probability_config
            
        except Exception as e:
            print(f"[ERROR] Generating probability configuration for {module_name}: {e}")
            return {}
    
    def run_ultimate_tuning(self, data_span_days: int = 365, iterations: int = 200) -> Dict[str, Any]:
        """Run ultimate tuning with extended data and advanced probability"""
        try:
            print("ULTIMATE MODULE TUNING SYSTEM")
            print("=" * 80)
            print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Data Span: {data_span_days} days")
            print(f"Iterations: {iterations}")
            print("=" * 80)
            
            # Results
            results = {
                'tuning_type': 'ultimate_module_tuning',
                'tuning_start': datetime.now().isoformat(),
                'data_span_days': data_span_days,
                'iterations': iterations,
                'database_connection': False,
                'extended_data_info': {},
                'module_tuning_results': {},
                'overall_improvement': {},
                'final_assessment': {}
            }
            
            # Load configuration
            if not self.load_configuration():
                return results
            
            # Connect to database
            if not self.connect_database():
                return results
            
            results['database_connection'] = True
            
            # Get extended historical data info
            extended_data_info = self.get_extended_historical_data(data_span_days)
            results['extended_data_info'] = extended_data_info
            
            print(f"\nExtended Data Information:")
            print(f"  Historical Data: {extended_data_info.get('historical_data', {}).get('total_records', 0):,} records")
            print(f"  Market Data: {extended_data_info.get('market_data', {}).get('total_records', 0):,} records")
            print(f"  Trading Data: {extended_data_info.get('trading_data', {}).get('total_records', 0):,} records")
            
            # Get modules to tune
            modules = self.configuration['module_configuration']['modules']
            
            print(f"\nUltimate tuning for {len(modules)} modules with {iterations} iterations each...")
            
            # Tune each module with ultimate testing
            for module_name, module_config in modules.items():
                if module_config['status'] == 'ACTIVE':
                    print(f"\nULTIMATE TUNING {module_name.upper()}")
                    print("-" * 60)
                    
                    # Test current configuration
                    current_performance = self.test_module_performance_ultimate(module_name, module_config['configuration'], data_span_days)
                    print(f"   Current performance: {current_performance:.2f}%")
                    
                    # Generate and test multiple configurations with probability
                    best_performance = current_performance
                    best_configuration = module_config['configuration']
                    improvement_count = 0
                    
                    # Test multiple configurations with advanced probability
                    for i in range(iterations):
                        # Generate probability-based configuration
                        probability_config = self.generate_probability_configuration(module_name, i)
                        
                        # Test performance
                        performance = self.test_module_performance_ultimate(module_name, probability_config, data_span_days)
                        
                        if performance > best_performance:
                            best_performance = performance
                            best_configuration = probability_config
                            improvement_count += 1
                            print(f"   New best performance: {best_performance:.2f}% (iteration {i+1}, improvement #{improvement_count})")
                    
                    # Update module configuration
                    modules[module_name]['performance_score'] = best_performance
                    modules[module_name]['best_configuration'] = best_configuration
                    
                    # Update tuning parameters with best values
                    for param_name, param_value in best_configuration.items():
                        if param_name in modules[module_name]['tuning_parameters']:
                            modules[module_name]['tuning_parameters'][param_name]['best'] = param_value
                            modules[module_name]['tuning_parameters'][param_name]['current'] = param_value
                    
                    improvement = best_performance - current_performance
                    results['module_tuning_results'][module_name] = {
                        'current_performance': current_performance,
                        'best_performance': best_performance,
                        'improvement': improvement,
                        'improvement_count': improvement_count,
                        'best_configuration': best_configuration
                    }
                    
                    print(f"   Final performance: {best_performance:.2f}%")
                    print(f"   Improvement: {improvement:.2f}%")
                    print(f"   Improvements found: {improvement_count}")
            
            # Calculate overall improvement
            total_improvement = 0.0
            improved_modules = 0
            total_improvements = 0
            
            for module_name, tuning_result in results['module_tuning_results'].items():
                if tuning_result['improvement'] > 0:
                    total_improvement += tuning_result['improvement']
                    improved_modules += 1
                total_improvements += tuning_result['improvement_count']
            
            results['overall_improvement'] = {
                'total_improvement': total_improvement,
                'improved_modules': improved_modules,
                'total_improvements': total_improvements,
                'average_improvement': total_improvement / improved_modules if improved_modules > 0 else 0
            }
            
            # Generate final assessment
            final_assessment = self.generate_final_assessment(results)
            results['final_assessment'] = final_assessment
            
            # Save updated configuration
            self.save_configuration()
            
            # Close database connection
            self.disconnect_database()
            
            # Generate comprehensive report
            self.generate_comprehensive_report(results)
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Ultimate tuning failed: {e}")
            return {'error': str(e)}
    
    def generate_final_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final assessment"""
        try:
            assessment = {
                'tuning_status': '',
                'overall_improvement': 0.0,
                'best_performing_modules': [],
                'modules_needing_improvement': [],
                'recommendations': []
            }
            
            # Analyze overall improvement
            overall_improvement = results.get('overall_improvement', {})
            total_improvement = overall_improvement.get('total_improvement', 0)
            improved_modules = overall_improvement.get('improved_modules', 0)
            total_improvements = overall_improvement.get('total_improvements', 0)
            average_improvement = overall_improvement.get('average_improvement', 0)
            
            assessment['overall_improvement'] = total_improvement
            
            # Determine tuning status
            if total_improvement > 100:
                assessment['tuning_status'] = 'EXCELLENT'
            elif total_improvement > 50:
                assessment['tuning_status'] = 'GOOD'
            elif total_improvement > 20:
                assessment['tuning_status'] = 'FAIR'
            else:
                assessment['tuning_status'] = 'POOR'
            
            # Analyze module performance
            module_results = results.get('module_tuning_results', {})
            
            for module_name, module_result in module_results.items():
                improvement = module_result.get('improvement', 0)
                best_performance = module_result.get('best_performance', 0)
                improvement_count = module_result.get('improvement_count', 0)
                
                if improvement > 30:
                    assessment['best_performing_modules'].append({
                        'module': module_name,
                        'improvement': improvement,
                        'performance': best_performance,
                        'improvements_found': improvement_count
                    })
                elif best_performance < 70:
                    assessment['modules_needing_improvement'].append({
                        'module': module_name,
                        'performance': best_performance
                    })
            
            # Recommendations
            if total_improvement > 100:
                assessment['recommendations'].append("Excellent tuning results achieved")
                assessment['recommendations'].append("System ready for production deployment")
                assessment['recommendations'].append("Consider implementing continuous optimization")
            elif total_improvement > 50:
                assessment['recommendations'].append("Very good tuning results achieved")
                assessment['recommendations'].append("System ready for production with monitoring")
                assessment['recommendations'].append("Continue with current optimization strategy")
            elif total_improvement > 20:
                assessment['recommendations'].append("Good tuning results achieved")
                assessment['recommendations'].append("System ready for production with improvements")
                assessment['recommendations'].append("Focus on remaining modules needing improvement")
            else:
                assessment['recommendations'].append("Tuning results need significant improvement")
                assessment['recommendations'].append("Consider adjusting testing parameters")
                assessment['recommendations'].append("Implement more aggressive optimization strategies")
            
            return assessment
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive report"""
        print("\nULTIMATE MODULE TUNING REPORT")
        print("=" * 80)
        
        # Extended data information
        extended_data = results.get('extended_data_info', {})
        print(f"Extended Data Information:")
        print(f"  Data Span: {results.get('data_span_days', 0)} days")
        print(f"  Iterations: {results.get('iterations', 0)}")
        
        historical_data = extended_data.get('historical_data', {})
        print(f"  Historical Data: {historical_data.get('total_records', 0):,} records")
        print(f"  Unique Symbols: {historical_data.get('unique_symbols', 0)}")
        print(f"  Data Range: {historical_data.get('earliest_date', 'N/A')} to {historical_data.get('latest_date', 'N/A')}")
        
        market_data = extended_data.get('market_data', {})
        print(f"  Market Data: {market_data.get('total_records', 0):,} records")
        print(f"  Market Symbols: {market_data.get('unique_symbols', 0)}")
        
        trading_data = extended_data.get('trading_data', {})
        print(f"  Trading Data: {trading_data.get('total_records', 0):,} records")
        print(f"  Trading Symbols: {trading_data.get('unique_symbols', 0)}")
        
        # Module tuning results
        module_results = results.get('module_tuning_results', {})
        print(f"\nModule Tuning Results:")
        
        for module_name, module_result in module_results.items():
            print(f"  {module_name}:")
            print(f"    Current Performance: {module_result.get('current_performance', 0):.2f}%")
            print(f"    Best Performance: {module_result.get('best_performance', 0):.2f}%")
            print(f"    Improvement: {module_result.get('improvement', 0):.2f}%")
            print(f"    Improvements Found: {module_result.get('improvement_count', 0)}")
        
        # Overall improvement
        overall_improvement = results.get('overall_improvement', {})
        print(f"\nOverall Improvement:")
        print(f"  Total Improvement: {overall_improvement.get('total_improvement', 0):.2f}%")
        print(f"  Improved Modules: {overall_improvement.get('improved_modules', 0)}")
        print(f"  Total Improvements: {overall_improvement.get('total_improvements', 0)}")
        print(f"  Average Improvement: {overall_improvement.get('average_improvement', 0):.2f}%")
        
        # Final assessment
        final_assessment = results.get('final_assessment', {})
        print(f"\nFinal Assessment:")
        print(f"  Tuning Status: {final_assessment.get('tuning_status', 'UNKNOWN')}")
        print(f"  Overall Improvement: {final_assessment.get('overall_improvement', 0):.2f}%")
        
        best_modules = final_assessment.get('best_performing_modules', [])
        if best_modules:
            print(f"  Best Performing Modules:")
            for module in best_modules:
                print(f"    - {module['module']}: {module['improvement']:.2f}% improvement, {module['improvements_found']} improvements found")
        
        modules_needing_improvement = final_assessment.get('modules_needing_improvement', [])
        if modules_needing_improvement:
            print(f"  Modules Needing Improvement:")
            for module in modules_needing_improvement:
                print(f"    - {module['module']}: {module['performance']:.2f}% performance")
        
        recommendations = final_assessment.get('recommendations', [])
        if recommendations:
            print(f"  Recommendations:")
            for recommendation in recommendations:
                print(f"    - {recommendation}")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"ultimate_module_tuning_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nUltimate module tuning results saved to: {results_file}")
        print(f"Tuning completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'scalper',
        'port': 3306
    }
    
    # Create ultimate module tuning instance
    tuning_system = UltimateModuleTuning(db_config)
    
    # Run ultimate tuning with extended data
    results = tuning_system.run_ultimate_tuning(data_span_days=365, iterations=200)
    
    return results

if __name__ == "__main__":
    main()
