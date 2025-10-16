"""
Watchlist API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date, timedelta
from app.database import get_db
from app.services.watchlist_service import WatchlistService
from app.models.watchlist import WatchlistType
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

# Pydantic schemas
class CreateWatchlistRequest(BaseModel):
    name: str
    description: Optional[str] = None
    watchlist_type: str = "personal"  # personal, shared, public
    is_public: bool = False
    default_columns: Optional[List[str]] = None

class AddSymbolRequest(BaseModel):
    symbol: str
    exchange: Optional[str] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None

class CreateAlertRequest(BaseModel):
    item_id: str
    alert_type: str  # price, volume, rsi, custom
    condition: str  # above, below, equals
    threshold_value: float
    notify_email: bool = False
    cooldown_minutes: int = 60

class WatchlistResponse(BaseModel):
    watchlist_id: str
    name: str
    description: Optional[str]
    watchlist_type: str
    is_public: bool
    total_items: int
    last_updated: Optional[str]
    items: List[Dict]

@router.post("/create")
async def create_watchlist(
    watchlist_request: CreateWatchlistRequest,
    db: Session = Depends(get_db)
):
    """Create new watchlist"""
    try:
        # Validate watchlist type
        valid_types = [t.value for t in WatchlistType]
        if watchlist_request.watchlist_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid watchlist type. Valid options: {valid_types}")
        
        # Convert to enum
        watchlist_type = WatchlistType(watchlist_request.watchlist_type)
        
        # Create watchlist service
        watchlist_service = WatchlistService(db)
        
        # Create watchlist
        result = watchlist_service.create_watchlist(
            name=watchlist_request.name,
            description=watchlist_request.description,
            watchlist_type=watchlist_type,
            is_public=watchlist_request.is_public,
            default_columns=watchlist_request.default_columns
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{watchlist_id}/add-symbol")
async def add_symbol_to_watchlist(
    watchlist_id: str,
    symbol_request: AddSymbolRequest,
    db: Session = Depends(get_db)
):
    """Add symbol to watchlist"""
    try:
        watchlist_service = WatchlistService(db)
        result = watchlist_service.add_symbol_to_watchlist(
            watchlist_id=watchlist_id,
            symbol=symbol_request.symbol,
            exchange=symbol_request.exchange,
            sector=symbol_request.sector,
            market_cap=symbol_request.market_cap
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding symbol to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{watchlist_id}/remove-symbol/{symbol}")
async def remove_symbol_from_watchlist(
    watchlist_id: str,
    symbol: str,
    db: Session = Depends(get_db)
):
    """Remove symbol from watchlist"""
    try:
        watchlist_service = WatchlistService(db)
        result = watchlist_service.remove_symbol_from_watchlist(watchlist_id, symbol)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing symbol from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist_data(
    watchlist_id: str,
    include_indicators: bool = Query(True, description="Include technical indicators"),
    db: Session = Depends(get_db)
):
    """Get watchlist data with real-time updates"""
    try:
        watchlist_service = WatchlistService(db)
        result = watchlist_service.get_watchlist_data(watchlist_id, include_indicators)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return WatchlistResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting watchlist data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{watchlist_id}/alerts")
async def create_watchlist_alert(
    watchlist_id: str,
    alert_request: CreateAlertRequest,
    db: Session = Depends(get_db)
):
    """Create watchlist alert"""
    try:
        watchlist_service = WatchlistService(db)
        result = watchlist_service.create_watchlist_alert(
            watchlist_id=watchlist_id,
            item_id=alert_request.item_id,
            alert_type=alert_request.alert_type,
            condition=alert_request.condition,
            threshold_value=alert_request.threshold_value,
            notify_email=alert_request.notify_email,
            cooldown_minutes=alert_request.cooldown_minutes
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating watchlist alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{watchlist_id}/alerts/check")
async def check_watchlist_alerts(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Check and trigger watchlist alerts"""
    try:
        watchlist_service = WatchlistService(db)
        alerts = watchlist_service.check_watchlist_alerts(watchlist_id)
        
        return {
            "watchlist_id": watchlist_id,
            "triggered_alerts": alerts,
            "total_triggered": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Error checking watchlist alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{watchlist_id}/performance")
async def get_watchlist_performance(
    watchlist_id: str,
    days: int = Query(30, description="Number of days for performance calculation"),
    db: Session = Depends(get_db)
):
    """Get watchlist performance metrics"""
    try:
        watchlist_service = WatchlistService(db)
        result = watchlist_service.get_watchlist_performance(watchlist_id, days)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting watchlist performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_watchlists(
    limit: int = Query(50, description="Maximum number of watchlists to return"),
    offset: int = Query(0, description="Number of watchlists to skip"),
    db: Session = Depends(get_db)
):
    """List all watchlists"""
    try:
        watchlist_service = WatchlistService(db)
        watchlists = watchlist_service.list_watchlists(limit=limit, offset=offset)
        
        return {
            "watchlists": watchlists,
            "total_count": len(watchlists)
        }
        
    except Exception as e:
        logger.error(f"Error listing watchlists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Delete watchlist"""
    try:
        watchlist_service = WatchlistService(db)
        result = watchlist_service.delete_watchlist(watchlist_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{watchlist_id}/update")
async def update_watchlist_data(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Manually update watchlist data"""
    try:
        watchlist_service = WatchlistService(db)
        watchlist_service._update_watchlist_data(watchlist_id)
        
        return {
            "watchlist_id": watchlist_id,
            "status": "updated",
            "message": "Watchlist data updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating watchlist data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{watchlist_id}/alerts")
async def get_watchlist_alerts(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Get all alerts for a watchlist"""
    try:
        from app.models.watchlist import WatchlistAlert
        
        alerts = db.query(WatchlistAlert).filter(
            WatchlistAlert.watchlist_id == watchlist_id
        ).all()
        
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "alert_id": alert.alert_id,
                "item_id": alert.item_id,
                "alert_type": alert.alert_type,
                "condition": alert.condition,
                "threshold_value": alert.threshold_value,
                "is_active": alert.is_active,
                "is_triggered": alert.is_triggered,
                "trigger_count": alert.trigger_count,
                "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None,
                "notify_email": alert.notify_email,
                "cooldown_minutes": alert.cooldown_minutes,
                "created_at": alert.created_at.isoformat()
            })
        
        return {
            "watchlist_id": watchlist_id,
            "alerts": alert_list,
            "total_count": len(alert_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting watchlist alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{watchlist_id}/alerts/{alert_id}/toggle")
async def toggle_alert(
    watchlist_id: str,
    alert_id: str,
    is_active: bool = Body(..., description="Alert active status"),
    db: Session = Depends(get_db)
):
    """Toggle alert active status"""
    try:
        from app.models.watchlist import WatchlistAlert
        
        alert = db.query(WatchlistAlert).filter(
            WatchlistAlert.alert_id == alert_id,
            WatchlistAlert.watchlist_id == watchlist_id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_active = is_active
        db.commit()
        
        return {
            "alert_id": alert_id,
            "is_active": is_active,
            "message": f"Alert {'activated' if is_active else 'deactivated'} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling alert: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{watchlist_id}/quick-actions")
async def get_quick_actions(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Get quick action buttons for watchlist"""
    try:
        from app.models.watchlist import WatchlistQuickAction
        
        actions = db.query(WatchlistQuickAction).filter(
            WatchlistQuickAction.watchlist_id == watchlist_id,
            WatchlistQuickAction.is_visible == True
        ).order_by(WatchlistQuickAction.created_at).all()
        
        action_list = []
        for action in actions:
            action_list.append({
                "action_id": action.action_id,
                "action_name": action.action_name,
                "action_type": action.action_type,
                "button_text": action.button_text,
                "button_color": action.button_color,
                "button_icon": action.button_icon,
                "action_url": action.action_url,
                "action_params": action.action_params
            })
        
        return {
            "watchlist_id": watchlist_id,
            "quick_actions": action_list,
            "total_count": len(action_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting quick actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{watchlist_id}/filters")
async def get_watchlist_filters(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Get watchlist filters"""
    try:
        from app.models.watchlist import WatchlistFilter
        
        filters = db.query(WatchlistFilter).filter(
            WatchlistFilter.watchlist_id == watchlist_id
        ).all()
        
        filter_list = []
        for filter_item in filters:
            filter_list.append({
                "filter_id": filter_item.filter_id,
                "filter_name": filter_item.filter_name,
                "filter_type": filter_item.filter_type,
                "filter_condition": filter_item.filter_condition,
                "filter_value": filter_item.filter_value,
                "is_active": filter_item.is_active,
                "is_global": filter_item.is_global,
                "created_at": filter_item.created_at.isoformat()
            })
        
        return {
            "watchlist_id": watchlist_id,
            "filters": filter_list,
            "total_count": len(filter_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting watchlist filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{watchlist_id}/columns")
async def get_watchlist_columns(
    watchlist_id: str,
    db: Session = Depends(get_db)
):
    """Get custom watchlist columns"""
    try:
        from app.models.watchlist import WatchlistColumn
        
        columns = db.query(WatchlistColumn).filter(
            WatchlistColumn.watchlist_id == watchlist_id
        ).order_by(WatchlistColumn.sort_order).all()
        
        column_list = []
        for column in columns:
            column_list.append({
                "column_id": column.column_id,
                "column_name": column.column_name,
                "column_type": column.column_type,
                "data_source": column.data_source,
                "is_visible": column.is_visible,
                "sort_order": column.sort_order,
                "width": column.width,
                "calculation_formula": column.calculation_formula,
                "update_frequency": column.update_frequency
            })
        
        return {
            "watchlist_id": watchlist_id,
            "columns": column_list,
            "total_count": len(column_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting watchlist columns: {e}")
        raise HTTPException(status_code=500, detail=str(e))
