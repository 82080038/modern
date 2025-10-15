"""
Watchlist Service untuk Advanced Watchlist Features
"""
from sqlalchemy.orm import Session
from app.models.watchlist import (
    Watchlist, WatchlistItem, WatchlistAlert, WatchlistPerformance, 
    WatchlistColumn, WatchlistFilter, WatchlistQuickAction, WatchlistType
)
from app.services.data_service import DataService
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import logging
import json

logger = logging.getLogger(__name__)

class WatchlistService:
    """Service untuk watchlist operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
    
    def create_watchlist(self,
                        name: str,
                        description: str = None,
                        watchlist_type: WatchlistType = WatchlistType.PERSONAL,
                        is_public: bool = False,
                        default_columns: List[str] = None) -> Dict:
        """Create new watchlist"""
        try:
            # Generate unique watchlist ID
            watchlist_id = f"WL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Default columns
            if not default_columns:
                default_columns = ["symbol", "current_price", "price_change_percent", "volume", "rsi"]
            
            # Create watchlist
            watchlist = Watchlist(
                watchlist_id=watchlist_id,
                name=name,
                description=description,
                watchlist_type=watchlist_type,
                is_public=is_public,
                default_columns=default_columns
            )
            
            self.db.add(watchlist)
            self.db.commit()
            
            return {
                "watchlist_id": watchlist_id,
                "name": name,
                "status": "created",
                "message": "Watchlist created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating watchlist: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def add_symbol_to_watchlist(self,
                               watchlist_id: str,
                               symbol: str,
                               exchange: str = None,
                               sector: str = None,
                               market_cap: float = None) -> Dict:
        """Add symbol to watchlist"""
        try:
            # Check if watchlist exists
            watchlist = self.db.query(Watchlist).filter(Watchlist.watchlist_id == watchlist_id).first()
            if not watchlist:
                return {"error": "Watchlist not found"}
            
            # Check if symbol already exists
            existing_item = self.db.query(WatchlistItem).filter(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.symbol == symbol.upper()
            ).first()
            
            if existing_item:
                return {"error": "Symbol already in watchlist"}
            
            # Generate unique item ID
            item_id = f"WI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create watchlist item
            item = WatchlistItem(
                item_id=item_id,
                watchlist_id=watchlist_id,
                symbol=symbol.upper(),
                exchange=exchange,
                sector=sector,
                market_cap=market_cap
            )
            
            self.db.add(item)
            
            # Update watchlist total items
            watchlist.total_items += 1
            watchlist.last_updated = datetime.now()
            
            self.db.commit()
            
            # Fetch initial data
            self._update_watchlist_item_data(item_id)
            
            return {
                "item_id": item_id,
                "symbol": symbol.upper(),
                "status": "added",
                "message": "Symbol added to watchlist successfully"
            }
            
        except Exception as e:
            logger.error(f"Error adding symbol to watchlist: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def remove_symbol_from_watchlist(self, watchlist_id: str, symbol: str) -> Dict:
        """Remove symbol from watchlist"""
        try:
            # Find and remove item
            item = self.db.query(WatchlistItem).filter(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.symbol == symbol.upper()
            ).first()
            
            if not item:
                return {"error": "Symbol not found in watchlist"}
            
            # Remove related alerts
            self.db.query(WatchlistAlert).filter(
                WatchlistAlert.item_id == item.item_id
            ).delete()
            
            # Remove item
            self.db.delete(item)
            
            # Update watchlist total items
            watchlist = self.db.query(Watchlist).filter(Watchlist.watchlist_id == watchlist_id).first()
            if watchlist:
                watchlist.total_items = max(0, watchlist.total_items - 1)
                watchlist.last_updated = datetime.now()
            
            self.db.commit()
            
            return {
                "symbol": symbol.upper(),
                "status": "removed",
                "message": "Symbol removed from watchlist successfully"
            }
            
        except Exception as e:
            logger.error(f"Error removing symbol from watchlist: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_watchlist_data(self, watchlist_id: str, include_indicators: bool = True) -> Dict:
        """Get watchlist data with real-time updates"""
        try:
            # Get watchlist
            watchlist = self.db.query(Watchlist).filter(Watchlist.watchlist_id == watchlist_id).first()
            if not watchlist:
                return {"error": "Watchlist not found"}
            
            # Get watchlist items
            items = self.db.query(WatchlistItem).filter(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.is_active == True
            ).all()
            
            # Update data for all items
            if watchlist.auto_update:
                self._update_watchlist_data(watchlist_id)
            
            # Format items data
            items_data = []
            for item in items:
                item_data = {
                    "item_id": item.item_id,
                    "symbol": item.symbol,
                    "exchange": item.exchange,
                    "sector": item.sector,
                    "market_cap": item.market_cap,
                    "current_price": item.current_price,
                    "price_change": item.price_change,
                    "price_change_percent": item.price_change_percent,
                    "volume": item.volume,
                    "last_updated": item.last_updated.isoformat() if item.last_updated else None
                }
                
                # Add technical indicators if requested
                if include_indicators:
                    item_data.update({
                        "rsi": item.rsi,
                        "macd": item.macd,
                        "sma_20": item.sma_20,
                        "sma_50": item.sma_50,
                        "sma_200": item.sma_200,
                        "custom_metrics": item.custom_metrics
                    })
                
                items_data.append(item_data)
            
            return {
                "watchlist_id": watchlist_id,
                "name": watchlist.name,
                "description": watchlist.description,
                "total_items": len(items_data),
                "last_updated": watchlist.last_updated.isoformat() if watchlist.last_updated else None,
                "items": items_data
            }
            
        except Exception as e:
            logger.error(f"Error getting watchlist data: {e}")
            return {"error": str(e)}
    
    def _update_watchlist_data(self, watchlist_id: str):
        """Update all watchlist items with latest data"""
        try:
            items = self.db.query(WatchlistItem).filter(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.is_active == True
            ).all()
            
            for item in items:
                self._update_watchlist_item_data(item.item_id)
            
            # Update watchlist last_updated
            watchlist = self.db.query(Watchlist).filter(Watchlist.watchlist_id == watchlist_id).first()
            if watchlist:
                watchlist.last_updated = datetime.now()
                self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating watchlist data: {e}")
    
    def _update_watchlist_item_data(self, item_id: str):
        """Update individual watchlist item data"""
        try:
            item = self.db.query(WatchlistItem).filter(WatchlistItem.item_id == item_id).first()
            if not item:
                return
            
            # Get real-time data
            price_data = self.data_service.get_real_time_price(item.symbol)
            if price_data:
                item.current_price = price_data.get('price')
                item.price_change = price_data.get('change')
                item.price_change_percent = price_data.get('change_percent')
                item.volume = price_data.get('volume')
            
            # Calculate technical indicators
            historical_data = self.data_service.get_historical_candlestick_data(
                item.symbol, '1D', datetime.now() - timedelta(days=200), datetime.now()
            )
            
            if historical_data and len(historical_data) >= 20:
                prices = [bar['close'] for bar in historical_data]
                
                # Calculate RSI
                item.rsi = self._calculate_rsi(prices, 14)
                
                # Calculate MACD
                macd_data = self._calculate_macd(prices, 12, 26, 9)
                item.macd = macd_data.get('macd')
                
                # Calculate SMAs
                item.sma_20 = self._calculate_sma(prices, 20)
                item.sma_50 = self._calculate_sma(prices, 50)
                item.sma_200 = self._calculate_sma(prices, 200)
            
            item.last_updated = datetime.now()
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating watchlist item data: {e}")
    
    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        if len(gains) < period:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float], fast: int, slow: int, signal: int) -> Dict:
        """Calculate MACD"""
        if len(prices) < slow:
            return {"macd": 0}
        
        fast_ema = self._calculate_ema(prices, fast)
        slow_ema = self._calculate_ema(prices, slow)
        
        macd = fast_ema - slow_ema
        
        return {"macd": macd}
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate SMA"""
        if len(prices) < period:
            return 0
        return sum(prices[-period:]) / period
    
    def create_watchlist_alert(self,
                              watchlist_id: str,
                              item_id: str,
                              alert_type: str,
                              condition: str,
                              threshold_value: float,
                              notify_email: bool = False,
                              cooldown_minutes: int = 60) -> Dict:
        """Create watchlist alert"""
        try:
            # Generate unique alert ID
            alert_id = f"WA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create alert
            alert = WatchlistAlert(
                alert_id=alert_id,
                watchlist_id=watchlist_id,
                item_id=item_id,
                alert_type=alert_type,
                condition=condition,
                threshold_value=threshold_value,
                notify_email=notify_email,
                cooldown_minutes=cooldown_minutes
            )
            
            self.db.add(alert)
            self.db.commit()
            
            return {
                "alert_id": alert_id,
                "status": "created",
                "message": "Alert created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating watchlist alert: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def check_watchlist_alerts(self, watchlist_id: str) -> List[Dict]:
        """Check and trigger watchlist alerts"""
        try:
            alerts = self.db.query(WatchlistAlert).filter(
                WatchlistAlert.watchlist_id == watchlist_id,
                WatchlistAlert.is_active == True,
                WatchlistAlert.is_triggered == False
            ).all()
            
            triggered_alerts = []
            
            for alert in alerts:
                # Get current item data
                item = self.db.query(WatchlistItem).filter(WatchlistItem.item_id == alert.item_id).first()
                if not item:
                    continue
                
                # Check alert conditions
                should_trigger = False
                current_value = None
                
                if alert.alert_type == "price":
                    current_value = item.current_price
                    if alert.condition == "above" and current_value > alert.threshold_value:
                        should_trigger = True
                    elif alert.condition == "below" and current_value < alert.threshold_value:
                        should_trigger = True
                
                elif alert.alert_type == "volume":
                    current_value = item.volume
                    if alert.condition == "above" and current_value > alert.threshold_value:
                        should_trigger = True
                
                elif alert.alert_type == "rsi":
                    current_value = item.rsi
                    if alert.condition == "above" and current_value > alert.threshold_value:
                        should_trigger = True
                    elif alert.condition == "below" and current_value < alert.threshold_value:
                        should_trigger = True
                
                if should_trigger:
                    # Check cooldown
                    if alert.last_triggered:
                        time_since_last = datetime.now() - alert.last_triggered
                        if time_since_last.total_seconds() < (alert.cooldown_minutes * 60):
                            continue
                    
                    # Trigger alert
                    alert.is_triggered = True
                    alert.trigger_count += 1
                    alert.last_triggered = datetime.now()
                    
                    triggered_alerts.append({
                        "alert_id": alert.alert_id,
                        "symbol": item.symbol,
                        "alert_type": alert.alert_type,
                        "condition": alert.condition,
                        "threshold_value": alert.threshold_value,
                        "current_value": current_value,
                        "triggered_at": datetime.now().isoformat()
                    })
            
            self.db.commit()
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking watchlist alerts: {e}")
            return []
    
    def get_watchlist_performance(self, watchlist_id: str, days: int = 30) -> Dict:
        """Get watchlist performance metrics"""
        try:
            # Get performance data
            performance_data = self.db.query(WatchlistPerformance).filter(
                WatchlistPerformance.watchlist_id == watchlist_id,
                WatchlistPerformance.date >= date.today() - timedelta(days=days)
            ).order_by(WatchlistPerformance.date.desc()).all()
            
            if not performance_data:
                return {"error": "No performance data available"}
            
            # Calculate metrics
            total_return = 0
            if len(performance_data) > 1:
                total_return = (performance_data[0].total_value - performance_data[-1].total_value) / performance_data[-1].total_value
            
            # Get best and worst performers
            best_performer = performance_data[0].top_performer if performance_data else None
            worst_performer = performance_data[0].worst_performer if performance_data else None
            
            return {
                "watchlist_id": watchlist_id,
                "period_days": days,
                "total_return": total_return,
                "current_value": performance_data[0].total_value if performance_data else 0,
                "best_performer": best_performer,
                "worst_performer": worst_performer,
                "performance_data": [
                    {
                        "date": p.date.isoformat(),
                        "total_value": p.total_value,
                        "total_change": p.total_change,
                        "total_change_percent": p.total_change_percent,
                        "top_performer": p.top_performer,
                        "worst_performer": p.worst_performer
                    }
                    for p in performance_data
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting watchlist performance: {e}")
            return {"error": str(e)}
    
    def list_watchlists(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all watchlists"""
        try:
            watchlists = self.db.query(Watchlist).order_by(Watchlist.created_at.desc()).offset(offset).limit(limit).all()
            
            watchlist_list = []
            for watchlist in watchlists:
                watchlist_list.append({
                    "watchlist_id": watchlist.watchlist_id,
                    "name": watchlist.name,
                    "description": watchlist.description,
                    "watchlist_type": watchlist.watchlist_type.value,
                    "is_public": watchlist.is_public,
                    "total_items": watchlist.total_items,
                    "last_updated": watchlist.last_updated.isoformat() if watchlist.last_updated else None,
                    "created_at": watchlist.created_at.isoformat()
                })
            
            return watchlist_list
            
        except Exception as e:
            logger.error(f"Error listing watchlists: {e}")
            return []
    
    def delete_watchlist(self, watchlist_id: str) -> Dict:
        """Delete watchlist and all related data"""
        try:
            # Delete related records
            self.db.query(WatchlistAlert).filter(WatchlistAlert.watchlist_id == watchlist_id).delete()
            self.db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).delete()
            self.db.query(WatchlistPerformance).filter(WatchlistPerformance.watchlist_id == watchlist_id).delete()
            self.db.query(WatchlistColumn).filter(WatchlistColumn.watchlist_id == watchlist_id).delete()
            self.db.query(WatchlistFilter).filter(WatchlistFilter.watchlist_id == watchlist_id).delete()
            self.db.query(WatchlistQuickAction).filter(WatchlistQuickAction.watchlist_id == watchlist_id).delete()
            
            # Delete watchlist
            deleted_count = self.db.query(Watchlist).filter(Watchlist.watchlist_id == watchlist_id).delete()
            
            if deleted_count == 0:
                return {"error": "Watchlist not found"}
            
            self.db.commit()
            
            return {
                "watchlist_id": watchlist_id,
                "status": "deleted",
                "message": "Watchlist deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting watchlist: {e}")
            self.db.rollback()
            return {"error": str(e)}
