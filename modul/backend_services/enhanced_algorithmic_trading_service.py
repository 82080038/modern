"""
Enhanced Algorithmic Trading Service
===================================

Service untuk algorithmic trading dengan implementasi algoritma terbukti
menggunakan scikit-learn, XGBoost, dan CatBoost untuk meningkatkan akurasi.

Author: AI Assistant
Date: 2025-01-17
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score
import xgboost as xgb
import catboost as cb
from app.models.trading import Strategy, StrategyRule, Order, Position, Portfolio
from app.models.market_data import MarketData
from app.services.risk_management_service import RiskManagementService

logger = logging.getLogger(__name__)

class EnhancedAlgorithmicTradingService:
    """
    Enhanced Algorithmic Trading Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = RiskManagementService(db)
        self.running_strategies = {}
        self.models = {}
        self.performance_tracker = {}
        
        # Initialize proven algorithms
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize proven ML models"""
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            ),
            'catboost': cb.CatBoostClassifier(
                iterations=100,
                depth=6,
                learning_rate=0.1,
                random_seed=42,
                verbose=False
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        }
    
    async def start_strategy(self, strategy_id: int, portfolio_id: int) -> Dict[str, Any]:
        """Start algorithmic trading strategy dengan enhanced algorithms"""
        try:
            # Get strategy from database
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return {'error': 'Strategy not found'}
            
            # Get portfolio
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {'error': 'Portfolio not found'}
            
            # Initialize strategy execution
            strategy_key = f"{strategy_id}_{portfolio_id}"
            self.running_strategies[strategy_key] = {
                'strategy_id': strategy_id,
                'portfolio_id': portfolio_id,
                'started_at': datetime.now(),
                'status': 'running',
                'model': None,
                'performance': {}
            }
            
            # Train model with historical data
            model_performance = await self._train_strategy_model(strategy_id, portfolio_id)
            
            # Start real-time execution
            asyncio.create_task(self._execute_strategy(strategy_key))
            
            return {
                'success': True,
                'strategy_id': strategy_id,
                'portfolio_id': portfolio_id,
                'model_performance': model_performance,
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Error starting strategy: {e}")
            return {'error': str(e)}
    
    async def _train_strategy_model(self, strategy_id: int, portfolio_id: int) -> Dict[str, Any]:
        """Train ML model untuk strategy dengan historical data"""
        try:
            # Get historical market data
            historical_data = await self._get_historical_data(strategy_id)
            
            if len(historical_data) < 100:
                return {'error': 'Insufficient historical data'}
            
            # Prepare features dan targets
            features, targets = self._prepare_training_data(historical_data)
            
            # Split data untuk training dan validation
            tscv = TimeSeriesSplit(n_splits=5)
            best_model = None
            best_score = 0
            model_scores = {}
            
            # Test semua models
            for model_name, model in self.models.items():
                scores = []
                
                for train_idx, val_idx in tscv.split(features):
                    X_train, X_val = features.iloc[train_idx], features.iloc[val_idx]
                    y_train, y_val = targets.iloc[train_idx], targets.iloc[val_idx]
                    
                    # Train model
                    model.fit(X_train, y_train)
                    
                    # Predict dan evaluate
                    y_pred = model.predict(X_val)
                    accuracy = accuracy_score(y_val, y_pred)
                    precision = precision_score(y_val, y_pred, average='weighted')
                    recall = recall_score(y_val, y_pred, average='weighted')
                    
                    scores.append({
                        'accuracy': accuracy,
                        'precision': precision,
                        'recall': recall
                    })
                
                # Calculate average scores
                avg_accuracy = np.mean([s['accuracy'] for s in scores])
                avg_precision = np.mean([s['precision'] for s in scores])
                avg_recall = np.mean([s['recall'] for s in scores])
                
                model_scores[model_name] = {
                    'accuracy': avg_accuracy,
                    'precision': avg_precision,
                    'recall': avg_recall,
                    'f1_score': 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
                }
                
                # Track best model
                if avg_accuracy > best_score:
                    best_score = avg_accuracy
                    best_model = model_name
            
            # Train best model dengan all data
            best_model_instance = self.models[best_model]
            best_model_instance.fit(features, targets)
            
            # Store model
            strategy_key = f"{strategy_id}_{portfolio_id}"
            self.running_strategies[strategy_key]['model'] = best_model_instance
            self.running_strategies[strategy_key]['model_name'] = best_model
            
            return {
                'best_model': best_model,
                'best_score': best_score,
                'all_scores': model_scores,
                'training_samples': len(features)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {'error': str(e)}
    
    async def _get_historical_data(self, strategy_id: int) -> pd.DataFrame:
        """Get historical market data untuk training"""
        try:
            # Get strategy rules
            strategy_rules = self.db.query(StrategyRule).filter(
                StrategyRule.strategy_id == strategy_id
            ).all()
            
            if not strategy_rules:
                return pd.DataFrame()
            
            # Get symbols from strategy rules
            symbols = [rule.symbol for rule in strategy_rules if rule.symbol]
            
            if not symbols:
                return pd.DataFrame()
            
            # Get historical data for symbols
            historical_data = []
            for symbol in symbols:
                market_data = self.db.query(MarketData).filter(
                    MarketData.symbol == symbol,
                    MarketData.timestamp >= datetime.now() - timedelta(days=365)
                ).order_by(MarketData.timestamp).all()
                
                for data in market_data:
                    historical_data.append({
                        'timestamp': data.timestamp,
                        'symbol': data.symbol,
                        'open': data.open_price,
                        'high': data.high_price,
                        'low': data.low_price,
                        'close': data.close_price,
                        'volume': data.volume
                    })
            
            return pd.DataFrame(historical_data)
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features dan targets untuk ML training"""
        try:
            if data.empty:
                return pd.DataFrame(), pd.Series()
            
            # Sort by timestamp
            data = data.sort_values('timestamp')
            
            # Calculate technical indicators
            data['sma_5'] = data.groupby('symbol')['close'].rolling(5).mean().reset_index(0, drop=True)
            data['sma_20'] = data.groupby('symbol')['close'].rolling(20).mean().reset_index(0, drop=True)
            data['sma_50'] = data.groupby('symbol')['close'].rolling(50).mean().reset_index(0, drop=True)
            
            # RSI
            data['rsi'] = self._calculate_rsi(data['close'])
            
            # MACD
            data['macd'], data['macd_signal'] = self._calculate_macd(data['close'])
            
            # Bollinger Bands
            data['bb_upper'], data['bb_lower'] = self._calculate_bollinger_bands(data['close'])
            
            # Price changes
            data['price_change_1d'] = data.groupby('symbol')['close'].pct_change(1)
            data['price_change_5d'] = data.groupby('symbol')['close'].pct_change(5)
            data['price_change_20d'] = data.groupby('symbol')['close'].pct_change(20)
            
            # Volume indicators
            data['volume_sma'] = data.groupby('symbol')['volume'].rolling(20).mean().reset_index(0, drop=True)
            data['volume_ratio'] = data['volume'] / data['volume_sma']
            
            # Create target (next day price direction)
            data['next_close'] = data.groupby('symbol')['close'].shift(-1)
            data['target'] = (data['next_close'] > data['close']).astype(int)
            
            # Select features
            feature_columns = [
                'sma_5', 'sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal',
                'bb_upper', 'bb_lower', 'price_change_1d', 'price_change_5d', 
                'price_change_20d', 'volume_ratio'
            ]
            
            # Remove rows with NaN values
            data_clean = data.dropna(subset=feature_columns + ['target'])
            
            features = data_clean[feature_columns]
            targets = data_clean['target']
            
            return features, targets
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame(), pd.Series()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std: float = 2) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std_dev = prices.rolling(window=period).std()
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        return upper_band, lower_band
    
    async def _execute_strategy(self, strategy_key: str):
        """Execute strategy dengan real-time data"""
        try:
            strategy_info = self.running_strategies[strategy_key]
            model = strategy_info['model']
            strategy_id = strategy_info['strategy_id']
            portfolio_id = strategy_info['portfolio_id']
            
            while strategy_info['status'] == 'running':
                # Get current market data
                current_data = await self._get_current_market_data(strategy_id)
                
                if not current_data.empty:
                    # Prepare features
                    features = self._prepare_realtime_features(current_data)
                    
                    if not features.empty:
                        # Make prediction
                        prediction = model.predict(features)
                        confidence = model.predict_proba(features).max()
                        
                        # Execute trade based on prediction
                        if confidence > 0.7:  # High confidence threshold
                            await self._execute_trade(
                                strategy_id, portfolio_id, prediction[0], confidence
                            )
                
                # Wait before next execution
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Error executing strategy {strategy_key}: {e}")
            strategy_info['status'] = 'error'
    
    async def _get_current_market_data(self, strategy_id: int) -> pd.DataFrame:
        """Get current market data untuk strategy"""
        try:
            # Get strategy symbols
            strategy_rules = self.db.query(StrategyRule).filter(
                StrategyRule.strategy_id == strategy_id
            ).all()
            
            symbols = [rule.symbol for rule in strategy_rules if rule.symbol]
            
            if not symbols:
                return pd.DataFrame()
            
            # Get latest market data
            current_data = []
            for symbol in symbols:
                latest_data = self.db.query(MarketData).filter(
                    MarketData.symbol == symbol
                ).order_by(MarketData.timestamp.desc()).first()
                
                if latest_data:
                    current_data.append({
                        'timestamp': latest_data.timestamp,
                        'symbol': latest_data.symbol,
                        'open': latest_data.open_price,
                        'high': latest_data.high_price,
                        'low': latest_data.low_price,
                        'close': latest_data.close_price,
                        'volume': latest_data.volume
                    })
            
            return pd.DataFrame(current_data)
            
        except Exception as e:
            logger.error(f"Error getting current market data: {e}")
            return pd.DataFrame()
    
    def _prepare_realtime_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features untuk real-time prediction"""
        try:
            if data.empty:
                return pd.DataFrame()
            
            # Calculate technical indicators (same as training)
            data['sma_5'] = data.groupby('symbol')['close'].rolling(5).mean().reset_index(0, drop=True)
            data['sma_20'] = data.groupby('symbol')['close'].rolling(20).mean().reset_index(0, drop=True)
            data['sma_50'] = data.groupby('symbol')['close'].rolling(50).mean().reset_index(0, drop=True)
            data['rsi'] = self._calculate_rsi(data['close'])
            data['macd'], data['macd_signal'] = self._calculate_macd(data['close'])
            data['bb_upper'], data['bb_lower'] = self._calculate_bollinger_bands(data['close'])
            data['price_change_1d'] = data.groupby('symbol')['close'].pct_change(1)
            data['price_change_5d'] = data.groupby('symbol')['close'].pct_change(5)
            data['price_change_20d'] = data.groupby('symbol')['close'].pct_change(20)
            data['volume_sma'] = data.groupby('symbol')['volume'].rolling(20).mean().reset_index(0, drop=True)
            data['volume_ratio'] = data['volume'] / data['volume_sma']
            
            # Select features
            feature_columns = [
                'sma_5', 'sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal',
                'bb_upper', 'bb_lower', 'price_change_1d', 'price_change_5d', 
                'price_change_20d', 'volume_ratio'
            ]
            
            features = data[feature_columns].dropna()
            return features
            
        except Exception as e:
            logger.error(f"Error preparing realtime features: {e}")
            return pd.DataFrame()
    
    async def _execute_trade(self, strategy_id: int, portfolio_id: int, prediction: int, confidence: float):
        """Execute trade berdasarkan prediction"""
        try:
            # Get current positions
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            
            # Risk management check
            risk_check = await self.risk_service.check_position_limits(portfolio_id)
            if not risk_check['allowed']:
                logger.warning(f"Trade blocked by risk management: {risk_check['reason']}")
                return
            
            # Create order based on prediction
            if prediction == 1:  # Buy signal
                order_type = 'market'
                side = 'buy'
            else:  # Sell signal
                order_type = 'market'
                side = 'sell'
            
            # Create order
            order = Order(
                portfolio_id=portfolio_id,
                symbol='AAPL',  # Default symbol, should be dynamic
                order_type=order_type,
                side=side,
                quantity=100,  # Default quantity, should be calculated
                price=0,  # Market order
                status='pending',
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            
            logger.info(f"Order created: {order.id} for strategy {strategy_id} with confidence {confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    async def stop_strategy(self, strategy_id: int, portfolio_id: int) -> Dict[str, Any]:
        """Stop algorithmic trading strategy"""
        try:
            strategy_key = f"{strategy_id}_{portfolio_id}"
            
            if strategy_key in self.running_strategies:
                self.running_strategies[strategy_key]['status'] = 'stopped'
                del self.running_strategies[strategy_key]
                
                return {
                    'success': True,
                    'message': 'Strategy stopped successfully'
                }
            else:
                return {'error': 'Strategy not found or not running'}
                
        except Exception as e:
            logger.error(f"Error stopping strategy: {e}")
            return {'error': str(e)}
    
    def get_running_strategies(self) -> List[Dict[str, Any]]:
        """Get list of running strategies"""
        try:
            running = []
            for key, strategy in self.running_strategies.items():
                running.append({
                    'strategy_key': key,
                    'strategy_id': strategy['strategy_id'],
                    'portfolio_id': strategy['portfolio_id'],
                    'started_at': strategy['started_at'],
                    'status': strategy['status'],
                    'model_name': strategy.get('model_name', 'unknown')
                })
            
            return running
            
        except Exception as e:
            logger.error(f"Error getting running strategies: {e}")
            return []
