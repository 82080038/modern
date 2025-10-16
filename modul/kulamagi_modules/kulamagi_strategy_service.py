"""
Christian Kulamagi Trading Strategy Service
Implementasi strategi trading Christian Kulamagi yang berhasil mengubah $5,000 menjadi $100+ juta
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.market_data import MarketData, HistoricalData
from app.models.trading import Portfolio, Position, Order
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class KulamagiStrategyService:
    """
    Service untuk implementasi strategi Christian Kulamagi:
    1. Market condition filter (NASDAQ > EMA 10 > EMA 20)
    2. Momentum stock screener (1M, 3M, 6M performance)
    3. Breakout strategy dengan konsolidasi
    4. Position sizing 0.25%-1% per trade
    5. Trailing stop berdasarkan EMA 10/20
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_per_trade_min = 0.0025  # 0.25%
        self.risk_per_trade_max = 0.01   # 1%
        self.max_position_size = 0.1    # 10% max position
        self.partial_profit_ratio = 0.33  # Take 1/3 profit early
        
    async def check_market_condition(self) -> Dict[str, Any]:
        """
        Check market condition berdasarkan NASDAQ > EMA 10 > EMA 20
        Returns: market_favorable, nasdaq_price, ema_10, ema_20
        """
        try:
            # Get NASDAQ data (using ^IXIC symbol)
            nasdaq_data = self.db.query(HistoricalData).filter(
                HistoricalData.symbol == "^IXIC",
                HistoricalData.timestamp >= datetime.now() - timedelta(days=50)
            ).order_by(HistoricalData.timestamp.desc()).limit(50).all()
            
            if len(nasdaq_data) < 20:
                return {
                    "market_favorable": False,
                    "reason": "Insufficient NASDAQ data",
                    "nasdaq_price": None,
                    "ema_10": None,
                    "ema_20": None
                }
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': data.timestamp,
                'close': data.close_price,
                'volume': data.volume
            } for data in nasdaq_data])
            
            # Calculate EMAs
            df['ema_10'] = df['close'].ewm(span=10).mean()
            df['ema_20'] = df['close'].ewm(span=20).mean()
            
            # Get latest values
            current_price = df['close'].iloc[-1]
            ema_10 = df['ema_10'].iloc[-1]
            ema_20 = df['ema_20'].iloc[-1]
            
            # Check Kulamagi condition: NASDAQ > EMA 10 > EMA 20
            market_favorable = (current_price > ema_10 > ema_20)
            
            return {
                "market_favorable": market_favorable,
                "nasdaq_price": current_price,
                "ema_10": ema_10,
                "ema_20": ema_20,
                "condition": f"NASDAQ: {current_price:.2f} > EMA10: {ema_10:.2f} > EMA20: {ema_20:.2f}" if market_favorable else "Market not favorable"
            }
            
        except Exception as e:
            logger.error(f"Error checking market condition: {e}")
            return {
                "market_favorable": False,
                "reason": f"Error: {str(e)}",
                "nasdaq_price": None,
                "ema_10": None,
                "ema_20": None
            }
    
    async def screen_momentum_stocks(self, min_performance_1m: float = 0.20, 
                                   min_performance_3m: float = 0.30,
                                   min_performance_6m: float = 0.50) -> List[Dict[str, Any]]:
        """
        Screen stocks dengan momentum kuat berdasarkan performance 1M, 3M, 6M
        """
        try:
            # Get all symbols with historical data
            symbols = self.db.query(HistoricalData.symbol).distinct().all()
            momentum_stocks = []
            
            for symbol_tuple in symbols:
                symbol = symbol_tuple[0]
                
                # Skip index symbols
                if symbol.startswith('^'):
                    continue
                
                # Get historical data for different periods
                now = datetime.now()
                
                # 1 month data
                data_1m = self.db.query(HistoricalData).filter(
                    HistoricalData.symbol == symbol,
                    HistoricalData.timestamp >= now - timedelta(days=30)
                ).order_by(HistoricalData.timestamp.asc()).all()
                
                # 3 months data
                data_3m = self.db.query(HistoricalData).filter(
                    HistoricalData.symbol == symbol,
                    HistoricalData.timestamp >= now - timedelta(days=90)
                ).order_by(HistoricalData.timestamp.asc()).all()
                
                # 6 months data
                data_6m = self.db.query(HistoricalData).filter(
                    HistoricalData.symbol == symbol,
                    HistoricalData.timestamp >= now - timedelta(days=180)
                ).order_by(HistoricalData.timestamp.asc()).all()
                
                if len(data_1m) < 10 or len(data_3m) < 20 or len(data_6m) < 30:
                    continue
                
                # Calculate performance
                current_price = data_1m[-1].close_price
                
                # 1 month performance
                price_1m_ago = data_1m[0].close_price
                performance_1m = (current_price / price_1m_ago - 1) if price_1m_ago > 0 else 0
                
                # 3 months performance
                price_3m_ago = data_3m[0].close_price
                performance_3m = (current_price / price_3m_ago - 1) if price_3m_ago > 0 else 0
                
                # 6 months performance
                price_6m_ago = data_6m[0].close_price
                performance_6m = (current_price / price_6m_ago - 1) if price_6m_ago > 0 else 0
                
                # Check if meets momentum criteria
                if (performance_1m >= min_performance_1m and 
                    performance_3m >= min_performance_3m and 
                    performance_6m >= min_performance_6m):
                    
                    momentum_stocks.append({
                        "symbol": symbol,
                        "current_price": current_price,
                        "performance_1m": performance_1m,
                        "performance_3m": performance_3m,
                        "performance_6m": performance_6m,
                        "total_performance": performance_1m + performance_3m + performance_6m
                    })
            
            # Sort by total performance
            momentum_stocks.sort(key=lambda x: x['total_performance'], reverse=True)
            
            return momentum_stocks[:20]  # Return top 20 momentum stocks
            
        except Exception as e:
            logger.error(f"Error screening momentum stocks: {e}")
            return []
    
    async def analyze_breakout_setup(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze breakout setup untuk saham tertentu
        Mencari: momentum leg -> konsolidasi -> breakout dengan volume
        """
        try:
            # Get recent data (last 3 months)
            data = self.db.query(HistoricalData).filter(
                HistoricalData.symbol == symbol,
                HistoricalData.timestamp >= datetime.now() - timedelta(days=90)
            ).order_by(HistoricalData.timestamp.asc()).all()
            
            if len(data) < 50:
                return {"setup_found": False, "reason": "Insufficient data"}
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': d.timestamp,
                'close': d.close_price,
                'high': d.high_price,
                'low': d.low_price,
                'volume': d.volume
            } for d in data])
            
            # Calculate indicators
            df['ema_10'] = df['close'].ewm(span=10).mean()
            df['ema_20'] = df['close'].ewm(span=20).mean()
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Find momentum leg (recent strong move)
            recent_30_days = df.tail(30)
            momentum_leg = self._find_momentum_leg(recent_30_days)
            
            if not momentum_leg:
                return {"setup_found": False, "reason": "No momentum leg found"}
            
            # Find consolidation phase
            consolidation = self._find_consolidation_phase(df, momentum_leg)
            
            if not consolidation:
                return {"setup_found": False, "reason": "No consolidation found"}
            
            # Check for breakout
            breakout = self._check_breakout(df, consolidation)
            
            return {
                "setup_found": breakout is not None,
                "momentum_leg": momentum_leg,
                "consolidation": consolidation,
                "breakout": breakout,
                "current_price": df['close'].iloc[-1],
                "ema_10": df['ema_10'].iloc[-1],
                "ema_20": df['ema_20'].iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing breakout setup for {symbol}: {e}")
            return {"setup_found": False, "reason": f"Error: {str(e)}"}
    
    def _find_momentum_leg(self, df: pd.DataFrame) -> Optional[Dict]:
        """Find momentum leg (30-100% move in short period)"""
        if len(df) < 10:
            return None
        
        # Look for significant moves in last 20 days
        for i in range(10, len(df)):
            start_price = df['close'].iloc[i-10]
            end_price = df['close'].iloc[i]
            move_percent = (end_price / start_price - 1) * 100
            
            if 30 <= move_percent <= 100:  # 30-100% move
                return {
                    "start_date": df['timestamp'].iloc[i-10],
                    "end_date": df['timestamp'].iloc[i],
                    "start_price": start_price,
                    "end_price": end_price,
                    "move_percent": move_percent
                }
        
        return None
    
    def _find_consolidation_phase(self, df: pd.DataFrame, momentum_leg: Dict) -> Optional[Dict]:
        """Find consolidation phase after momentum leg"""
        momentum_end_idx = df[df['timestamp'] == momentum_leg['end_date']].index[0]
        
        # Look for consolidation in next 20-30 days
        consolidation_data = df.iloc[momentum_end_idx:momentum_end_idx+30]
        
        if len(consolidation_data) < 10:
            return None
        
        # Check if price is consolidating (tight range, declining volume)
        high_price = consolidation_data['high'].max()
        low_price = consolidation_data['low'].min()
        range_percent = (high_price - low_price) / low_price * 100
        
        # Consolidation should be tight (less than 15% range)
        if range_percent > 15:
            return None
        
        # Volume should be declining
        volume_trend = consolidation_data['volume'].iloc[-5:].mean() / consolidation_data['volume'].iloc[:5].mean()
        
        if volume_trend > 0.8:  # Volume not declining enough
            return None
        
        return {
            "start_date": consolidation_data['timestamp'].iloc[0],
            "end_date": consolidation_data['timestamp'].iloc[-1],
            "high": high_price,
            "low": low_price,
            "range_percent": range_percent,
            "volume_trend": volume_trend
        }
    
    def _check_breakout(self, df: pd.DataFrame, consolidation: Dict) -> Optional[Dict]:
        """Check for breakout from consolidation"""
        consolidation_end_idx = df[df['timestamp'] == consolidation['end_date']].index[0]
        
        # Check next 5 days for breakout
        breakout_data = df.iloc[consolidation_end_idx:consolidation_end_idx+5]
        
        if len(breakout_data) < 2:
            return None
        
        # Look for price breaking above consolidation high with volume
        for i in range(1, len(breakout_data)):
            current_price = breakout_data['close'].iloc[i]
            current_volume = breakout_data['volume'].iloc[i]
            avg_volume = breakout_data['volume'].iloc[:i].mean()
            
            # Breakout: price above consolidation high + volume spike
            if (current_price > consolidation['high'] and 
                current_volume > avg_volume * 1.5):
                
                return {
                    "date": breakout_data['timestamp'].iloc[i],
                    "price": current_price,
                    "volume": current_volume,
                    "volume_ratio": current_volume / avg_volume,
                    "breakout_level": consolidation['high']
                }
        
        return None
    
    async def calculate_position_size(self, portfolio_id: int, symbol: str, 
                                    entry_price: float, stop_loss: float) -> Dict[str, Any]:
        """
        Calculate position size berdasarkan risk per trade (0.25%-1%)
        """
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Calculate risk per share
            risk_per_share = entry_price - stop_loss
            
            if risk_per_share <= 0:
                return {"error": "Invalid stop loss level"}
            
            # Calculate position size based on risk per trade
            portfolio_value = portfolio.total_value
            risk_amount = portfolio_value * self.risk_per_trade_max  # Use max risk (1%)
            
            # Calculate shares based on risk
            shares_by_risk = int(risk_amount / risk_per_share)
            
            # Calculate position value
            position_value = shares_by_risk * entry_price
            
            # Check position size limit (10% max)
            max_position_value = portfolio_value * self.max_position_size
            max_shares = int(max_position_value / entry_price)
            
            # Use smaller of the two
            final_shares = min(shares_by_risk, max_shares)
            final_position_value = final_shares * entry_price
            
            return {
                "shares": final_shares,
                "position_value": final_position_value,
                "risk_amount": final_shares * risk_per_share,
                "risk_percent": (final_shares * risk_per_share) / portfolio_value * 100,
                "position_percent": final_position_value / portfolio_value * 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def generate_trading_signals(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        Generate trading signals berdasarkan strategi Kulamagi
        """
        try:
            signals = []
            
            # 1. Check market condition
            market_condition = await self.check_market_condition()
            
            if not market_condition["market_favorable"]:
                return [{
                    "type": "market_filter",
                    "action": "wait",
                    "reason": "Market not favorable - NASDAQ not above EMA 10 > EMA 20",
                    "market_data": market_condition
                }]
            
            # 2. Screen momentum stocks
            momentum_stocks = await self.screen_momentum_stocks()
            
            if not momentum_stocks:
                return [{
                    "type": "momentum_filter",
                    "action": "wait",
                    "reason": "No momentum stocks found",
                    "market_data": market_condition
                }]
            
            # 3. Analyze breakout setups for top momentum stocks
            for stock in momentum_stocks[:10]:  # Analyze top 10
                setup = await self.analyze_breakout_setup(stock["symbol"])
                
                if setup["setup_found"]:
                    # Calculate position size
                    entry_price = setup["current_price"]
                    stop_loss = setup["consolidation"]["low"]  # Stop below consolidation
                    
                    position_size = await self.calculate_position_size(
                        portfolio_id, stock["symbol"], entry_price, stop_loss
                    )
                    
                    if "error" not in position_size:
                        signals.append({
                            "type": "kulamagi_signal",
                            "action": "buy",
                            "symbol": stock["symbol"],
                            "entry_price": entry_price,
                            "stop_loss": stop_loss,
                            "target_price": entry_price * 1.5,  # 50% target
                            "position_size": position_size,
                            "setup": setup,
                            "momentum": stock
                        })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return [{"type": "error", "action": "wait", "reason": f"Error: {str(e)}"}]
    
    async def manage_exit_strategy(self, position: Position) -> Dict[str, Any]:
        """
        Manage exit strategy dengan trailing stop berdasarkan EMA 10/20
        """
        try:
            # Get recent data for the position
            data = self.db.query(HistoricalData).filter(
                HistoricalData.symbol == position.symbol,
                HistoricalData.timestamp >= datetime.now() - timedelta(days=30)
            ).order_by(HistoricalData.timestamp.desc()).limit(20).all()
            
            if len(data) < 10:
                return {"action": "hold", "reason": "Insufficient data"}
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'timestamp': d.timestamp,
                'close': d.close_price,
                'high': d.high_price,
                'low': d.low_price
            } for d in data])
            
            # Calculate EMAs
            df['ema_10'] = df['close'].ewm(span=10).mean()
            df['ema_20'] = df['close'].ewm(span=20).mean()
            
            current_price = df['close'].iloc[0]  # Most recent
            ema_10 = df['ema_10'].iloc[0]
            ema_20 = df['ema_20'].iloc[0]
            
            # Check if price closed below EMA 10 or EMA 20
            if current_price < ema_10:
                return {
                    "action": "sell",
                    "reason": f"Price {current_price:.2f} below EMA 10 {ema_10:.2f}",
                    "exit_price": current_price
                }
            elif current_price < ema_20:
                return {
                    "action": "sell",
                    "reason": f"Price {current_price:.2f} below EMA 20 {ema_20:.2f}",
                    "exit_price": current_price
                }
            
            # Check for partial profit taking (after 3-5 days)
            days_held = (datetime.now() - position.created_at).days
            if days_held >= 3 and position.quantity > 0:
                # Take 1/3 profit
                partial_quantity = int(position.quantity * self.partial_profit_ratio)
                return {
                    "action": "partial_sell",
                    "quantity": partial_quantity,
                    "reason": f"Partial profit taking after {days_held} days",
                    "exit_price": current_price
                }
            
            return {
                "action": "hold",
                "reason": "Position still favorable",
                "current_price": current_price,
                "ema_10": ema_10,
                "ema_20": ema_20
            }
            
        except Exception as e:
            logger.error(f"Error managing exit strategy: {e}")
            return {"action": "hold", "reason": f"Error: {str(e)}"}
